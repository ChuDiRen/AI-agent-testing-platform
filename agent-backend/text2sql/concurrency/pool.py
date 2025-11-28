"""
连接池管理

提供数据库连接池管理
"""

from typing import Any, Dict, Optional
from contextlib import asynccontextmanager
import asyncio


class ConnectionPoolManager:
    """连接池管理器
    
    管理多个数据库连接池
    """
    
    def __init__(
        self,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: int = 30
    ):
        """初始化连接池管理器
        
        Args:
            pool_size: 池大小
            max_overflow: 最大溢出连接数
            pool_timeout: 获取连接超时时间
        """
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        
        self._pools: Dict[int, Any] = {}
        self._lock = asyncio.Lock()
    
    async def get_pool(self, connection_id: int) -> Any:
        """获取指定连接的池
        
        Args:
            connection_id: 连接ID
            
        Returns:
            连接池
        """
        async with self._lock:
            if connection_id not in self._pools:
                from ..database.db_manager import get_database_manager
                manager = get_database_manager(connection_id)
                self._pools[connection_id] = manager
            return self._pools[connection_id]
    
    @asynccontextmanager
    async def acquire_connection(self, connection_id: int):
        """获取数据库连接
        
        Args:
            connection_id: 连接ID
            
        Yields:
            数据库连接
        """
        pool = await self.get_pool(connection_id)
        
        with pool.get_connection() as conn:
            yield conn
    
    async def close_pool(self, connection_id: int):
        """关闭指定连接池
        
        Args:
            connection_id: 连接ID
        """
        async with self._lock:
            if connection_id in self._pools:
                self._pools[connection_id].close()
                del self._pools[connection_id]
    
    async def close_all(self):
        """关闭所有连接池"""
        async with self._lock:
            for pool in self._pools.values():
                pool.close()
            self._pools.clear()
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息
        
        Returns:
            统计信息
        """
        return {
            "pool_count": len(self._pools),
            "pool_ids": list(self._pools.keys()),
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow
        }


# 全局连接池管理器
_pool_manager: Optional[ConnectionPoolManager] = None


def get_pool_manager() -> ConnectionPoolManager:
    """获取全局连接池管理器"""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = ConnectionPoolManager()
    return _pool_manager


async def get_connection(connection_id: int):
    """获取数据库连接的便捷函数"""
    manager = get_pool_manager()
    async with manager.acquire_connection(connection_id) as conn:
        yield conn
