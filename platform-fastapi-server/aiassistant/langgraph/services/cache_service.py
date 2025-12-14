"""
CacheService - 缓存服务

提供内存缓存，避免重复LLM调用
"""
import hashlib
import logging
from typing import Optional, Any, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CacheService:
    """缓存服务类"""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(seconds=ttl_seconds)

    def _generate_key(self, *args) -> str:
        """生成缓存键"""
        content = "|".join(str(arg) for arg in args)
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self._cache:
            entry = self._cache[key]
            if datetime.now() - entry["created_at"] < self._ttl:
                logger.debug(f"Cache hit: {key[:8]}...")
                return entry["value"]
            else:
                del self._cache[key]  # 过期删除
        return None

    def set(self, key: str, value: Any) -> None:
        """设置缓存"""
        self._cache[key] = {"value": value, "created_at": datetime.now()}
        logger.debug(f"Cache set: {key[:8]}...")

    def get_or_set(self, key: str, factory) -> Any:
        """获取或设置缓存"""
        value = self.get(key)
        if value is None:
            value = factory()
            self.set(key, value)
        return value

    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()

    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)
