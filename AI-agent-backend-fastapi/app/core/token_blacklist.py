"""Token 黑名单管理 - 使用 Redis"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import redis
from app.core.config import settings


class TokenBlacklist:
    """Token 黑名单服务"""
    
    def __init__(self):
        """初始化 Redis 连接"""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if hasattr(settings, 'REDIS_PASSWORD') and settings.REDIS_PASSWORD else None,
                decode_responses=True
            )
            # 测试连接
            self.redis_client.ping()
        except Exception as e:
            print(f"⚠️  Redis 连接失败,Token黑名单功能将不可用: {e}")
            self.redis_client = None
    
    def add_to_blacklist(self, token: str, expires_in: int = None) -> bool:
        """
        将 token 添加到黑名单
        
        Args:
            token: JWT token
            expires_in: 过期时间(秒),默认为 ACCESS_TOKEN_EXPIRE_MINUTES
        
        Returns:
            是否添加成功
        """
        if not self.redis_client:
            return False
        
        try:
            # 使用 token 的哈希值作为 key,节省空间
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # 如果没有指定过期时间,使用默认的 token 过期时间
            if expires_in is None:
                expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            
            # 添加到黑名单,设置过期时间
            self.redis_client.setex(
                f"blacklist:{token_hash}",
                expires_in,
                datetime.now(timezone.utc).isoformat()
            )
            return True
        except Exception as e:
            print(f"❌ 添加 token 到黑名单失败: {e}")
            return False
    
    def is_blacklisted(self, token: str) -> bool:
        """
        检查 token 是否在黑名单中
        
        Args:
            token: JWT token
        
        Returns:
            是否在黑名单中
        """
        if not self.redis_client:
            return False
        
        try:
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            return self.redis_client.exists(f"blacklist:{token_hash}") > 0
        except Exception as e:
            print(f"❌ 检查 token 黑名单失败: {e}")
            return False
    
    def remove_from_blacklist(self, token: str) -> bool:
        """
        从黑名单中移除 token
        
        Args:
            token: JWT token
        
        Returns:
            是否移除成功
        """
        if not self.redis_client:
            return False
        
        try:
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            self.redis_client.delete(f"blacklist:{token_hash}")
            return True
        except Exception as e:
            print(f"❌ 从黑名单移除 token 失败: {e}")
            return False
    
    def clear_all(self) -> bool:
        """清空所有黑名单 token"""
        if not self.redis_client:
            return False
        
        try:
            # 删除所有匹配的 key
            for key in self.redis_client.scan_iter("blacklist:*"):
                self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"❌ 清空黑名单失败: {e}")
            return False


# 全局实例
token_blacklist = TokenBlacklist()



