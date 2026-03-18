from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TelegramPendingPhone(Base):
    __tablename__ = "telegram_pending_phones"

    id: Mapped[int] = mapped_column(primary_key=True)

    chat_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    telegram_user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    phone_e164: Mapped[str] = mapped_column(String(32), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(tz=timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    used: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
