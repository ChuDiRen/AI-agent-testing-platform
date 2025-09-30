"""
菜单管理API - 兼容vue-fastapi-admin格式
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.utils.permissions import get_current_user  # 修正导入路径
from app.db.session import get_db  # 修正导入路径
from app.dto.base_dto import Success, Fail
from app.dto.menu_dto import MenuCreateRequest, MenuUpdateRequest
from app.entity.user import User
from app.service.menu_service import MenuService

router = APIRouter()


@router.get("/list", summary="获取菜单列表")
async def get_menu_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(9999, ge=1, description="每页数量"),
    name: Optional[str] = Query(None, description="菜单名称"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取菜单列表"""
    try:
        menu_service = MenuService(db)
        
        # 构建查询条件
        filters = {}
        if name:
            filters['name'] = name
        
        # 获取菜单列表
        menus = await menu_service.get_menu_list(filters=filters)
        
        # 构建响应数据
        menu_list = []
        for menu in menus:
            menu_data = {
                "id": menu.id,
                "name": menu.name,
                "parent_id": menu.parent_id,
                "path": menu.path,
                "component": menu.component,
                "icon": menu.icon,
                "order_num": menu.order_num,
                "redirect": menu.redirect,
                "is_visible": menu.is_visible,
                "keep_alive": menu.keep_alive,
                "created_at": menu.created_at
            }
            menu_list.append(menu_data)
        
        response_data = {
            "items": menu_list,
            "total": len(menu_list)
        }
        
        return Success(data=response_data)
        
    except Exception as e:
        return Fail(msg=f"获取菜单列表失败: {str(e)}")


@router.post("/create", summary="创建菜单")
async def create_menu(
    menu_data: MenuCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建菜单"""
    try:
        menu_service = MenuService(db)
        
        # 检查菜单名是否已存在
        existing_menu = await menu_service.get_menu_by_name(menu_data.name)
        if existing_menu:
            return Fail(msg="菜单名已存在")
        
        # 检查路径是否已存在
        if menu_data.path:
            existing_path = await menu_service.get_menu_by_path(menu_data.path)
            if existing_path:
                return Fail(msg="菜单路径已存在")
        
        # 创建菜单
        new_menu = await menu_service.create_menu(
            name=menu_data.name,
            parent_id=menu_data.parent_id,
            path=menu_data.path,
            component=menu_data.component,
            icon=menu_data.icon,
            order_num=menu_data.order_num,
            redirect=menu_data.redirect,
            is_visible=menu_data.is_visible,
            keep_alive=menu_data.keep_alive
        )
        
        return Success(data={"id": new_menu.id}, msg="创建成功")
        
    except Exception as e:
        return Fail(msg=f"创建菜单失败: {str(e)}")


@router.post("/update", summary="更新菜单")
async def update_menu(
    menu_data: MenuUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新菜单"""
    try:
        menu_service = MenuService(db)
        
        # 检查菜单是否存在
        menu = await menu_service.get_menu_by_id(menu_data.id)
        if not menu:
            return Fail(msg="菜单不存在")
        
        # 检查菜单名是否已被其他菜单使用
        if menu_data.name != menu.name:
            existing_menu = await menu_service.get_menu_by_name(menu_data.name)
            if existing_menu and existing_menu.id != menu_data.id:
                return Fail(msg="菜单名已被其他菜单使用")
        
        # 检查路径是否已被其他菜单使用
        if menu_data.path and menu_data.path != menu.path:
            existing_path = await menu_service.get_menu_by_path(menu_data.path)
            if existing_path and existing_path.id != menu_data.id:
                return Fail(msg="菜单路径已被其他菜单使用")
        
        # 检查是否设置自己为父菜单
        if menu_data.parent_id == menu_data.id:
            return Fail(msg="不能设置自己为父菜单")
        
        # 更新菜单
        await menu_service.update_menu(
            menu_id=menu_data.id,
            name=menu_data.name,
            parent_id=menu_data.parent_id,
            path=menu_data.path,
            component=menu_data.component,
            icon=menu_data.icon,
            order_num=menu_data.order_num,
            redirect=menu_data.redirect,
            is_visible=menu_data.is_visible,
            keep_alive=menu_data.keep_alive
        )
        
        return Success(msg="更新成功")
        
    except Exception as e:
        return Fail(msg=f"更新菜单失败: {str(e)}")


@router.delete("/delete", summary="删除菜单")
async def delete_menu(
    menu_id: int = Query(..., description="菜单ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除菜单"""
    try:
        menu_service = MenuService(db)
        
        # 检查菜单是否存在
        menu = await menu_service.get_menu_by_id(menu_id)
        if not menu:
            return Fail(msg="菜单不存在")
        
        # 检查是否有子菜单
        children_count = await menu_service.get_children_count(menu_id)
        if children_count > 0:
            return Fail(msg=f"该菜单下有 {children_count} 个子菜单，请先删除子菜单")
        
        # 删除菜单
        await menu_service.delete_menu(menu_id)
        
        return Success(msg="删除成功")
        
    except Exception as e:
        return Fail(msg=f"删除菜单失败: {str(e)}")
