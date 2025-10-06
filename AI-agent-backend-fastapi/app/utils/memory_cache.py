# Copyright (c) 2025 左岚. All rights reserved.
"""内存缓存模块 - 提供线程安全的TTL缓存实现"""
import time
from threading import RLock
from typing import Any, Optional, Dict, List


class MemoryCache:
    """线程安全的内存缓存实现，支持TTL过期机制"""

    def __init__(self):
        self._cache: Dict[str, Any] = {}  # 缓存数据
        self._ttl: Dict[str, float] = {}  # 过期时间戳
        self._lock = RLock()  # 线程锁

    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值，过期则返回默认值"""
        with self._lock:
            if self._is_expired(key):
                self.delete(key)
                return default
            return self._cache.get(key, default)

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存值，ttl单位为秒"""
        with self._lock:
            self._cache[key] = value
            self._ttl[key] = time.time() + ttl
            return True

    def setex(self, key: str, ttl: int, value: Any) -> bool:
        """Redis兼容接口：设置带过期时间的值"""
        return self.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """删除缓存项"""
        with self._lock:
            self._cache.pop(key, None)
            self._ttl.pop(key, None)
            return True

    def exists(self, key: str) -> int:
        """检查键是否存在（Redis兼容接口，返回1或0）"""
        with self._lock:
            if self._is_expired(key):
                self.delete(key)
                return 0
            return 1 if key in self._cache else 0

    def keys(self, pattern: str = "*") -> List[str]:
        """获取所有匹配的键（简化版，仅支持*通配符）"""
        with self._lock:
            self._cleanup_expired()
            if pattern == "*":
                return list(self._cache.keys())
            # 简单的通配符匹配
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                return [k for k in self._cache.keys() if k.startswith(prefix)]
            return [k for k in self._cache.keys() if k == pattern]

    def scan_iter(self, match: str = "*") -> List[str]:
        """扫描迭代器（Redis兼容接口）"""
        return self.keys(match)

    def flushdb(self) -> bool:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._ttl.clear()
            return True

    def ping(self) -> bool:
        """健康检查（Redis兼容接口）"""
        return True

    def _is_expired(self, key: str) -> bool:
        """检查键是否过期"""
        if key not in self._ttl:
            return False
        return time.time() > self._ttl[key]

    def _cleanup_expired(self) -> None:
        """清理过期的键"""
        expired_keys = [k for k in self._ttl.keys() if self._is_expired(k)]
        for key in expired_keys:
            self.delete(key)

