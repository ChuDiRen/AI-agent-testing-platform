"""
限流器

提供请求速率限制和并发控制
"""

import asyncio
import time
from typing import Optional
from contextlib import asynccontextmanager
from dataclasses import dataclass


@dataclass
class RateLimitInfo:
    """限流信息"""
    limit: int
    remaining: int
    reset_at: float
    
    @property
    def retry_after(self) -> float:
        """返回重试等待时间（秒）"""
        return max(0, self.reset_at - time.time())


class RateLimiter:
    """请求速率限制器
    
    使用滑动窗口算法限制请求速率
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_second: int = 0
    ):
        """初始化限流器
        
        Args:
            requests_per_minute: 每分钟请求数限制
            requests_per_second: 每秒请求数限制（优先）
        """
        if requests_per_second > 0:
            self.max_requests = requests_per_second
            self.window_seconds = 1
        else:
            self.max_requests = requests_per_minute
            self.window_seconds = 60
        
        self._requests = []
        self._lock = asyncio.Lock()
    
    def _cleanup_old_requests(self):
        """清理过期的请求记录"""
        cutoff = time.time() - self.window_seconds
        self._requests = [t for t in self._requests if t > cutoff]
    
    async def acquire(self) -> RateLimitInfo:
        """获取请求许可
        
        如果超过限制，会等待直到可以发送请求
        
        Returns:
            限流信息
        """
        async with self._lock:
            self._cleanup_old_requests()
            
            if len(self._requests) >= self.max_requests:
                # 需要等待
                wait_time = self._requests[0] + self.window_seconds - time.time()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    self._cleanup_old_requests()
            
            # 记录请求
            now = time.time()
            self._requests.append(now)
            
            return RateLimitInfo(
                limit=self.max_requests,
                remaining=self.max_requests - len(self._requests),
                reset_at=now + self.window_seconds
            )
    
    async def check(self) -> RateLimitInfo:
        """检查限流状态（不消耗配额）
        
        Returns:
            限流信息
        """
        async with self._lock:
            self._cleanup_old_requests()
            
            now = time.time()
            remaining = self.max_requests - len(self._requests)
            
            if self._requests:
                reset_at = self._requests[0] + self.window_seconds
            else:
                reset_at = now + self.window_seconds
            
            return RateLimitInfo(
                limit=self.max_requests,
                remaining=remaining,
                reset_at=reset_at
            )
    
    @asynccontextmanager
    async def limited(self):
        """限流上下文管理器
        
        Usage:
            async with limiter.limited():
                # 执行请求
                pass
        """
        await self.acquire()
        yield


class ConcurrencyLimiter:
    """并发限制器
    
    限制同时执行的请求数量
    """
    
    def __init__(self, max_concurrent: int = 100):
        """初始化并发限制器
        
        Args:
            max_concurrent: 最大并发数
        """
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._active_count = 0
        self._lock = asyncio.Lock()
    
    @property
    def active_count(self) -> int:
        """当前活跃请求数"""
        return self._active_count
    
    @property
    def available(self) -> int:
        """可用并发数"""
        return self.max_concurrent - self._active_count
    
    @asynccontextmanager
    async def acquire(self):
        """获取并发许可
        
        Usage:
            async with limiter.acquire():
                # 执行请求
                pass
        """
        async with self._semaphore:
            async with self._lock:
                self._active_count += 1
            try:
                yield
            finally:
                async with self._lock:
                    self._active_count -= 1
    
    async def wait_for_slot(self, timeout: float = None) -> bool:
        """等待可用槽位
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            是否成功获取槽位
        """
        try:
            if timeout:
                await asyncio.wait_for(
                    self._semaphore.acquire(),
                    timeout=timeout
                )
            else:
                await self._semaphore.acquire()
            
            self._semaphore.release()
            return True
            
        except asyncio.TimeoutError:
            return False


class CombinedLimiter:
    """组合限流器
    
    同时应用速率限制和并发限制
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        max_concurrent: int = 100
    ):
        """初始化组合限流器
        
        Args:
            requests_per_minute: 每分钟请求数限制
            max_concurrent: 最大并发数
        """
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.concurrency_limiter = ConcurrencyLimiter(max_concurrent)
    
    @asynccontextmanager
    async def acquire(self):
        """获取请求许可
        
        同时满足速率和并发限制
        """
        await self.rate_limiter.acquire()
        async with self.concurrency_limiter.acquire():
            yield


# 全局限流器实例
_global_limiter: Optional[CombinedLimiter] = None


def get_limiter(
    requests_per_minute: int = 60,
    max_concurrent: int = 100
) -> CombinedLimiter:
    """获取全局限流器
    
    Args:
        requests_per_minute: 每分钟请求数
        max_concurrent: 最大并发数
        
    Returns:
        CombinedLimiter实例
    """
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = CombinedLimiter(
            requests_per_minute=requests_per_minute,
            max_concurrent=max_concurrent
        )
    return _global_limiter
