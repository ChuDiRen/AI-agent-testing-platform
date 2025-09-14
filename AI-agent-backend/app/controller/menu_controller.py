# Copyright (c) 2025 左岚. All rights reserved.
"""
菜单Controller
处理菜单相关的HTTP请求
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse, Success, Fail
from app.dto.menu_dto import (
    MenuCreateRequest,
    MenuUpdateRequest,
    MenuResponse,
    MenuTreeNode,
    UserMenuResponse,
    MenuIdRequest,
    MenuDeleteRequest,
    UserMenuRequest,
    UserMenuTreeResponse,
    UserMenuTreeNode,
    MenuSearchRequest
)
from app.service.menu_service import MenuService
from app.middleware.auth import get_current_user
from app.utils.log_decorators import log_operation, log_user_action

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.post("/create-menu", response_model=ApiResponse[MenuResponse], summary="创建菜单")
@log_operation(
    operation_type="CREATE",
    resource_type="MENU",
    operation_desc="创建菜单",
    include_request=True
)
async def create_menu(
    request: MenuCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建新菜单
    
    - **parent_id**: 上级菜单ID，0表示顶级菜单
    - **menu_name**: 菜单/按钮名称
    - **menu_type**: 类型，'0'菜单 '1'按钮
    - **path**: 路由路径（可选）
    - **component**: 路由组件（可选）
    - **perms**: 权限标识（可选）
    - **icon**: 图标（可选）
    - **order_num**: 排序号（可选）
    """
    try:
        menu_service = MenuService(db)
        menu = menu_service.create_menu(
            parent_id=request.parent_id,
            menu_name=request.menu_name,
            menu_type=request.menu_type,
            path=request.path,
            component=request.component,
            perms=request.perms,
            icon=request.icon,
            order_num=request.order_num,
            is_active=request.is_active
        )

        # 转换为字典格式
        menu_dict = {
            "menu_id": menu.id,
            "parent_id": menu.parent_id,
            "menu_name": menu.menu_name,
            "path": menu.path,
            "component": menu.component,
            "perms": menu.perms,
            "icon": menu.icon,
            "menu_type": menu.menu_type,
            "order_num": menu.order_num,
            "is_active": menu.is_active,
            "create_time": menu.create_time.isoformat() if menu.create_time else None,
            "modify_time": menu.modify_time.isoformat() if menu.modify_time else None
        }

        logger.info(f"Menu created successfully: {menu.menu_name}")
        return Success(code=200, msg="菜单创建成功", data=menu_dict)
        
    except Exception as e:
        logger.error(f"Unexpected error creating menu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建菜单失败"
        )


@router.post("/get-menu-tree", response_model=ApiResponse[List[MenuTreeNode]], summary="获取菜单树")
async def get_menu_tree(
    request: MenuSearchRequest = MenuSearchRequest(),
    db: Session = Depends(get_db)
):
    """
    获取完整的菜单树结构，支持搜索过滤
    """
    try:
        menu_service = MenuService(db)

        tree_data = menu_service.get_menu_tree(
            keyword=request.keyword,
            is_active=request.is_active
        )

        # 直接返回字典格式的树形数据
        return Success(code=200, msg="获取菜单树成功", data=tree_data or [])

    except Exception as e:
        logger.error(f"Error getting menu tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取菜单树失败"
        )


@router.post("/get-menu-info", response_model=ApiResponse[MenuResponse], summary="获取菜单详情")
async def get_menu_info(
    request: MenuIdRequest,
    db: Session = Depends(get_db)
):
    """
    根据ID获取菜单详情

    - **menu_id**: 菜单ID（请求体传参）
    """
    try:
        menu_service = MenuService(db)
        menu = menu_service.get_menu_by_id(request.menu_id)
        
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        
        # 转换为字典格式
        menu_dict = {
            "menu_id": menu.id,
            "parent_id": menu.parent_id,
            "menu_name": menu.menu_name,
            "path": menu.path,
            "component": menu.component,
            "perms": menu.perms,
            "icon": menu.icon,
            "menu_type": menu.menu_type,
            "order_num": menu.order_num,
            "is_active": menu.is_active,
            "create_time": menu.create_time.isoformat() if menu.create_time else None,
            "modify_time": menu.modify_time.isoformat() if menu.modify_time else None
        }

        return Success(code=200, msg="获取菜单详情成功", data=menu_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting menu {request.menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取菜单详情失败"
        )


@router.post("/update-menu", response_model=ApiResponse[MenuResponse], summary="更新菜单")
@log_operation(
    operation_type="UPDATE",
    resource_type="MENU",
    operation_desc="更新菜单",
    include_request=True
)
async def update_menu(
    request: MenuUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新菜单信息

    - **menu_id**: 菜单ID（请求体传参）
    - **menu_name**: 新的菜单名称（可选）
    - **path**: 新的路由路径（可选）
    - **component**: 新的路由组件（可选）
    - **perms**: 新的权限标识（可选）
    - **icon**: 新的图标（可选）
    - **order_num**: 新的排序号（可选）
    """
    try:
        menu_service = MenuService(db)
        menu = menu_service.update_menu(
            menu_id=request.menu_id,
            menu_name=request.menu_name,
            path=request.path,
            component=request.component,
            perms=request.perms,
            icon=request.icon,
            order_num=request.order_num,
            is_active=request.is_active
        )

        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )

        # 转换为字典格式
        menu_dict = {
            "menu_id": menu.id,
            "parent_id": menu.parent_id,
            "menu_name": menu.menu_name,
            "path": menu.path,
            "component": menu.component,
            "perms": menu.perms,
            "icon": menu.icon,
            "menu_type": menu.menu_type,
            "order_num": menu.order_num,
            "is_active": menu.is_active,
            "create_time": menu.create_time.isoformat() if menu.create_time else None,
            "modify_time": menu.modify_time.isoformat() if menu.modify_time else None
        }

        logger.info(f"Menu updated successfully: {request.menu_id}")
        return Success(code=200, msg="菜单更新成功", data=menu_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating menu {request.menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新菜单失败"
        )


@router.post("/delete-menu", response_model=ApiResponse[bool], summary="删除菜单")
@log_operation(
    operation_type="DELETE",
    resource_type="MENU",
    operation_desc="删除菜单",
    include_request=True
)
async def delete_menu(
    request: MenuDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    删除菜单

    - **menu_id**: 菜单ID（请求体传参）
    """
    try:
        menu_service = MenuService(db)
        success = menu_service.delete_menu(request.menu_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )

        logger.info(f"Menu deleted successfully: {request.menu_id}")
        return Success(code=200, msg="菜单删除成功", data=True)

    except ValueError as e:
        logger.warning(f"Menu deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting menu {request.menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除菜单失败"
        )


@router.post("/get-user-menus", response_model=ApiResponse[UserMenuResponse], summary="获取用户菜单")
async def get_user_menus(
    request: UserMenuRequest,
    db: Session = Depends(get_db)
):
    """
    获取用户的菜单权限

    - **user_id**: 用户ID（请求体传参）
    """
    try:
        menu_service = MenuService(db)
        
        # 获取用户菜单
        user_menus = menu_service.get_user_menus(request.user_id)

        # 获取用户权限
        user_permissions = menu_service.get_user_permissions(request.user_id)

        # 转换为字典格式的树形结构
        def menu_to_dict(menu):
            return {
                "menu_id": menu.id,
                "parent_id": menu.parent_id,
                "menu_name": menu.menu_name,
                "path": menu.path,
                "component": menu.component,
                "perms": menu.perms,
                "icon": menu.icon,
                "menu_type": menu.menu_type,
                "order_num": menu.order_num,
                "children": []
            }

        menu_dict = {}
        for menu in user_menus:
            menu_dict[menu.id] = menu_to_dict(menu)

        # 构建父子关系
        tree = []
        for menu_node in menu_dict.values():
            if menu_node["parent_id"] == 0:
                tree.append(menu_node)
            else:
                parent = menu_dict.get(menu_node["parent_id"])
                if parent:
                    parent["children"].append(menu_node)

        response_data = {
            "menus": tree,
            "permissions": user_permissions
        }

        return Success(code=200, msg="获取用户菜单成功", data=response_data)

    except Exception as e:
        logger.error(f"Error getting user menus for user {request.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户菜单失败"
        )


@router.post("/get-user-routes", response_model=ApiResponse[UserMenuTreeResponse], summary="获取用户动态路由")
async def get_user_routes(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取当前用户的动态路由结构 - 用于前端动态路由
    """
    try:
        menu_service = MenuService(db)

        # 获取用户动态路由树
        user_routes = menu_service.get_user_menu_tree(current_user.id)

        # 获取用户权限
        user_permissions = menu_service.get_user_permissions(current_user.id)

        response_data = UserMenuTreeResponse(
            routes=user_routes,
            permissions=user_permissions
        )

        return Success(code=200, msg="获取用户路由成功", data=response_data)

    except Exception as e:
        logger.error(f"Error getting user routes for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户路由失败"
        )
