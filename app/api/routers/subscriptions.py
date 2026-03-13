from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.subscriptions import create_subscription, list_subscriptions
from app.schemas.subscription import SubscriptionCreate, SubscriptionOut

router = APIRouter()


@router.get("")
async def get_subscriptions(
    chat_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> dict:
    items = list_subscriptions(db, chat_id=chat_id)
    return {"items": [SubscriptionOut.model_validate(x).model_dump() for x in items]}


@router.post("")
async def post_subscription(payload: SubscriptionCreate, db: Session = Depends(get_db)) -> dict:
    sub = create_subscription(
        db,
        chat_id=payload.chat_id,
        keyword=payload.keyword,
        region=payload.region,
        min_price=payload.min_price,
    )
    return {"item": SubscriptionOut.model_validate(sub).model_dump()}
