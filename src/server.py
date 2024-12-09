import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from api import api_router
from configs import SERVER_PORT, SERVER_HOST

app = FastAPI(
    title="Telegram Remote Sessions Server",
    version="0.0.2"
)

app.include_router(api_router)


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


if __name__ == '__main__':
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
