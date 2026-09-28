from fastapi import FastAPI
from api.auth import router as auth_router
from api.xray import router as xray_router

app = FastAPI(title="PneumoDetect")

app.include_router(auth_router)
app.include_router(xray_router)


@app.get("/health")
def health():
    return {"status": "ok"}