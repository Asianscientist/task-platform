from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Task, TaskStatus, User
from app.schemas import TaskCreate, TaskResponse
from app.services.queue import enqueue_task

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = Task(
        user_id=user.id,
        type=data.type,
        payload=data.payload,
        status=TaskStatus.QUEUED,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        enqueue_task(str(task.id))
    except Exception as exc:
        task.status = TaskStatus.FAILED
        task.error = f"Queue unavailable: {exc}"
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=503, detail="Queue unavailable")

    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list(
        db.scalars(
            select(Task)
            .where(Task.user_id == user.id)
            .order_by(Task.created_at.desc())
            .limit(100)
        )
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = db.scalar(select(Task).where(Task.id == task_id, Task.user_id == user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == TaskStatus.RUNNING:
        raise HTTPException(status_code=409, detail="Cannot delete a running task")
    db.delete(task)
    db.commit()
