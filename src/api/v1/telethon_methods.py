from fastapi import APIRouter, Depends
from fastapi.responses import Response


from context import context
from trs import TRSBackendClient

router = APIRouter(prefix="/client", tags=["Telethon methods"])


@router.get("/get_me")
async def get_me(client: TRSBackendClient = Depends(context.get_client)):
    async with client:
        me = await client.get_me()
        return Response(me.to_json(), media_type="application/json")
