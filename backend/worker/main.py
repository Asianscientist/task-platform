import json
import threading
import time
from datetime import datetime, timezone

from prometheus_client import Counter, Gauge, start_http_server
from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models import Task, TaskStatus
from app.services.queue import pop_task

settings = get_settings()

PROCESSED = Counter("worker_tasks_processed_total", "Tasks processed", ["status", "type"])
PROCESSING_SECONDS = Gauge("worker_current_task_seconds", "Current task elapsed time")
QUEUE_DEPTH = Gauge("worker_queue_depth", "Redis queue depth")


def execute_task(task_type: str, payload: dict) -> str:
    if task_type == "sleep":
        seconds = float(payload.get("seconds", 1))
        if seconds < 0 or seconds > 60:
            raise ValueError("sleep seconds must be between 0 and 60")
        time.sleep(seconds)
        return json.dumps({"slept_seconds": seconds})

    if task_type == "echo":
        return json.dumps({"echo": payload.get("message", "")})

    raise ValueError(f"Unknown task type: {task_type}")


def process(task_id: str):
    db = SessionLocal()
    start = time.perf_counter()
    task = None
    try:
        task = db.scalar(select(Task).where(Task.id == task_id))
        if not task:
            return

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        task.error = None
        db.commit()

        result = execute_task(task.type, task.payload or {})

        task.status = TaskStatus.COMPLETED
        task.result = result
        PROCESSED.labels("completed", task.type).inc()
    except Exception as exc:
        if task:
            task.status = TaskStatus.FAILED
            task.error = str(exc)
        PROCESSED.labels("failed", task.type if task else "unknown").inc()
    finally:
        if task:
            task.completed_at = datetime.now(timezone.utc)
            db.commit()
        PROCESSING_SECONDS.set(0)
        db.close()


def main():
    init_db()
    start_http_server(settings.worker_metrics_port)

    while True:
        try:
            item = pop_task(timeout=5)
            QUEUE_DEPTH.set(0 if item is None else 1)
            if item:
                PROCESSING_SECONDS.set(0)
                process(item["task_id"])
        except Exception:
            time.sleep(1)


if __name__ == "__main__":
    main()
