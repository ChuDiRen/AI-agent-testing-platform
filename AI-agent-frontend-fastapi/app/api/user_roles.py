"""用户角色关联路由"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel

from app.core.database import get_db
from app.schemas.common import APIResponse
from app.schemas.role import RoleResponse
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role

router = APIRouter(prefix="/user-roles", tags=["用户角色关联"])


class AssignRolesRequest(BaseModel):
    """分配角色请求"""
    user_id: int
    role_ids: List[int]


@router.post("/assign", response_model=APIResponse[None])
async def assign_roles_to_user(
    request: AssignRolesRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """为用户分配角色"""
    # 删除现有角色关联
    await db.execute(
        delete(UserRole).where(UserRole.user_id == request.user_id)
    )
    
    # 创建新的角色关联
    for role_id in request.role_ids:
        user_role = UserRole(user_id=request.user_id, role_id=role_id)
        db.add(user_role)
    
    await db.commit()
    
    return APIResponse(message="角色分配成功")


@router.get("/{user_id}/roles", response_model=APIResponse[List[RoleResponse]])
async def get_user_roles(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[RoleResponse]]:
    """获取用户的角色列表"""
    # 查询用户的角色
    result = await db.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
    )
    roles = result.scalars().all()
    
    return APIResponse(
        data=[RoleResponse.model_validate(role) for role in roles]
    )


@router.delete("/{user_id}/roles/{role_id}", response_model=APIResponse[None])
async def remove_role_from_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """移除用户的某个角色"""
    await db.execute(
        delete(UserRole)
        .where(UserRole.user_id == user_id, UserRole.role_id == role_id)
    )
    await db.commit()
    
    return APIResponse(message="角色移除成功")

