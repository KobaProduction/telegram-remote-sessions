import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from configs import SERVER_PORT, SERVER_HOST
from server.api import api_router

SERVER_VERSION = "0.0.3"
SERVER_NAME = "Telegram Remote Sessions Server"

app = FastAPI(
    title=SERVER_NAME,
    version=SERVER_VERSION
)

app.include_router(api_router)


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


@app.get("/status")
async def get_status():
    return {
        "status": "ok",
        "version": SERVER_VERSION,
        "server_name": SERVER_NAME
    }


if __name__ == '__main__':
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
