from .sessions import sessions_router
from .telegram_methods import router as telegram_methods_router
from fastapi import APIRouter

api_v1 = APIRouter(prefix="/v1", tags=["API v1"])
api_v1.include_router(sessions_router)
api_v1.include_router(telegram_methods_router)
