from json import loads

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from server import context
from trs import TRSBackendClient, tl_requests

router = APIRouter(prefix="/client", tags=["Telethon methods"])


@router.get("/get_me")
async def get_me(client: TRSBackendClient = Depends(context.get_client)):
    if not client.is_connected():
        await client.connect()
    me = await client.get_me()
    print(me.to_dict())
    return JSONResponse(loads(me.to_json()))

@router.post("/request")
async def send_tl_request(name: str, data: dict, client: TRSBackendClient = Depends(context.get_client)):
    request = tl_requests.get(name)
    if not request:
        return JSONResponse({
            "status": False, "message": f"TLRequest '{name}' not found!"},
            status_code=status.HTTP_404_NOT_FOUND
        )
    try:
        result = await client(request(**data))
    except TypeError as e:
        return JSONResponse({"message": f"Error: {e}"}, status_code=status.HTTP_400_BAD_REQUEST)
    print(result)
    return {"status": "ok", "method_name": name, "data": data}
