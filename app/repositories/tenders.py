from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models.tender import Tender


def upsert_tender(
    db: Session,
    *,
    source: str,
    source_id: str,
    title: str,
    price,
    currency: str | None,
    region: str | None,
    published_at,
    deadline_at,
    url: str | None,
    raw_json: dict | None,
) -> Tender:
    stmt = (
        insert(Tender)
        .values(
            source=source,
            source_id=source_id,
            title=title,
            price=price,
            currency=currency,
            region=region,
            published_at=published_at,
            deadline_at=deadline_at,
            url=url,
            raw_json=raw_json,
        )
        .on_conflict_do_update(
            index_elements=[Tender.source, Tender.source_id],
            set_={
                "title": title,
                "price": price,
                "currency": currency,
                "region": region,
                "published_at": published_at,
                "deadline_at": deadline_at,
                "url": url,
                "raw_json": raw_json,
            },
        )
        .returning(Tender)
    )
    row = db.execute(stmt).scalar_one()
    db.commit()
    return row


def get_tender_by_source_id(db: Session, *, source: str, source_id: str) -> Tender | None:
    stmt = select(Tender).where(Tender.source == source, Tender.source_id == source_id)
    return db.execute(stmt).scalar_one_or_none()
