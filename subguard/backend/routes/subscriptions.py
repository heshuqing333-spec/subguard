from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from extensions import db
from models import Subscription, subscription_to_dict


subscriptions_bp = Blueprint("subscriptions", __name__, url_prefix="/api/subscriptions")

VALID_CYCLES = {"monthly", "yearly", "weekly", "trial", "custom"}
VALID_STATUSES = {"active", "paused", "cancelled"}


def error_response(message, status_code=400):
    return jsonify({"error": message}), status_code


def parse_date(value, field_name):
    if not value:
        raise ValueError(f"{field_name} is required")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from exc


def parse_price(value):
    if value is None or value == "":
        raise ValueError("price is required")
    try:
        price = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("price must be a valid number") from exc
    if price < 0:
        raise ValueError("price must be greater than or equal to 0")
    return price


def parse_int(value, field_name, default=None, minimum=None, maximum=None):
    if value is None:
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be an integer") from exc
    if minimum is not None and parsed < minimum:
        raise ValueError(f"{field_name} must be greater than or equal to {minimum}")
    if maximum is not None and parsed > maximum:
        raise ValueError(f"{field_name} must be less than or equal to {maximum}")
    return parsed


def validate_subscription_payload(payload, partial=False):
    if not isinstance(payload, dict):
        raise ValueError("request body must be a JSON object")

    data = {}

    if not partial or "name" in payload:
        name = str(payload.get("name", "")).strip()
        if not name:
            raise ValueError("name is required")
        data["name"] = name

    if not partial or "price" in payload:
        data["price"] = parse_price(payload.get("price"))

    if not partial or "cycle" in payload:
        cycle = str(payload.get("cycle", "")).strip()
        if cycle not in VALID_CYCLES:
            raise ValueError("cycle must be one of: monthly, yearly, weekly, trial, custom")
        data["cycle"] = cycle

    if not partial or "next_due_date" in payload:
        data["next_due_date"] = parse_date(payload.get("next_due_date"), "next_due_date")

    optional_string_fields = ["category", "payment_method", "notes"]
    for field in optional_string_fields:
        if field in payload:
            value = payload.get(field)
            data[field] = str(value).strip() if value is not None else None

    if "status" in payload:
        status = str(payload.get("status", "")).strip()
        if status not in VALID_STATUSES:
            raise ValueError("status must be one of: active, paused, cancelled")
        data["status"] = status

    if "usage_count" in payload:
        data["usage_count"] = parse_int(payload.get("usage_count"), "usage_count", minimum=0)

    if "importance" in payload:
        data["importance"] = parse_int(payload.get("importance"), "importance", minimum=1, maximum=5)

    return data


@subscriptions_bp.get("")
def list_subscriptions():
    subscriptions = Subscription.query.order_by(Subscription.next_due_date.asc()).all()
    return jsonify([subscription_to_dict(item) for item in subscriptions])


@subscriptions_bp.get("/upcoming")
def upcoming_subscriptions():
    days = request.args.get("days", 7)
    try:
        days = parse_int(days, "days", minimum=0)
    except ValueError as exc:
        return error_response(str(exc))

    today = date.today()
    end_date = today + timedelta(days=days)
    subscriptions = (
        Subscription.query.filter(
            Subscription.status == "active",
            Subscription.next_due_date.isnot(None),
            Subscription.next_due_date >= today,
            Subscription.next_due_date <= end_date,
        )
        .order_by(Subscription.next_due_date.asc())
        .all()
    )
    return jsonify([subscription_to_dict(item) for item in subscriptions])


@subscriptions_bp.get("/<int:subscription_id>")
def get_subscription(subscription_id):
    subscription = db.session.get(Subscription, subscription_id)
    if subscription is None:
        return error_response("subscription not found", 404)
    return jsonify(subscription_to_dict(subscription))


@subscriptions_bp.post("")
def create_subscription():
    payload = request.get_json(silent=True)
    try:
        data = validate_subscription_payload(payload)
    except ValueError as exc:
        return error_response(str(exc))

    subscription = Subscription(**data)
    db.session.add(subscription)
    db.session.commit()

    return jsonify(subscription_to_dict(subscription)), 201


@subscriptions_bp.put("/<int:subscription_id>")
def update_subscription(subscription_id):
    subscription = db.session.get(Subscription, subscription_id)
    if subscription is None:
        return error_response("subscription not found", 404)

    payload = request.get_json(silent=True)
    try:
        data = validate_subscription_payload(payload, partial=True)
    except ValueError as exc:
        return error_response(str(exc))

    for key, value in data.items():
        setattr(subscription, key, value)

    db.session.commit()

    return jsonify(subscription_to_dict(subscription))


@subscriptions_bp.delete("/<int:subscription_id>")
def delete_subscription(subscription_id):
    subscription = db.session.get(Subscription, subscription_id)
    if subscription is None:
        return error_response("subscription not found", 404)

    db.session.delete(subscription)
    db.session.commit()

    return jsonify({"message": "subscription deleted", "id": subscription_id})
