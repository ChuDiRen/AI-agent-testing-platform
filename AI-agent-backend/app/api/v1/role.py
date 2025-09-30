"""
角色管理API - 兼容vue-fastapi-admin格式
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user  # 修正导入路径
from app.db.session import get_db  # 修正导入路径
from app.dto.base_dto import Success, Fail
from app.dto.role_dto import RoleCreateRequest, RoleUpdateRequest, RoleMenuAssignRequest  # 修正导入路径
from app.entity.user import User
from app.service.role_service import RoleService
from pydantic import BaseModel, Field  # 用于创建临时DTO

router = APIRouter()


# 临时DTO定义
class RoleAuthorizedRequest(BaseModel):
    """角色权限设置请求"""
    id: int = Field(..., description="角色ID")
    menu_ids: List[int] = Field(default=[], description="菜单ID列表")
    api_infos: List[dict] = Field(default=[], description="API权限信息列表")


@router.get("/list", summary="获取角色列表")
async def get_role_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role_name: Optional[str] = Query(None, description="角色名"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    try:
        role_service = RoleService(db)
        
        # 构建查询条件
        filters = {}
        if role_name:
            filters['name'] = role_name
        
        # 获取角色列表
        roles, total = await role_service.get_role_list(
            page=page,
            page_size=page_size,
            filters=filters
        )
        
        # 构建响应数据
        role_list = []
        for role in roles:
            role_data = {
                "id": role.id,
                "name": role.name,
                "desc": role.description,
                "created_at": role.created_at
            }
            role_list.append(role_data)
        
        response_data = {
            "items": role_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }
        
        return Success(data=response_data)
        
    except Exception as e:
        return Fail(msg=f"获取角色列表失败: {str(e)}")


@router.post("/create", summary="创建角色")
async def create_role(
    role_data: RoleCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建角色"""
    try:
        role_service = RoleService(db)
        
        # 检查角色名是否已存在
        existing_role = await role_service.get_role_by_name(role_data.name)
        if existing_role:
            return Fail(msg="角色名已存在")
        
        # 创建角色
        new_role = await role_service.create_role(
            name=role_data.name,
            description=role_data.desc
        )
        
        return Success(data={"id": new_role.id}, msg="创建成功")
        
    except Exception as e:
        return Fail(msg=f"创建角色失败: {str(e)}")


@router.post("/update", summary="更新角色")
async def update_role(
    role_data: RoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新角色"""
    try:
        role_service = RoleService(db)
        
        # 检查角色是否存在
        role = await role_service.get_role_by_id(role_data.id)
        if not role:
            return Fail(msg="角色不存在")
        
        # 检查角色名是否已被其他角色使用
        if role_data.name != role.name:
            existing_role = await role_service.get_role_by_name(role_data.name)
            if existing_role and existing_role.id != role_data.id:
                return Fail(msg="角色名已被其他角色使用")
        
        # 更新角色
        await role_service.update_role(
            role_id=role_data.id,
            name=role_data.name,
            description=role_data.desc
        )
        
        return Success(msg="更新成功")
        
    except Exception as e:
        return Fail(msg=f"更新角色失败: {str(e)}")


@router.delete("/delete", summary="删除角色")
async def delete_role(
    role_id: int = Query(..., description="角色ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除角色"""
    try:
        role_service = RoleService(db)
        
        # 检查角色是否存在
        role = await role_service.get_role_by_id(role_id)
        if not role:
            return Fail(msg="角色不存在")
        
        # 检查角色是否被用户使用
        user_count = await role_service.get_role_user_count(role_id)
        if user_count > 0:
            return Fail(msg=f"该角色正在被 {user_count} 个用户使用，无法删除")
        
        # 删除角色
        await role_service.delete_role(role_id)
        
        return Success(msg="删除成功")
        
    except Exception as e:
        return Fail(msg=f"删除角色失败: {str(e)}")


@router.post("/authorized", summary="设置角色权限")
async def update_role_authorized(
    auth_data: RoleAuthorizedRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """设置角色权限"""
    try:
        role_service = RoleService(db)
        
        # 检查角色是否存在
        role = await role_service.get_role_by_id(auth_data.id)
        if not role:
            return Fail(msg="角色不存在")
        
        # 设置角色权限
        await role_service.set_role_permissions(
            role_id=auth_data.id,
            menu_ids=auth_data.menu_ids,
            api_infos=auth_data.api_infos
        )
        
        return Success(msg="权限设置成功")
        
    except Exception as e:
        return Fail(msg=f"权限设置失败: {str(e)}")


@router.get("/authorized", summary="获取角色权限")
async def get_role_authorized(
    id: int = Query(..., description="角色ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取角色权限"""
    try:
        role_service = RoleService(db)
        
        # 检查角色是否存在
        role = await role_service.get_role_by_id(id)
        if not role:
            return Fail(msg="角色不存在")
        
        # 获取角色权限
        menus, apis = await role_service.get_role_permissions(id)
        
        # 构建响应数据
        menu_list = [{"id": menu.id, "name": menu.name} for menu in menus]
        api_list = [{"id": api.id, "path": api.path, "method": api.method} for api in apis]
        
        response_data = {
            "menus": menu_list,
            "apis": api_list
        }
        
        return Success(data=response_data)
        
    except Exception as e:
        return Fail(msg=f"获取角色权限失败: {str(e)}")
