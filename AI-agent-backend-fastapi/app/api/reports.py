# Copyright (c) 2025 左岚. All rights reserved.
"""测试报告API路由"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import io

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.report_service import ReportService
from app.services.report_exporter import report_exporter
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


@router.get("/{report_id}/export/{format}")
async def export_report_file(
    report_id: int,
    format: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    导出测试报告为文件
    
    Args:
        report_id: 报告ID
        format: 导出格式 (pdf/excel)
    
    Returns:
        文件流
    """
    # 验证格式
    if format not in ['pdf', 'excel']:
        raise HTTPException(status_code=400, detail="不支持的导出格式，仅支持pdf和excel")
    
    # 获取报告详情
    service = ReportService(db)
    report = await service.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="测试报告不存在")
    
    # 获取报告的执行记录
    executions = await service.get_report_executions(report_id)
    
    # 构建导出数据
    export_data = {
        "report_id": report.report_id,
        "report_name": report.report_name,
        "test_type": report.report_type,
        "total_cases": report.total_cases,
        "passed_cases": report.passed_cases,
        "failed_cases": report.failed_cases,
        "skipped_cases": report.total_cases - report.passed_cases - report.failed_cases,
        "pass_rate": report.pass_rate,
        "duration": report.duration or 0,
        "start_time": report.start_time.strftime("%Y-%m-%d %H:%M:%S") if report.start_time else "N/A",
        "end_time": report.end_time.strftime("%Y-%m-%d %H:%M:%S") if report.end_time else "N/A",
        "test_results": [
            {
                "testcase_name": exec.testcase.name if exec.testcase else "N/A",
                "status": exec.status,
                "duration": exec.duration or 0,
                "executed_at": exec.executed_at.strftime("%Y-%m-%d %H:%M:%S") if exec.executed_at else "N/A",
                "error_message": exec.error_message or ""
            }
            for exec in executions
        ]
    }
    
    try:
        # 导出为对应格式
        if format == 'pdf':
            file_bytes = report_exporter.export_to_pdf(export_data)
            media_type = "application/pdf"
            filename = f"test_report_{report_id}.pdf"
        else:  # excel
            file_bytes = report_exporter.export_to_excel(export_data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"test_report_{report_id}.xlsx"
        
        # 返回文件流
        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出功能不可用: {str(e)}。请安装所需的依赖库。"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )

