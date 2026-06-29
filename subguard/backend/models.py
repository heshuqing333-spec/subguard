from extensions import db
from services.scoring import score_subscription


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(60), nullable=False, default="其他")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cycle = db.Column(db.String(30), nullable=False, default="monthly")
    next_due_date = db.Column(db.Date, nullable=True)
    payment_method = db.Column(db.String(60), nullable=False, default="微信")
    status = db.Column(db.String(30), nullable=False, default="active")
    usage_count = db.Column(db.Integer, nullable=False, default=0)
    importance = db.Column(db.Integer, nullable=False, default=3)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )


class CancelGuide(db.Model):
    __tablename__ = "cancel_guides"

    id = db.Column(db.Integer, primary_key=True)
    payment_method = db.Column(db.String(60), nullable=False)
    platform_name = db.Column(db.String(120), nullable=False)
    guide_steps = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)


def format_date(value):
    return value.isoformat() if value else None


def format_datetime(value):
    return value.isoformat(timespec="seconds") if value else None


def subscription_to_dict(subscription):
    data = {
        "id": subscription.id,
        "name": subscription.name,
        "category": subscription.category,
        "price": float(subscription.price),
        "cycle": subscription.cycle,
        "next_due_date": format_date(subscription.next_due_date),
        "payment_method": subscription.payment_method,
        "status": subscription.status,
        "usage_count": subscription.usage_count,
        "importance": subscription.importance,
        "notes": subscription.notes,
        "created_at": format_datetime(subscription.created_at),
        "updated_at": format_datetime(subscription.updated_at),
    }
    data.update(score_subscription(subscription))
    return data


def cancel_guide_to_dict(guide):
    return {
        "id": guide.id,
        "payment_method": guide.payment_method,
        "platform_name": guide.platform_name,
        "guide_steps": guide.guide_steps,
        "created_at": format_datetime(guide.created_at),
    }
