from __future__ import annotations

import asyncio
import os
import re
from datetime import datetime, timedelta, timezone

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.base import Base


PHONE_RE = re.compile(r"^\+?\d{10,16}$")
PENDING_TTL_MINUTES = int(os.getenv("TELEGRAM_VERIFY_TTL_MINUTES", "10"))


def _token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN") or getattr(settings, "telegram_bot_token", "")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    return token


def _normalize_phone(s: str) -> str:
    return s.strip().replace(" ", "")


def _api_base() -> str:
    # Inside docker-compose network
    return os.getenv("API_BASE_URL", "http://api:8000")


async def _api_verify_telegram_contact(
    *,
    phone: str,
    phone_from_telegram: str,
    telegram_user_id: str,
    chat_id: str,
) -> dict:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(
            f"{_api_base()}/auth/verify_telegram_contact",
            json={
                "phone": phone,
                "telegram_user_id": telegram_user_id,
                "chat_id": chat_id,
                "phone_from_telegram": phone_from_telegram,
            },
        )
        r.raise_for_status()
        return r.json()


# --- DB model for pending verify ---
try:
    from sqlalchemy import Boolean, DateTime, Integer, String
    from sqlalchemy.orm import Mapped, mapped_column

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

except Exception:
    # If imports fail for some reason, bot should still crash fast at startup.
    TelegramPendingPhone = None  # type: ignore


def _save_pending_phone(*, chat_id: str, telegram_user_id: str, phone_e164: str) -> None:
    if TelegramPendingPhone is None:
        raise RuntimeError("TelegramPendingPhone model is not available")

    db = SessionLocal()
    try:
        now = datetime.now(tz=timezone.utc)
        expires_at = now + timedelta(minutes=PENDING_TTL_MINUTES)

        # mark old pending as used to avoid ambiguity
        db.query(TelegramPendingPhone).filter(
            TelegramPendingPhone.chat_id == chat_id,
            TelegramPendingPhone.telegram_user_id == telegram_user_id,
            TelegramPendingPhone.used.is_(False),
        ).update({"used": True})

        row = TelegramPendingPhone(
            chat_id=chat_id,
            telegram_user_id=telegram_user_id,
            phone_e164=phone_e164,
            expires_at=expires_at,
            used=False,
        )
        db.add(row)
        db.commit()
    finally:
        db.close()


def _get_pending_phone(*, chat_id: str, telegram_user_id: str) -> str | None:
    if TelegramPendingPhone is None:
        raise RuntimeError("TelegramPendingPhone model is not available")

    db = SessionLocal()
    try:
        now = datetime.now(tz=timezone.utc)
        row = (
            db.query(TelegramPendingPhone)
            .filter(
                TelegramPendingPhone.chat_id == chat_id,
                TelegramPendingPhone.telegram_user_id == telegram_user_id,
                TelegramPendingPhone.used.is_(False),
                TelegramPendingPhone.expires_at > now,
            )
            .order_by(TelegramPendingPhone.id.desc())
            .first()
        )
        return row.phone_e164 if row else None
    finally:
        db.close()


def _mark_pending_used(*, chat_id: str, telegram_user_id: str) -> None:
    if TelegramPendingPhone is None:
        raise RuntimeError("TelegramPendingPhone model is not available")

    db = SessionLocal()
    try:
        db.query(TelegramPendingPhone).filter(
            TelegramPendingPhone.chat_id == chat_id,
            TelegramPendingPhone.telegram_user_id == telegram_user_id,
            TelegramPendingPhone.used.is_(False),
        ).update({"used": True})
        db.commit()
    finally:
        db.close()


def _contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отправить контакт", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


async def cmd_start(message: Message) -> None:
    text = (
        "TenderFox — бот уведомлений.\n\n"
        "Сначала привяжем Telegram к твоему аккаунту: /verify\n\n"
        "Подписки создаются через API (Swagger) после авторизации."
    )
    await message.answer(text)


async def cmd_verify(message: Message) -> None:
    await message.answer(
        "Пришли номер телефона в формате +79991234567 (как при регистрации)."
    )


@F.text
async def on_text(message: Message) -> None:
    text = (message.text or "").strip()
    if text.startswith("/"):
        # ignore commands here
        return

    phone = _normalize_phone(text)
    if not PHONE_RE.match(phone):
        await message.answer("Не похоже на номер. Пример: +79991234567")
        return

    chat_id = str(message.chat.id)
    telegram_user_id = str(message.from_user.id) if message.from_user else ""
    if not telegram_user_id:
        await message.answer("Не смог определить telegram_user_id")
        return

    _save_pending_phone(chat_id=chat_id, telegram_user_id=telegram_user_id, phone_e164=phone)
    await message.answer(
        "Отлично. Теперь отправь контакт кнопкой ниже.",
        reply_markup=_contact_keyboard(),
    )


@F.contact
async def on_contact(message: Message) -> None:
    if not message.contact or not message.contact.phone_number:
        await message.answer("Контакт не содержит номера телефона")
        return

    chat_id = str(message.chat.id)
    telegram_user_id = str(message.from_user.id) if message.from_user else ""
    if not telegram_user_id:
        await message.answer("Не смог определить telegram_user_id")
        return

    phone = _get_pending_phone(chat_id=chat_id, telegram_user_id=telegram_user_id)
    if not phone:
        await message.answer("Сначала пришли номер текстом: /verify")
        return

    phone_from_telegram = _normalize_phone(message.contact.phone_number)

    try:
        await _api_verify_telegram_contact(
            phone=phone,
            phone_from_telegram=phone_from_telegram,
            telegram_user_id=telegram_user_id,
            chat_id=chat_id,
        )
        _mark_pending_used(chat_id=chat_id, telegram_user_id=telegram_user_id)
        await message.answer("Готово: телефон подтверждён, Telegram привязан.")
    except httpx.HTTPStatusError as e:
        await message.answer(f"Ошибка API: {e.response.status_code} {e.response.text}")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


async def main() -> None:
    bot = Bot(token=_token())
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_verify, Command("verify"))

    # handlers via decorators above

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
