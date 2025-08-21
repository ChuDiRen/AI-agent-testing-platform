"""
通用工具函数
提供常用的助手函数
"""

import hashlib
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from email_validator import validate_email, EmailNotValidError

from app.core.logger import get_logger

logger = get_logger(__name__)


def generate_uuid() -> str:
    """
    生成UUID字符串
    
    Returns:
        UUID字符串
    """
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """
    生成短ID
    
    Args:
        length: ID长度
        
    Returns:
        短ID字符串
    """
    import random
    import string
    
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        
    Returns:
        格式化后的日期时间字符串
    """
    if dt is None:
        return ""
    
    # 确保时区信息
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        dt_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        日期时间对象或None
    """
    try:
        return datetime.strptime(dt_str, format_str)
    except ValueError:
        logger.warning(f"Failed to parse datetime: {dt_str}")
        return None


def validate_email_address(email: str) -> bool:
    """
    验证邮箱地址格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否有效
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone_number(phone: str) -> bool:
    """
    验证手机号格式（简单验证）
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    if not phone:
        return False
    
    # 移除所有非数字字符
    digits_only = re.sub(r'\D', '', phone)
    
    # 检查长度（10-15位数字）
    return 10 <= len(digits_only) <= 15


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    清理字符串
    
    Args:
        text: 输入文本
        max_length: 最大长度
        
    Returns:
        清理后的字符串
    """
    if not text:
        return ""
    
    # 去除首尾空白
    text = text.strip()
    
    # 移除危险字符
    text = re.sub(r'[<>"\']', '', text)
    
    # 限制长度
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """
    生成数据哈希值
    
    Args:
        data: 要哈希的数据
        algorithm: 哈希算法
        
    Returns:
        哈希值
    """
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """
    遮蔽敏感数据
    
    Args:
        data: 敏感数据
        mask_char: 遮蔽字符
        visible_chars: 可见字符数
        
    Returns:
        遮蔽后的数据
    """
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    visible_part = data[:visible_chars]
    masked_part = mask_char * (len(data) - visible_chars)
    
    return visible_part + masked_part


def convert_size_to_bytes(size_str: str) -> int:
    """
    转换大小字符串为字节数
    
    Args:
        size_str: 大小字符串（如 "10MB", "1GB"）
        
    Returns:
        字节数
    """
    size_str = size_str.upper().strip()
    
    # 提取数字和单位
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([KMGT]?B?)$', size_str)
    if not match:
        raise ValueError(f"Invalid size format: {size_str}")
    
    number = float(match.group(1))
    unit = match.group(2)
    
    # 转换为字节
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 ** 2,
        'GB': 1024 ** 3,
        'TB': 1024 ** 4,
    }
    
    return int(number * multipliers.get(unit, 1))


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的大小字符串
    """
    if size_bytes == 0:
        return "0B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f}{units[unit_index]}"


def deep_merge_dict(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    深度合并字典
    
    Args:
        dict1: 第一个字典
        dict2: 第二个字典
        
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    扁平化字典
    
    Args:
        data: 要扁平化的字典
        parent_key: 父键名
        sep: 分隔符
        
    Returns:
        扁平化后的字典
    """
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    将列表分块
    
    Args:
        data: 要分块的列表
        chunk_size: 块大小
        
    Returns:
        分块后的列表
    """
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def remove_duplicates(data: List[Any], key_func: Optional[callable] = None) -> List[Any]:
    """
    移除列表中的重复项
    
    Args:
        data: 输入列表
        key_func: 用于确定唯一性的键函数
        
    Returns:
        去重后的列表
    """
    if key_func is None:
        return list(dict.fromkeys(data))
    
    seen = set()
    result = []
    
    for item in data:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result


def safe_cast(value: Any, target_type: type, default: Any = None) -> Any:
    """
    安全类型转换
    
    Args:
        value: 要转换的值
        target_type: 目标类型
        default: 默认值
        
    Returns:
        转换后的值或默认值
    """
    try:
        return target_type(value)
    except (ValueError, TypeError):
        return default


def is_valid_json(json_str: str) -> bool:
    """
    检查字符串是否为有效的JSON
    
    Args:
        json_str: JSON字符串
        
    Returns:
        是否有效
    """
    try:
        import json
        json.loads(json_str)
        return True
    except (ValueError, TypeError):
        return False


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    截断字符串
    
    Args:
        text: 输入文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的字符串
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def get_client_ip(request) -> str:
    """
    获取客户端IP地址
    
    Args:
        request: FastAPI请求对象
        
    Returns:
        IP地址
    """
    # 检查代理头
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # 返回直接连接的IP
    return request.client.host if request.client else "unknown"


# 导出所有工具函数
__all__ = [
    "generate_uuid",
    "generate_short_id",
    "format_datetime",
    "parse_datetime",
    "validate_email_address",
    "validate_phone_number",
    "sanitize_string",
    "generate_hash",
    "mask_sensitive_data",
    "convert_size_to_bytes",
    "format_file_size",
    "deep_merge_dict",
    "flatten_dict",
    "chunk_list",
    "remove_duplicates",
    "safe_cast",
    "is_valid_json",
    "truncate_string",
    "get_client_ip",
]
