from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TelegramPendingPhone(Base):
    __tablename__ = "telegram_pending_phones"

    id: Mapped[int] = mapped_column(primary_key=True)

    phone_e164: Mapped[str] = mapped_column(String(32), unique=True, index=True)

    telegram_user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    chat_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # NOTE: can be used for soft-invalidation if needed
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
