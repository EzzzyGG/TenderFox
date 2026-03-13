from fastapi import APIRouter, Query

router = APIRouter()


@router.get("")
async def search(
    keyword: str = Query(min_length=2),
    region: str | None = None,
) -> dict:
    # TODO: replace with real source (zakupki.gov.ru) + normalization
    return {"count": 0, "items": [], "query": {"keyword": keyword, "region": region}}
