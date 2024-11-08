import typing
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from configs import SESSIONS_PATH
from telegram.errors import SessionNotExits, TFAException
from telegram import TFAManager, TFASessionParameters


class SessionProxyData(BaseModel):
    session_name: str
    proxy: typing.Optional[str]

class FullSessionDataData(SessionProxyData, TFASessionParameters):
    file_path: Path

class SessionList(BaseModel):
    sessions: typing.List[str]

session_manager = TFAManager(sessions_path=SESSIONS_PATH)
app = FastAPI(
    title="TFA Server",
    version="0.0.1"
)

@app.exception_handler(TFAException)
async def unicorn_exception_handler(request: Request, exc: TFAException):
    match type(exc).__name__:
        case "SessionNotExits":
            status_code = status.HTTP_400_BAD_REQUEST
        case _:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return JSONResponse(
        status_code=status_code,
        content={"error": f"{type(exc).__name__}: {exc.message}."},
    )

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/sessions/get")
async def read_sessions():
    return SessionList(sessions=session_manager.get_available_sessions_names())


@app.get("/sessions/get/{name}")
def read_session(name: str):
    client = session_manager.get_client(name)
    return FullSessionDataData(
        session_name=name,
        proxy=client.proxy,
        file_path=client.session.filename,
        **client.session.session_params.model_dump()
    )

@app.get("/sessions/get_proxy/{name}")
def get_proxy(name: str):
    client = session_manager.get_client(name)
    return SessionProxyData(session_name=name, proxy=client.proxy)