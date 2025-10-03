"""权限管理路由"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.permission import PermissionCreate, PermissionUpdate, PermissionResponse
from app.schemas.common import APIResponse
from app.repositories.permission_repository import PermissionRepository
from app.models.permission import Permission
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.post("/", response_model=APIResponse[PermissionResponse], status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: PermissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PermissionResponse]:
    """创建权限"""
    permission_repo = PermissionRepository(db)
    
    # 检查权限代码是否已存在
    existing = await permission_repo.get_by_code(permission_data.code)
    if existing:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="权限代码已存在")
    
    new_permission = Permission(**permission_data.model_dump())
    permission = await permission_repo.create(new_permission)
    
    return APIResponse(
        message="权限创建成功",
        data=PermissionResponse.model_validate(permission)
    )


@router.get("/", response_model=APIResponse[List[PermissionResponse]])
async def get_permissions(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[PermissionResponse]]:
    """获取权限列表"""
    permission_repo = PermissionRepository(db)
    permissions = await permission_repo.get_all(skip=skip, limit=limit)
    
    return APIResponse(
        data=[PermissionResponse.model_validate(p) for p in permissions]
    )


@router.get("/{permission_id}", response_model=APIResponse[PermissionResponse])
async def get_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PermissionResponse]:
    """获取权限详情"""
    permission_repo = PermissionRepository(db)
    permission = await permission_repo.get_by_id(permission_id)
    
    if not permission:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="权限不存在")
    
    return APIResponse(
        data=PermissionResponse.model_validate(permission)
    )


@router.put("/{permission_id}", response_model=APIResponse[PermissionResponse])
async def update_permission(
    permission_id: int,
    permission_data: PermissionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PermissionResponse]:
    """更新权限"""
    permission_repo = PermissionRepository(db)
    permission = await permission_repo.get_by_id(permission_id)
    
    if not permission:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="权限不存在")
    
    # 更新字段
    update_data = permission_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(permission, field, value)
    
    permission = await permission_repo.update(permission)
    
    return APIResponse(
        message="权限更新成功",
        data=PermissionResponse.model_validate(permission)
    )


@router.delete("/{permission_id}", response_model=APIResponse[None])
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除权限"""
    permission_repo = PermissionRepository(db)
    permission = await permission_repo.get_by_id(permission_id)
    
    if not permission:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="权限不存在")
    
    await permission_repo.delete(permission)
    
    return APIResponse(
        message="权限删除成功"
    )

