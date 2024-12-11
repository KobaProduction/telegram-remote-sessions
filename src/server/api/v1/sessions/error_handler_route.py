from typing import Callable

from fastapi import Request, status
from fastapi.responses import Response, JSONResponse
from fastapi.routing import APIRoute

from trs.errors import TelegramRemoteSessionException
from .entities import SessionResponseStatus


class RouteWithErrorHandling(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except Exception as exc:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                exc_message = str(exc)
                if isinstance(exc, TelegramRemoteSessionException) and type(exc).__name__ == "SessionNotExits":
                    status_code = status.HTTP_400_BAD_REQUEST
                    exc_message = exc.message
                return JSONResponse(
                    status_code=status_code,
                    content=SessionResponseStatus(
                        status=False,
                        message=f"Error - {type(exc).__name__}: {exc_message}.",
                    ).model_dump()
                )
        return custom_route_handler
