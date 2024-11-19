from fastapi import FastAPI

from api import client_methods_router, session_router, sessions_exception_handler
from telegram.errors import TelegramRemoteSessionException

app = FastAPI(
    title="Telegram Remote Sessions Server",
    version="0.0.1"
)

app.include_router(client_methods_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.exception_handler(TelegramRemoteSessionException)(sessions_exception_handler)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
