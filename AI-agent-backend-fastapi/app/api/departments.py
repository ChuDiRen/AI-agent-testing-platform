"""部门管理路由 - 对应 t_dept 表"""
from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.common import APIResponse
from app.services.department_service import DepartmentService
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/departments", tags=["部门管理"])


@router.post("/", response_model=APIResponse[DepartmentResponse], status_code=status.HTTP_201_CREATED)
async def create_department(
    dept_data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[DepartmentResponse]:
    """
    创建部门
    
    - **parent_id**: 上级部门ID，顶级部门为0
    - **dept_name**: 部门名称
    - **order_num**: 排序号
    """
    dept_service = DepartmentService(db)
    dept = await dept_service.create_department(dept_data)
    
    return APIResponse(
        message="部门创建成功",
        data=DepartmentResponse.model_validate(dept)
    )


@router.get("/", response_model=APIResponse[List[DepartmentResponse]])
async def get_departments(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=100, description="限制数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[DepartmentResponse]]:
    """获取部门列表"""
    dept_service = DepartmentService(db)
    depts = await dept_service.get_all_departments(skip=skip, limit=limit)
    
    return APIResponse(
        data=[DepartmentResponse.model_validate(dept) for dept in depts]
    )


@router.get("/{dept_id}", response_model=APIResponse[DepartmentResponse])
async def get_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[DepartmentResponse]:
    """获取部门详情"""
    dept_service = DepartmentService(db)
    dept = await dept_service.get_department_by_id(dept_id)
    
    return APIResponse(
        data=DepartmentResponse.model_validate(dept)
    )


@router.put("/{dept_id}", response_model=APIResponse[DepartmentResponse])
async def update_department(
    dept_id: int,
    dept_data: DepartmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[DepartmentResponse]:
    """更新部门"""
    dept_service = DepartmentService(db)
    dept = await dept_service.update_department(dept_id, dept_data)
    
    return APIResponse(
        message="部门更新成功",
        data=DepartmentResponse.model_validate(dept)
    )


@router.delete("/{dept_id}")
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除部门"""
    dept_service = DepartmentService(db)
    await dept_service.delete_department(dept_id)
    
    return APIResponse(message="部门删除成功")

