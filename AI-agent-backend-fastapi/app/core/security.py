"""安全工具类 - JWT Token 和密码加密"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import re
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API密钥加密器 (使用 Fernet 对称加密)
# 注意: 生产环境应该从环境变量读取加密密钥
def _get_encryption_key():
    """获取或生成加密密钥"""
    if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
        # 如果ENCRYPTION_KEY已经是有效的Fernet密钥格式，直接使用
        key = settings.ENCRYPTION_KEY
        if isinstance(key, str):
            key = key.encode()
        # 验证是否是有效的Fernet密钥（32字节base64编码）
        try:
            Fernet(key)
            return key
        except Exception:
            # 如果不是有效的Fernet密钥，生成一个新的
            pass
    # 生成新密钥
    return Fernet.generate_key()

_encryption_key = _get_encryption_key()
_cipher_suite = Fernet(_encryption_key)


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    验证密码强度
    
    要求:
    - 至少8个字符
    - 包含至少一个大写字母
    - 包含至少一个小写字母
    - 包含至少一个数字
    - 包含至少一个特殊字符
    """
    if len(password) < 8:
        return False, "密码长度至少为8个字符"
    
    if not re.search(r"[A-Z]", password):
        return False, "密码必须包含至少一个大写字母"
    
    if not re.search(r"[a-z]", password):
        return False, "密码必须包含至少一个小写字母"
    
    if not re.search(r"\d", password):
        return False, "密码必须包含至少一个数字"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "密码必须包含至少一个特殊字符"
    
    return True, "密码强度符合要求"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def encrypt_api_key(api_key: str) -> str:
    """加密API密钥"""
    if not api_key:
        return ""
    return _cipher_suite.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """解密API密钥"""
    if not encrypted_key:
        return ""
    try:
        return _cipher_suite.decrypt(encrypted_key.encode()).decode()
    except Exception:
        return encrypted_key  # 如果解密失败，返回原值（兼容未加密的旧数据）


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})  # 添加token类型标识
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})  # 添加token类型标识
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 验证token类型
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """解码刷新令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # 验证token类型
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None

