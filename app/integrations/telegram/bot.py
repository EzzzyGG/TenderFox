from __future__ import annotations

import asyncio
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from app.core.config import settings


def _token() -> str:
    token = os.getenv("TELEGRAM_BOT_TOKEN") or getattr(settings, "telegram_bot_token", "")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    return token


async def cmd_start(message: Message) -> None:
    text = (
        "TenderFox — бот для тендеров.\n\n"
        "Команды:\n"
        "/add <ключевые слова> [регион_код] — добавить подписку\n"
        "/my — показать подписки\n\n"
        "Пример: /add мебель 77"
    )
    await message.answer(text)


async def cmd_my(message: Message) -> None:
    # Пока без Telegram API-авторизации: используем chat_id как ключ
    import httpx

    chat_id = str(message.chat.id)
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get("http://api:8000/subscriptions", params={"chat_id": chat_id})
        r.raise_for_status()
        data = r.json()

    items = data.get("items") or []
    if not items:
        await message.answer("Подписок пока нет. Добавь: /add мебель 77")
        return

    lines = ["Твои подписки:"]
    for it in items[:50]:
        kw = it.get("keyword")
        region = it.get("region")
        min_price = it.get("min_price")
        lines.append(f"- {kw} | регион: {region or '-'} | мин.цена: {min_price or '-'}")

    await message.answer("\n".join(lines))


async def cmd_add(message: Message) -> None:
    import httpx

    # Parse: /add <keyword...> [region]
    parts = (message.text or "").split()
    if len(parts) < 2:
        await message.answer("Формат: /add <ключевые слова> [регион_код]. Пример: /add мебель 77")
        return

    chat_id = str(message.chat.id)

    region = None
    if len(parts) >= 3 and parts[-1].isdigit():
        region = parts[-1]
        keyword = " ".join(parts[1:-1]).strip()
    else:
        keyword = " ".join(parts[1:]).strip()

    payload = {"chat_id": chat_id, "keyword": keyword, "region": region, "min_price": None}

    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post("http://api:8000/subscriptions", json=payload)
        r.raise_for_status()

    await message.answer(f"Подписка добавлена: {keyword} (регион: {region or '-'})")


async def main() -> None:
    bot = Bot(token=_token())
    dp = Dispatcher()

    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_my, Command("my"))
    dp.message.register(cmd_add, Command("add"))

    # Fallback
    @dp.message(F.text)
    async def any_text(message: Message) -> None:
        await message.answer("Напиши /start")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
