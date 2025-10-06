# Copyright (c) 2025 左岚. All rights reserved.
"""统一缓存客户端 - 支持Redis和内存缓存自动降级"""
import json
import pickle
from typing import Any, Optional, List
import redis
from app.core.config import settings
from app.utils.memory_cache import MemoryCache


class CacheClient:
    """统一缓存客户端，优先使用Redis，失败时自动降级到内存缓存"""

    def __init__(self):
        self.is_redis = False  # 是否使用Redis
        self.client: Any = None  # 缓存客户端实例
        self._init_client()

    def _init_client(self) -> None:
        """初始化缓存客户端"""
        try:
            # 尝试连接Redis
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=False
            )
            self.client.ping()
            self.is_redis = True
            print("✅ Redis连接成功，使用Redis缓存")
        except Exception as e:
            print(f"⚠️  Redis连接失败: {e}")
            print("📦 自动降级到内存缓存")
            self.client = MemoryCache()
            self.is_redis = False

    def is_available(self) -> bool:
        """检查缓存是否可用"""
        if self.client is None:
            return False
        try:
            self.client.ping()
            return True
        except Exception:
            return False

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """设置缓存值"""
        if not self.is_available():
            return False
        try:
            if self.is_redis:
                # Redis序列化处理
                if isinstance(value, (dict, list, tuple)):
                    serialized_value = json.dumps(value, ensure_ascii=False)
                elif isinstance(value, (int, float, str, bool)):
                    serialized_value = str(value)
                else:
                    serialized_value = pickle.dumps(value).hex()
                    key += ":pickle"
                return bool(self.client.setex(key, ttl, serialized_value))
            else:
                # 内存缓存直接存储
                return self.client.set(key, value, ttl)
        except Exception as e:
            print(f"❌ 设置缓存失败 {key}: {e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取缓存值"""
        if not self.is_available():
            return default
        try:
            if self.is_redis:
                value = self.client.get(key)
                if value is None:
                    # 尝试获取pickle序列化的值
                    pickle_key = key + ":pickle"
                    pickle_value = self.client.get(pickle_key)
                    if pickle_value is not None:
                        try:
                            return pickle.loads(bytes.fromhex(pickle_value))
                        except Exception:
                            return default
                    return default
                # 尝试JSON反序列化
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            else:
                return self.client.get(key, default)
        except Exception as e:
            print(f"❌ 获取缓存失败 {key}: {e}")
            return default

    def delete(self, key: str) -> bool:
        """删除缓存"""
        if not self.is_available():
            return False
        try:
            self.client.delete(key)
            # 同时删除可能的pickle版本
            if self.is_redis:
                self.client.delete(key + ":pickle")
            return True
        except Exception as e:
            print(f"❌ 删除缓存失败 {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.is_available():
            return False
        try:
            result = self.client.exists(key)
            return result > 0 if isinstance(result, int) else bool(result)
        except Exception as e:
            print(f"❌ 检查缓存失败 {key}: {e}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配的键列表"""
        if not self.is_available():
            return []
        try:
            if self.is_redis:
                return self.client.keys(pattern)
            else:
                return self.client.keys(pattern)
        except Exception as e:
            print(f"❌ 获取键列表失败: {e}")
            return []

    def scan_iter(self, match: str = "*") -> List[str]:
        """扫描匹配的键（迭代器）"""
        if not self.is_available():
            return []
        try:
            if self.is_redis:
                return list(self.client.scan_iter(match))
            else:
                return self.client.scan_iter(match)
        except Exception as e:
            print(f"❌ 扫描键失败: {e}")
            return []

    def flushdb(self) -> bool:
        """清空所有缓存"""
        if not self.is_available():
            return False
        try:
            self.client.flushdb()
            print("⚠️  所有缓存已清空")
            return True
        except Exception as e:
            print(f"❌ 清空缓存失败: {e}")
            return False


# 全局缓存客户端实例（单例模式）
_cache_client_instance: Optional[CacheClient] = None


def get_cache_client() -> CacheClient:
    """获取缓存客户端实例（单例模式）"""
    global _cache_client_instance
    if _cache_client_instance is None:
        _cache_client_instance = CacheClient()
    return _cache_client_instance


def reset_cache_client() -> None:
    """重置缓存客户端实例（用于测试）"""
    global _cache_client_instance
    _cache_client_instance = None

