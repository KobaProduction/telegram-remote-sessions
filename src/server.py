import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from api import client_methods_router, session_router, sessions_exception_handler
from trs.errors import TelegramRemoteSessionException

app = FastAPI(
    title="Telegram Remote Sessions Server",
    version="0.0.1"
)

app.include_router(client_methods_router, prefix="/api")
app.include_router(session_router, prefix="/api")
app.exception_handler(TelegramRemoteSessionException)(sessions_exception_handler)


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=3000)
