from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TenderOut(BaseModel):
    source: str
    source_id: str
    title: str
    price: Decimal | None
    currency: str | None
    region: str | None
    published_at: datetime | None
    deadline_at: datetime | None
    url: str | None

    model_config = {"from_attributes": True}
