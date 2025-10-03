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
        
        # 搜索功能
        if keyword:
            search_filter = or_(
                User.username.contains(keyword),
                User.email.contains(keyword),
                User.full_name.contains(keyword)
            )
            query = query.where(search_filter)
        
        # 过滤功能
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 分页查询
        query = query.offset(pagination.skip).limit(pagination.limit)
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return list(users), total
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户信息"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新字段
        if user_data.email is not None:
            # 检查邮箱是否已被使用
            existing_email = await self.user_repo.get_by_email(user_data.email)
            if existing_email and existing_email.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被使用"
                )
            user.email = user_data.email
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.password is not None:
            user.password = get_password_hash(user_data.password)
        
        return await self.user_repo.update(user)
    
    async def delete_user(self, user_id: int) -> None:
        """删除用户"""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        await self.user_repo.delete(user)

