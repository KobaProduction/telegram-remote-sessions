from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from server.context import context
from trs import TRSBackendClient

router = APIRouter(prefix="/client", tags=["Telethon methods"])


@router.get("/get_me")
async def get_me(client: TRSBackendClient = Depends(context.get_client)):
    if not client.is_connected():
        await client.connect()
    me = await client.get_me()
    return JSONResponse(me.to_json())