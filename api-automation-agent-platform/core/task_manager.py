"""
异步任务管理系统 - 后台任务执行和监控

职责：
- 异步任务调度和执行
- 任务状态跟踪
- 任务结果存储
- 任务队列管理
- 任务超时和重试
"""
from typing import Any, Dict, List, Optional, Callable
import asyncio
import uuid
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field

from core.logging_config import get_logger

logger = get_logger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"          # 等待执行
    RUNNING = "running"          # 执行中
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"      # 已取消
    TIMEOUT = "timeout"          # 超时


@dataclass
class Task:
    """任务数据模型"""
    task_id: str
    task_type: str
    task_name: str
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "task_name": self.task_name,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }


class TaskManager:
    """
    异步任务管理器

    核心功能：
    - 任务创建和调度
    - 任务状态管理
    - 任务执行监控
    - 任务结果存储
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        """
        初始化任务管理器

        Args:
            max_concurrent_tasks: 最大并发任务数
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._worker_started = False

        logger.info(f"任务管理器初始化完成: max_concurrent={max_concurrent_tasks}")

    async def start_workers(self):
        """启动后台工作线程"""
        if not self._worker_started:
            self._worker_started = True
            # 启动多个工作协程
            for i in range(self.max_concurrent_tasks):
                asyncio.create_task(self._worker(i))
            logger.info(f"启动 {self.max_concurrent_tasks} 个工作协程")

    async def _worker(self, worker_id: int):
        """工作协程 - 从队列中获取任务并执行"""
        logger.info(f"工作协程 {worker_id} 启动")

        while True:
            try:
                # 从队列获取任务
                task_id, task_func, task_args, task_kwargs = await self.task_queue.get()

                # 获取信号量
                async with self.semaphore:
                    task = self.tasks.get(task_id)
                    if task and task.status == TaskStatus.PENDING:
                        await self._execute_task(task, task_func, task_args, task_kwargs)

                # 标记任务完成
                self.task_queue.task_done()

            except Exception as e:
                logger.error(f"工作协程 {worker_id} 异常: {e}", exc_info=e)
                await asyncio.sleep(1)

    async def create_task(
        self,
        task_type: str,
        task_name: str,
        task_func: Callable,
        *args,
        timeout: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """
        创建异步任务

        Args:
            task_type: 任务类型
            task_name: 任务名称
            task_func: 任务执行函数
            timeout: 超时时间（秒）
            metadata: 任务元数据
            *args, **kwargs: 传递给任务函数的参数

        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())

        # 创建任务对象
        task = Task(
            task_id=task_id,
            task_type=task_type,
            task_name=task_name,
            metadata=metadata or {}
        )

        if timeout:
            task.metadata["timeout"] = timeout

        # 保存任务
        self.tasks[task_id] = task

        # 加入队列
        await self.task_queue.put((task_id, task_func, args, kwargs))

        logger.info(f"创建任务: {task_id} - {task_name}")
        return task_id

    async def _execute_task(
        self,
        task: Task,
        task_func: Callable,
        args: tuple,
        kwargs: dict
    ):
        """执行任务"""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow().isoformat()

        logger.info(f"开始执行任务: {task.task_id} - {task.task_name}")

        try:
            # 获取超时设置
            timeout = task.metadata.get("timeout")

            # 执行任务（带超时控制）
            if timeout:
                result = await asyncio.wait_for(
                    task_func(*args, **kwargs),
                    timeout=timeout
                )
            else:
                result = await task_func(*args, **kwargs)

            # 任务成功
            task.status = TaskStatus.COMPLETED
            task.result = result
            task.progress = 100.0
            task.completed_at = datetime.utcnow().isoformat()

            logger.info(f"任务执行成功: {task.task_id}")

        except asyncio.TimeoutError:
            task.status = TaskStatus.TIMEOUT
            task.error = f"任务超时（{timeout}秒）"
            task.completed_at = datetime.utcnow().isoformat()
            logger.error(f"任务超时: {task.task_id}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow().isoformat()
            logger.error(f"任务执行失败: {task.task_id} - {e}", exc_info=e)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务信息"""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def get_task_status(self, task_id: str) -> Optional[str]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        return task.status.value if task else None

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务结果"""
        task = self.tasks.get(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        task_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        列出任务

        Args:
            status: 按状态筛选
            task_type: 按类型筛选
            limit: 返回数量限制

        Returns:
            任务列表
        """
        tasks = list(self.tasks.values())

        # 筛选
        if status:
            tasks = [t for t in tasks if t.status == status]
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]

        # 按创建时间倒序排序
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        # 限制数量
        tasks = tasks[:limit]

        return [t.to_dict() for t in tasks]

    async def cancel_task(self, task_id: str) -> bool:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        task = self.tasks.get(task_id)

        if not task:
            return False

        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False

        # 如果任务正在运行，尝试取消
        if task_id in self.running_tasks:
            self.running_tasks[task_id].cancel()
            del self.running_tasks[task_id]

        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow().isoformat()

        logger.info(f"任务已取消: {task_id}")
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """获取任务统计信息"""
        total = len(self.tasks)
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        running = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        cancelled = sum(1 for t in self.tasks.values() if t.status == TaskStatus.CANCELLED)
        timeout = sum(1 for t in self.tasks.values() if t.status == TaskStatus.TIMEOUT)

        return {
            "total_tasks": total,
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
            "cancelled": cancelled,
            "timeout": timeout,
            "queue_size": self.task_queue.qsize(),
            "max_concurrent": self.max_concurrent_tasks
        }

    def cleanup_old_tasks(self, days: int = 7):
        """
        清理旧任务

        Args:
            days: 保留天数
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        tasks_to_remove = []
        for task_id, task in self.tasks.items():
            created_at = datetime.fromisoformat(task.created_at)
            if created_at < cutoff_time and task.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
                TaskStatus.TIMEOUT
            ]:
                tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self.tasks[task_id]

        logger.info(f"清理了 {len(tasks_to_remove)} 个旧任务")


# 全局任务管理器实例
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    """获取全局任务管理器实例"""
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager

