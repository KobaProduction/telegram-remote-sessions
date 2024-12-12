from inspect import getmembers

from fastapi import APIRouter, Depends, Query

from server import context
from trs import TRSManager, TRSessionParameters
from trs.sessions import TRSessionState

from .entities import SessionList, FullSessionInfo, SessionResponseStatus, SessionAuthCodeHash, SessionAuthUser
from .error_handler_route import RouteWithErrorHandling

router = APIRouter(route_class=RouteWithErrorHandling, tags=["Sessions Methods"])

session_states = sorted(getmembers(TRSessionState, predicate=lambda x: isinstance(x, int)), key=lambda x: x[1])
states = ", ".join(f"{x[0]} - {x[1]}" for x in session_states)


@router.get("/sessions/read")
async def read_all_sessions(active: bool | None = Query(None, description="Account active state"),
                       state: TRSessionState | None = Query(None, description=states),
                       manager: TRSManager = Depends(context.get_session_manager)) -> SessionList:
    return SessionList(sessions=await manager.get_clients(active=active, state=state))


@router.get("/session/read")
async def read_session(name: str, manager: TRSManager = Depends(context.get_session_manager)) -> FullSessionInfo:
    client = await manager.get_client(name)
    return FullSessionInfo(
        is_active=client.session.active,
        is_broken=client.session.state == TRSessionState.BROKEN,
        is_authenticated=client.session.state == TRSessionState.AUTHENTICATED,
        session_parameters=client.session.session_params,
        proxy=client.session.proxy
    )


@router.post("/session/create")
async def create_new_session(name: str, session_parameters: TRSessionParameters,
                             manager: TRSManager = Depends(context.get_session_manager)) -> FullSessionInfo:
    await manager.create_client(name=name, session_params=session_parameters)
    return await read_session(name=name, manager=manager)


@router.delete("/session/delete")
async def delete_exist_session(name: str,
                               manager: TRSManager = Depends(context.get_session_manager)) -> SessionResponseStatus:
    await manager.delete_client(name=name)
    return SessionResponseStatus(status=True, message="Session successful removed!")

@router.put("/session/update")
async def update_exist_session(name: str,
                               active: bool | None = None,
                               proxy: str | None = Query(None, description="send 'null' to delete proxy"),
                               manager: TRSManager = Depends(context.get_session_manager)) -> FullSessionInfo:
    client = await manager.get_client(name)
    if active is not None and not active:
        client.session.deactivate()
    elif active:
        client.session.activate()
    if proxy is not None:
        proxy = None if proxy == "null" else proxy
        client.session.set_proxy(proxy)
    if proxy:
        client.set_proxy(proxy)
    return await read_session(name=name, manager=manager)

@router.get("/session/send_auth_code")
async def send_auth_code(name: str,
                         phone: str,
                         manager: TRSManager = Depends(context.get_session_manager)) -> SessionAuthCodeHash:
    client = await manager.get_client(name)
    if not client.is_connected():
        await client.connect()
    try:
        result = await client.send_code_request(phone=phone)
    finally:
        await client.disconnect()
    return SessionAuthCodeHash(phone=phone, hash=result.phone_code_hash)

@router.get("/session/auth")
async def confirm_auth(name: str,
                         phone: str,
                         code: str,
                         password: str | None = None,
                         phone_code_hash: str | None = None,
                         manager: TRSManager = Depends(context.get_session_manager)) -> SessionAuthUser:
    client = await manager.get_client(name)
    if not client.is_connected():
        await client.connect()
    try:
        user = await client.sign_in(phone=phone, code=code, password=password, phone_code_hash=phone_code_hash)
    finally:
        await client.disconnect()
    return SessionAuthUser(id=user.id, first_name=user.first_name, last_name=user.last_name, username=user.username)