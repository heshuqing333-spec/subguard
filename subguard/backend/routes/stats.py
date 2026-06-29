from datetime import date, timedelta

from flask import Blueprint, jsonify

from models import Subscription, subscription_to_dict


stats_bp = Blueprint("stats", __name__, url_prefix="/api/stats")


def estimate_costs(subscription):
    price = float(subscription.price or 0)
    cycle = subscription.cycle

    if cycle == "monthly":
        return price, price * 12
    if cycle == "yearly":
        return price / 12, price
    if cycle == "weekly":
        return price * 4, price * 52
    return price, price


def add_group_amount(groups, key, monthly_cost, yearly_cost):
    name = key or "未分类"
    if name not in groups:
        groups[name] = {
            "name": name,
            "monthly_cost": 0,
            "yearly_cost": 0,
            "count": 0,
        }

    groups[name]["monthly_cost"] += monthly_cost
    groups[name]["yearly_cost"] += yearly_cost
    groups[name]["count"] += 1


def rounded_stats(groups):
    return [
        {
            **value,
            "monthly_cost": round(value["monthly_cost"], 2),
            "yearly_cost": round(value["yearly_cost"], 2),
        }
        for value in sorted(groups.values(), key=lambda item: item["monthly_cost"], reverse=True)
    ]


@stats_bp.get("/summary")
def stats_summary():
    active_subscriptions = Subscription.query.filter(Subscription.status == "active").all()
    current_subscription_count = Subscription.query.filter(Subscription.status != "cancelled").count()

    total_monthly_cost = 0
    total_yearly_cost = 0
    category_groups = {}
    payment_method_groups = {}
    enriched_subscriptions = []

    for subscription in active_subscriptions:
        monthly_cost, yearly_cost = estimate_costs(subscription)
        total_monthly_cost += monthly_cost
        total_yearly_cost += yearly_cost
        add_group_amount(category_groups, subscription.category, monthly_cost, yearly_cost)
        add_group_amount(payment_method_groups, subscription.payment_method, monthly_cost, yearly_cost)

        item = subscription_to_dict(subscription)
        item["monthly_cost"] = round(monthly_cost, 2)
        item["yearly_cost"] = round(yearly_cost, 2)
        enriched_subscriptions.append(item)

    today = date.today()
    upcoming_end_date = today + timedelta(days=7)
    upcoming_count = sum(
        1
        for subscription in active_subscriptions
        if subscription.next_due_date
        and today <= subscription.next_due_date <= upcoming_end_date
    )

    top_expensive = sorted(
        enriched_subscriptions,
        key=lambda item: item["monthly_cost"],
        reverse=True,
    )[:5]

    total_monthly_cost = round(total_monthly_cost, 2)
    total_yearly_cost = round(total_yearly_cost, 2)

    return jsonify(
        {
            "total_monthly_cost": total_monthly_cost,
            "total_yearly_cost": total_yearly_cost,
            "subscription_count": current_subscription_count,
            "upcoming_count": upcoming_count,
            "category_stats": rounded_stats(category_groups),
            "payment_method_stats": rounded_stats(payment_method_groups),
            "top_expensive": top_expensive,
            "monthly_expense": total_monthly_cost,
        }
    )
