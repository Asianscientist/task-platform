from fastapi import APIRouter

from app.config import get_settings
from app.schemas import WorkerResponse
from app.services.queue import queue_length

router = APIRouter(prefix="/api/workers", tags=["workers"])


@router.get("", response_model=list[WorkerResponse])
def workers():
    settings = get_settings()
    return [
        WorkerResponse(
            worker_id=settings.worker_id,
            status="online",
            queue=settings.queue_name,
        )
    ]


@router.get("/queue")
def queue_status():
    return {"queue": get_settings().queue_name, "length": queue_length()}
