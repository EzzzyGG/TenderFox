from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # NEW: subscriptions belong to user
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # legacy: used by old bot/API flow
    chat_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    keyword: Mapped[str] = mapped_column(String(200), nullable=False)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    min_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
