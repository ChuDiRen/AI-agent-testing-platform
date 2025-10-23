"""
异步 HTTP 客户端管理器
使用 asyncio.run() 简化实现,每次创建新事件循环但复用 AsyncClient 连接池
"""
import httpx
import asyncio
import logging
from typing import Optional
import time

# 配置日志
logger = logging.getLogger(__name__)

# 配置 httpx 日志级别为 WARNING,减少调试信息
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class AsyncClientManager:
    """异步客户端管理器 - 单例模式,复用连接池"""

    _client: Optional[httpx.AsyncClient] = None  # 单例客户端实例
    _request_count: int = 0  # 请求计数器

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
        if cls._client is None or cls._client.is_closed:
            # 默认配置
            default_config = {
                'timeout': kwargs.get('timeout', 30.0),
                'follow_redirects': kwargs.get('follow_redirects', True),
                'verify': kwargs.get('verify', True),
            }
            cls._client = httpx.AsyncClient(**default_config)
            logger.info("✅ AsyncClient 已创建 | 连接池已初始化")
        return cls._client

    @classmethod
    async def close(cls):
        """关闭异步客户端,释放资源"""
        if cls._client is not None and not cls._client.is_closed:
            await cls._client.aclose()
            logger.info(f"🔒 AsyncClient 已关闭 | 总请求数: {cls._request_count}")
            cls._client = None
            cls._request_count = 0


def run_async(coro):
    """
    在同步上下文中运行异步协程
    使用 asyncio.run() 创建新事件循环,但复用 AsyncClient 连接池

    参数:
        coro: 异步协程对象

    返回:
        协程的返回值
    """
    import time
    start_time = time.time()

    try:
        # 使用 asyncio.run() 运行协程
        # 虽然每次创建新事件循环,但 AsyncClient 单例会复用连接池
        result = asyncio.run(coro)

        # 记录请求计数
        AsyncClientManager._request_count += 1

        # 记录性能日志
        elapsed = (time.time() - start_time) * 1000  # 转换为毫秒
        logger.info(f"⚡ 请求完成 | 耗时: {elapsed:.2f}ms | 总请求数: {AsyncClientManager._request_count}")

        return result
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error(f"❌ 请求失败 | 耗时: {elapsed:.2f}ms | 错误: {str(e)}")
        raise

