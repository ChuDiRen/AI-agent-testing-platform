"""
用户 CRUD 操作
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """用户 CRUD"""
    
    async def get_by_username(
        self,
        db: AsyncSession,
        username: str
    ) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(
            select(User).filter(User.username == username)
        )
        return result.scalars().first()


# 创建全局实例
user = CRUDUser(User)
