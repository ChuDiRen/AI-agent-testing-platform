"""
异步 HTTP 客户端管理器
使用单例模式管理 httpx.AsyncClient,实现连接池复用
"""
import httpx
import asyncio
from typing import Optional


class AsyncClientManager:
    """异步客户端管理器 - 单例模式"""
    
    _client: Optional[httpx.AsyncClient] = None  # 单例客户端实例
    _lock = asyncio.Lock()  # 异步锁,确保线程安全
    
    @classmethod
    async def get_client(cls, **kwargs) -> httpx.AsyncClient:
        """
        获取异步客户端实例(单例)
        
        参数:
            **kwargs: httpx.AsyncClient 的配置参数
                - timeout: 超时配置,默认 30 秒
                - follow_redirects: 是否跟随重定向,默认 True
                - verify: SSL 验证,默认 True
        
        返回:
            httpx.AsyncClient: 异步客户端实例
        """
        if cls._client is None:
            async with cls._lock:
                if cls._client is None:  # 双重检查锁定
                    # 默认配置
                    default_config = {
                        'timeout': kwargs.get('timeout', 30.0),
                        'follow_redirects': kwargs.get('follow_redirects', True),
                        'verify': kwargs.get('verify', True),
                    }
                    cls._client = httpx.AsyncClient(**default_config)
        return cls._client
    
    @classmethod
    async def close(cls):
        """关闭异步客户端,释放资源"""
        if cls._client is not None:
            await cls._client.aclose()
            cls._client = None
    
    @classmethod
    def close_sync(cls):
        """同步方式关闭客户端(用于清理)"""
        if cls._client is not None:
            asyncio.run(cls.close())


def run_async(coro):
    """
    在同步上下文中运行异步协程

    参数:
        coro: 异步协程对象

    返回:
        协程的返回值
    """
    # 直接使用 asyncio.run() 创建新的事件循环
    # 这是 Python 3.7+ 推荐的方式
    return asyncio.run(coro)

