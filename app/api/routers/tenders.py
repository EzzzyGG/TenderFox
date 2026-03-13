from fastapi import APIRouter

router = APIRouter()


@router.get("/{tender_id}")
async def get_tender(tender_id: str) -> dict:
    # TODO: fetch from DB; if missing — fetch from source
    return {"id": tender_id, "status": "TODO"}
