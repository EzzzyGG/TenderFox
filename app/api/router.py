from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.api.routers.search import router as search_router
from app.api.routers.subscriptions import router as subscriptions_router
from app.api.routers.tenders import router as tenders_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(auth_router)
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(subscriptions_router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(tenders_router, prefix="/tenders", tags=["tenders"])
