from inspect import getmembers

from fastapi import APIRouter, Depends, Query

from context import context
from trs import TRSManager, TRSessionParameters
from trs.sessions import TRSessionState

from .entities import SessionList, FullSessionInfo, SessionResponseStatus
from .error_handler_route import RouteWithErrorHandling

router = APIRouter(prefix="/sessions", route_class=RouteWithErrorHandling)

session_states = sorted(getmembers(TRSessionState, predicate=lambda x: isinstance(x, int)), key=lambda x: x[1])
states = ", ".join(f"{x[0]} - {x[1]}" for x in session_states)


@router.get("/get")
async def get_sessions(active: bool | None = Query(None, description="Account active state"),
                       state: TRSessionState | None = Query(None, description=states),
                       manager: TRSManager = Depends(context.get_session_manager)) -> SessionList:
    return SessionList(sessions=await manager.get_clients(active=active, state=state))


@router.get("/get/{name}")
async def get_session(name: str, manager: TRSManager = Depends(context.get_session_manager)) -> FullSessionInfo:
    client = await manager.get_client(name)
    return FullSessionInfo(
        name=name,
        is_active=client.session.active,
        is_broken=client.session.state == TRSessionState.BROKEN,
        is_authenticated=client.session.state == TRSessionState.AUTHENTICATED,
        session_parameters=client.session.session_params,
        proxy=client.session.proxy
    )


@router.post("/new")
async def create_new_session(name: str, session_parameters: TRSessionParameters,
                             manager: TRSManager = Depends(context.get_session_manager)) -> FullSessionInfo:
    await manager.create_client(name=name, session_params=session_parameters)
    return await get_session(name=name, manager=manager)


@router.delete("/remove")
async def remove_exist_session(name: str,
                               manager: TRSManager = Depends(context.get_session_manager)) -> SessionResponseStatus:
    await manager.remove_client(name=name)
    return SessionResponseStatus(status=True, message="Session successful removed!")
