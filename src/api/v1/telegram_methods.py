from pickle import dumps as pickle_dumps, loads as pickle_loads
from json import dumps

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from fastapi.requests import Request
from starlette.responses import JSONResponse

from context import context
from trs import TRSBackendClient, convert_to_pre_json, convert_from_pre_json, convert_objects_from_dict


router = APIRouter(prefix="/client", tags=["Client Methods"])


@router.post("/send_pickle_request")
async def send_pickle_request(request: Request, client: TRSBackendClient = Depends(context.get_client)):
    if request.headers.get("content-type") != "application/python-pickle":
        return JSONResponse(
            content={"error": "set content type application/python-pickle"},
            status_code=status.HTTP_400_BAD_REQUEST
        )
    data = await request.body()
    if not data:
        return JSONResponse({"error" : "Empty body"}, status_code=status.HTTP_400_BAD_REQUEST)
    async with client:
        result = await client(pickle_loads(data), ordered=False)
        return Response(content=pickle_dumps(result), media_type="application/python-pickle")


@router.post("/send_raw_request")
async def send_request(body: dict, ordered: bool = False, client: TRSBackendClient = Depends(context.get_client)):
    async with client:
        cleaned = convert_from_pre_json(body)
        request = convert_objects_from_dict(cleaned)
        result = await client(request, ordered=ordered)
        data = convert_to_pre_json({"raw": result})
        return Response(dumps(data), media_type="application/json")


@router.get("/get_me")
async def get_me(client: TRSBackendClient = Depends(context.get_client)):
    async with client:
        me = await client.get_me()
        return Response(me.to_json(), media_type="application/json")