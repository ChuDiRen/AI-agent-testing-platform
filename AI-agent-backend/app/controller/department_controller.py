# Copyright (c) 2025 左岚. All rights reserved.
"""
部门Controller
处理部门相关的HTTP请求
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.db.session import get_db
from app.dto.base import ApiResponse
from app.dto.department_dto import (
    DepartmentCreateRequest,
    DepartmentUpdateRequest,
    DepartmentResponse,
    DepartmentTreeNode,
    DepartmentListResponse,
    DepartmentStatusResponse,
    DepartmentIdRequest,
    DepartmentListRequest,
    DepartmentDeleteRequest
)
from app.service.department_service import DepartmentService

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.post("/create-department", response_model=ApiResponse[DepartmentResponse], summary="创建部门")
async def create_department(
    request: DepartmentCreateRequest,
    db: Session = Depends(get_db)
):
    """
    创建新部门
    
    - **parent_id**: 上级部门ID，0表示顶级部门
    - **dept_name**: 部门名称
    - **order_num**: 排序号（可选）
    """
    try:
        department_service = DepartmentService(db)
        department = department_service.create_department(
            parent_id=request.parent_id,
            dept_name=request.dept_name,
            order_num=request.order_num
        )
        
        # 转换为响应格式
        dept_response = DepartmentResponse(
            dept_id=department.id,  # 修复：使用正确的属性名
            parent_id=department.parent_id,
            dept_name=department.dept_name,
            order_num=department.order_num,
            create_time=department.create_time,
            modify_time=department.modify_time
        )
        
        logger.info(f"Department created successfully: {department.dept_name}")
        return ApiResponse.success_response(data=dept_response, message="部门创建成功")
        
    except ValueError as e:
        logger.warning(f"Department creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error creating department: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建部门失败"
        )


@router.post("/get-department-tree", response_model=ApiResponse[List[DepartmentTreeNode]], summary="获取部门树")
async def get_department_tree(
    db: Session = Depends(get_db)
):
    """
    获取完整的部门树结构
    """
    try:
        department_service = DepartmentService(db)
        tree_data = department_service.get_department_tree()
        
        # 转换为响应格式
        def convert_to_tree_node(node_data):
            children = node_data.get("children") or []
            return DepartmentTreeNode(
                dept_id=node_data.get("dept_id"),
                parent_id=node_data.get("parent_id"),
                dept_name=node_data.get("dept_name"),
                order_num=node_data.get("order_num"),
                create_time=node_data.get("create_time"),
                modify_time=node_data.get("modify_time"),
                children=[convert_to_tree_node(child) for child in children]
            )
        
        tree_nodes = [convert_to_tree_node(node) for node in (tree_data or [])]
        return ApiResponse.success_response(data=tree_nodes, message="获取部门树成功")
        
    except Exception as e:
        logger.error(f"Error getting department tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门树失败"
        )


@router.post("/get-department-list", response_model=ApiResponse[DepartmentListResponse], summary="获取部门列表")
async def get_department_list(
    request: DepartmentListRequest = None,
    db: Session = Depends(get_db)
):
    """
    获取部门列表（支持分页和筛选）

    - **page**: 页码（可选）
    - **size**: 每页大小（可选）
    - **dept_name**: 部门名称筛选（可选）
    """
    try:
        department_service = DepartmentService(db)
        departments = department_service.get_all_departments()
        
        # 转换为响应格式
        dept_responses = [
            DepartmentResponse(
                dept_id=dept.id,  # 修复：使用正确的属性名
                parent_id=dept.parent_id,
                dept_name=dept.dept_name,
                order_num=dept.order_num,
                create_time=dept.create_time,
                modify_time=dept.modify_time
            )
            for dept in departments
        ]
        
        dept_list_response = DepartmentListResponse(departments=dept_responses)
        
        return ApiResponse.success_response(data=dept_list_response, message="获取部门列表成功")
        
    except Exception as e:
        logger.error(f"Error getting departments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门列表失败"
        )


@router.post("/get-department-info", response_model=ApiResponse[DepartmentResponse], summary="获取部门详情")
async def get_department_info(
    request: DepartmentIdRequest,
    db: Session = Depends(get_db)
):
    """
    根据ID获取部门详情

    - **dept_id**: 部门ID（请求体传参）
    """
    try:
        department_service = DepartmentService(db)
        department = department_service.get_department_by_id(request.dept_id)
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        dept_response = DepartmentResponse(
            dept_id=department.id,  # 修复：使用正确的属性名
            parent_id=department.parent_id,
            dept_name=department.dept_name,
            order_num=department.order_num,
            create_time=department.create_time,
            modify_time=department.modify_time
        )
        
        return ApiResponse.success_response(data=dept_response, message="获取部门详情成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting department {request.dept_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门详情失败"
        )


@router.post("/update-department", response_model=ApiResponse[DepartmentResponse], summary="更新部门")
async def update_department(
    request: DepartmentUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    更新部门信息

    - **dept_id**: 部门ID（请求体传参）
    - **dept_name**: 新的部门名称（可选）
    - **order_num**: 新的排序号（可选）
    """
    try:
        department_service = DepartmentService(db)
        department = department_service.update_department(
            dept_id=request.dept_id,
            dept_name=request.dept_name,
            order_num=request.order_num
        )
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        dept_response = DepartmentResponse(
            dept_id=department.id,  # 修复：使用正确的属性名
            parent_id=department.parent_id,
            dept_name=department.dept_name,
            order_num=department.order_num,
            create_time=department.create_time,
            modify_time=department.modify_time
        )
        
        logger.info(f"Department updated successfully: {request.dept_id}")
        return ApiResponse.success_response(data=dept_response, message="部门更新成功")
        
    except ValueError as e:
        logger.warning(f"Department update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating department {request.dept_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新部门失败"
        )


@router.post("/delete-department", response_model=ApiResponse[bool], summary="删除部门")
async def delete_department(
    request: DepartmentDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    删除部门

    - **dept_id**: 部门ID（请求体传参）
    """
    try:
        department_service = DepartmentService(db)
        success = department_service.delete_department(request.dept_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        logger.info(f"Department deleted successfully: {request.dept_id}")
        return ApiResponse.success_response(data=True, message="部门删除成功")

    except ValueError as e:
        logger.warning(f"Department deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error deleting department {request.dept_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除部门失败"
        )


@router.post("/status", response_model=ApiResponse[DepartmentStatusResponse], summary="获取部门状态")
async def get_department_status(
    request: DepartmentIdRequest,
    db: Session = Depends(get_db)
):
    """
    获取部门状态信息（是否有子部门、是否有用户、是否可删除）

    - **dept_id**: 部门ID（请求体传参）
    """
    try:
        department_service = DepartmentService(db)
        department = department_service.get_department_by_id(request.dept_id)
        
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        
        has_children = department_service.has_children(dept_id)
        has_users = department_service.has_users(dept_id)
        can_delete = department_service.can_delete(dept_id)
        
        status_response = DepartmentStatusResponse(
            dept_id=department.id,  # 修复：使用正确的属性名
            dept_name=department.dept_name,
            has_children=has_children,
            has_users=has_users,
            can_delete=can_delete
        )
        
        return ApiResponse.success_response(data=status_response, message="获取部门状态成功")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting department status {dept_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门状态失败"
        )
