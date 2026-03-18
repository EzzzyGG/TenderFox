from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription import Subscription


def create_subscription(
    db: Session,
    *,
    user_id: int,
    keyword: str,
    region: str | None,
    min_price,
) -> Subscription:
    sub = Subscription(user_id=user_id, keyword=keyword, region=region, min_price=min_price, active=True)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def list_subscriptions(db: Session, *, user_id: int) -> list[Subscription]:
    stmt = select(Subscription).where(Subscription.user_id == user_id).order_by(Subscription.id.desc())
    return list(db.execute(stmt).scalars().all())
