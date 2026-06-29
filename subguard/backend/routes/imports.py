from flask import Blueprint, jsonify, request

from services.csv_import import parse_csv_subscriptions
from services.image_import import parse_bill_image
from services.text_import import parse_bill_text


imports_bp = Blueprint("imports", __name__, url_prefix="/api/import")


@imports_bp.post("/text")
def import_text():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "请提交 JSON 请求体。"}), 400

    text = payload.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "请提供需要识别的账单文本。"}), 400

    try:
        subscription = parse_bill_text(text)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    return jsonify({"subscription": subscription})


@imports_bp.post("/image")
def import_image():
    if "file" not in request.files:
        return jsonify({"error": "请上传账单截图文件。"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "请选择需要上传的图片。"}), 400

    try:
        result = parse_bill_image(file)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 501
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 422

    return jsonify(result)


@imports_bp.post("/csv")
def import_csv():
    if "file" not in request.files:
        return jsonify({"error": "请上传 CSV 文件，字段需包含 date、merchant、amount、payment_method。"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "请选择需要上传的 CSV 文件。"}), 400

    try:
        subscriptions = parse_csv_subscriptions(file)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "CSV 解析失败，请确认文件格式和字段内容正确。"}), 400

    return jsonify({"subscriptions": subscriptions, "count": len(subscriptions)})
