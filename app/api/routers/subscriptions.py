from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.subscriptions import create_subscription, list_subscriptions
from app.schemas.subscription import SubscriptionCreate, SubscriptionOut

router = APIRouter()


@router.get("")
async def get_subscriptions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items = list_subscriptions(db, user_id=user.id)
    return {"items": [SubscriptionOut.model_validate(x).model_dump() for x in items]}


@router.post("")
async def post_subscription(
    payload: SubscriptionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    sub = create_subscription(
        db,
        user_id=user.id,
        keyword=payload.keyword,
        region=payload.region,
        min_price=payload.min_price,
        max_price=payload.max_price,
        exclude_keywords=payload.exclude_keywords,
        days_back=payload.days_back,
    )
    return {"item": SubscriptionOut.model_validate(sub).model_dump()}
