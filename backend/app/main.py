import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.models import db_models  # noqa: ensure models are loaded
from app.routers import scenarios, sessions, ws

# Configure logging so ws.py output appears in uvicorn logs
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()],
)

app = FastAPI(title="SpeakCoach AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(scenarios.router, prefix="/api", tags=["scenarios"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(ws.router, prefix="/api", tags=["websocket"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
