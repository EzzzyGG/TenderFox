from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)

    keyword: Mapped[str] = mapped_column(String(120), index=True)
    region: Mapped[str | None] = mapped_column(String(32), index=True, nullable=True)

    min_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    max_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)

    exclude_keywords: Mapped[str | None] = mapped_column(String(512), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
