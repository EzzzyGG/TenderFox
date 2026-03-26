from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.delivery import Delivery
from app.models.subscription import Subscription
from app.models.tender import Tender
from app.models.telegram_link import TelegramLink
from app.sources.gosplan.client import GosplanClient
from app.sources.gosplan.normalize import normalize_purchase

log = logging.getLogger(__name__)


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def _setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, level, logging.INFO))


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

POLL_INTERVAL_SECONDS = _env_int("SCHEDULER_INTERVAL_SECONDS", 300)
STAGE = _env_int("SCHEDULER_STAGE", 1)
LIMIT_PER_SUB = _env_int("SCHEDULER_LIMIT_PER_SUB", 50)
MAX_MESSAGES_PER_CYCLE = _env_int("SCHEDULER_MAX_MESSAGES_PER_CYCLE", 300)
SLEEP_BETWEEN_MESSAGES_MS = _env_int("SCHEDULER_SLEEP_BETWEEN_MESSAGES_MS", 100)
DRY_RUN = _env_bool("SCHEDULER_DRY_RUN", False)


async def _send_telegram_message(chat_id: int, text: str) -> None:
    if DRY_RUN:
        log.info("[DRY_RUN] send to chat_id=%s: %s", chat_id, text[:200])
        return

    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text})
        resp.raise_for_status()


def _resolve_chat_id(db: Session, user_id: int) -> int | None:
    row = db.execute(
        select(TelegramLink.chat_id).where(TelegramLink.user_id == user_id)
    ).first()
    if not row:
        return None
    return int(row[0])


def _already_delivered(db: Session, subscription_id: int, tender_id: int) -> bool:
    row = db.execute(
        select(Delivery.id).where(
            Delivery.subscription_id == subscription_id,
            Delivery.tender_id == tender_id,
        )
    ).first()
    return row is not None


def _mark_delivered(db: Session, subscription_id: int, tender_id: int) -> None:
    db.add(
        Delivery(
            subscription_id=subscription_id,
            tender_id=tender_id,
            status="sent",
            sent_at=datetime.now(timezone.utc),
        )
    )


async def run_once() -> None:
    client = GosplanClient()
    with SessionLocal() as db:
        subs = (
            db.execute(select(Subscription).where(Subscription.is_active.is_(True)))
            .scalars()
            .all()
        )

        sent_messages = 0

        for sub in subs:
            if sent_messages >= MAX_MESSAGES_PER_CYCLE:
                log.warning("Reached MAX_MESSAGES_PER_CYCLE=%s", MAX_MESSAGES_PER_CYCLE)
                break

            if sub.user_id is None:
                continue

            chat_id = _resolve_chat_id(db, sub.user_id)
            if not chat_id:
                continue

            data = await client.list_purchases(
                keyword=sub.keyword,
                region=int(sub.region) if sub.region and sub.region.isdigit() else None,
                limit=LIMIT_PER_SUB,
                stage=STAGE,
            )
            items = data.get("items") or data.get("results") or data.get("data") or []

            for raw in items:
                norm = normalize_purchase(raw)

                tender = db.execute(
                    select(Tender).where(
                        Tender.source == norm.source,
                        Tender.source_id == norm.source_id,
                    )
                ).scalar_one_or_none()

                if tender is None:
                    tender = Tender(
                        source=norm.source,
                        source_id=norm.source_id,
                        title=norm.title,
                        url=norm.url,
                        region=norm.region,
                        price=norm.price,
                        currency=norm.currency,
                        deadline_at=norm.deadline_at,
                        published_at=norm.published_at,
                        raw_json=norm.raw,
                    )
                    db.add(tender)
                    db.flush()
                else:
                    tender.title = norm.title
                    tender.url = norm.url
                    tender.region = norm.region
                    tender.price = norm.price
                    tender.currency = norm.currency
                    tender.deadline_at = norm.deadline_at
                    tender.published_at = norm.published_at
                    tender.raw_json = norm.raw

                if _already_delivered(db, sub.id, tender.id):
                    continue

                text = f"{tender.title}\n{tender.url or ''}".strip()
                await _send_telegram_message(chat_id, text)
                _mark_delivered(db, sub.id, tender.id)
                sent_messages += 1

                if SLEEP_BETWEEN_MESSAGES_MS > 0:
                    await asyncio.sleep(SLEEP_BETWEEN_MESSAGES_MS / 1000.0)

        db.commit()


async def main() -> None:
    _setup_logging()
    log.info(
        "Scheduler starting: interval=%s stage=%s limit_per_sub=%s max_messages=%s dry_run=%s",
        POLL_INTERVAL_SECONDS,
        STAGE,
        LIMIT_PER_SUB,
        MAX_MESSAGES_PER_CYCLE,
        DRY_RUN,
    )

    while True:
        started = datetime.now(timezone.utc)
        try:
            await run_once()
        except Exception:
            log.exception("Scheduler cycle failed")

        elapsed = (datetime.now(timezone.utc) - started).total_seconds()
        sleep_for = max(0, POLL_INTERVAL_SECONDS - int(elapsed))
        await asyncio.sleep(sleep_for)


if __name__ == "__main__":
    asyncio.run(main())
