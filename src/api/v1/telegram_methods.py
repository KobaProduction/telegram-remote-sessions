from json import dumps

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from context import context
from telegram import TFABackendClient, convert_to_pre_json, convert_from_pre_json, convert_objects_from_dict


router = APIRouter(prefix="/client", tags=["Client Methods"])


@router.post("/send_raw_request")
async def send_request(body: dict, ordered: bool = False, client: TFABackendClient = Depends(context.get_client)):
    async with client:
        cleaned = convert_from_pre_json(body)
        request = convert_objects_from_dict(cleaned)
        result = await client(request, ordered=ordered)
        data = convert_to_pre_json({"raw": result})
        return Response(dumps(data), media_type="application/json")


@router.get("/get_me")
async def get_me(client: TFABackendClient = Depends(context.get_client)):
    async with client:
        me = await client.get_me()
        return Response(me.to_json(), media_type="application/json")