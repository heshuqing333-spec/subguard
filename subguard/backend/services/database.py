from datetime import date
from decimal import Decimal

from extensions import db
from models import CancelGuide, Subscription


def init_database(app):
    with app.app_context():
        db.create_all()
        seed_mock_data()


def seed_mock_data():
    if Subscription.query.first() is None:
        subscriptions = [
            Subscription(
                name="腾讯视频会员",
                category="影音娱乐",
                price=Decimal("30.00"),
                cycle="monthly",
                next_due_date=date(2026, 6, 18),
                payment_method="微信",
                status="active",
                usage_count=12,
                importance=4,
                notes="家庭常用，续费前确认是否有优惠。",
            ),
            Subscription(
                name="ChatGPT Plus",
                category="AI工具",
                price=Decimal("20.00"),
                cycle="monthly",
                next_due_date=date(2026, 6, 22),
                payment_method="网页支付",
                status="active",
                usage_count=28,
                importance=5,
                notes="工作学习高频使用。",
            ),
            Subscription(
                name="iCloud 200GB",
                category="云存储",
                price=Decimal("21.00"),
                cycle="monthly",
                next_due_date=date(2026, 7, 1),
                payment_method="Apple ID",
                status="active",
                usage_count=8,
                importance=5,
                notes="照片和设备备份。",
            ),
            Subscription(
                name="得到年度会员",
                category="学习",
                price=Decimal("238.00"),
                cycle="yearly",
                next_due_date=date(2026, 11, 11),
                payment_method="支付宝",
                status="paused",
                usage_count=2,
                importance=3,
                notes="使用频率偏低，续费前评估。",
            ),
        ]
        db.session.add_all(subscriptions)

    if CancelGuide.query.first() is None:
        guides = [
            CancelGuide(
                payment_method="微信",
                platform_name="微信自动续费",
                guide_steps="微信 > 我 > 服务 > 钱包 > 支付设置 > 自动续费，选择对应服务后关闭。",
            ),
            CancelGuide(
                payment_method="支付宝",
                platform_name="支付宝免密支付",
                guide_steps="支付宝 > 我的 > 设置 > 支付设置 > 免密支付/自动扣款，选择服务后关闭。",
            ),
            CancelGuide(
                payment_method="Apple ID",
                platform_name="Apple 订阅",
                guide_steps="设置 > Apple ID > 订阅，选择对应项目后取消订阅。",
            ),
        ]
        db.session.add_all(guides)

    db.session.commit()
