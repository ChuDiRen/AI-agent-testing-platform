"""
依赖注入：获取当前用户
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user_crud import user as user_crud
from app.db.session import get_db
from app.models import User


async def get_current_user(
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前登录用户（从 Token 中解析）"""
    # TODO: 从 request.state 获取用户 ID（已在 auth 中间件中设置）
    # 暂时返回默认用户
    user = await user_crud.get(db, id=1)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户未登录"
        )
    return user


async def get_optional_user(
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选）"""
    # TODO: 从 Token 中解析
    return None


# 创建可选用户依赖实例
get_current_user_optional = get_optional_user
