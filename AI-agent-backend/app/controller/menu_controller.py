# Copyright (c) 2025 左岚. All rights reserved.
"""
菜单Controller
处理菜单相关的HTTP请求
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse
from app.dto.menu_dto import (
    MenuCreateRequest,
    MenuUpdateRequest,
    MenuResponse,
    MenuTreeResponse,
    MenuTreeNode,
    UserMenuResponse
)
from app.service.menu_service import MenuService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.post("/", response_model=ApiResponse[MenuResponse], summary="创建菜单")
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
            order_num=request.order_num
        )
        
        # 转换为响应格式
        menu_response = MenuResponse(
            menu_id=menu.menu_id,
            parent_id=menu.parent_id,
            menu_name=menu.menu_name,
            path=menu.PATH,
            component=menu.COMPONENT,
            perms=menu.perms,
            icon=menu.icon,
            menu_type=menu.TYPE,
            order_num=menu.order_num,
            create_time=menu.create_time,
            modify_time=menu.modify_time
        )
        
        logger.info(f"Menu created successfully: {menu.menu_name}")
        return ApiResponse.success_response(data=menu_response, message="菜单创建成功")
        
    except Exception as e:
        logger.error(f"Unexpected error creating menu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建菜单失败"
        )


@router.get("/tree", response_model=ApiResponse[List[MenuTreeNode]], summary="获取菜单树")
async def get_menu_tree(
    db: Session = Depends(get_db)
):
    """
    获取完整的菜单树结构
    """
    try:
        menu_service = MenuService(db)
        tree_data = menu_service.get_menu_tree()
        
        # 转换为响应格式
        def convert_to_tree_node(node_data):
            children = node_data.get("children") or []
            return MenuTreeNode(
                menu_id=node_data.get("menu_id"),
                parent_id=node_data.get("parent_id"),
                menu_name=node_data.get("menu_name"),
                path=node_data.get("path"),
                component=node_data.get("component"),
                perms=node_data.get("perms"),
                icon=node_data.get("icon"),
                menu_type=node_data.get("type"),
                order_num=node_data.get("order_num"),
                children=[convert_to_tree_node(child) for child in children]
            )
        
        tree_nodes = [convert_to_tree_node(node) for node in (tree_data or [])]
        
        return ApiResponse.success_response(data=tree_nodes, message="获取菜单树成功")
        
    except Exception as e:
        logger.error(f"Error getting menu tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取菜单树失败"
        )


@router.get("/{menu_id}", response_model=ApiResponse[MenuResponse], summary="获取菜单详情")
async def get_menu(
    menu_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取菜单详情
    
    - **menu_id**: 菜单ID
    """
    try:
        menu_service = MenuService(db)
        menu = menu_service.get_menu_by_id(menu_id)
        
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        
        menu_response = MenuResponse(
            menu_id=menu.menu_id,
            parent_id=menu.parent_id,
            menu_name=menu.menu_name,
            path=menu.PATH,
            component=menu.COMPONENT,
            perms=menu.perms,
            icon=menu.icon,
            menu_type=menu.TYPE,
            order_num=menu.order_num,
            create_time=menu.create_time,
            modify_time=menu.modify_time
        )
        
        return ApiResponse.success_response(data=menu_response, message="获取菜单详情成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取菜单详情失败"
        )


@router.put("/{menu_id}", response_model=ApiResponse[MenuResponse], summary="更新菜单")
async def update_menu(
    menu_id: int,
    request: MenuUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新菜单信息
    
    - **menu_id**: 菜单ID
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
            menu_id=menu_id,
            menu_name=request.menu_name,
            path=request.path,
            component=request.component,
            perms=request.perms,
            icon=request.icon,
            order_num=request.order_num
        )
        
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        
        menu_response = MenuResponse(
            menu_id=menu.menu_id,
            parent_id=menu.parent_id,
            menu_name=menu.menu_name,
            path=menu.PATH,
            component=menu.COMPONENT,
            perms=menu.perms,
            icon=menu.icon,
            menu_type=menu.TYPE,
            order_num=menu.order_num,
            create_time=menu.create_time,
            modify_time=menu.modify_time
        )
        
        logger.info(f"Menu updated successfully: {menu_id}")
        return ApiResponse.success_response(data=menu_response, message="菜单更新成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新菜单失败"
        )


@router.delete("/{menu_id}", response_model=ApiResponse[bool], summary="删除菜单")
async def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db)
):
    """
    删除菜单
    
    - **menu_id**: 菜单ID
    """
    try:
        menu_service = MenuService(db)
        success = menu_service.delete_menu(menu_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="菜单不存在"
            )
        
        logger.info(f"Menu deleted successfully: {menu_id}")
        return ApiResponse.success_response(data=True, message="菜单删除成功")
        
    except ValueError as e:
        logger.warning(f"Menu deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting menu {menu_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除菜单失败"
        )


@router.get("/user/{user_id}", response_model=ApiResponse[UserMenuResponse], summary="获取用户菜单")
async def get_user_menus(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户的菜单权限
    
    - **user_id**: 用户ID
    """
    try:
        menu_service = MenuService(db)
        
        # 获取用户菜单
        user_menus = menu_service.get_user_menus(user_id)
        
        # 获取用户权限
        user_permissions = menu_service.get_user_permissions(user_id)
        
        # 转换为树形结构
        menu_dict = {}
        for menu in user_menus:
            menu_dict[menu.menu_id] = MenuTreeNode(
                menu_id=menu.menu_id,
                parent_id=menu.parent_id,
                menu_name=menu.menu_name,
                path=menu.PATH,
                component=menu.COMPONENT,
                perms=menu.perms,
                icon=menu.icon,
                menu_type=menu.TYPE,
                order_num=menu.order_num,
                children=[]
            )
        
        # 构建父子关系
        tree = []
        for menu_node in menu_dict.values():
            if menu_node.parent_id == 0:
                tree.append(menu_node)
            else:
                parent = menu_dict.get(menu_node.parent_id)
                if parent:
                    parent.children.append(menu_node)
        
        user_menu_response = UserMenuResponse(
            menus=tree,
            permissions=user_permissions
        )
        
        return ApiResponse.success_response(data=user_menu_response, message="获取用户菜单成功")
        
    except Exception as e:
        logger.error(f"Error getting user menus for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户菜单失败"
        )
