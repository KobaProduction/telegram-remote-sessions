from fastapi import APIRouter

from .sessions import sessions_router
from .telethon_methods import router as telethon_methods_router
from .trs_methods import router as trs_methods_router


api_v1 = APIRouter(prefix="/v1")
api_v1.include_router(sessions_router)
api_v1.include_router(trs_methods_router)
api_v1.include_router(telethon_methods_router)