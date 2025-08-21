"""
Redis客户端工具
提供Redis缓存操作功能
"""

import json
import pickle
from typing import Any, Optional, Union, List, Dict
from datetime import timedelta
import redis
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class RedisClient:
    """
    Redis客户端类
    提供缓存操作的封装
    """

    def __init__(self):
        """
        初始化Redis客户端
        """
        try:
            redis_config = settings.redis_url_parsed
            self.client = redis.Redis(
                host=redis_config["host"],
                port=redis_config["port"],
                db=redis_config["db"],
                password=redis_config["password"],
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # 测试连接
            self.client.ping()
            logger.info("Redis client initialized successfully")
            
        except Exception as e:
            logger.info(f"Redis connection failed (this is normal in development): {str(e)}")
            logger.info("Application will continue without Redis caching")
            self.client = None

    def is_available(self) -> bool:
        """
        检查Redis是否可用
        
        Returns:
            是否可用
        """
        if self.client is None:
            return False
        
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def _get_key(self, key: str) -> str:
        """
        获取带前缀的键名
        
        Args:
            key: 原始键名
            
        Returns:
            带前缀的键名
        """
        return f"{settings.CACHE_PREFIX}{key}"

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 键名
            value: 值
            ttl: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._get_key(key)
            
            # 序列化值
            if isinstance(value, (dict, list, tuple)):
                serialized_value = json.dumps(value, ensure_ascii=False)
            elif isinstance(value, (int, float, str, bool)):
                serialized_value = str(value)
            else:
                # 使用pickle序列化复杂对象
                serialized_value = pickle.dumps(value).hex()
                cache_key += ":pickle"
            
            # 设置过期时间
            expire_time = ttl or settings.CACHE_TTL
            
            result = self.client.setex(cache_key, expire_time, serialized_value)
            
            if result:
                logger.debug(f"Cache set: {key} (TTL: {expire_time}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error setting cache {key}: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 键名
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        if not self.is_available():
            return default
        
        try:
            cache_key = self._get_key(key)
            
            # 尝试获取普通值
            value = self.client.get(cache_key)
            
            if value is None:
                # 尝试获取pickle序列化的值
                pickle_key = cache_key + ":pickle"
                pickle_value = self.client.get(pickle_key)
                
                if pickle_value is not None:
                    try:
                        return pickle.loads(bytes.fromhex(pickle_value))
                    except Exception:
                        logger.warning(f"Failed to deserialize pickle value for key: {key}")
                        return default
                
                return default
            
            # 尝试JSON反序列化
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # 返回原始字符串值
                return value
                
        except Exception as e:
            logger.error(f"Error getting cache {key}: {str(e)}")
            return default

    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 键名
            
        Returns:
            是否删除成功
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._get_key(key)
            pickle_key = cache_key + ":pickle"
            
            # 删除两种可能的键
            result1 = self.client.delete(cache_key)
            result2 = self.client.delete(pickle_key)
            
            success = result1 > 0 or result2 > 0
            
            if success:
                logger.debug(f"Cache deleted: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting cache {key}: {str(e)}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查缓存是否存在
        
        Args:
            key: 键名
            
        Returns:
            是否存在
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._get_key(key)
            pickle_key = cache_key + ":pickle"
            
            return self.client.exists(cache_key) or self.client.exists(pickle_key)
            
        except Exception as e:
            logger.error(f"Error checking cache existence {key}: {str(e)}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间
        
        Args:
            key: 键名
            ttl: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._get_key(key)
            result = self.client.expire(cache_key, ttl)
            
            if result:
                logger.debug(f"Cache expiration set: {key} (TTL: {ttl}s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error setting cache expiration {key}: {str(e)}")
            return False

    def ttl(self, key: str) -> int:
        """
        获取缓存剩余过期时间
        
        Args:
            key: 键名
            
        Returns:
            剩余时间（秒），-1表示永不过期，-2表示不存在
        """
        if not self.is_available():
            return -2
        
        try:
            cache_key = self._get_key(key)
            return self.client.ttl(cache_key)
            
        except Exception as e:
            logger.error(f"Error getting cache TTL {key}: {str(e)}")
            return -2

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递增缓存值
        
        Args:
            key: 键名
            amount: 递增量
            
        Returns:
            递增后的值或None
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._get_key(key)
            result = self.client.incrby(cache_key, amount)
            
            logger.debug(f"Cache incremented: {key} by {amount} = {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error incrementing cache {key}: {str(e)}")
            return None

    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递减缓存值
        
        Args:
            key: 键名
            amount: 递减量
            
        Returns:
            递减后的值或None
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._get_key(key)
            result = self.client.decrby(cache_key, amount)
            
            logger.debug(f"Cache decremented: {key} by {amount} = {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error decrementing cache {key}: {str(e)}")
            return None

    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量获取缓存值
        
        Args:
            keys: 键名列表
            
        Returns:
            键值对字典
        """
        if not self.is_available():
            return {}
        
        result = {}
        for key in keys:
            result[key] = self.get(key)
        
        return result

    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        批量设置缓存值
        
        Args:
            mapping: 键值对字典
            ttl: 过期时间（秒）
            
        Returns:
            是否全部设置成功
        """
        if not self.is_available():
            return False
        
        success_count = 0
        for key, value in mapping.items():
            if self.set(key, value, ttl):
                success_count += 1
        
        return success_count == len(mapping)

    def delete_many(self, keys: List[str]) -> int:
        """
        批量删除缓存
        
        Args:
            keys: 键名列表
            
        Returns:
            删除成功的数量
        """
        if not self.is_available():
            return 0
        
        success_count = 0
        for key in keys:
            if self.delete(key):
                success_count += 1
        
        return success_count

    def clear_pattern(self, pattern: str) -> int:
        """
        根据模式清除缓存
        
        Args:
            pattern: 键名模式（支持通配符）
            
        Returns:
            删除的键数量
        """
        if not self.is_available():
            return 0
        
        try:
            cache_pattern = self._get_key(pattern)
            keys = self.client.keys(cache_pattern)
            
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cleared {deleted} cache keys matching pattern: {pattern}")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {str(e)}")
            return 0

    def flush_all(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            是否成功
        """
        if not self.is_available():
            return False
        
        try:
            self.client.flushdb()
            logger.warning("All cache cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error flushing all cache: {str(e)}")
            return False


# 创建全局Redis客户端实例
redis_client = RedisClient()

# 导出Redis客户端
__all__ = ["RedisClient", "redis_client"]
