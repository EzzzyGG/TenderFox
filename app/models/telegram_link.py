from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TelegramLink(Base):
    __tablename__ = "telegram_links"

    __table_args__ = (
        UniqueConstraint("user_id", name="uq_telegram_links_user"),
        UniqueConstraint("telegram_user_id", name="uq_telegram_links_tg_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    telegram_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(64), nullable=False)

    phone_e164_from_telegram: Mapped[str | None] = mapped_column(String(32), nullable=True)

    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
