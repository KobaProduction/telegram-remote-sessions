from pickle import dumps as pickle_dumps, loads as pickle_loads
from json import dumps

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response, JSONResponse
from fastapi.requests import Request
from telethon.errors import RPCError

from context import context
from trs import TRSBackendClient, convert_to_pre_json, convert_from_pre_json, convert_objects_from_dict, TRSManager
from trs.errors import SessionNotExits
from trs.sessions import TRSessionState

router = APIRouter(prefix="/trs/client", tags=["TRS Client methods"])


@router.post("/send_pickle_request")
async def send_pickle_request(session_name: str,
                              request: Request,
                              manager: TRSManager = Depends(context.get_session_manager)):
    if request.headers.get("content-type") != "application/python-pickle":
        return JSONResponse(
            content={"error": "set content type application/python-pickle"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    data = await request.body()
    if not data:
        return JSONResponse({"error": "Empty body"}, status_code=status.HTTP_400_BAD_REQUEST)
    try:
        client = await manager.get_client(session_name)
    except SessionNotExits:
        return JSONResponse({"error": "Session not exist"}, status_code=status.HTTP_400_BAD_REQUEST)
    if client.session.state != TRSessionState.AUTHENTICATED:
        return JSONResponse({"error": "Session not authed"}, status_code=status.HTTP_401_UNAUTHORIZED)


    if not client.is_connected():
        await client.connect()
    try:
        result = await client(pickle_loads(data), ordered=False)
    except RPCError as e:
        result = e
    except Exception:
        raise
    return Response(content=pickle_dumps(result), media_type="application/python-pickle")


@router.post("/send_raw_request")
async def send_request(body: dict, ordered: bool = False, client: TRSBackendClient = Depends(context.get_client)):
    async with client:
        cleaned = convert_from_pre_json(body)
        request = convert_objects_from_dict(cleaned)
        result = await client(request, ordered=ordered)
        data = convert_to_pre_json({"raw": result})
        return Response(dumps(data), media_type="application/json")
