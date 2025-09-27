# Copyright (c) 2025 左岚. All rights reserved.
"""
API端点Controller
处理API端点管理相关的HTTP请求
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.utils.permissions import require_permission
from app.entity.user import User
from app.service.api_endpoint_service import ApiEndpointService
from app.dto.api_endpoint_dto import (
    ApiEndpointCreateRequest,
    ApiEndpointUpdateRequest,
    ApiEndpointQueryRequest,
    ApiEndpointResponse,
    ApiEndpointListResponse,
    ApiStatisticsResponse
)
from app.dto.base import ApiResponse
from app.utils.exceptions import BusinessException

# 创建路由器
router = APIRouter(prefix="/api/v1/api-endpoints", tags=["API端点管理"])


@router.post("/", response_model=ApiResponse[ApiEndpointResponse])
@require_permission("api:create")
async def create_api_endpoint(
    request: ApiEndpointCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建API端点
    
    需要权限: api:create
    """
    try:
        service = ApiEndpointService(db)
        api_endpoint = service.create_api_endpoint(request, current_user.id)
        
        return ApiResponse(
            success=True,
            message="API端点创建成功",
            data=api_endpoint
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建API端点失败: {str(e)}"
        )


@router.put("/{api_id}", response_model=ApiResponse[ApiEndpointResponse])
@require_permission("api:update")
async def update_api_endpoint(
    api_id: int,
    request: ApiEndpointUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新API端点
    
    需要权限: api:update
    """
    try:
        service = ApiEndpointService(db)
        api_endpoint = service.update_api_endpoint(api_id, request)
        
        return ApiResponse(
            success=True,
            message="API端点更新成功",
            data=api_endpoint
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新API端点失败: {str(e)}"
        )


@router.delete("/{api_id}", response_model=ApiResponse[bool])
@require_permission("api:delete")
async def delete_api_endpoint(
    api_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除API端点
    
    需要权限: api:delete
    """
    try:
        service = ApiEndpointService(db)
        result = service.delete_api_endpoint(api_id)
        
        return ApiResponse(
            success=True,
            message="API端点删除成功",
            data=result
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除API端点失败: {str(e)}"
        )


@router.get("/{api_id}", response_model=ApiResponse[ApiEndpointResponse])
@require_permission("api:view")
async def get_api_endpoint(
    api_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取API端点详情
    
    需要权限: api:view
    """
    try:
        service = ApiEndpointService(db)
        api_endpoint = service.get_api_endpoint(api_id)
        
        return ApiResponse(
            success=True,
            message="获取API端点成功",
            data=api_endpoint
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取API端点失败: {str(e)}"
        )


@router.get("/", response_model=ApiResponse[ApiEndpointListResponse])
@require_permission("api:view")
async def get_api_endpoints(
    page: int = 1,
    size: int = 10,
    keyword: str = None,
    method: str = None,
    status: str = None,
    module: str = None,
    permission: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取API端点列表
    
    需要权限: api:view
    """
    try:
        request = ApiEndpointQueryRequest(
            page=page,
            size=size,
            keyword=keyword,
            method=method,
            status=status,
            module=module,
            permission=permission
        )
        
        service = ApiEndpointService(db)
        result = service.get_api_endpoints(request)
        
        return ApiResponse(
            success=True,
            message="获取API端点列表成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取API端点列表失败: {str(e)}"
        )


@router.get("/statistics/overview", response_model=ApiResponse[ApiStatisticsResponse])
@require_permission("api:view")
async def get_api_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取API统计数据
    
    需要权限: api:view
    """
    try:
        service = ApiEndpointService(db)
        statistics = service.get_api_statistics()
        
        return ApiResponse(
            success=True,
            message="获取API统计数据成功",
            data=statistics
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取API统计数据失败: {str(e)}"
        )


@router.get("/metadata/modules", response_model=ApiResponse[List[str]])
@require_permission("api:view")
async def get_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有模块列表
    
    需要权限: api:view
    """
    try:
        service = ApiEndpointService(db)
        modules = service.get_modules()
        
        return ApiResponse(
            success=True,
            message="获取模块列表成功",
            data=modules
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模块列表失败: {str(e)}"
        )


@router.get("/metadata/permissions", response_model=ApiResponse[List[str]])
@require_permission("api:view")
async def get_permissions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有权限列表
    
    需要权限: api:view
    """
    try:
        service = ApiEndpointService(db)
        permissions = service.get_permissions()
        
        return ApiResponse(
            success=True,
            message="获取权限列表成功",
            data=permissions
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取权限列表失败: {str(e)}"
        )


@router.get("/metadata/methods", response_model=ApiResponse[List[str]])
@require_permission("api:view")
async def get_methods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有HTTP方法列表
    
    需要权限: api:view
    """
    try:
        service = ApiEndpointService(db)
        methods = service.get_methods()
        
        return ApiResponse(
            success=True,
            message="获取HTTP方法列表成功",
            data=methods
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取HTTP方法列表失败: {str(e)}"
        )


@router.post("/batch/status", response_model=ApiResponse[int])
@require_permission("api:update")
async def batch_update_status(
    api_ids: List[int],
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量更新API状态

    需要权限: api:update
    """
    try:
        service = ApiEndpointService(db)
        updated_count = service.batch_update_status(api_ids, status)

        return ApiResponse(
            success=True,
            message=f"批量更新成功，共更新{updated_count}个API端点",
            data=updated_count
        )
    except BusinessException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量更新失败: {str(e)}"
        )


@router.post("/sync", response_model=ApiResponse[Dict[str, Any]])
@require_permission("api:create")
async def sync_api_endpoints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    从路由同步API端点

    需要权限: api:create
    """
    try:
        service = ApiEndpointService(db)
        result = service.sync_api_endpoints_from_routes(current_user.id)

        return ApiResponse(
            success=True,
            message="API端点同步完成",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步API端点失败: {str(e)}"
        )
