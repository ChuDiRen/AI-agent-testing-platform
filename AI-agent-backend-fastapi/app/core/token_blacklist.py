# Copyright (c) 2025 左岚. All rights reserved.
"""Token黑名单管理 - 使用统一缓存客户端（支持Redis和内存缓存）"""
from datetime import datetime, timezone
from typing import Optional
import hashlib
from app.core.config import settings
from app.utils.cache_client import get_cache_client


class TokenBlacklist:
    """Token黑名单服务，基于统一缓存客户端"""

    def __init__(self):
        """初始化缓存客户端"""
        self.cache = get_cache_client()  # 使用统一缓存客户端

    def add_to_blacklist(self, token: str, expires_in: int = None) -> bool:
        """将token添加到黑名单"""
        if not token:
            return False

        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()  # 使用哈希值节省空间

            if expires_in is None:  # 默认使用token过期时间
                expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

            key = f"blacklist:{token_hash}"
            value = datetime.now(timezone.utc).isoformat()
            return self.cache.set(key, value, expires_in)
        except Exception as e:
            print(f"❌ 添加token到黑名单失败: {e}")
            return False

    def is_blacklisted(self, token: str) -> bool:
        """检查token是否在黑名单中"""
        if not token:
            return False

        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            key = f"blacklist:{token_hash}"
            return self.cache.exists(key)
        except Exception as e:
            print(f"❌ 检查token黑名单失败: {e}")
            return False

    def remove_from_blacklist(self, token: str) -> bool:
        """从黑名单中移除token"""
        if not token:
            return False

        try:
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            key = f"blacklist:{token_hash}"
            return self.cache.delete(key)
        except Exception as e:
            print(f"❌ 从黑名单移除token失败: {e}")
            return False

    def clear_all(self) -> bool:
        """清空所有黑名单token"""
        try:
            keys = self.cache.scan_iter("blacklist:*")  # 扫描所有黑名单键
            for key in keys:
                self.cache.delete(key)
            return True
        except Exception as e:
            print(f"❌ 清空黑名单失败: {e}")
            return False


# 全局实例
token_blacklist = TokenBlacklist()



