"""
请求队列

提供请求排队和优先级调度
"""

import asyncio
import time
from typing import Any, Callable, Dict, Optional, Awaitable
from dataclasses import dataclass, field
from enum import IntEnum
import heapq


class Priority(IntEnum):
    """请求优先级"""
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass(order=True)
class QueueItem:
    """队列项"""
    priority: int
    timestamp: float = field(compare=True)
    request_id: str = field(compare=False)
    data: Any = field(compare=False, default=None)
    callback: Optional[Callable] = field(compare=False, default=None)


class RequestQueue:
    """请求队列
    
    支持优先级排序的请求队列
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        num_workers: int = 10
    ):
        """初始化请求队列
        
        Args:
            max_size: 最大队列大小
            num_workers: 工作线程数
        """
        self.max_size = max_size
        self.num_workers = num_workers
        
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=max_size)
        self._workers = []
        self._running = False
        self._processed_count = 0
        self._error_count = 0
        
    @property
    def size(self) -> int:
        """当前队列大小"""
        return self._queue.qsize()
    
    @property
    def is_full(self) -> bool:
        """队列是否已满"""
        return self._queue.full()
    
    @property
    def stats(self) -> Dict[str, Any]:
        """队列统计信息"""
        return {
            "size": self.size,
            "max_size": self.max_size,
            "num_workers": self.num_workers,
            "running": self._running,
            "processed": self._processed_count,
            "errors": self._error_count
        }
    
    async def enqueue(
        self,
        request_id: str,
        data: Any,
        priority: Priority = Priority.NORMAL,
        callback: Optional[Callable[[Any], Awaitable]] = None
    ) -> bool:
        """添加请求到队列
        
        Args:
            request_id: 请求ID
            data: 请求数据
            priority: 优先级
            callback: 处理完成后的回调
            
        Returns:
            是否成功添加
        """
        if self.is_full:
            return False
        
        item = QueueItem(
            priority=priority.value,
            timestamp=time.time(),
            request_id=request_id,
            data=data,
            callback=callback
        )
        
        await self._queue.put(item)
        return True
    
    async def dequeue(self) -> Optional[QueueItem]:
        """从队列获取请求
        
        Returns:
            队列项，如果队列为空返回None
        """
        try:
            return await asyncio.wait_for(
                self._queue.get(),
                timeout=1.0
            )
        except asyncio.TimeoutError:
            return None
    
    async def start_workers(
        self,
        handler: Callable[[Any], Awaitable[Any]]
    ):
        """启动工作线程
        
        Args:
            handler: 请求处理函数
        """
        if self._running:
            return
        
        self._running = True
        
        for i in range(self.num_workers):
            worker = asyncio.create_task(
                self._worker_loop(f"worker-{i}", handler)
            )
            self._workers.append(worker)
    
    async def _worker_loop(
        self,
        worker_name: str,
        handler: Callable[[Any], Awaitable[Any]]
    ):
        """工作线程循环
        
        Args:
            worker_name: 工作线程名称
            handler: 处理函数
        """
        while self._running:
            item = await self.dequeue()
            
            if item is None:
                continue
            
            try:
                result = await handler(item.data)
                self._processed_count += 1
                
                if item.callback:
                    await item.callback(result)
                    
            except Exception as e:
                self._error_count += 1
                
                if item.callback:
                    await item.callback({"error": str(e)})
    
    async def stop_workers(self):
        """停止所有工作线程"""
        self._running = False
        
        # 等待所有工作线程完成
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
    
    async def clear(self):
        """清空队列"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break


class AsyncTaskManager:
    """异步任务管理器
    
    管理后台异步任务
    """
    
    def __init__(self, max_tasks: int = 100):
        """初始化任务管理器
        
        Args:
            max_tasks: 最大任务数
        """
        self.max_tasks = max_tasks
        self._tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
    
    async def submit(
        self,
        task_id: str,
        coro: Awaitable,
        on_complete: Optional[Callable] = None
    ) -> bool:
        """提交任务
        
        Args:
            task_id: 任务ID
            coro: 协程
            on_complete: 完成回调
            
        Returns:
            是否成功提交
        """
        async with self._lock:
            if len(self._tasks) >= self.max_tasks:
                return False
            
            if task_id in self._tasks:
                return False
            
            async def wrapped():
                try:
                    result = await coro
                    if on_complete:
                        on_complete(result)
                finally:
                    async with self._lock:
                        self._tasks.pop(task_id, None)
            
            task = asyncio.create_task(wrapped())
            self._tasks[task_id] = task
            return True
    
    async def cancel(self, task_id: str) -> bool:
        """取消任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            是否成功取消
        """
        async with self._lock:
            if task_id in self._tasks:
                self._tasks[task_id].cancel()
                del self._tasks[task_id]
                return True
            return False
    
    def get_status(self, task_id: str) -> Optional[str]:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态
        """
        if task_id not in self._tasks:
            return None
        
        task = self._tasks[task_id]
        if task.done():
            return "completed"
        elif task.cancelled():
            return "cancelled"
        else:
            return "running"
    
    @property
    def active_count(self) -> int:
        """活跃任务数"""
        return len(self._tasks)
