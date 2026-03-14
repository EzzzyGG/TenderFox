from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.tenders import get_tender_by_source_id, upsert_tender
from app.schemas.tender import TenderOut
from app.sources.gosplan.client import GosplanClient
from app.sources.gosplan.normalize import normalize_purchase

router = APIRouter()


@router.get("/{tender_id}")
async def get_tender(tender_id: str, db: Session = Depends(get_db)) -> dict:
    # Try DB cache first
    cached = get_tender_by_source_id(db, source="gosplan_fz44", source_id=tender_id)
    if cached:
        return {"item": TenderOut.model_validate(cached).model_dump()}

    # Fetch from source
    client = GosplanClient()
    raw = await client.get_purchase(tender_id)

    # gosplan detail might wrap object
    item = raw.get("item") or raw.get("data") or raw
    n = normalize_purchase(item)

    t = upsert_tender(
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

    return {"item": TenderOut.model_validate(t).model_dump()}
