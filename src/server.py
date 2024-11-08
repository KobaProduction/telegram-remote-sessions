from fastapi import FastAPI

app = FastAPI(
    title="TFA Server",
    version="0.0.1"
)

@app.get("/status")
def get_status():
    return {"status": "ok"}