"""用户服务"""
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_

from app.models.user import User
from app.schemas.user import UserUpdate
from app.schemas.pagination import PaginationParams
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash


class UserService:
    """用户服务类"""
    
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """获取所有用户"""
        return await self.user_repo.get_all(skip=skip, limit=limit)
    
    async def get_users_paginated(
        self,
        pagination: PaginationParams,
        keyword: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """分页获取用户列表（支持搜索和过滤）"""
        query = select(User)

        # 搜索功能 - 修复字段名称
        if keyword:
            search_filter = or_(
                User.username.contains(keyword),
                User.email.contains(keyword) if User.email else False
            )
            query = query.where(search_filter)

        # 过滤功能 - 修复is_active判断
        if is_active is not None:
            status_value = "1" if is_active else "0"  # User模型使用status字段，"1"表示激活
            query = query.where(User.status == status_value)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.offset(pagination.skip).limit(pagination.limit)
        result = await self.db.execute(query)
        users = result.scalars().all()

        return list(users), total or 0  # 确保返回值不为None

    async def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        dept_id: Optional[int] = None,
        ssex: Optional[str] = '2',
        description: Optional[str] = None
    ) -> User:
        """创建新用户"""
        from datetime import datetime

        try:
            # 创建用户对象
            new_user = User(
                username=username,
                password=get_password_hash(password),
                email=email,
                mobile=mobile,
                dept_id=dept_id,
                status='1',  # 默认启用
                ssex=ssex,
                description=description,
                create_time=datetime.now()
            )

            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)

            return new_user
        except Exception as e:
            await self.db.rollback()  # 发生异常时回滚事务
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建用户失败: {str(e)}"
            )

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户信息"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        try:
            # 更新字段
            update_dict = user_data.model_dump(exclude_unset=True)

            for field, value in update_dict.items():
                if field == "password" and value is not None:
                    user.password = get_password_hash(value)  # 密码需要加密
                elif hasattr(user, field):
                    setattr(user, field, value)

            # 更新修改时间
            from datetime import datetime
            user.modify_time = datetime.now()

            return await self.user_repo.update(user)
        except Exception as e:
            await self.db.rollback()  # 发生异常时回滚事务
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"更新用户失败: {str(e)}"
            )
    
    async def delete_user(self, user_id: int) -> None:
        """删除用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        try:
            await self.user_repo.delete(user)
        except Exception as e:
            await self.db.rollback()  # 发生异常时回滚事务
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"删除用户失败: {str(e)}"
            )

