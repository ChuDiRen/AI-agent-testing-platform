from datetime import datetime, timedelta
from typing import Optional, Dict

from config.dev_settings import settings
from jose import jwt, JWTError

from .logger import get_logger

logger = get_logger(__name__)

class JwtUtils:
    
    @staticmethod
    def create_token(username: str, password: str) -> str: # 创建JWT token
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "username": username,
            "password": password,
            "exp": expire
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict]: # 验证JWT token
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            logger.warning(f"Token验证失败: {e}")
            return None
