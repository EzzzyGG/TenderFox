from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    keyword: str = Field(min_length=2, max_length=200)
    region: str | None = Field(default=None, max_length=100)
    min_price: Decimal | None = None


class SubscriptionOut(BaseModel):
    id: int
    user_id: int

    # legacy (kept for transition; may be null)
    chat_id: str | None = None

    keyword: str
    region: str | None
    min_price: Decimal | None
    active: bool

    model_config = {"from_attributes": True}
