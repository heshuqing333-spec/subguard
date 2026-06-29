from datetime import timedelta
from io import BytesIO

import pandas as pd


REQUIRED_COLUMNS = {"date", "merchant", "amount", "payment_method"}
CYCLE_CANDIDATES = [
    ("weekly", 7, 2),
    ("monthly", 30, 5),
    ("yearly", 365, 25),
]


def parse_csv_subscriptions(file_storage):
    frame = pd.read_csv(BytesIO(file_storage.read()))
    validate_columns(frame)

    frame = normalize_frame(frame)
    results = []

    for merchant, group in frame.groupby("merchant"):
        candidate = detect_subscription(merchant, group)
        if candidate:
            results.append(candidate)

    results.sort(key=lambda item: item["confidence"], reverse=True)
    return results


def validate_columns(frame):
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ValueError(f"CSV 缺少必要字段：{missing_text}")


def normalize_frame(frame):
    normalized = frame.copy()
    normalized["merchant"] = normalized["merchant"].astype(str).str.strip()
    normalized["payment_method"] = normalized["payment_method"].astype(str).str.strip()
    normalized["amount"] = pd.to_numeric(normalized["amount"], errors="coerce").abs()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    normalized = normalized.dropna(subset=["date", "merchant", "amount"])
    normalized = normalized[normalized["merchant"] != ""]
    return normalized.sort_values(["merchant", "date"])


def detect_subscription(merchant, group):
    if len(group) < 2:
        return None

    amounts = group["amount"]
    amount_diff = float(amounts.max() - amounts.min())
    if amount_diff >= 1:
        return None

    dates = group["date"].sort_values().tolist()
    intervals = [
        (dates[index] - dates[index - 1]).days
        for index in range(1, len(dates))
        if (dates[index] - dates[index - 1]).days > 0
    ]
    if not intervals:
        return None

    cycle, cycle_days, interval_gap = match_cycle(intervals)
    if cycle is None:
        return None

    last_date = dates[-1].date()
    next_due_date = last_date + timedelta(days=cycle_days)
    payment_method = group["payment_method"].mode()
    confidence = calculate_confidence(len(group), amount_diff, interval_gap)

    return {
        "name": merchant,
        "price": round(float(amounts.median()), 2),
        "cycle": cycle,
        "next_due_date": next_due_date.isoformat(),
        "payment_method": payment_method.iloc[0] if not payment_method.empty else "",
        "confidence": confidence,
        "evidence": build_evidence(group, intervals, amount_diff, cycle),
    }


def match_cycle(intervals):
    avg_interval = sum(intervals) / len(intervals)
    best_match = None

    for cycle, days, tolerance in CYCLE_CANDIDATES:
        gap = abs(avg_interval - days)
        if gap <= tolerance and all(abs(interval - days) <= tolerance for interval in intervals):
            if best_match is None or gap < best_match[2]:
                best_match = (cycle, days, gap)

    if best_match is None:
        return None, None, None
    return best_match


def calculate_confidence(count, amount_diff, interval_gap):
    score = 0.62
    score += min(count - 2, 3) * 0.06
    score += max(0, 0.15 - amount_diff * 0.08)
    score += max(0, 0.12 - interval_gap * 0.02)
    return round(min(score, 0.98), 2)


def build_evidence(group, intervals, amount_diff, cycle):
    interval_text = "、".join(str(interval) for interval in intervals)
    return (
        f"商户出现 {len(group)} 次；金额差异 {amount_diff:.2f} 元；"
        f"相邻交易间隔为 {interval_text} 天，接近 {cycle} 周期。"
    )
