from inspect import getmembers

from fastapi import APIRouter, Depends, Query

from context import context
from trs import TRSManager
from trs.sessions import TRSessionState

from .entities import SessionList, FullSessionInfo
from .error_handler_route import RouteWithErrorHandling

router = APIRouter(prefix="/sessions", route_class=RouteWithErrorHandling)

session_states = sorted(getmembers(TRSessionState, predicate=lambda x: isinstance(x, int)), key=lambda x: x[1])
states = ", ".join(f"{x[0]} - {x[1]}" for x in session_states)


@router.get("/get")
async def get_sessions(active: bool | None = Query(None, description="Account active state"),
                        state: TRSessionState | None = Query(None, description=states),
                        manager: TRSManager = Depends(context.get_session_manager)) -> SessionList:
    return SessionList(sessions=manager.get_sessions(active=active, state=state))


@router.get("/get/{name}")
def get_session(name: str, manager: TRSManager = Depends(context.get_session_manager)) -> FullSessionInfo:
    client = manager.get_client(name)
    return FullSessionInfo(
        name=name,
        is_active=client.session.active,
        is_broken=client.session.state == TRSessionState.BROKEN,
        is_authenticated=client.session.state == TRSessionState.AUTHENTICATED,
        session_parameters=client.session.session_params,
        proxy=client.session.proxy
    )
