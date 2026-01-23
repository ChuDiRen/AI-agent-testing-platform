"""
User CRUD 操作
"""
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.crud.base import CRUDBase
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import AuthService


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User CRUD 操作类"""

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """创建用户（包含密码哈希处理）"""
        obj_in_data = obj_in.model_dump()
        
        # 处理密码哈希
        if "password" in obj_in_data:
            password = obj_in_data.pop("password")
            obj_in_data["password_hash"] = AuthService.get_password_hash(password)
        
        # 确保时间字段被正确设置
        from datetime import datetime
        if "created_at" not in obj_in_data:
            obj_in_data["created_at"] = datetime.utcnow()
        if "updated_at" not in obj_in_data:
            obj_in_data["updated_at"] = datetime.utcnow()
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_users(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """获取启用的用户列表"""
        result = await db.execute(
            select(User)
            .where(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(User.id.desc())
        )
        return result.scalars().all()

    async def update_last_login(
        self, db: AsyncSession, *, user_id: int
    ) -> User:
        """更新最后登录时间"""
        user_obj = await self.get(db, id=user_id)
        from datetime import datetime
        return await self.update(
            db, db_obj=user_obj, obj_in={"last_login_at": datetime.utcnow()}
        )

    async def count_total_users(self, db: AsyncSession) -> int:
        """统计总用户数"""
        result = await db.execute(select(func.count(User.id)))
        return result.scalar() or 0

    async def count_active_users(self, db: AsyncSession) -> int:
        """统计激活用户数"""
        result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        return result.scalar() or 0

    # 创建 User CRUD 实例
user = CRUDUser(User)
