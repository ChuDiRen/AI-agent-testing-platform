# Copyright (c) 2025 左岚. All rights reserved.
"""测试报告API路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.report_service import ReportService
from app.schemas.report import (
    TestReportCreate, TestReportUpdate, TestReportResponse, TestReportDetail,
    TestReportStatistics, TestExecutionResponse, ReportGenerateRequest, ReportExportRequest
)
from app.schemas.common import APIResponse
from app.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter()


@router.post("/", response_model=APIResponse[TestReportResponse])
async def create_report(
    report_data: TestReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestReportResponse]:
    """创建测试报告"""
    service = ReportService(db)
    report = await service.create_report(report_data, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="测试报告创建成功",
        data=TestReportResponse.model_validate(report)
    )


@router.get("/", response_model=APIResponse[PaginatedResponse[TestReportResponse]])
async def get_reports(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    report_type: Optional[str] = Query(None, description="报告类型"),
    status: Optional[str] = Query(None, description="状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PaginatedResponse[TestReportResponse]]:
    """获取测试报告列表"""
    service = ReportService(db)
    pagination = PaginationParams(page=page, page_size=page_size)
    
    reports, total = await service.get_reports_paginated(
        pagination=pagination,
        keyword=keyword,
        report_type=report_type,
        status=status
    )
    
    paginated_data = PaginatedResponse.create(
        items=[TestReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size
    )
    
    return APIResponse(
        success=True,
        data=paginated_data
    )


@router.get("/statistics", response_model=APIResponse[TestReportStatistics])
async def get_statistics(
    report_type: Optional[str] = Query(None, description="报告类型"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestReportStatistics]:
    """获取统计信息"""
    service = ReportService(db)
    stats = await service.get_statistics(report_type=report_type)
    
    return APIResponse(
        success=True,
        data=stats
    )


@router.get("/{report_id}", response_model=APIResponse[TestReportDetail])
async def get_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestReportDetail]:
    """获取测试报告详情"""
    service = ReportService(db)
    report = await service.get_report(report_id)
    
    if not report:
        return APIResponse(
            success=False,
            message="测试报告不存在"
        )
    
    return APIResponse(
        success=True,
        data=TestReportDetail.model_validate(report)
    )


@router.put("/{report_id}", response_model=APIResponse[TestReportResponse])
async def update_report(
    report_id: int,
    report_data: TestReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestReportResponse]:
    """更新测试报告"""
    service = ReportService(db)
    
    report = await service.update_report(report_id, report_data)
    if not report:
        return APIResponse(
            success=False,
            message="测试报告不存在"
        )
    
    return APIResponse(
        success=True,
        message="测试报告更新成功",
        data=TestReportResponse.model_validate(report)
    )


@router.delete("/{report_id}", response_model=APIResponse[None])
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除测试报告"""
    service = ReportService(db)
    success = await service.delete_report(report_id)
    
    if not success:
        return APIResponse(
            success=False,
            message="测试报告不存在"
        )
    
    return APIResponse(
        success=True,
        message="测试报告删除成功"
    )


@router.post("/generate", response_model=APIResponse[TestReportResponse])
async def generate_report(
    request: ReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[TestReportResponse]:
    """生成测试报告"""
    service = ReportService(db)
    report = await service.generate_report(request, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="测试报告生成成功",
        data=TestReportResponse.model_validate(report)
    )


@router.get("/{report_id}/executions", response_model=APIResponse[list[TestExecutionResponse]])
async def get_report_executions(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[list[TestExecutionResponse]]:
    """获取报告的执行记录"""
    service = ReportService(db)
    executions = await service.get_report_executions(report_id)
    
    return APIResponse(
        success=True,
        data=[TestExecutionResponse.model_validate(e) for e in executions]
    )


@router.post("/export", response_model=APIResponse[dict])
async def export_report(
    request: ReportExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[dict]:
    """导出测试报告"""
    service = ReportService(db)
    file_path = await service.export_report(request.report_id, request.format)
    
    if not file_path:
        return APIResponse(
            success=False,
            message="测试报告不存在"
        )
    
    return APIResponse(
        success=True,
        message="报告导出成功",
        data={
            "file_path": file_path,
            "format": request.format
        }
    )

