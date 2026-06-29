import calendar
import re
from datetime import datetime
from decimal import Decimal


KNOWN_PLATFORMS = [
    "腾讯视频VIP",
    "腾讯视频",
    "爱奇艺",
    "优酷",
    "哔哩哔哩",
    "网易云音乐黑胶VIP",
    "网易云音乐",
    "QQ音乐",
    "iCloud+",
    "iCloud",
    "ChatGPT",
    "Notion",
    "百度网盘",
    "WPS",
    "知乎盐选",
    "B站大会员",
    "毒霸",
    "金山毒霸",
]

PAYMENT_KEYWORDS = [
    ("花呗", "支付宝"),
    ("支付宝", "支付宝"),
    ("微信", "微信"),
    ("Apple", "Apple ID"),
    ("苹果", "Apple ID"),
    ("银行卡", "银行卡"),
    ("信用卡", "银行卡"),
    ("网页支付", "网页支付"),
]

CYCLE_KEYWORDS = [
    ("连续包月", "monthly"),
    ("包月", "monthly"),
    ("月付", "monthly"),
    ("每月", "monthly"),
    ("连续包年", "yearly"),
    ("包年", "yearly"),
    ("年付", "yearly"),
    ("每年", "yearly"),
    ("包周", "weekly"),
    ("周付", "weekly"),
    ("每周", "weekly"),
    ("试用", "trial"),
]


def parse_bill_text(text):
    normalized = normalize_text(text)
    result = {
        "name": extract_name(normalized),
        "price": extract_price(normalized),
        "next_due_date": extract_next_due_date(normalized),
        "payment_method": extract_payment_method(normalized),
        "cycle": extract_cycle(normalized),
    }

    if result["next_due_date"] is None:
        result["next_due_date"] = infer_due_date_from_duration(normalized)

    result["confidence"] = calculate_confidence(result, normalized)

    if not is_recognition_successful(result):
        raise ValueError("暂未识别出明确的订阅信息，请补充商户名称、金额或续费日期后再试。")

    return result


def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r"(?<=[\u4e00-\u9fa5])\s+(?=[\u4e00-\u9fa5])", "", text.strip())
    text = re.sub(r"(?<=[\u4e00-\u9fa5])\s+(?=\d)", " ", text)
    text = re.sub(r"(?<=\d)\s+(?=[\u4e00-\u9fa5])", " ", text)
    return re.sub(r"\s+", " ", text)


def extract_name(text):
    product = extract_field_value(text, "商品说明")
    if product:
        return clean_name(product)

    for platform in KNOWN_PLATFORMS:
        if platform.lower() in text.lower():
            return platform

    merchant = extract_field_value(text, "收款方全称") or extract_field_value(text, "商户名称")
    if merchant:
        return clean_name(merchant)

    patterns = [
        r"开通(?P<name>.+?)(?:连续包月|连续包年|包月|包年|订阅)",
        r"用于\s*(?P<name>.+?)\s*订阅",
        r"扣款成功[:：]\s*(?P<name>.+?)[,，]",
        r"商户[:：]\s*(?P<name>.+?)[,，]",
        r"项目[:：]\s*(?P<name>.+?)[,，]",
        r"(?P<name>[\u4e00-\u9fa5A-Za-z0-9+\- ]{2,40})(?:会员|VIP|订阅)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return clean_name(match.group("name"))
    return None


def extract_field_value(text, field_name):
    pattern = rf"{field_name}\s*(?P<value>.+?)(?=(?:支付奖励|收单机构|收款方全称|账单分类|标签|计入收支|备注|支付时间|付款方式|商品说明|更多|$))"
    match = re.search(pattern, text)
    if match:
        return match.group("value").strip(" ：:")
    return None


def clean_name(value):
    value = value.strip(" ，,。.：:")
    value = re.sub(r"\s+", "", value)
    return value


def extract_price(text):
    patterns = [
        r"[¥￥]\s*[-−]?\s*(?P<price>\d+(?:\.\d{1,2})?)",
        r"(?<![\d:-])[-−]\s*(?P<price>\d+\.\d{1,2})(?!\d)",
        r"(?:金额|收取|扣款|支付|合计|实付)?\s*(?P<price>\d+(?:\.\d{1,2})?)\s*元",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(Decimal(match.group("price")))
    return None


def extract_next_due_date(text):
    patterns = [
        r"(?:将于|下次续订日期为|下次扣费日期为|续费日期为|到期时间|到期日期)\s*(?P<date>\d{4}[-/.]\d{1,2}[-/.]\d{1,2})",
        r"(?P<date>\d{4}[-/.]\d{1,2}[-/.]\d{1,2})\s*(?:自动续费|续订|扣费|到期)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return normalize_date(match.group("date"))
    return None


def extract_payment_time(text):
    match = re.search(r"支付时间\s*(?P<datetime>\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)", text)
    if not match:
        match = re.search(r"(?P<datetime>\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)", text)
    if not match:
        return None

    value = match.group("datetime").replace("/", "-").replace(".", "-")
    fmt = "%Y-%m-%d %H:%M:%S" if value.count(":") == 2 else "%Y-%m-%d %H:%M"
    try:
        return datetime.strptime(value, fmt).date()
    except ValueError:
        return None


def infer_due_date_from_duration(text):
    payment_date = extract_payment_time(text)
    if not payment_date:
        return None

    month_match = re.search(r"(?P<count>\d+)\s*个?月", text)
    if month_match:
        return add_months(payment_date, int(month_match.group("count"))).isoformat()

    year_match = re.search(r"(?P<count>\d+)\s*年", text)
    if year_match:
        return add_months(payment_date, int(year_match.group("count")) * 12).isoformat()

    week_match = re.search(r"(?P<count>\d+)\s*周", text)
    if week_match:
        from datetime import timedelta
        return (payment_date + timedelta(days=int(week_match.group("count")) * 7)).isoformat()

    return None


def add_months(date_value, months):
    month = date_value.month - 1 + months
    year = date_value.year + month // 12
    month = month % 12 + 1
    day = min(date_value.day, calendar.monthrange(year, month)[1])
    return date_value.replace(year=year, month=month, day=day)


def normalize_date(value):
    parts = re.split(r"[-/.]", value)
    if len(parts) != 3:
        return value
    year, month, day = parts
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"


def extract_payment_method(text):
    for keyword, payment_method in PAYMENT_KEYWORDS:
        if keyword.lower() in text.lower():
            return payment_method
    return None


def extract_cycle(text):
    for keyword, cycle in CYCLE_KEYWORDS:
        if keyword in text:
            return cycle
    if re.search(r"\d+\s*个?月|\d+\s*年|\d+\s*周", text):
        return "custom"
    if "订阅" in text or "续费" in text or "会员" in text:
        return "monthly"
    return None


def calculate_confidence(result, text):
    score = 0.0
    weights = {
        "name": 0.25,
        "price": 0.25,
        "next_due_date": 0.2,
        "payment_method": 0.15,
        "cycle": 0.15,
    }
    for field, weight in weights.items():
        if result.get(field) is not None:
            score += weight

    subscription_keywords = ["订阅", "续费", "包月", "包年", "会员", "VIP", "扣款", "自动续费", "商品说明"]
    if any(keyword.lower() in text.lower() for keyword in subscription_keywords):
        score = min(score + 0.05, 1.0)

    return round(score, 2)


def is_recognition_successful(result):
    return bool(result["name"] and result["price"] is not None and result["confidence"] >= 0.45)
