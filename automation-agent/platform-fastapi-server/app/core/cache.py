"""
内存缓存管理器
使用 TTL Cache 提供带过期时间的内存缓存功能
支持单例模式，提供便捷的缓存操作接口
"""
import json
import threading
from typing import Any, Optional, Dict, List, Callable
from cachetools import TTLCache
from app.core.logger import logger


class MemoryCacheManager:
    """内存缓存管理器（单例模式）"""
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
    
    def __init__(self, maxsize: int = 10000, ttl: int = 3600):
        """
        初始化缓存管理器
        
        Args:
            maxsize: 缓存最大条目数，默认10000
            ttl: 缓存过期时间（秒），默认3600秒（1小时）
        """
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
        
        # 主缓存
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
        
        # 命名空间缓存（支持不同业务模块使用独立缓存空间）
        self.namespaces: Dict[str, TTLCache] = {}
        
        logger.info(f"✅ 内存缓存管理器初始化成功: maxsize={maxsize}, ttl={ttl}秒")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取缓存值
        
        Args:
            key: 缓存键
            default: 默认值，当键不存在时返回
            
        Returns:
            缓存值或默认值
        """
        try:
            return self.cache.get(key, default)
        except Exception as e:
            logger.error(f"获取缓存失败: key={key}, error={e}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
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
            if ttl is not None:
                # 如果指定了TTL，使用临时缓存
                temp_cache = TTLCache(maxsize=len(self.cache) + 1, ttl=ttl)
                temp_cache[key] = value
                # 将临时缓存的值复制到主缓存
                self.cache[key] = value
            else:
                self.cache[key] = value
            return True
        except Exception as e:
            logger.error(f"设置缓存失败: key={key}, error={e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        删除缓存
        
        Args:
            key: 缓存键
            
        Returns:
            是否删除成功
        """
        try:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
        except Exception as e:
            logger.error(f"删除缓存失败: key={key}, error={e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
            
        Returns:
            是否存在
        """
        try:
            return key in self.cache
        except Exception as e:
            logger.error(f"检查缓存存在失败: key={key}, error={e}")
            return False
    
    def clear(self) -> bool:
        """
        清空所有缓存
        
        Returns:
            是否清空成功
        """
        try:
            self.cache.clear()
            for cache in self.namespaces.values():
                cache.clear()
            logger.info("✅ 缓存已清空")
            return True
        except Exception as e:
            logger.error(f"清空缓存失败: error={e}")
            return False
    
    def get_or_set(self, key: str, func: Callable, ttl: Optional[int] = None) -> Any:
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
            if key in self.cache:
                return self.cache[key]
            
            # 调用函数生成值
            value = func()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"获取或设置缓存失败: key={key}, error={e}")
            # 缓存失败时直接调用函数
            try:
                return func()
            except:
                return None
    
    def get_json(self, key: str, default: Any = None) -> Any:
        """
        获取JSON格式的缓存值并反序列化
        
        Args:
            key: 缓存键
            default: 默认值
            
        Returns:
            反序列化的对象或默认值
        """
        try:
            value = self.get(key)
            if value is not None and isinstance(value, str):
                return json.loads(value)
            return default
        except Exception as e:
            logger.error(f"获取JSON缓存失败: key={key}, error={e}")
            return default
    
    def set_json(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
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
            json_value = json.dumps(value, ensure_ascii=False)
            return self.set(key, json_value, ttl)
        except Exception as e:
            logger.error(f"设置JSON缓存失败: key={key}, error={e}")
            return False
    
    # ========== 命名空间支持 ==========
    
    def get_namespace(self, namespace: str, maxsize: int = 1000, ttl: int = 3600) -> TTLCache:
        """
        获取或创建命名空间缓存
        
        Args:
            namespace: 命名空间名称
            maxsize: 缓存最大条目数
            ttl: 缓存过期时间（秒）
            
        Returns:
            命名空间缓存对象
        """
        if namespace not in self.namespaces:
            self.namespaces[namespace] = TTLCache(maxsize=maxsize, ttl=ttl)
            logger.info(f"✅ 创建命名空间缓存: {namespace}")
        return self.namespaces[namespace]
    
    def get_from_namespace(self, namespace: str, key: str, default: Any = None) -> Any:
        """
        从命名空间获取缓存
        
        Args:
            namespace: 命名空间名称
            key: 缓存键
            default: 默认值
            
        Returns:
            缓存值或默认值
        """
        try:
            if namespace in self.namespaces:
                cache = self.namespaces[namespace]
                return cache.get(key, default)
            return default
        except Exception as e:
            logger.error(f"从命名空间获取缓存失败: namespace={namespace}, key={key}, error={e}")
            return default
    
    def set_to_namespace(self, namespace: str, key: str, value: Any, maxsize: int = 1000, ttl: int = 3600) -> bool:
        """
        设置命名空间缓存
        
        Args:
            namespace: 命名空间名称
            key: 缓存键
            value: 缓存值
            maxsize: 缓存最大条目数
            ttl: 缓存过期时间（秒）
            
        Returns:
            是否设置成功
        """
        try:
            cache = self.get_namespace(namespace, maxsize, ttl)
            cache[key] = value
            return True
        except Exception as e:
            logger.error(f"设置命名空间缓存失败: namespace={namespace}, key={key}, error={e}")
            return False
    
    # ========== 统计信息 ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        Returns:
            统计信息字典
        """
        try:
            stats = {
                "main_cache": {
                    "size": len(self.cache),
                    "maxsize": self.cache.maxsize,
                    "ttl": self.cache.ttl
                },
                "namespaces": {}
            }
            
            for ns_name, ns_cache in self.namespaces.items():
                stats["namespaces"][ns_name] = {
                    "size": len(ns_cache),
                    "maxsize": ns_cache.maxsize,
                    "ttl": ns_cache.ttl
                }
            
            return stats
        except Exception as e:
            logger.error(f"获取缓存统计信息失败: error={e}")
            return {}


# 全局实例
cache_manager = MemoryCacheManager()
