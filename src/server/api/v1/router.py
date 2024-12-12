from fastapi import APIRouter
from pydantic import BaseModel

from .sessions import sessions_router
from .telethon_methods import router as telethon_methods_router
from .trs_methods import router as trs_methods_router
from ... import SERVER_VERSION, SERVER_NAME

api_v1 = APIRouter(prefix="/v1")
api_v1.include_router(sessions_router)
api_v1.include_router(trs_methods_router)
api_v1.include_router(telethon_methods_router)

class ServerStatus(BaseModel):
    status: bool
    version: str
    server_name: str

@api_v1.get("/status")
async def get_status() -> ServerStatus:
    return ServerStatus(status=True, version=SERVER_VERSION, server_name=SERVER_NAME)