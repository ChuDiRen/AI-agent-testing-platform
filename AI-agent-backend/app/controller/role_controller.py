# Copyright (c) 2025 左岚. All rights reserved.
"""
角色Controller
处理角色相关的HTTP请求
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse, Success, Fail
from app.dto.role_dto import (
    RoleCreateRequest,
    RoleUpdateRequest,
    RoleResponse,
    RoleListResponse,
    RoleMenuAssignRequest,
    RolePermissionResponse,
    RoleIdRequest,
    RoleListRequest,
    RoleDeleteRequest
)
from app.service.role_service import RoleService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.post("/create-role", response_model=ApiResponse[RoleResponse], summary="创建角色")
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
            role_id=role.role_id,
            role_name=role.role_name,
            remark=role.remark,
            create_time=role.create_time,
            modify_time=role.modify_time
        )
        
        logger.info(f"Role created successfully: {role.role_name}")
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


@router.post("/get-role-list", response_model=ApiResponse[RoleListResponse], summary="获取角色列表")
async def get_role_list(
    request: RoleListRequest,
    db: Session = Depends(get_db)
):
    """
    获取角色列表（支持分页和搜索）

    - **page**: 页码（从1开始）
    - **size**: 每页大小（1-100）
    - **keyword**: 关键词搜索
    """
    try:
        role_service = RoleService(db)
        result = role_service.get_roles_with_pagination(page=request.page, size=request.size)
        
        # 转换为字典格式
        roles = [
            {
                "role_id": role_data["role_id"],
                "role_name": role_data["role_name"],
                "remark": role_data["remark"],
                "create_time": role_data["create_time"].isoformat() if hasattr(role_data["create_time"], 'isoformat') and role_data["create_time"] else role_data["create_time"],
                "modify_time": role_data["modify_time"].isoformat() if hasattr(role_data["modify_time"], 'isoformat') and role_data["modify_time"] else role_data["modify_time"]
            }
            for role_data in result["roles"]
        ]

        response_data = {
            "roles": roles,
            "total": result["total"],
            "page": result["page"],
            "size": result["size"],
            "pages": result["pages"]
        }

        return Success(code=200, msg="获取角色列表成功", data=response_data)
        
    except Exception as e:
        logger.error(f"Error getting roles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色列表失败"
        )


@router.post("/get-role-info", response_model=ApiResponse[RoleResponse], summary="获取角色详情")
async def get_role_info(
    request: RoleIdRequest,
    db: Session = Depends(get_db)
):
    """
    根据ID获取角色详情

    - **role_id**: 角色ID（请求体传参）
    """
    try:
        role_service = RoleService(db)
        role = role_service.get_role_by_id(request.role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        role_response = RoleResponse(
            role_id=role.role_id,
            role_name=role.role_name,
            remark=role.remark,
            create_time=role.create_time,
            modify_time=role.modify_time
        )
        
        return ApiResponse.success_response(data=role_response, message="获取角色详情成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role {request.role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色详情失败"
        )


@router.post("/update-role", response_model=ApiResponse[RoleResponse], summary="更新角色")
async def update_role(
    request: RoleUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新角色信息

    - **role_id**: 角色ID（请求体传参）
    - **role_name**: 新的角色名称（可选）
    - **remark**: 新的角色描述（可选）
    """
    try:
        role_service = RoleService(db)
        role = role_service.update_role(
            role_id=request.role_id,
            role_name=request.role_name,
            remark=request.remark
        )
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        role_response = RoleResponse(
            role_id=role.role_id,
            role_name=role.role_name,
            remark=role.remark,
            create_time=role.create_time,
            modify_time=role.modify_time
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
        logger.error(f"Unexpected error updating role {request.role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色失败"
        )


@router.post("/delete-role", response_model=ApiResponse[bool], summary="删除角色")
async def delete_role(
    request: RoleDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    删除角色

    - **role_id**: 角色ID（请求体传参）
    """
    try:
        role_service = RoleService(db)
        success = role_service.delete_role(request.role_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        logger.info(f"Role deleted successfully: {request.role_id}")
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
        logger.error(f"Unexpected error deleting role {request.role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除角色失败"
        )


@router.post("/assign-role-menus", response_model=ApiResponse[bool], summary="分配菜单权限")
async def assign_role_menus(
    request: RoleMenuAssignRequest,
    db: Session = Depends(get_db)
):
    """
    为角色分配菜单权限

    - **role_id**: 角色ID（请求体传参）
    - **menu_ids**: 菜单ID列表
    """
    try:
        role_service = RoleService(db)
        success = role_service.assign_menus_to_role(request.role_id, request.menu_ids)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        logger.info(f"Menus assigned to role successfully: {request.role_id}")
        return ApiResponse.success_response(data=True, message="菜单权限分配成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning menus to role {request.role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="分配菜单权限失败"
        )


@router.post("/get-role-permissions", response_model=ApiResponse[RolePermissionResponse], summary="获取角色权限")
async def get_role_permissions(
    request: RoleIdRequest,
    db: Session = Depends(get_db)
):
    """
    获取角色的权限信息

    - **role_id**: 角色ID（请求体传参）
    """
    try:
        role_service = RoleService(db)
        role = role_service.get_role_by_id(request.role_id)
        
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="角色不存在"
            )
        
        permissions = role_service.get_role_permissions(request.role_id)
        menu_ids = role_service.get_role_menu_ids(request.role_id)

        permission_response = RolePermissionResponse(
            role_id=role.role_id,
            role_name=role.role_name,
            permissions=permissions,
            menu_ids=menu_ids
        )

        return ApiResponse.success_response(data=permission_response, message="获取角色权限成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting role permissions {request.role_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取角色权限失败"
        )
