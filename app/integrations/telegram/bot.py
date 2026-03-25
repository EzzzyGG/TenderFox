from __future__ import annotations

import asyncio
import os
import re
from datetime import datetime, timedelta, timezone

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.telegram_link import TelegramLink
from app.models.telegram_pending_phone import TelegramPendingPhone
from app.utils.phone import normalize_phone_e164


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://api:8000")
VERIFY_TTL_MINUTES = int(os.getenv("TELEGRAM_VERIFY_TTL_MINUTES", "15"))


dp = Dispatcher()


def _is_contact_message(msg: Message) -> bool:
    return msg.contact is not None and msg.contact.phone_number is not None


@dp.message(Command("start"))
async def start(msg: Message) -> None:
    await msg.answer(
        "Привет!\n\n"
        "Чтобы привязать Telegram к аккаунту TenderFox, отправь номер телефона командой:\n"
        "`/verify +79991234567`\n\n"
        "После этого нажми кнопку отправки контакта (Telegram предложит).",
        parse_mode="Markdown",
    )


@dp.message(Command("verify"))
async def verify_phone(msg: Message) -> None:
    if not msg.text:
        return

    m = re.match(r"^/verify\s+(.+)$", msg.text.strip())
    if not m:
        await msg.answer("Используй: /verify +79991234567")
        return

    raw_phone = m.group(1).strip()
    phone = normalize_phone_e164(raw_phone)
    if not phone:
        await msg.answer("Не смог распознать номер. Пример: /verify +79991234567")
        return

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=VERIFY_TTL_MINUTES)

    with SessionLocal() as db:
        # upsert pending
        existing = (
            db.query(TelegramPendingPhone)
            .filter(TelegramPendingPhone.phone_e164 == phone)
            .one_or_none()
        )
        if existing:
            existing.telegram_user_id = int(msg.from_user.id) if msg.from_user else None
            existing.chat_id = int(msg.chat.id)
            existing.expires_at = expires_at
        else:
            db.add(
                TelegramPendingPhone(
                    phone_e164=phone,
                    telegram_user_id=int(msg.from_user.id) if msg.from_user else None,
                    chat_id=int(msg.chat.id),
                    expires_at=expires_at,
                )
            )
        db.commit()

    await msg.answer(
        "Ок! Теперь отправь свой контакт (кнопка «Поделиться контактом»).\n"
        "Важно: контакт должен быть *твой*, не чужой.",
        parse_mode="Markdown",
    )


@dp.message(F.contact)
async def on_contact(msg: Message) -> None:
    if not _is_contact_message(msg):
        return

    phone = normalize_phone_e164(msg.contact.phone_number)
    if not phone:
        await msg.answer("Не смог распознать номер из контакта")
        return

    # call API to verify linking
    url = f"{API_BASE_URL}/auth/verify/telegram_contact"
    payload = {"phone_e164": phone, "telegram_user_id": msg.from_user.id, "chat_id": msg.chat.id}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        await msg.answer(f"Не удалось подтвердить: {resp.status_code} {resp.text[:200]}")
        return

    await msg.answer("Готово! Telegram привязан к аккаунту.")


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
