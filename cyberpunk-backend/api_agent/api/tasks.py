"""
API Automation Agent Platform - Task API Routes

This module handles task-related endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from typing import List

from api_agent import settings
from api_agent.db import get_session
from api_agent.models import (
    TaskDB, TaskCreate, TaskResponse, TaskStatus
)

router = APIRouter()


@router.post("/", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create a new task"""
    import uuid

    task_id = str(uuid.uuid4())
    db_task = TaskDB(
        task_id=task_id,
        name=task.name,
        description=task.description,
        user_id=task.user_id,
        meta_data=task.metadata
    )

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    return TaskResponse(
        task_id=db_task.task_id,
        name=db_task.name,
        description=db_task.description,
        status=db_task.status,
        created_at=db_task.created_at.isoformat(),
        updated_at=db_task.updated_at.isoformat(),
        started_at=db_task.started_at.isoformat() if db_task.started_at else None,
        completed_at=db_task.completed_at.isoformat() if db_task.completed_at else None,
        result=db_task.result,
        error=db_task.error,
        meta_data=db_task.meta_data
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    session: Session = Depends(get_session)
):
    """Get task by ID"""
    db_task = session.get(TaskDB, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        task_id=db_task.task_id,
        name=db_task.name,
        description=db_task.description,
        status=db_task.status,
        created_at=db_task.created_at.isoformat(),
        updated_at=db_task.updated_at.isoformat(),
        started_at=db_task.started_at.isoformat() if db_task.started_at else None,
        completed_at=db_task.completed_at.isoformat() if db_task.completed_at else None,
        result=db_task.result,
        error=db_task.error,
        meta_data=db_task.meta_data
    )


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all tasks"""
    statement = select(TaskDB).offset(skip).limit(limit)
    results = session.exec(statement).all()

    return [
        TaskResponse(
            task_id=task.task_id,
            name=task.name,
            description=task.description,
            status=task.status,
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            result=task.result,
            error=task.error,
            meta_data=task.meta_data
        )
        for task in results
    ]


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    session: Session = Depends(get_session)
):
    """Delete task by ID"""
    db_task = session.get(TaskDB, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(db_task)
    session.commit()

    return {"message": "Task deleted successfully"}
