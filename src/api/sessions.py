import typing

from fastapi import Depends, APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from context import context
from trs import TRSManager, TRSessionParameters
from trs.errors import TelegramRemoteSessionException

router = APIRouter(prefix="/sessions", tags=["Sessions"])


class SessionProxyData(BaseModel):
    session_name: str
    proxy: typing.Optional[str]


class FullSessionData(SessionProxyData, TRSessionParameters):
    file_path: str


class SessionList(BaseModel):
    sessions: typing.List[str]


async def sessions_exception_handler(request: Request, exc: TelegramRemoteSessionException):
    match type(exc).__name__:
        case "SessionNotExits":
            status_code = status.HTTP_400_BAD_REQUEST
        case _:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(
        status_code=status_code,
        content={"error": f"{type(exc).__name__}: {exc.message}."},
    )


@router.get("/get")
async def read_sessions(manager: TRSManager = Depends(context.get_session_manager)):
    return SessionList(sessions=manager.get_available_sessions_names())


@router.get("/get/{name}")
def read_session(name: str, manager: TRSManager = Depends(context.get_session_manager)):
    client = manager.get_client(name)
    return FullSessionData(
        session_name=name,
        proxy=client.proxy,
        file_path=client.session.filename,
        **client.session.session_params.model_dump()
    )


@router.get("/get_proxy/{name}")
def get_proxy(name: str, manager: TRSManager = Depends(context.get_session_manager)):
    client = manager.get_client(name)
    return SessionProxyData(session_name=name, proxy=client.proxy)
