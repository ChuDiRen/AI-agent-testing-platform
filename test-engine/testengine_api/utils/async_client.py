"""异步 HTTP 客户端管理器 - 基于 httpx 的连接池复用实现"""
import httpx
import asyncio
import logging
from typing import Optional
import os
import yaml

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING) # 减少 httpx 库日志输出
logging.getLogger("httpcore").setLevel(logging.WARNING) # 减少 httpcore 库日志输出


class AsyncClientManager:
    """异步客户端管理器 - 单例模式,真正复用连接池"""

    _client: Optional[httpx.AsyncClient] = None # 单例客户端实例
    _lock: Optional[asyncio.Lock] = None # 异步锁,保护单例创建
    _config_loaded = False # 配置加载标志
    _pool_config = {} # 连接池配置

    @classmethod
    def _load_config(cls):
        """加载连接池配置"""
        if cls._config_loaded:
            return

        config_path = os.path.join(os.path.dirname(__file__), 'httpx_config.yaml')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    cls._pool_config = yaml.safe_load(f) or {}
                logger.debug(f"连接池配置已加载: {config_path}")
            except Exception as e:
                logger.warning(f"加载连接池配置失败,使用默认配置: {e}")
                cls._pool_config = {}
        cls._config_loaded = True

    @classmethod
    async def get_client(cls, **kwargs) -> httpx.AsyncClient:
        """获取异步客户端实例(每次创建新实例,但复用配置)"""
        cls._load_config() # 加载配置(只加载一次)

        # 连接池限制配置
        pool_config = cls._pool_config.get('pool', {})
        limits = httpx.Limits(
            max_connections=pool_config.get('max_connections', 100), # 最大连接数
            max_keepalive_connections=pool_config.get('max_keepalive_connections', 20), # keep-alive 连接数
            keepalive_expiry=pool_config.get('keepalive_expiry', 30.0) # keep-alive 过期时间(秒)
        )

        # 超时配置
        timeout_config = cls._pool_config.get('timeout', {})
        timeout = httpx.Timeout(
            connect=timeout_config.get('connect', 10.0), # 连接超时
            read=timeout_config.get('read', 30.0), # 读取超时
            write=timeout_config.get('write', 10.0), # 写入超时
            pool=timeout_config.get('pool', 10.0) # 连接池超时
        )

        # 重试配置
        retry_config = cls._pool_config.get('retry', {})
        transport = httpx.AsyncHTTPTransport(
            retries=retry_config.get('max_retries', 3) # 最大重试次数
        )

        # 其他配置
        other_config = cls._pool_config.get('other', {})

        # 每次创建新客户端,但底层连接池会被httpx自动复用
        client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            transport=transport,
            follow_redirects=kwargs.get('follow_redirects', other_config.get('follow_redirects', True)),
            verify=kwargs.get('verify', other_config.get('verify', True)),
            http2=other_config.get('http2', False) # HTTP/2 支持
        )
        logger.debug("AsyncClient 已创建")
        return client

    @classmethod
    async def close(cls):
        """关闭异步客户端,释放资源"""
        if cls._client is not None and not cls._client.is_closed:
            await cls._client.aclose()
            logger.info("AsyncClient 已关闭,连接池已释放")
            cls._client = None

