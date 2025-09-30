"""
Menu模块API - 完全按照vue-fastapi-admin标准实现
提供菜单管理的CRUD功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.menu_service import MenuService

router = APIRouter()


@router.get("/list", summary="获取菜单列表")
async def get_menu_list(
    menu_name: Optional[str] = Query(None, description="菜单名称"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取菜单列表（树形结构）

    完全按照vue-fastapi-admin的接口规范实现
    返回完整的菜单树，不分页
    """
    try:
        menu_service = MenuService(db)

        # 获取菜单树
        menu_tree = menu_service.get_menu_tree(keyword=menu_name)

        # 按照vue-fastapi-admin的响应格式
        return Success(data=menu_tree)

    except Exception as e:
        return Fail(msg=f"获取菜单列表失败: {str(e)}")


@router.post("/create", summary="创建菜单")
async def create_menu(
    parent_id: int = Body(0, description="父菜单ID，0表示顶级菜单"),
    menu_name: str = Body(..., description="菜单名称"),
    menu_type: str = Body("0", description="菜单类型：0菜单 1按钮"),
    path: Optional[str] = Body(None, description="路由路径"),
    component: Optional[str] = Body(None, description="组件路径"),
    perms: Optional[str] = Body(None, description="权限标识"),
    icon: Optional[str] = Body(None, description="图标"),
    order_num: Optional[float] = Body(0, description="排序号"),
    is_active: bool = Body(True, description="是否启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新菜单

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        menu_service = MenuService(db)

        # 创建菜单
        new_menu = menu_service.create_menu(
            parent_id=parent_id,
            menu_name=menu_name,
            menu_type=menu_type,
            path=path,
            component=component,
            perms=perms,
            icon=icon,
            order_num=order_num,
            is_active=is_active
        )

        return Success(data={"menu_id": new_menu.id}, msg="创建成功")

    except ValueError as e:
        return Fail(msg=str(e))
    except Exception as e:
        return Fail(msg=f"创建菜单失败: {str(e)}")


@router.post("/update", summary="更新菜单")
async def update_menu(
    menu_id: int = Body(..., description="菜单ID"),
    parent_id: int = Body(0, description="父菜单ID"),
    menu_name: str = Body(..., description="菜单名称"),
    menu_type: str = Body("0", description="菜单类型：0菜单 1按钮"),
    path: Optional[str] = Body(None, description="路由路径"),
    component: Optional[str] = Body(None, description="组件路径"),
    perms: Optional[str] = Body(None, description="权限标识"),
    icon: Optional[str] = Body(None, description="图标"),
    order_num: Optional[float] = Body(0, description="排序号"),
    is_active: bool = Body(True, description="是否启用"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新菜单信息

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        menu_service = MenuService(db)

        # 检查菜单是否存在
        menu = menu_service.get_menu_by_id(menu_id)
        if not menu:
            return Fail(msg="菜单不存在")

        # 检查是否设置自己为父菜单
        if parent_id == menu_id:
            return Fail(msg="不能设置自己为父菜单")

        # 更新菜单
        menu.parent_id = parent_id
        menu.menu_name = menu_name
        menu.menu_type = menu_type
        menu.path = path
        menu.component = component
        menu.perms = perms
        menu.icon = icon
        menu.order_num = order_num
        menu.is_active = is_active

        menu_service.db.commit()

        return Success(msg="更新成功")

    except Exception as e:
        menu_service.db.rollback()
        return Fail(msg=f"更新菜单失败: {str(e)}")


@router.delete("/delete", summary="删除菜单")
async def delete_menu(
    menu_id: int = Query(..., description="菜单ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除菜单

    完全按照vue-fastapi-admin的接口规范实现
    """
    try:
        menu_service = MenuService(db)

        # 检查菜单是否存在
        menu = menu_service.get_menu_by_id(menu_id)
        if not menu:
            return Fail(msg="菜单不存在")

        # 检查是否有子菜单
        children = menu_service.get_children_menus(menu_id)
        if children:
            return Fail(msg=f"该菜单下有 {len(children)} 个子菜单，请先删除子菜单")

        # 删除菜单
        menu_service.delete_menu(menu_id)

        return Success(msg="删除成功")

    except Exception as e:
        return Fail(msg=f"删除菜单失败: {str(e)}")
