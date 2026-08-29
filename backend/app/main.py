from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.auth import router as auth_router
from app.api.tasks import router as tasks_router
from app.api.workers import router as workers_router
from app.config import get_settings
from app.database import init_db
from app.middleware.metrics import metrics_middleware

settings = get_settings()

app = FastAPI(
    title="Task Platform API",
    version="1.0.0",
    description="Small real-time task/job processing platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(metrics_middleware)

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(workers_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


@app.get("/metrics", tags=["system"])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
