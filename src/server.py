from fastapi import FastAPI

from api import session_router, sessions_exception_handler
from telegram.errors import TFAException

app = FastAPI(
    title="TFA Server",
    version="0.0.1"
)

app.include_router(session_router)
app.exception_handler(TFAException)(sessions_exception_handler)

@app.get("/")
async def read_root():
    return {"Hello": "World"}