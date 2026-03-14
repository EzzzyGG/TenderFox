from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.tenders import upsert_tender
from app.schemas.tender import TenderOut
from app.sources.gosplan.client import GosplanClient
from app.sources.gosplan.normalize import normalize_purchase

router = APIRouter()


@router.get("")
async def search(
    keyword: str = Query(min_length=2),
    region: int | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    client = GosplanClient()
    data = await client.list_purchases(keyword=keyword, region=region, limit=limit)

    items = data.get("items") or data.get("results") or data.get("data") or []
    normalized = [normalize_purchase(x) for x in items]

    out_items = []
    for n in normalized:
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
        out_items.append(TenderOut.model_validate(t).model_dump())

    return {"count": len(out_items), "items": out_items}
