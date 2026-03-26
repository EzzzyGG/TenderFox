from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class SubscriptionCreate(BaseModel):
    keyword: str = Field(min_length=2, max_length=200)
    region: str | None = Field(default=None, max_length=100)

    min_price: Decimal | None = None
    max_price: Decimal | None = None

    # comma-separated list: "word1,word2"
    exclude_keywords: str | None = Field(default=None, max_length=500)

    # filter tenders by published_at >= now - days_back
    days_back: int | None = Field(default=None, ge=1, le=60)


class SubscriptionOut(BaseModel):
    id: int
    user_id: int

    keyword: str
    region: str | None = None

    min_price: Decimal | None = None
    max_price: Decimal | None = None
    exclude_keywords: str | None = None
    days_back: int | None = None

    active: bool = Field(validation_alias="is_active")

    model_config = {"from_attributes": True}
