from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription import Subscription


def create_subscription(
    db: Session,
    *,
    chat_id: str,
    keyword: str,
    region: str | None,
    min_price,
) -> Subscription:
    sub = Subscription(chat_id=chat_id, keyword=keyword, region=region, min_price=min_price, active=True)
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


def list_subscriptions(db: Session, *, chat_id: str | None = None) -> list[Subscription]:
    stmt = select(Subscription).order_by(Subscription.id.desc())
    if chat_id:
        stmt = stmt.where(Subscription.chat_id == chat_id)
    return list(db.execute(stmt).scalars().all())
