"""角色管理路由"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.schemas.common import APIResponse
from app.services.role_service import RoleService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("/", response_model=APIResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[RoleResponse]:
    """创建角色"""
    role_service = RoleService(db)
    role = await role_service.create_role(role_data)
    
    return APIResponse(
        message="角色创建成功",
        data=RoleResponse.model_validate(role)
    )


@router.get("/", response_model=APIResponse[List[RoleResponse]])
async def get_roles(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[RoleResponse]]:
    """获取角色列表"""
    role_service = RoleService(db)
    roles = await role_service.get_all_roles(skip=skip, limit=limit)

    return APIResponse(
        data=[RoleResponse.model_validate(role) for role in roles]
    )


@router.get("/{role_id}", response_model=APIResponse[RoleResponse])
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[RoleResponse]:
    """获取角色详情"""
    role_service = RoleService(db)
    role = await role_service.get_role_by_id(role_id)

    return APIResponse(
        data=RoleResponse.model_validate(role)
    )


@router.put("/{role_id}", response_model=APIResponse[RoleResponse])
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[RoleResponse]:
    """更新角色"""
    role_service = RoleService(db)
    role = await role_service.update_role(role_id, role_data)
    
    return APIResponse(
        message="角色更新成功",
        data=RoleResponse.model_validate(role)
    )


@router.delete("/{role_id}", response_model=APIResponse[None])
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除角色"""
    role_service = RoleService(db)
    await role_service.delete_role(role_id)
    
    return APIResponse(
        message="角色删除成功"
    )

