from __future__ import annotations

import asyncio
import logging
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
from app.models.telegram_link import TelegramLink
from app.sources.gosplan.client import GosplanClient
from app.sources.gosplan.normalize import normalize_purchase

logger = logging.getLogger("tenderfox.scheduler")

POLL_INTERVAL_SECONDS = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "300"))
STAGE = int(os.getenv("SCHEDULER_STAGE", "1"))
LIMIT_PER_SUB = int(os.getenv("SCHEDULER_LIMIT_PER_SUB", "20"))

MAX_MESSAGES_PER_CYCLE = int(os.getenv("SCHEDULER_MAX_MESSAGES_PER_CYCLE", "30"))
SLEEP_BETWEEN_MESSAGES_MS = int(os.getenv("SCHEDULER_SLEEP_BETWEEN_MESSAGES_MS", "250"))
DRY_RUN = os.getenv("SCHEDULER_DRY_RUN", "false").lower() in {"1", "true", "yes"}
ALLOW_LEGACY_CHAT_ID = os.getenv("SCHEDULER_ALLOW_LEGACY_CHAT_ID", "true").lower() in {"1", "true", "yes"}


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
        ms = dt.astimezone(timezone(timedelta(hours=3)))
        return ms.strftime("%Y-%m-%d %H:%M")
    return str(dt)


def _resolve_chat_id(db: Session, sub: Subscription) -> tuple[str | None, str]:
    """Return (chat_id, source) where source in {'telegram_links','legacy','missing'}."""
    if getattr(sub, "user_id", None):
        chat_id = db.execute(
            select(TelegramLink.chat_id).where(TelegramLink.user_id == sub.user_id)
        ).scalar_one_or_none()
        if chat_id:
            return str(chat_id), "telegram_links"

    if ALLOW_LEGACY_CHAT_ID and getattr(sub, "chat_id", None):
        return str(sub.chat_id), "legacy"

    return None, "missing"


async def send_message(bot_token: str, chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "disable_web_page_preview": True,
            },
        )
        if r.status_code == 429:
            try:
                data = r.json()
                retry_after = int(data.get("parameters", {}).get("retry_after", 1))
            except Exception:
                retry_after = 1
            raise RuntimeError(f"Telegram rate limited (429), retry_after={retry_after}")
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


def mark_failed(db: Session, delivery_id: int, error_text: str) -> None:
    d = db.get(Delivery, delivery_id)
    if not d:
        return
    d.status = "failed"
    db.commit()
    logger.warning("delivery_failed delivery_id=%s error=%s", delivery_id, error_text)


def build_message(sub: Subscription, tender: Tender) -> str:
    parts = [
        "🦊 TenderFox",
        f"Запрос: {sub.keyword} | регион: {sub.region or '-'}",
        "",
        tender.title,
        f"Цена: {_format_price(tender.price)}",
        f"Дедлайн: {_dt_str(tender.deadline_at)}",
    ]
    if tender.url:
        parts.append(tender.url)
    return "\n".join(parts).strip()


async def process_once(bot_token: str) -> dict:
    from app.repositories.tenders import upsert_tender

    client = GosplanClient()
    db = SessionLocal()

    stats = {
        "subs": 0,
        "new_deliveries": 0,
        "sent": 0,
        "dry_run": DRY_RUN,
        "capped": False,
        "resolved_via_link": 0,
        "resolved_via_legacy": 0,
        "missing_chat_id": 0,
        "allow_legacy_chat_id": ALLOW_LEGACY_CHAT_ID,
    }

    try:
        subs = list(
            db.execute(select(Subscription).where(Subscription.active.is_(True))).scalars().all()
        )
        stats["subs"] = len(subs)
        logger.info("cycle_start subs=%s dry_run=%s", len(subs), DRY_RUN)

        sent_in_cycle = 0

        for sub in subs:
            if sent_in_cycle >= MAX_MESSAGES_PER_CYCLE:
                stats["capped"] = True
                logger.info("cycle_cap_reached max_messages=%s", MAX_MESSAGES_PER_CYCLE)
                break

            chat_id, source = _resolve_chat_id(db, sub)
            if not chat_id:
                stats["missing_chat_id"] += 1
                logger.info(
                    "skip_no_chat_id subscription_id=%s user_id=%s",
                    sub.id,
                    getattr(sub, "user_id", None),
                )
                continue

            if source == "telegram_links":
                stats["resolved_via_link"] += 1
            elif source == "legacy":
                stats["resolved_via_legacy"] += 1

            region = None
            if sub.region and str(sub.region).isdigit():
                region = int(sub.region)

            try:
                data = await client.list_purchases(
                    keyword=sub.keyword,
                    region=region,
                    limit=LIMIT_PER_SUB,
                    skip=0,
                    stage=STAGE,
                )
            except Exception as e:
                logger.exception("source_error subscription_id=%s err=%s", sub.id, e)
                continue

            items = data.get("items") or data.get("results") or data.get("data") or []
            logger.info("source_ok subscription_id=%s items=%s", sub.id, len(items))

            for raw in items:
                if sent_in_cycle >= MAX_MESSAGES_PER_CYCLE:
                    stats["capped"] = True
                    break

                n = normalize_purchase(raw)
                if not n.source_id:
                    continue

                try:
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
                except Exception as e:
                    logger.exception(
                        "db_upsert_error subscription_id=%s source_id=%s err=%s",
                        sub.id,
                        n.source_id,
                        e,
                    )
                    continue

                created = create_delivery(db, subscription_id=sub.id, tender_id=t.id)
                if not created:
                    continue

                stats["new_deliveries"] += 1

                delivery = db.execute(
                    select(Delivery).where(
                        Delivery.subscription_id == sub.id,
                        Delivery.tender_id == t.id,
                    )
                ).scalar_one()

                text = build_message(sub, t)

                if DRY_RUN:
                    logger.info(
                        "dry_run_send chat_id=%s delivery_id=%s via=%s",
                        chat_id,
                        delivery.id,
                        source,
                    )
                    mark_sent(db, delivery.id)
                    sent_in_cycle += 1
                    stats["sent"] += 1
                    continue

                try:
                    await send_message(bot_token, chat_id, text)
                    mark_sent(db, delivery.id)
                    sent_in_cycle += 1
                    stats["sent"] += 1
                    await asyncio.sleep(SLEEP_BETWEEN_MESSAGES_MS / 1000)
                except Exception as e:
                    mark_failed(db, delivery.id, str(e))

        logger.info(
            "cycle_done subs=%s new_deliveries=%s sent=%s capped=%s via_link=%s via_legacy=%s missing_chat_id=%s allow_legacy=%s",
            stats["subs"],
            stats["new_deliveries"],
            stats["sent"],
            stats["capped"],
            stats["resolved_via_link"],
            stats["resolved_via_legacy"],
            stats["missing_chat_id"],
            stats["allow_legacy_chat_id"],
        )
        return stats

    finally:
        db.close()


async def main() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    logger.info(
        "scheduler_start interval=%s stage=%s limit_per_sub=%s max_msgs=%s dry_run=%s allow_legacy=%s",
        POLL_INTERVAL_SECONDS,
        STAGE,
        LIMIT_PER_SUB,
        MAX_MESSAGES_PER_CYCLE,
        DRY_RUN,
        ALLOW_LEGACY_CHAT_ID,
    )

    while True:
        try:
            await process_once(bot_token)
        except Exception as e:
            logger.exception("cycle_crash err=%s", e)
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(main())
