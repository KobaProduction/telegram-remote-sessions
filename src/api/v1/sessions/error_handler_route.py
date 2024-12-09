from typing import Callable

from fastapi import Request, status
from fastapi.responses import Response, JSONResponse
from fastapi.routing import APIRoute, APIRouter

from trs.errors import TelegramRemoteSessionException


class RouteWithErrorHandling(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as exc:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                if isinstance(exc, TelegramRemoteSessionException) and type(exc).__name__ == "SessionNotExits":
                    status_code = status.HTTP_400_BAD_REQUEST
                return JSONResponse(
                    status_code=status_code,
                    content={"error": f"{type(exc).__name__}: {exc.message}."},
                )
        return custom_route_handler
