from datetime import datetime, timedelta
from typing import Optional, Dict

from config.dev_settings import settings
from jose import jwt, JWTError, ExpiredSignatureError

from .logger import get_logger

logger = get_logger(__name__)

class JwtUtils:
    
    @staticmethod
    def create_token(user_id: int, username: str) -> str: # 创建JWT token，只存储user_id和username
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),  # 标准JWT字段，存储用户ID
            "username": username,
            "exp": expire
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token
    
    @staticmethod
    def get_user_id_from_token(token: str) -> Optional[int]: # 从token中获取用户ID
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            return int(user_id) if user_id else None
        except (JWTError, ValueError) as e:
            logger.warning(f"从Token获取用户ID失败: {e}")
            return None
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]: # 验证JWT token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Token验证失败: {e}")
            return None
    
    @staticmethod
    def refresh_token(token: str) -> Optional[str]:
        """
        刷新 token：即使 token 已过期，只要签名有效就可以刷新
        返回新的 token 或 None（如果签名无效）
        """
        try:
            # 允许过期的 token 解码（不验证过期时间）
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}
            )
            user_id = payload.get("sub")
            username = payload.get("username")
            if user_id and username:
                # 生成新的 token
                return JwtUtils.create_token(int(user_id), username)
            return None
        except JWTError as e:
            logger.warning(f"Token刷新失败: {e}")
            return None
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """检查 token 是否过期"""
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return False
        except ExpiredSignatureError:
            return True
        except JWTError:
            return True
