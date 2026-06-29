def calculate_subscription_score(subscription):
    score = 60

    importance = int(subscription.importance or 0)
    usage_count = int(subscription.usage_count or 0)
    price = float(subscription.price or 0)

    score += importance * 6
    score += min(usage_count * 3, 30)

    if price > 50:
        score -= 20
    elif price > 30:
        score -= 10

    if usage_count == 0:
        score -= 25

    return max(0, min(100, score))


def get_subscription_suggestion(score):
    if score >= 80:
        return "建议保留"
    if score >= 50:
        return "建议观察"
    return "建议取消或暂停"


def score_subscription(subscription):
    score = calculate_subscription_score(subscription)
    return {
        "score": score,
        "suggestion": get_subscription_suggestion(score),
    }
