# Copyright (c) 2025 左岚. All rights reserved.
"""
套件API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse

from ..services.suite_service import SuiteService
from ..schemas.suite import SuiteCreate, SuiteUpdate, SuiteResponse, SuiteListResponse

router = APIRouter()


@router.post("/", response_model=APIResponse[SuiteResponse])
async def create_suite(
    suite_data: SuiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建测试套件"""
    service = SuiteService(db)
    suite = await service.create_suite(suite_data, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="套件创建成功",
        data=SuiteResponse.model_validate(suite)
    )


@router.get("/", response_model=APIResponse[SuiteListResponse])
async def get_suites(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取套件列表"""
    service = SuiteService(db)
    suites, total = await service.get_suites(page, page_size, keyword)
    
    return APIResponse(
        success=True,
        data=SuiteListResponse(
            total=total,
            items=[SuiteResponse.model_validate(s) for s in suites]
        )
    )


@router.get("/{suite_id}", response_model=APIResponse[SuiteResponse])
async def get_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取套件详情"""
    service = SuiteService(db)
    suite = await service.get_suite(suite_id)
    
    if not suite:
        return APIResponse(success=False, message="套件不存在")
    
    return APIResponse(
        success=True,
        data=SuiteResponse.model_validate(suite)
    )


@router.put("/{suite_id}", response_model=APIResponse[SuiteResponse])
async def update_suite(
    suite_id: int,
    suite_data: SuiteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新套件"""
    service = SuiteService(db)
    suite = await service.update_suite(suite_id, suite_data)
    
    if not suite:
        return APIResponse(success=False, message="套件不存在")
    
    return APIResponse(
        success=True,
        message="套件更新成功",
        data=SuiteResponse.model_validate(suite)
    )


@router.delete("/{suite_id}", response_model=APIResponse[None])
async def delete_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除套件"""
    service = SuiteService(db)
    success = await service.delete_suite(suite_id)
    
    if not success:
        return APIResponse(success=False, message="套件不存在")
    
    return APIResponse(success=True, message="套件删除成功")

