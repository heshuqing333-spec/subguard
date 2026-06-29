from flask import Blueprint, jsonify, request


cancel_guides_bp = Blueprint("cancel_guides", __name__, url_prefix="/api/cancel-guides")

CANCEL_GUIDES = [
    {
        "payment_method": "微信",
        "platform_name": "微信支付",
        "guide_steps": "微信 → 我 → 服务 → 钱包 → 支付设置 → 自动续费 / 扣费服务 → 选择服务 → 关闭扣费",
    },
    {
        "payment_method": "支付宝",
        "platform_name": "支付宝",
        "guide_steps": "支付宝 → 我的 → 设置 → 支付设置 → 免密支付 / 自动扣款 → 选择服务 → 关闭服务",
    },
    {
        "payment_method": "Apple ID",
        "platform_name": "Apple ID",
        "guide_steps": "设置 → Apple ID → 订阅 → 选择订阅项目 → 取消订阅",
    },
    {
        "payment_method": "Google Play",
        "platform_name": "Google Play",
        "guide_steps": "Google Play → 个人头像 → 付款和订阅 → 订阅 → 选择项目 → 取消订阅",
    },
    {
        "payment_method": "网页支付",
        "platform_name": "网页支付",
        "guide_steps": "进入对应平台官网 → 登录账号 → 会员中心 / 账户设置 → 订阅管理 → 取消自动续费",
    },
]


@cancel_guides_bp.get("")
def list_cancel_guides():
    payment_method = request.args.get("payment_method", "").strip()
    if not payment_method:
        return jsonify({"cancel_guides": CANCEL_GUIDES, "count": len(CANCEL_GUIDES)})

    guides = [
        guide
        for guide in CANCEL_GUIDES
        if guide["payment_method"].lower() == payment_method.lower()
    ]
    return jsonify({"cancel_guides": guides, "count": len(guides)})
