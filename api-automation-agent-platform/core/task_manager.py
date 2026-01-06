"""
Task Manager - Async Task Management System

Manages background task execution, status tracking, and result retrieval.
"""
from typing import Any, Dict, Optional, Callable, Awaitable
from datetime import datetime
import asyncio
import json
import uuid

from api_agent.models import TaskDB, TaskStatus
from api_agent.db import get_session


class TaskManager:
    """
    Async Task Manager

    Handles:
    - Background task execution
    - Status tracking and updates
    - Result storage and retrieval
    - Error handling and retry
    """

    def __init__(self):
        """Initialize task manager"""
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_results: Dict[str, Any] = {}
        self.max_concurrent_tasks = 10
        self.task_semaphore = asyncio.Semaphore(self.max_concurrent_tasks)

    async def create_task(
        self,
        name: str,
        func: Callable[..., Awaitable[Any]],
        description: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Create a new background task

        Args:
            name: Task name
            func: Async function to execute
            description: Optional description
            user_id: Optional user ID
            **kwargs: Arguments to pass to the function

        Returns:
            Task ID
        """

        task_id = str(uuid.uuid4())

        # Create task in database
        task = TaskDB(
            task_id=task_id,
            name=name,
            description=description,
            user_id=user_id,
            status=TaskStatus.PENDING,
            meta_data={"kwargs": kwargs}
        )

        session = next(get_session())
        session.add(task)
        session.commit()

        # Schedule background execution
        asyncio_task = asyncio.create_task(
            self._execute_task(task_id, func, kwargs)
        )

        self.running_tasks[task_id] = asyncio_task

        return task_id

    async def _execute_task(
        self,
        task_id: str,
        func: Callable[..., Awaitable[Any]],
        kwargs: Dict[str, Any]
    ):
        """
        Execute task in background

        Args:
            task_id: Task ID
            func: Function to execute
            kwargs: Function arguments
        """

        async with self.task_semaphore:
            try:
                # Update status to running
                await self._update_task_status(task_id, TaskStatus.RUNNING)

                # Execute function
                result = await func(**kwargs)

                # Store result
                self.task_results[task_id] = result

                # Update status to completed
                await self._update_task_status(
                    task_id,
                    TaskStatus.COMPLETED,
                    result=result
                )

            except Exception as e:
                # Update status to failed
                await self._update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    error=str(e)
                )

            finally:
                # Remove from running tasks
                self.running_tasks.pop(task_id, None)

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task status

        Args:
            task_id: Task ID

        Returns:
            Task status information or None
        """

        session = next(get_session())

        task = session.query(TaskDB).filter(TaskDB.task_id == task_id).first()

        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "status": task.status.value,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error": task.error,
            "metadata": task.meta_data
        }

    async def get_task_result(self, task_id: str) -> Optional[Any]:
        """
        Get task result

        Args:
            task_id: Task ID

        Returns:
            Task result or None
        """

        return self.task_results.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running task

        Args:
            task_id: Task ID

        Returns:
            True if cancelled successfully
        """

        if task_id not in self.running_tasks:
            return False

        task = self.running_tasks[task_id]
        task.cancel()

        await self._update_task_status(task_id, TaskStatus.CANCELLED)

        return True

    async def list_tasks(
        self,
        user_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> list:
        """
        List tasks

        Args:
            user_id: Optional user ID filter
            status: Optional status filter
            limit: Maximum number of tasks to return

        Returns:
            List of tasks
        """

        session = next(get_session())

        query = session.query(TaskDB)

        if user_id:
            query = query.filter(TaskDB.user_id == user_id)

        if status:
            query = query.filter(TaskDB.status == status)

        query = query.order_by(TaskDB.created_at.desc()).limit(limit)

        tasks = query.all()

        return [
            {
                "task_id": task.task_id,
                "name": task.name,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in tasks
        ]

    async def _update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ):
        """Update task status in database"""

        session = next(get_session())

        task = session.query(TaskDB).filter(TaskDB.task_id == task_id).first()

        if task:
            task.status = status
            task.updated_at = datetime.utcnow()

            if status == TaskStatus.RUNNING:
                task.started_at = datetime.utcnow()
            elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                task.completed_at = datetime.utcnow()

            if result:
                task.result = result

            if error:
                task.error = error

            session.commit()

    async def cleanup_old_tasks(self, days: int = 7):
        """
        Clean up old completed tasks

        Args:
            days: Number of days after which to clean up
        """

        from datetime import timedelta

        session = next(get_session())

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        old_tasks = session.query(TaskDB).filter(
            TaskDB.status.in_([TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]),
            TaskDB.completed_at < cutoff_date
        ).all()

        for task in old_tasks:
            # Clean up results
            self.task_results.pop(task.task_id, None)
            session.delete(task)

        session.commit()

        return len(old_tasks)


# Global task manager instance
task_manager = TaskManager()
