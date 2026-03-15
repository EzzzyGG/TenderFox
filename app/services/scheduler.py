from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.delivery import Delivery
from app.models.subscription import Subscription
from app.models.tender import Tender
from app.sources.gosplan.client import GosplanClient
from app.sources.gosplan.normalize import normalize_purchase


POLL_INTERVAL_SECONDS = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "300"))
STAGE = int(os.getenv("SCHEDULER_STAGE", "1"))
LIMIT_PER_SUB = int(os.getenv("SCHEDULER_LIMIT_PER_SUB", "20"))


def _format_price(price) -> str:
    if price is None:
        return "—"
    try:
        return f"{float(price):,.0f} ₽".replace(",", " ")
    except Exception:
        return f"{price} ₽"


def _dt_str(dt) -> str:
    if not dt:
        return "—"
    if isinstance(dt, datetime):
        # show Moscow time
        ms = dt.astimezone(timezone(timedelta(hours=3)))
        return ms.strftime("%Y-%m-%d %H:%M")
    return str(dt)


async def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(url, json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True})
        r.raise_for_status()


def create_delivery(db: Session, *, subscription_id: int, tender_id: int) -> bool:
    d = Delivery(subscription_id=subscription_id, tender_id=tender_id, status="queued")
    db.add(d)
    try:
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def mark_sent(db: Session, delivery_id: int) -> None:
    d = db.get(Delivery, delivery_id)
    if not d:
        return
    d.status = "sent"
    d.sent_at = datetime.now(tz=timezone.utc)
    db.commit()


async def process_once(bot_token: str) -> None:
    client = GosplanClient()

    db = SessionLocal()
    try:
        subs = list(db.execute(select(Subscription).where(Subscription.active.is_(True))).scalars().all())
        for sub in subs:
            region = None
            if sub.region and str(sub.region).isdigit():
                region = int(sub.region)

            data = await client.list_purchases(
                keyword=sub.keyword,
                region=region,
                limit=LIMIT_PER_SUB,
                skip=0,
                stage=STAGE,
            )
            items = data.get("items") or data.get("results") or data.get("data") or []

            for raw in items:
                n = normalize_purchase(raw)

                # Upsert tender into DB (simple: try get by unique index, else insert)
                # We rely on unique index (source, source_id). We'll do an upsert with raw SQLAlchemy core insert.
                from app.repositories.tenders import upsert_tender

                t: Tender = upsert_tender(
                    db,
                    source=n.source,
                    source_id=n.source_id,
                    title=n.title,
                    price=n.price,
                    currency=n.currency,
                    region=n.region,
                    published_at=n.published_at,
                    deadline_at=n.deadline_at,
                    url=n.url,
                    raw_json=n.raw,
                )

                created = create_delivery(db, subscription_id=sub.id, tender_id=t.id)
                if not created:
                    continue

                # Fetch latest delivery row id (quickly)
                delivery = db.execute(
                    select(Delivery).where(
                        Delivery.subscription_id == sub.id,
                        Delivery.tender_id == t.id,
                    )
                ).scalar_one()

                text = (
                    f"🦊 TenderFox\n"
                    f"Запрос: {sub.keyword} | регион: {sub.region or '-'}\n\n"
                    f"{t.title}\n"
                    f"Цена: {_format_price(t.price)}\n"
                    f"Опубликован: {_dt_str(t.published_at)}\n"
                    f"Дедлайн: {_dt_str(t.deadline_at)}\n"
                    f"{t.url or ''}"
                ).strip()

                await send_message(bot_token, sub.chat_id, text)
                mark_sent(db, delivery.id)

    finally:
        db.close()


async def main() -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    while True:
        try:
            await process_once(bot_token)
        except Exception:
            # keep running; logs will show in docker
            pass
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
