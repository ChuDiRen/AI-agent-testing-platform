"""
Role模块API - 完全按照vue-fastapi-admin标准实现
提供角色管理的CRUD和权限分配功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.role_service import RoleService

router = APIRouter()


@router.get("/list", summary="获取角色列表")
async def get_role_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=10000, description="每页数量"),  # 提高限制以支持获取所有角色
    role_name: Optional[str] = Query(None, description="角色名"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色列表（分页）

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        role_service = RoleService(db)

        # 构建查询条件
        filters = {}
        if role_name:
            filters['role_name'] = role_name

        # 获取角色列表
        roles, total = await role_service.get_role_list(
            page=page,
            page_size=page_size,
            filters=filters
        )

        # 构建响应数据 - 字段名匹配前端
        role_list = []
        for role in roles:
            role_data = {
                "id": role.id,  # 前端期望id
                "name": role.role_name,  # 前端期望name
                "desc": role.remark or "",  # 前端期望desc
                "is_active": role.is_active,
                "created_at": role.create_time.strftime("%Y-%m-%d %H:%M:%S") if role.create_time else ""
            }
            role_list.append(role_data)

        # 直接返回数组,用于角色选择器
        return Success(data=role_list)

    except Exception as e:
        return Fail(msg=f"获取角色列表失败: {str(e)}")


@router.post("/create", summary="创建角色")
async def create_role(
    name: str = Body(..., description="角色名称"),  # 前端传name
    desc: Optional[str] = Body(None, description="角色描述"),  # 前端传desc
    is_active: bool = Body(True, description="是否启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新角色

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        role_service = RoleService(db)

        # 检查角色名是否已存在
        existing_role = role_service.get_role_by_name(name)
        if existing_role:
            return Fail(msg="角色名已存在")

        # 创建角色
        new_role = role_service.create_role(
            role_name=name,
            remark=desc
        )

        # 设置是否启用
        new_role.is_active = is_active
        role_service.db.commit()

        return Success(data={"id": new_role.id}, msg="创建成功")  # 返回id而不是role_id

    except ValueError as e:
        return Fail(msg=str(e))
    except Exception as e:
        return Fail(msg=f"创建角色失败: {str(e)}")


@router.post("/update", summary="更新角色")
async def update_role(
    id: int = Body(..., description="角色ID"),  # 前端传id
    name: str = Body(..., description="角色名称"),  # 前端传name
    desc: Optional[str] = Body(None, description="角色描述"),  # 前端传desc
    is_active: bool = Body(True, description="是否启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新角色信息

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        role_service = RoleService(db)

        # 检查角色是否存在
        role = role_service.get_role_by_id(id)
        if not role:
            return Fail(msg="角色不存在")

        # 检查角色名是否已被其他角色使用
        if name != role.role_name:
            existing_role = role_service.get_role_by_name(name)
            if existing_role and existing_role.id != id:
                return Fail(msg="角色名已被其他角色使用")

        # 更新角色
        role.role_name = name
        role.remark = desc
        role.is_active = is_active
        role_service.db.commit()

        return Success(msg="更新成功")

    except Exception as e:
        role_service.db.rollback()
        return Fail(msg=f"更新角色失败: {str(e)}")


@router.delete("/delete", summary="删除角色")
async def delete_role(
    role_id: int = Query(..., description="角色ID"),  # 前端传role_id
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除角色

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        role_service = RoleService(db)

        # 检查角色是否存在
        role = role_service.get_role_by_id(role_id)
        if not role:
            return Fail(msg="角色不存在")

        # 检查角色是否被用户使用
        user_count = await role_service.get_role_user_count(role_id)
        if user_count > 0:
            return Fail(msg=f"该角色正在被 {user_count} 个用户使用，无法删除")

        # 删除角色 (delete_role是同步方法,不需要await)
        role_service.delete_role(role_id)

        return Success(msg="删除成功")

    except Exception as e:
        return Fail(msg=f"删除角色失败: {str(e)}")


@router.post("/authorized", summary="更新角色权限")
async def update_role_authorized(
    role_id: int = Body(..., description="角色ID"),
    menu_ids: List[int] = Body(default=[], description="菜单ID列表"),
    api_ids: List[int] = Body(default=[], description="API ID列表"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新角色权限（菜单权限和API权限）

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        role_service = RoleService(db)

        # 检查角色是否存在
        role = role_service.get_role_by_id(role_id)
        if not role:
            return Fail(msg="角色不存在")

        # 设置角色权限
        await role_service.set_role_permissions(
            role_id=role_id,
            menu_ids=menu_ids,
            api_ids=api_ids
        )

        return Success(msg="权限设置成功")

    except Exception as e:
        return Fail(msg=f"权限设置失败: {str(e)}")


@router.get("/authorized", summary="获取角色权限")
async def get_role_authorized(
    id: int = Query(..., description="角色ID"),  # 前端传id,不是role_id
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色的权限配置

    完全按照vue-fastapi-admin的接口规范实现
    返回菜单ID列表和API ID列表
    """
    try:
        role_service = RoleService(db)

        # 检查角色是否存在
        role = role_service.get_role_by_id(id)  # 使用id参数
        if not role:
            return Fail(msg="角色不存在")

        # 获取角色的菜单和API权限
        menus, apis = await role_service.get_role_authorized_data(id)  # 获取完整的菜单和API对象

        # 按照vue-fastapi-admin的响应格式
        response_data = {
            "menus": menus,  # 菜单对象列表
            "apis": apis     # API对象列表
        }

        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取角色权限失败: {str(e)}")
