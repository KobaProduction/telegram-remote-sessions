import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from configs import SERVER_HOST, SERVER_PORT
from server import api_router, SERVER_NAME, SERVER_VERSION

app = FastAPI(
    title=SERVER_NAME,
    version=SERVER_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
async def read_root():
    return RedirectResponse("/docs")


if __name__ == '__main__':
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)
