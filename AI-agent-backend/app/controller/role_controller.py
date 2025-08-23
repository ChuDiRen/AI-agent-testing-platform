# Copyright (c) 2025 左岚. All rights reserved.
"""
角色Controller
处理角色相关的HTTP请求
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse
from app.dto.role_dto import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleResponse,
    RoleListResponse,
    RoleMenuAssignRequest,
    RolePermissionResponse
)
from app.service.role_service import RoleService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("/", response_model=ApiResponse[RoleResponse], summary="创建角色")
async def create_role(
    request: RoleCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建新角色
    
    - **role_name**: 角色名称（必填，最大10个字符）
    - **remark**: 角色描述（可选，最大100个字符）
    """
    try:
        role_service = RoleService(db)
        role = role_service.create_role(
            role_name=request.role_name,
            remark=request.remark
        )
        
        # 转换为响应格式
        role_response = RoleResponse(
            role_id=role.ROLE_ID,
            role_name=role.ROLE_NAME,
            remark=role.REMARK,
            create_time=role.CREATE_TIME,
            modify_time=role.MODIFY_TIME
        )
        
        logger.info(f"Role created successfully: {role.ROLE_NAME}")
        return ApiResponse.success_response(data=role_response, message="角色创建成功")
        
    except ValueError as e:
        logger.warning(f"Role creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建角色失败"
        )


@router.get("/", response_model=ApiResponse[RoleListResponse], summary="获取角色列表")
async def get_roles(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db)
):
    """
    分页获取角色列表
    
    - **page**: 页码（从1开始）
    - **size**: 每页大小（1-100）
    """
    try:
        role_service = RoleService(db)
        result = role_service.get_roles_with_pagination(page=page, size=size)
        
        # 转换为响应格式
        roles = [
            RoleResponse(
                role_id=role_data["role_id"],
                role_name=role_data["role_name"],
                remark=role_data["remark"],
                create_time=role_data["create_time"],
                modify_time=role_data["modify_time"]
            )
            for role_data in result["roles"]
        ]
        
        role_list_response = RoleListResponse(
            roles=roles,
            total=result["total"],
            page=result["page"],
            size=result["size"],
            pages=result["pages"]
        )
        
        return ApiResponse.success_response(data=role_list_response, message="获取角色列表成功")
        
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色列表失败"
        )


@router.get("/{role_id}", response_model=ApiResponse[RoleResponse], summary="获取角色详情")
async def get_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    根据ID获取角色详情
    
    - **role_id**: 角色ID
    """
    try:
        role_service = RoleService(db)
        role = role_service.get_role_by_id(role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        role_response = RoleResponse(
            role_id=role.ROLE_ID,
            role_name=role.ROLE_NAME,
            remark=role.REMARK,
            create_time=role.CREATE_TIME,
            modify_time=role.MODIFY_TIME
        )
        
        return ApiResponse.success_response(data=role_response, message="获取角色详情成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色详情失败"
        )


@router.put("/{role_id}", response_model=ApiResponse[RoleResponse], summary="更新角色")
async def update_role(
    role_id: int,
    request: RoleUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新角色信息
    
    - **role_id**: 角色ID
    - **role_name**: 新的角色名称（可选）
    - **remark**: 新的角色描述（可选）
    """
    try:
        role_service = RoleService(db)
        role = role_service.update_role(
            role_id=role_id,
            role_name=request.role_name,
            remark=request.remark
        )
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        role_response = RoleResponse(
            role_id=role.ROLE_ID,
            role_name=role.ROLE_NAME,
            remark=role.REMARK,
            create_time=role.CREATE_TIME,
            modify_time=role.MODIFY_TIME
        )
        
        logger.info(f"Role updated successfully: {role_id}")
        return ApiResponse.success_response(data=role_response, message="角色更新成功")
        
    except ValueError as e:
        logger.warning(f"Role update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating role {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败"
        )


@router.delete("/{role_id}", response_model=ApiResponse[bool], summary="删除角色")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    删除角色
    
    - **role_id**: 角色ID
    """
    try:
        role_service = RoleService(db)
        success = role_service.delete_role(role_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        logger.info(f"Role deleted successfully: {role_id}")
        return ApiResponse.success_response(data=True, message="角色删除成功")
        
    except ValueError as e:
        logger.warning(f"Role deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting role {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )


@router.post("/{role_id}/menus", response_model=ApiResponse[bool], summary="分配菜单权限")
async def assign_menus_to_role(
    role_id: int,
    request: RoleMenuAssignRequest,
    db: Session = Depends(get_db)
):
    """
    为角色分配菜单权限
    
    - **role_id**: 角色ID
    - **menu_ids**: 菜单ID列表
    """
    try:
        role_service = RoleService(db)
        success = role_service.assign_menus_to_role(role_id, request.menu_ids)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        logger.info(f"Menus assigned to role successfully: {role_id}")
        return ApiResponse.success_response(data=True, message="菜单权限分配成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning menus to role {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配菜单权限失败"
        )


@router.get("/{role_id}/permissions", response_model=ApiResponse[RolePermissionResponse], summary="获取角色权限")
async def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    获取角色的权限信息
    
    - **role_id**: 角色ID
    """
    try:
        role_service = RoleService(db)
        role = role_service.get_role_by_id(role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        permissions = role_service.get_role_permissions(role_id)
        menu_ids = role_service.get_role_menu_ids(role_id)
        
        permission_response = RolePermissionResponse(
            role_id=role.ROLE_ID,
            role_name=role.ROLE_NAME,
            permissions=permissions,
            menu_ids=menu_ids
        )
        
        return ApiResponse.success_response(data=permission_response, message="获取角色权限成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role permissions {role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色权限失败"
        )
