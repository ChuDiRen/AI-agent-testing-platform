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
from app.dto.base import ApiResponse, Success, Fail
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
from app.utils.log_decorators import log_operation, log_user_action

logger = get_logger(__name__)

# 创建路由器
router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.post("/create-department", response_model=ApiResponse[DepartmentResponse], summary="创建部门")
@log_operation(
    operation_type="CREATE",
    resource_type="DEPARTMENT",
    operation_desc="创建部门",
    include_request=True
)
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
        
        # 转换为字典格式
        dept_dict = {
            "dept_id": department.id,
            "parent_id": department.parent_id,
            "dept_name": department.dept_name,
            "order_num": department.order_num,
            "create_time": department.create_time.isoformat() if department.create_time else None,
            "modify_time": department.modify_time.isoformat() if department.modify_time else None
        }

        logger.info(f"Department created successfully: {department.dept_name}")
        return Success(code=200, msg="部门创建成功", data=dept_dict)
        
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
@log_operation(
    operation_type="VIEW",
    resource_type="DEPARTMENT",
    operation_desc="获取部门树"
)
async def get_department_tree(
    request: dict = {},
    db: Session = Depends(get_db)
):
    """
    获取完整的部门树结构
    """
    try:
        department_service = DepartmentService(db)
        keyword = request.get('keyword', '').strip() if request.get('keyword') else None
        tree_data = department_service.get_department_tree(keyword=keyword)

        # 直接返回字典格式的树形数据
        return Success(code=200, msg="获取部门树成功", data=tree_data or [])

    except Exception as e:
        logger.error(f"Error getting department tree: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门树失败"
        )


@router.post("/get-department-list", response_model=ApiResponse[DepartmentListResponse], summary="获取部门列表")
@log_operation(
    operation_type="VIEW",
    resource_type="DEPARTMENT",
    operation_desc="获取部门列表"
)
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

        # 获取所有部门
        departments = department_service.get_all_departments()

        # 转换为字典格式
        dept_list = [
            {
                "dept_id": dept.id,
                "parent_id": dept.parent_id,
                "dept_name": dept.dept_name,
                "order_num": dept.order_num,
                "create_time": dept.create_time.isoformat() if dept.create_time else None,
                "modify_time": dept.modify_time.isoformat() if dept.modify_time else None
            }
            for dept in departments
        ]

        return Success(code=200, msg="获取部门列表成功", data=dept_list)
        
    except Exception as e:
        logger.error(f"Error getting departments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门列表失败"
        )


@router.post("/get-department-info", response_model=ApiResponse[DepartmentResponse], summary="获取部门详情")
@log_operation(
    operation_type="VIEW",
    resource_type="DEPARTMENT",
    operation_desc="获取部门详情",
    include_request=True
)
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
        
        # 转换为字典格式
        dept_dict = {
            "dept_id": department.id,
            "parent_id": department.parent_id,
            "dept_name": department.dept_name,
            "order_num": department.order_num,
            "create_time": department.create_time.isoformat() if department.create_time else None,
            "modify_time": department.modify_time.isoformat() if department.modify_time else None
        }

        return Success(code=200, msg="获取部门详情成功", data=dept_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting department {request.dept_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门详情失败"
        )


@router.post("/update-department", response_model=ApiResponse[DepartmentResponse], summary="更新部门")
@log_operation(
    operation_type="UPDATE",
    resource_type="DEPARTMENT",
    operation_desc="更新部门",
    include_request=True
)
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
        
        # 转换为字典格式
        dept_dict = {
            "dept_id": department.id,
            "parent_id": department.parent_id,
            "dept_name": department.dept_name,
            "order_num": department.order_num,
            "create_time": department.create_time.isoformat() if department.create_time else None,
            "modify_time": department.modify_time.isoformat() if department.modify_time else None
        }

        logger.info(f"Department updated successfully: {request.dept_id}")
        return Success(code=200, msg="部门更新成功", data=dept_dict)
        
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
@log_operation(
    operation_type="DELETE",
    resource_type="DEPARTMENT",
    operation_desc="删除部门",
    include_request=True
)
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
        return Success(code=200, msg="部门删除成功", data=True)

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
        
        has_children = department_service.has_children(request.dept_id)
        has_users = department_service.has_users(request.dept_id)
        can_delete = department_service.can_delete(request.dept_id)

        # 转换为字典格式
        status_dict = {
            "dept_id": department.id,
            "dept_name": department.dept_name,
            "has_children": has_children,
            "has_users": has_users,
            "can_delete": can_delete
        }

        return Success(code=200, msg="获取部门状态成功", data=status_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting department status {request.dept_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取部门状态失败"
        )
