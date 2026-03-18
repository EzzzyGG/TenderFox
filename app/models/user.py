from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Normalized E.164, e.g. +79991234567
    phone_e164: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)

    phone_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    phone_verified_via: Mapped[str | None] = mapped_column(String(32), nullable=True)  # telegram_contact | sms

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
