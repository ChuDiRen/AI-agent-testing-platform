"""
并发控制测试
"""

import pytest
import asyncio
import time

from ..concurrency.limiter import RateLimiter, ConcurrencyLimiter, CombinedLimiter
from ..concurrency.queue import RequestQueue, Priority, AsyncTaskManager


class TestRateLimiter:
    """速率限制器测试"""
    
    @pytest.mark.asyncio
    async def test_basic_rate_limit(self):
        """测试基本速率限制"""
        limiter = RateLimiter(requests_per_second=5)
        
        # 应该能快速获取5个许可
        for _ in range(5):
            info = await limiter.acquire()
            assert info.remaining >= 0
    
    @pytest.mark.asyncio
    async def test_rate_limit_check(self):
        """测试限流状态检查"""
        limiter = RateLimiter(requests_per_second=10)
        
        info = await limiter.check()
        
        assert info.limit == 10
        assert info.remaining == 10
    
    @pytest.mark.asyncio
    async def test_rate_limit_context_manager(self):
        """测试限流上下文管理器"""
        limiter = RateLimiter(requests_per_second=5)
        
        async with limiter.limited():
            pass  # 执行请求
        
        info = await limiter.check()
        assert info.remaining == 4  # 使用了1个


class TestConcurrencyLimiter:
    """并发限制器测试"""
    
    @pytest.mark.asyncio
    async def test_basic_concurrency(self):
        """测试基本并发限制"""
        limiter = ConcurrencyLimiter(max_concurrent=2)
        
        results = []
        
        async def task(n):
            async with limiter.acquire():
                results.append(f"start_{n}")
                await asyncio.sleep(0.1)
                results.append(f"end_{n}")
        
        await asyncio.gather(task(1), task(2), task(3))
        
        # 所有任务都应该完成
        assert len(results) == 6
    
    @pytest.mark.asyncio
    async def test_active_count(self):
        """测试活跃计数"""
        limiter = ConcurrencyLimiter(max_concurrent=5)
        
        assert limiter.active_count == 0
        assert limiter.available == 5
    
    @pytest.mark.asyncio
    async def test_wait_for_slot(self):
        """测试等待槽位"""
        limiter = ConcurrencyLimiter(max_concurrent=1)
        
        # 应该能立即获取
        result = await limiter.wait_for_slot(timeout=1.0)
        assert result is True


class TestCombinedLimiter:
    """组合限流器测试"""
    
    @pytest.mark.asyncio
    async def test_combined_limiting(self):
        """测试组合限流"""
        limiter = CombinedLimiter(
            requests_per_minute=100,
            max_concurrent=5
        )
        
        executed = 0
        
        async def task():
            nonlocal executed
            async with limiter.acquire():
                executed += 1
                await asyncio.sleep(0.01)
        
        await asyncio.gather(*[task() for _ in range(10)])
        
        assert executed == 10


class TestRequestQueue:
    """请求队列测试"""
    
    @pytest.mark.asyncio
    async def test_enqueue_dequeue(self):
        """测试入队出队"""
        queue = RequestQueue(max_size=10)
        
        # 入队
        success = await queue.enqueue("req1", {"data": "test"})
        assert success is True
        assert queue.size == 1
        
        # 出队
        item = await queue.dequeue()
        assert item is not None
        assert item.request_id == "req1"
        assert queue.size == 0
    
    @pytest.mark.asyncio
    async def test_priority_ordering(self):
        """测试优先级排序"""
        queue = RequestQueue(max_size=10)
        
        await queue.enqueue("low", {}, Priority.LOW)
        await queue.enqueue("high", {}, Priority.HIGH)
        await queue.enqueue("normal", {}, Priority.NORMAL)
        
        # 高优先级应该先出队
        item1 = await queue.dequeue()
        assert item1.request_id == "high"
        
        item2 = await queue.dequeue()
        assert item2.request_id == "normal"
        
        item3 = await queue.dequeue()
        assert item3.request_id == "low"
    
    @pytest.mark.asyncio
    async def test_queue_full(self):
        """测试队列满"""
        queue = RequestQueue(max_size=2)
        
        await queue.enqueue("req1", {})
        await queue.enqueue("req2", {})
        
        # 队列满，应该失败
        success = await queue.enqueue("req3", {})
        assert success is False
    
    def test_queue_stats(self):
        """测试队列统计"""
        queue = RequestQueue(max_size=100, num_workers=5)
        
        stats = queue.stats
        
        assert stats["max_size"] == 100
        assert stats["num_workers"] == 5
        assert stats["size"] == 0


class TestAsyncTaskManager:
    """异步任务管理器测试"""
    
    @pytest.mark.asyncio
    async def test_submit_task(self):
        """测试提交任务"""
        manager = AsyncTaskManager(max_tasks=10)
        
        result_holder = []
        
        async def task():
            await asyncio.sleep(0.1)
            return "done"
        
        success = await manager.submit(
            "task1", 
            task(),
            on_complete=lambda r: result_holder.append(r)
        )
        
        assert success is True
        assert manager.active_count == 1
        
        # 等待任务完成
        await asyncio.sleep(0.2)
        
        assert "done" in result_holder
    
    @pytest.mark.asyncio
    async def test_cancel_task(self):
        """测试取消任务"""
        manager = AsyncTaskManager()
        cancelled_flag = False
        
        async def long_task():
            nonlocal cancelled_flag
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                cancelled_flag = True
                raise
        
        await manager.submit("task1", long_task())
        
        # 等待任务开始执行
        await asyncio.sleep(0.01)
        
        success = await manager.cancel("task1")
        assert success is True
        
        # 等待取消完成
        await asyncio.sleep(0.01)
        
        status = manager.get_status("task1")
        assert status is None  # 已删除
    
    @pytest.mark.asyncio
    async def test_max_tasks_limit(self):
        """测试最大任务数限制"""
        manager = AsyncTaskManager(max_tasks=2)
        
        async def task():
            try:
                await asyncio.sleep(0.1)  # 缩短等待时间
            except asyncio.CancelledError:
                pass
        
        await manager.submit("t1", task())
        await manager.submit("t2", task())
        
        # 超过限制 - 需要先创建协程，然后处理拒绝的情况
        coro = task()
        success = await manager.submit("t3", coro)
        assert success is False
        # 如果提交失败，需要关闭未使用的协程
        coro.close()
        
        # 等待已提交的任务完成
        await asyncio.sleep(0.15)
        
        # 取消所有任务
        await manager.cancel("t1")
        await manager.cancel("t2")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
