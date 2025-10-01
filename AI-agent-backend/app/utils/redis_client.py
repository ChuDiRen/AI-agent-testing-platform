"""
Redis客户端工具
提供Redis缓存操作功能
"""

import json
import pickle
from typing import Any, Optional, List, Dict

import redis

from app.core.config import settings
from app.core.logger import get_logger
from .memory_cache import MemoryCache

logger = get_logger(__name__)


class CacheClient:
    """
    缓存客户端类
    优先使用Redis，如果Redis连接失败，则自动降级到内存缓存。
    """

    def __init__(self):
        """
        初始化缓存客户端。
        """
        self.is_redis = False
        self.client: Any = None

        if settings.REDIS_ENABLED:
            try:
                redis_config = settings.redis_url_parsed
                self.client = redis.Redis(
                    host=redis_config["host"],
                    port=redis_config["port"],
                    db=redis_config["db"],
                    password=redis_config["password"],
                    decode_responses=True,
                    socket_connect_timeout=2,  # 缩短超时时间
                    socket_timeout=2,
                    retry_on_timeout=False
                )
                self.client.ping()
                self.is_redis = True
                logger.info("Redis client initialized successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {str(e)}")
                logger.info("Falling back to in-memory cache.")
                self.client = MemoryCache()
        else:
            logger.info("Redis is disabled. Using in-memory cache.")
            self.client = MemoryCache()

    def is_available(self) -> bool:
        """
        检查缓存客户端是否可用。
        对于内存缓存，总是可用的。
        对于Redis，会尝试ping来检查连接。
        """
        if self.client is None:
            return False
        if self.is_redis:
            try:
                self.client.ping()
                return True
            except Exception:
                logger.warning("Redis connection lost.")
                return False
        return True  # MemoryCache is always available

    def _get_key(self, key: str) -> str:
        """
        获取带前缀的键名（仅用于Redis）。
        """
        return f"{settings.CACHE_PREFIX}{key}"

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值。
        """
        if not self.is_available():
            return False

        expire_time = ttl if ttl is not None else settings.CACHE_TTL

        try:
            if self.is_redis:
                cache_key = self._get_key(key)
                # 序列化值
                if isinstance(value, (dict, list, tuple)):
                    serialized_value = json.dumps(value, ensure_ascii=False)
                elif isinstance(value, (int, float, str, bool)):
                    serialized_value = str(value)
                else:
                    serialized_value = pickle.dumps(value).hex()
                    cache_key += ":pickle"

                result = self.client.setex(cache_key, expire_time, serialized_value)
                if result:
                    logger.debug(f"Redis cache set: {key} (TTL: {expire_time}s)")
                return result
            else:
                return self.client.set(key, value, expire_time)
        except Exception as e:
            logger.error(f"Error setting cache {key}: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值。
        """
        if not self.is_available():
            return default

        try:
            if self.is_redis:
                cache_key = self._get_key(key)
                value = self.client.get(cache_key)

                if value is None:
                    pickle_key = cache_key + ":pickle"
                    pickle_value = self.client.get(pickle_key)
                    if pickle_value is not None:
                        try:
                            return pickle.loads(bytes.fromhex(pickle_value))
                        except Exception:
                            logger.warning(f"Failed to deserialize pickle value for key: {key}")
                            return default
                    return default

                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                return self.client.get(key, default)
        except Exception as e:
            logger.error(f"Error getting cache {key}: {str(e)}")
            return default

    def delete(self, key: str) -> bool:
        """
        删除缓存。
        """
        if not self.is_available():
            return False

        try:
            if self.is_redis:
                cache_key = self._get_key(key)
                pickle_key = cache_key + ":pickle"
                result1 = self.client.delete(cache_key)
                result2 = self.client.delete(pickle_key)
                success = result1 > 0 or result2 > 0
                if success:
                    logger.debug(f"Redis cache deleted: {key}")
                return success
            else:
                return self.client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache {key}: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在。
        """
        if not self.is_available():
            return False

        try:
            if self.is_redis:
                cache_key = self._get_key(key)
                pickle_key = cache_key + ":pickle"
                return self.client.exists(cache_key) or self.client.exists(pickle_key)
            else:
                return self.client.exists(key)
        except Exception as e:
            logger.error(f"Error checking cache existence for {key}: {str(e)}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间。
        注意：内存缓存不支持此操作。
        """
        if not self.is_available():
            return False
        if not self.is_redis:
            logger.warning("expire() is not supported by in-memory cache.")
            return False

        try:
            cache_key = self._get_key(key)
            result = self.client.expire(cache_key, ttl)
            if result:
                logger.debug(f"Redis cache expiration set: {key} (TTL: {ttl}s)")
            return result
        except Exception as e:
            logger.error(f"Error setting cache expiration for {key}: {str(e)}")
            return False

    def ttl(self, key: str) -> int:
        """
        获取缓存剩余过期时间。
        注意：内存缓存不支持此操作。
        """
        if not self.is_available():
            return -2
        if not self.is_redis:
            # 内存缓存可以返回一个近似值或不支持
            if self.client.exists(key):
                logger.warning("ttl() is not accurately supported by in-memory cache.")
                return -1 # 表示永不过期或未知
            return -2

        try:
            cache_key = self._get_key(key)
            return self.client.ttl(cache_key)
        except Exception as e:
            logger.error(f"Error getting cache TTL for {key}: {str(e)}")
            return -2

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递增缓存值。
        注意：内存缓存不支持此操作。
        """
        if not self.is_available():
            return None
        if not self.is_redis:
            logger.warning("increment() is not supported by in-memory cache.")
            return None

        try:
            cache_key = self._get_key(key)
            return self.client.incrby(cache_key, amount)
        except Exception as e:
            logger.error(f"Error incrementing cache {key}: {str(e)}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递减缓存值。
        注意：内存缓存不支持此操作。
        """
        if not self.is_available():
            return None
        if not self.is_redis:
            logger.warning("decrement() is not supported by in-memory cache.")
            return None

        try:
            cache_key = self._get_key(key)
            return self.client.decrby(cache_key, amount)
        except Exception as e:
            logger.error(f"Error decrementing cache {key}: {str(e)}")
            return None

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量获取缓存值。
        """
        if not self.is_available():
            return {}
        # This simple loop is compatible with both backends
        return {key: self.get(key) for key in keys}

    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        批量设置缓存值。
        """
        if not self.is_available():
            return False
        # This simple loop is compatible with both backends
        results = [self.set(key, value, ttl) for key, value in mapping.items()]
        return all(results)

    def delete_many(self, keys: List[str]) -> int:
        """
        批量删除缓存。
        """
        if not self.is_available():
            return 0
        # This simple loop is compatible with both backends
        return sum(1 for key in keys if self.delete(key))

    def clear_pattern(self, pattern: str) -> int:
        """
        根据模式清除缓存。
        注意：内存缓存不支持此操作。
        """
        if not self.is_available():
            return 0
        if not self.is_redis:
            logger.warning("clear_pattern() is not supported by in-memory cache.")
            return 0

        try:
            cache_pattern = self._get_key(pattern)
            keys = self.client.keys(cache_pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cleared {deleted} Redis cache keys matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {str(e)}")
            return 0

    def flush_all(self) -> bool:
        """
        清空所有缓存。
        """
        if not self.is_available():
            return False

        try:
            if self.is_redis:
                self.client.flushdb()
                logger.warning("All Redis cache cleared")
            else:
                self.client.flush()
            return True
        except Exception as e:
            logger.error(f"Error flushing all cache: {str(e)}")
            return False



# 全局缓存客户端实例（延迟初始化）
_cache_client_instance: Optional[CacheClient] = None


def get_cache_client() -> CacheClient:
    """
    获取缓存客户端实例（单例模式，延迟初始化）
    这样可以避免在模块导入时就创建实例，防止multiprocessing问题
    """
    global _cache_client_instance
    if _cache_client_instance is None:
        _cache_client_instance = CacheClient()
    return _cache_client_instance


def reset_cache_client() -> None:
    """
    重置缓存客户端实例（主要用于测试）
    """
    global _cache_client_instance
    _cache_client_instance = None


# 导出缓存客户端
__all__ = ["CacheClient", "get_cache_client", "reset_cache_client"]
