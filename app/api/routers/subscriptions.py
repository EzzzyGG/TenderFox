from fastapi import APIRouter

router = APIRouter()


@router.get("")
async def list_subscriptions() -> dict:
    # TODO: list from DB (later with auth/chat_id)
    return {"items": []}


@router.post("")
async def create_subscription() -> dict:
    # TODO: create subscription in DB
    return {"status": "TODO"}
