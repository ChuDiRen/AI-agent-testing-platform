# Copyright (c) 2025 左岚. All rights reserved.
"""
令牌黑名单工具（内存版）
可在生产替换为 Redis 实现
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import jwt

from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)

# token -> 过期时间
_BLACKLIST: Dict[str, datetime] = {}


def _get_exp_from_token(token: str) -> Optional[datetime]:
    try:
        claims = jwt.get_unverified_claims(token)
        exp_ts = claims.get("exp")
        if exp_ts:
            return datetime.fromtimestamp(exp_ts)
    except Exception as e:
        logger.warning(f"Cannot parse token exp: {e}")
    # 默认1天后清理，避免无限增长
    return datetime.utcnow() + timedelta(days=1)


def add_to_blacklist(token: str) -> None:
    if not token:
        return
    exp = _get_exp_from_token(token)
    if exp:
        _BLACKLIST[token] = exp
        logger.info("Token added to blacklist, exp=%s", exp.isoformat())


def is_blacklisted(token: str) -> bool:
    if not token:
        return False
    _cleanup()
    exp = _BLACKLIST.get(token)
    if not exp:
        return False
    # 在到期前视为已失效
    return datetime.utcnow() <= exp


def _cleanup() -> None:
    now = datetime.utcnow()
    expired = [t for t, exp in _BLACKLIST.items() if exp < now]
    for t in expired:
        _BLACKLIST.pop(t, None)


__all__ = ["add_to_blacklist", "is_blacklisted"] 