from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    chat_id: str = Field(min_length=1, max_length=64)
    keyword: str = Field(min_length=2, max_length=200)
    region: str | None = Field(default=None, max_length=100)
    min_price: Decimal | None = None


class SubscriptionOut(BaseModel):
    id: int
    chat_id: str
    keyword: str
    region: str | None
    min_price: Decimal | None
    active: bool

    model_config = {"from_attributes": True}
