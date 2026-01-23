"""
统一缓存管理器
支持Redis和内存缓存的自动降级
优先使用Redis，连接失败时降级到内存缓存
"""
import json
import threading
from typing import Any, Optional, Dict, Callable
from app.core.config import settings
from app.core.logger import logger

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis库未安装，将直接使用内存缓存")

from cachetools import TTLCache


class UnifiedCacheManager:
    """统一缓存管理器（单例模式）"""
    _instance_lock = threading.Lock()
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例实现"""
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        
        self.redis_client = None
        self.memory_cache = None
        self.use_redis = False
        self._initialized_cache = False
    
    async def initialize(self):
        """初始化缓存管理器，测试Redis连接，失败则使用内存缓存"""
        if self._initialized_cache:
            return
        
        self._initialized_cache = True
        logger.info("🔄 正在初始化缓存管理器...")
        
        # 尝试连接Redis
        if REDIS_AVAILABLE and settings.REDIS_FALLBACK_ENABLED:
            try:
                self.redis_client = await aioredis.from_url(
                    f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
                
                # 测试连接
                await self.redis_client.ping()
                self.use_redis = True
                logger.info("✅ 成功使用Redis缓存")
                return
            except Exception as e:
                logger.warning(f"⚠️ Redis连接失败: {e}，自动降级到内存缓存")
                if self.redis_client:
                    await self.redis_client.close()
                self.redis_client = None
        
        # 使用内存缓存
        self.memory_cache = TTLCache(
            maxsize=settings.MEMORY_CACHE_MAXSIZE,
            ttl=settings.MEMORY_CACHE_TTL
        )
        self.use_redis = False
        logger.info(f"✅ 使用内存缓存: maxsize={settings.MEMORY_CACHE_MAXSIZE}, ttl={settings.MEMORY_CACHE_TTL}秒")
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值，当键不存在时返回
            
        Returns:
            缓存值或默认值
        """
        try:
            if self.use_redis and self.redis_client:
                value = await self.redis_client.get(key)
                if value is not None:
                    # 尝试反序列化JSON
                    try:
                        return json.loads(value)
                    except:
                        return value
                return default
            else:
                return self.memory_cache.get(key, default)
        except Exception as e:
            logger.error(f"获取缓存失败: key={key}, error={e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），不设置则使用默认TTL
            
        Returns:
            是否设置成功
        """
        try:
            if self.use_redis and self.redis_client:
                # 序列化为JSON
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = str(value)
                
                if ttl is not None:
                    await self.redis_client.setex(key, ttl, value_str)
                else:
                    await self.redis_client.set(key, value_str)
                return True
            else:
                # 内存缓存
                if ttl is not None:
                    # 临时缓存
                    temp_cache = TTLCache(maxsize=len(self.memory_cache) + 1, ttl=ttl)
                    temp_cache[key] = value
                    self.memory_cache[key] = value
                else:
                    self.memory_cache[key] = value
                return True
        except Exception as e:
            logger.error(f"设置缓存失败: key={key}, error={e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        try:
            if self.use_redis and self.redis_client:
                result = await self.redis_client.delete(key)
                return result > 0
            else:
                if key in self.memory_cache:
                    del self.memory_cache[key]
                    return True
                return False
        except Exception as e:
            logger.error(f"删除缓存失败: key={key}, error={e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        try:
            if self.use_redis and self.redis_client:
                return await self.redis_client.exists(key) > 0
            else:
                return key in self.memory_cache
        except Exception as e:
            logger.error(f"检查缓存存在失败: key={key}, error={e}")
            return False
    
    async def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            是否清空成功
        """
        try:
            if self.use_redis and self.redis_client:
                await self.redis_client.flushdb()
            else:
                self.memory_cache.clear()
            logger.info("✅ 缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: error={e}")
            return False
    
    async def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
        """
        获取缓存，如果不存在则调用函数生成缓存
        
        Args:
            key: 缓存键
            func: 缓存生成函数
            ttl: 过期时间（秒）
            
        Returns:
            缓存值
        """
        try:
            value = await self.get(key)
            if value is not None:
                return value
            
            # 调用函数生成值
            result = func()
            await self.set(key, result, ttl)
            return result
        except Exception as e:
            logger.error(f"获取或设置缓存失败: key={key}, error={e}")
            try:
                return func()
            except:
                return None
    
    async def get_json(self, key: str, default: Any = None) -> Any:
        """
        获取JSON格式的缓存值并反序列化
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            反序列化的对象或默认值
        """
        try:
            value = await self.get(key)
            if value is not None:
                return value
            return default
        except Exception as e:
            logger.error(f"获取JSON缓存失败: key={key}, error={e}")
            return default
    
    async def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        将对象序列化为JSON后存储到缓存
        
        Args:
            key: 缓存键
            value: 要缓存的值
            ttl: 过期时间（秒）
            
        Returns:
            是否设置成功
        """
        try:
            return await self.set(key, value, ttl)
        except Exception as e:
            logger.error(f"设置JSON缓存失败: key={key}, error={e}")
            return False
    
    async def close(self):
        """关闭缓存连接"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error(f"关闭Redis连接失败: {e}")
    
    def get_backend_type(self) -> str:
        """
        获取当前使用的缓存后端类型
        
        Returns:
            "redis" 或 "memory"
        """
        return "redis" if self.use_redis else "memory"


# 全局实例
cache_manager = UnifiedCacheManager()
