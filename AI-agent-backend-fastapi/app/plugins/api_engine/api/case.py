# Copyright (c) 2025 左岚. All rights reserved.
"""
用例API路由
"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse

from ..services.case_service import CaseService
from ..schemas.case import CaseCreate, CaseUpdate, CaseResponse, CaseListResponse

router = APIRouter()


@router.post("/", response_model=APIResponse[CaseResponse])
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建测试用例"""
    service = CaseService(db)
    case = await service.create_case(case_data, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="用例创建成功",
        data=CaseResponse.model_validate(case)
    )


@router.get("/", response_model=APIResponse[CaseListResponse])
async def get_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    suite_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用例列表"""
    service = CaseService(db)
    cases, total = await service.get_cases(page, page_size, suite_id, keyword, status)
    
    return APIResponse(
        success=True,
        data=CaseListResponse(
            total=total,
            items=[CaseResponse.model_validate(c) for c in cases]
        )
    )


@router.get("/{case_id}", response_model=APIResponse[CaseResponse])
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取用例详情"""
    service = CaseService(db)
    case = await service.get_case(case_id)
    
    if not case:
        return APIResponse(success=False, message="用例不存在")
    
    return APIResponse(
        success=True,
        data=CaseResponse.model_validate(case)
    )


@router.put("/{case_id}", response_model=APIResponse[CaseResponse])
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新用例"""
    service = CaseService(db)
    case = await service.update_case(case_id, case_data)
    
    if not case:
        return APIResponse(success=False, message="用例不存在")
    
    return APIResponse(
        success=True,
        message="用例更新成功",
        data=CaseResponse.model_validate(case)
    )


@router.delete("/{case_id}", response_model=APIResponse[None])
async def delete_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除用例"""
    service = CaseService(db)
    success = await service.delete_case(case_id)
    
    if not success:
        return APIResponse(success=False, message="用例不存在")
    
    return APIResponse(success=True, message="用例删除成功")


@router.post("/{case_id}/clone", response_model=APIResponse[CaseResponse])
async def clone_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """克隆用例"""
    service = CaseService(db)
    case = await service.clone_case(case_id, current_user.user_id)
    
    if not case:
        return APIResponse(success=False, message="原用例不存在")
    
    return APIResponse(
        success=True,
        message="用例克隆成功",
        data=CaseResponse.model_validate(case)
    )


@router.post("/import", response_model=APIResponse[CaseResponse])
async def import_case(
    suite_id: int = Body(...),
    yaml_content: str = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """从YAML导入用例"""
    service = CaseService(db)
    case = await service.import_from_yaml(suite_id, yaml_content, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="用例导入成功",
        data=CaseResponse.model_validate(case)
    )

