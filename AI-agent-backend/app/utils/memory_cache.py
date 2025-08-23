"""
内存缓存模块
提供一个简单的、线程安全的、支持TTL的内存缓存实现。
"""

import time
from threading import RLock
from typing import Any, Optional, Dict

from app.core.logger import get_logger

logger = get_logger(__name__)


class MemoryCache:
    """
    一个简单的内存缓存实现，支持过期时间（TTL）和线程安全。
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
        self._lock = RLock()
        logger.info("Initialized in-memory cache")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存项。
        如果键不存在或已过期，则返回默认值。
        """
        with self._lock:
            if self._is_expired(key):
                self.delete(key)
                return default
            return self._cache.get(key, default)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存项。
        
        Args:
            key: 键名
            value: 值
            ttl: 过期时间（秒）。如果为None，则永不过期。
        """
        with self._lock:
            self._cache[key] = value
            if ttl is not None and ttl > 0:
                self._ttl[key] = time.time() + ttl
            else:
                # 如果ttl是None或0，表示永不过期，从ttl字典中移除
                if key in self._ttl:
                    del self._ttl[key]
            logger.debug(f"In-memory cache set: {key} (TTL: {ttl}s)")
        return True

    def delete(self, key: str) -> bool:
        """
        删除缓存项。
        """
        with self._lock:
            deleted = False
            if key in self._cache:
                del self._cache[key]
                deleted = True
            if key in self._ttl:
                del self._ttl[key]
            if deleted:
                logger.debug(f"In-memory cache deleted: {key}")
            return deleted

    def exists(self, key: str) -> bool:
        """
        检查缓存项是否存在且未过期。
        """
        with self._lock:
            if self._is_expired(key):
                self.delete(key)
                return False
            return key in self._cache

    def flush(self) -> bool:
        """
        清空所有缓存。
        """
        with self._lock:
            self._cache.clear()
            self._ttl.clear()
            logger.warning("In-memory cache flushed")
        return True

    def _is_expired(self, key: str) -> bool:
        """
        检查一个键是否已过期。
        """
        with self._lock:
            if key not in self._ttl:
                return False
            return time.time() > self._ttl[key]


# 创建全局内存缓存实例 (可选, 但此处我们由RedisClient动态创建)
# memory_cache = MemoryCache()

__all__ = ["MemoryCache"]
