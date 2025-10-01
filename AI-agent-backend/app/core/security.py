"""
安全相关功能
包含密码加密、JWT令牌处理等
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# 密码加密上下文
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS  # 使用配置中的rounds值
)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        加密后的密码哈希
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 加密后的密码哈希
        
    Returns:
        密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT访问令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"Created access token for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}")
        raise


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT刷新令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        logger.debug(f"Created refresh token for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create refresh token: {str(e)}")
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    验证令牌 - 增强版本，包含更详细的错误处理
    
    Args:
        token: JWT令牌
        token_type: 令牌类型 (access/refresh)
        
    Returns:
        解码后的数据或None
    """
    if not token or not isinstance(token, str):
        logger.warning("Invalid token format: token is empty or not a string")
        return None
    
    # 移除Bearer前缀（如果存在）
    if token.startswith("Bearer "):
        token = token[7:]
    
    try:
        # 验证JWT签名和结构
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 验证必要字段
        if not isinstance(payload, dict):
            logger.warning("Invalid token payload: not a dictionary")
            return None
        
        # 检查令牌类型
        token_type_in_payload = payload.get("type")
        if token_type_in_payload != token_type:
            logger.warning(f"Token type mismatch. Expected: {token_type}, Got: {token_type_in_payload}")
            return None
        
        # 检查过期时间
        exp = payload.get("exp")
        if exp is None:
            logger.warning("Token missing expiration time")
            return None
        
        try:
            exp_datetime = datetime.fromtimestamp(exp)
            if datetime.utcnow() > exp_datetime:
                logger.warning(f"Token has expired at {exp_datetime}")
                return None
        except (ValueError, OSError) as e:
            logger.warning(f"Invalid expiration timestamp: {exp}, error: {str(e)}")
            return None
        
        # 检查用户ID
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning("Token missing user ID (sub)")
            return None
        
        logger.debug(f"Token verified successfully for user: {user_id}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token signature has expired")
        return None
    except jwt.JWTClaimsError as e:
        logger.warning(f"Invalid token claims: {str(e)}")
        return None
    except jwt.JWTError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    从令牌中获取用户ID
    
    Args:
        token: JWT令牌
        
    Returns:
        用户ID或None
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def create_token_pair(user_id: int, additional_data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
    """
    创建令牌对（访问令牌和刷新令牌）

    Args:
        user_id: 用户ID
        additional_data: 额外的数据

    Returns:
        包含访问令牌和刷新令牌的字典
    """
    token_data = {"sub": str(user_id)}  # 确保sub是字符串类型

    if additional_data:
        token_data.update(additional_data)

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(user_id)})  # 刷新令牌只包含用户ID，确保是字符串

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    使用刷新令牌生成新的访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        新的访问令牌或None
    """
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # 创建新的访问令牌
    new_access_token = create_access_token({"sub": str(user_id)})  # 确保sub是字符串类型

    logger.info(f"Access token refreshed for user {user_id}")
    return new_access_token


def generate_password_reset_token(user_id: int) -> str:
    """
    生成密码重置令牌
    
    Args:
        user_id: 用户ID
        
    Returns:
        密码重置令牌
    """
    data = {"sub": str(user_id), "type": "password_reset"}  # 确保sub是字符串类型
    expires_delta = timedelta(hours=1)  # 密码重置令牌1小时过期
    
    return create_access_token(data, expires_delta)


def verify_password_reset_token(token: str) -> Optional[int]:
    """
    验证密码重置令牌
    
    Args:
        token: 密码重置令牌
        
    Returns:
        用户ID或None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != "password_reset":
            return None
        
        # 检查过期时间
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return payload.get("sub")
        
    except JWTError:
        return None


def generate_email_verification_token(user_id: int, email: str) -> str:
    """
    生成邮箱验证令牌
    
    Args:
        user_id: 用户ID
        email: 邮箱地址
        
    Returns:
        邮箱验证令牌
    """
    data = {"sub": str(user_id), "email": email, "type": "email_verification"}  # 确保sub是字符串类型
    expires_delta = timedelta(days=1)  # 邮箱验证令牌1天过期
    
    return create_access_token(data, expires_delta)


def verify_email_verification_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证邮箱验证令牌
    
    Args:
        token: 邮箱验证令牌
        
    Returns:
        包含用户ID和邮箱的字典或None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != "email_verification":
            return None
        
        # 检查过期时间
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
        
        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email")
        }
        
    except JWTError:
        return None


# 导出所有安全相关函数
__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_user_id_from_token",
    "create_token_pair",
    "refresh_access_token",
    "generate_password_reset_token",
    "verify_password_reset_token",
    "generate_email_verification_token",
    "verify_email_verification_token",
]
