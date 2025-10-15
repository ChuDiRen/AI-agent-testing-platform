"""
测试报告模块API
提供测试报告的CRUD和导出功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
import json

from app.utils.permissions import get_current_user
from app.db.session import get_db
from app.dto.base_dto import Success, Fail
from app.entity.user import User
from app.service.test_report_service import TestReportService
from app.utils.log_decorators import log_user_action

router = APIRouter()


@router.get("/", summary="获取测试报告列表")
@log_user_action(action="查看", resource_type="测试报告管理", description="查看报告列表")
async def get_test_report_list(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="报告名称关键词"),
    test_type: Optional[str] = Query(None, description="测试类型"),
    status: Optional[str] = Query(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试报告列表（分页）"""
    try:
        from app.dto.test_report_dto import TestReportSearchRequest
        
        report_service = TestReportService(db)

        # 使用 TestReportSearchRequest 构建搜索请求
        search_request = TestReportSearchRequest(
            keyword=keyword,
            report_type=test_type,  # API 参数名是 test_type，但 DTO 字段名是 report_type
            status=status,
            page=page,
            page_size=page_size
        )

        # 获取报告列表
        result = report_service.get_report_list(search_request)

        # 构建响应数据
        report_list = []
        for report in result.reports:
            # 计算通过率
            total_cases = report.total_cases or 0
            passed_cases = report.passed_cases or 0
            pass_rate = round((passed_cases / total_cases) * 100, 2) if total_cases > 0 else 0

            report_data = {
                "id": report.id,
                "name": report.name,
                "report_type": report.report_type,  # 正确的字段名
                "status": report.status,
                "total_cases": total_cases,
                "passed_cases": passed_cases,
                "failed_cases": report.failed_cases or 0,
                "skipped_cases": report.skipped_cases or 0,
                "pass_rate": pass_rate,
                "description": report.description or "",
                "created_at": report.created_at.strftime("%Y-%m-%d %H:%M:%S") if report.created_at else "",
                "updated_at": report.updated_at.strftime("%Y-%m-%d %H:%M:%S") if report.updated_at else ""
            }
            report_list.append(report_data)

        response_data = {
            "items": report_list,
            "total": result.total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"获取报告列表失败: {str(e)}")


@router.get("/{report_id}", summary="获取单个报告详情")
@log_user_action(action="查看", resource_type="测试报告管理", description="查看报告详情")
async def get_test_report_detail(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个测试报告的详细信息"""
    try:
        report_service = TestReportService(db)
        report = await report_service.get_report_by_id(report_id)

        if not report:
            return Fail(msg="测试报告不存在")

        # 计算通过率
        total_cases = report.total_cases or 0
        passed_cases = report.passed_cases or 0
        pass_rate = round((passed_cases / total_cases) * 100, 2) if total_cases > 0 else 0

        report_data = {
            "id": report.id,
            "name": report.name,
            "test_type": report.test_type,
            "status": report.status,
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": report.failed_cases or 0,
            "skipped_cases": report.skipped_cases or 0,
            "pass_rate": pass_rate,
            "description": report.description or "",
            "test_results": report.test_results or [],
            "execution_time": report.execution_time,
            "created_at": report.create_time.strftime("%Y-%m-%d %H:%M:%S") if report.create_time else "",
            "updated_at": report.update_time.strftime("%Y-%m-%d %H:%M:%S") if report.update_time else ""
        }

        return Success(data=report_data)

    except Exception as e:
        return Fail(msg=f"获取报告详情失败: {str(e)}")


@router.post("/", summary="创建测试报告")
@log_user_action(action="新建", resource_type="测试报告管理", description="新建测试报告")
async def create_test_report(
    name: str = Body(..., description="报告名称"),
    test_type: str = Body(..., description="测试类型"),
    description: Optional[str] = Body(None, description="报告描述"),
    total_cases: int = Body(0, description="总用例数"),
    passed_cases: int = Body(0, description="通过用例数"),
    failed_cases: int = Body(0, description="失败用例数"),
    skipped_cases: int = Body(0, description="跳过用例数"),
    test_results: Optional[List] = Body(default=[], description="测试结果详情"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新的测试报告"""
    try:
        report_service = TestReportService(db)

        # 创建测试报告
        new_report = await report_service.create_report(
            name=name,
            test_type=test_type,
            description=description,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            skipped_cases=skipped_cases,
            test_results=test_results,
            created_by=current_user.id
        )

        return Success(data={"id": new_report.id}, msg="创建成功")

    except Exception as e:
        return Fail(msg=f"创建测试报告失败: {str(e)}")


@router.put("/{report_id}", summary="更新测试报告")
@log_user_action(action="编辑", resource_type="测试报告管理", description="编辑测试报告")
async def update_test_report(
    report_id: int,
    name: Optional[str] = Body(None, description="报告名称"),
    test_type: Optional[str] = Body(None, description="测试类型"),
    description: Optional[str] = Body(None, description="报告描述"),
    total_cases: Optional[int] = Body(None, description="总用例数"),
    passed_cases: Optional[int] = Body(None, description="通过用例数"),
    failed_cases: Optional[int] = Body(None, description="失败用例数"),
    skipped_cases: Optional[int] = Body(None, description="跳过用例数"),
    test_results: Optional[List] = Body(None, description="测试结果详情"),
    status: Optional[str] = Body(None, description="状态"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新测试报告信息"""
    try:
        report_service = TestReportService(db)

        # 检查测试报告是否存在
        report = await report_service.get_report_by_id(report_id)
        if not report:
            return Fail(msg="测试报告不存在")

        # 更新测试报告
        await report_service.update_report(
            report_id=report_id,
            name=name,
            test_type=test_type,
            description=description,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            skipped_cases=skipped_cases,
            test_results=test_results,
            status=status,
            updated_by=current_user.id
        )

        return Success(msg="更新成功")

    except Exception as e:
        return Fail(msg=f"更新测试报告失败: {str(e)}")


@router.delete("/{report_id}", summary="删除测试报告")
@log_user_action(action="删除", resource_type="测试报告管理", description="删除测试报告")
async def delete_test_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除测试报告"""
    try:
        report_service = TestReportService(db)

        # 检查测试报告是否存在
        report = await report_service.get_report_by_id(report_id)
        if not report:
            return Fail(msg="测试报告不存在")

        # 删除测试报告
        await report_service.delete_report(report_id)

        return Success(msg="删除成功")

    except Exception as e:
        return Fail(msg=f"删除测试报告失败: {str(e)}")


@router.get("/{report_id}/export", summary="导出测试报告")
@log_user_action(action="导出", resource_type="测试报告管理", description="导出测试报告")
async def export_test_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出测试报告为PDF文件"""
    try:
        report_service = TestReportService(db)

        # 获取报告详情
        report = await report_service.get_report_by_id(report_id)
        if not report:
            return Fail(msg="测试报告不存在")

        # 创建PDF内容
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []

        # 样式
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        normal_style = styles['Normal']

        # 标题
        story.append(Paragraph(f"测试报告：{report.name}", title_style))
        story.append(Spacer(1, 20))

        # 基本信息
        basic_info = [
            ["报告名称", report.name],
            ["测试类型", report.test_type],
            ["状态", report.status],
            ["创建时间", report.create_time.strftime("%Y-%m-%d %H:%M:%S") if report.create_time else ""],
            ["描述", report.description or ""]
        ]

        basic_table = Table(basic_info, colWidths=[100, 300])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        story.append(basic_table)
        story.append(Spacer(1, 20))

        # 统计信息
        total_cases = report.total_cases or 0
        passed_cases = report.passed_cases or 0
        failed_cases = report.failed_cases or 0
        skipped_cases = report.skipped_cases or 0
        pass_rate = round((passed_cases / total_cases) * 100, 2) if total_cases > 0 else 0

        stats_info = [
            ["统计项", "数量", "百分比"],
            ["总用例数", str(total_cases), "100%"],
            ["通过用例", str(passed_cases), f"{pass_rate}%"],
            ["失败用例", str(failed_cases), f"{round((failed_cases / total_cases) * 100, 2)}%" if total_cases > 0 else "0%"],
            ["跳过用例", str(skipped_cases), f"{round((skipped_cases / total_cases) * 100, 2)}%" if total_cases > 0 else "0%"]
        ]

        stats_table = Table(stats_info, colWidths=[150, 100, 100])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(Paragraph("测试统计", styles['Heading2']))
        story.append(Spacer(1, 10))
        story.append(stats_table)
        story.append(Spacer(1, 20))

        # 测试结果详情（如果有）
        if report.test_results:
            story.append(Paragraph("测试结果详情", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            # 简化的测试结果展示
            results_data = [["用例名称", "状态", "执行时间"]]
            for result in report.test_results[:20]:  # 限制显示数量
                if isinstance(result, dict):
                    results_data.append([
                        result.get('name', 'N/A'),
                        result.get('status', 'N/A'),
                        result.get('execution_time', 'N/A')
                    ])

            if len(results_data) > 1:
                results_table = Table(results_data, colWidths=[200, 80, 100])
                results_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                story.append(results_table)

        # 生成PDF
        doc.build(story)
        buffer.seek(0)

        # 返回文件流
        return StreamingResponse(
            io.BytesIO(buffer.read()),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=test_report_{report_id}.pdf"}
        )

    except Exception as e:
        return Fail(msg=f"导出报告失败: {str(e)}")


@router.post("/search", summary="搜索测试报告")
@log_user_action(action="搜索", resource_type="测试报告管理", description="搜索测试报告")
async def search_test_reports(
    keyword: Optional[str] = Body(None, description="关键词"),
    test_type: Optional[str] = Body(None, description="测试类型"),
    status: Optional[str] = Body(None, description="状态"),
    page: int = Body(1, description="页码"),
    page_size: int = Body(20, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """搜索测试报告"""
    try:
        report_service = TestReportService(db)

        # 构建搜索条件
        filters = {}
        if keyword:
            filters['keyword'] = keyword
        if test_type:
            filters['test_type'] = test_type
        if status:
            filters['status'] = status

        # 执行搜索
        reports, total = await report_service.search_reports(
            filters=filters,
            page=page,
            page_size=page_size
        )

        # 构建响应数据
        report_list = []
        for report in reports:
            # 计算通过率
            total_cases = report.total_cases or 0
            passed_cases = report.passed_cases or 0
            pass_rate = round((passed_cases / total_cases) * 100, 2) if total_cases > 0 else 0

            report_data = {
                "id": report.id,
                "name": report.name,
                "test_type": report.test_type,
                "status": report.status,
                "total_cases": total_cases,
                "passed_cases": passed_cases,
                "failed_cases": report.failed_cases or 0,
                "skipped_cases": report.skipped_cases or 0,
                "pass_rate": pass_rate,
                "description": report.description or "",
                "created_at": report.create_time.strftime("%Y-%m-%d %H:%M:%S") if report.create_time else "",
                "updated_at": report.update_time.strftime("%Y-%m-%d %H:%M:%S") if report.update_time else ""
            }
            report_list.append(report_data)

        response_data = {
            "items": report_list,
            "total": total
        }
        return Success(data=response_data)

    except Exception as e:
        return Fail(msg=f"搜索测试报告失败: {str(e)}")


@router.get("/statistics/overview", summary="获取报告统计概览")
@log_user_action(action="查看", resource_type="测试报告管理", description="查看报告统计")
async def get_report_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取测试报告统计概览"""
    try:
        report_service = TestReportService(db)
        
        # 获取统计数据
        statistics = await report_service.get_report_statistics()
        
        return Success(data=statistics)

    except Exception as e:
        return Fail(msg=f"获取统计数据失败: {str(e)}")
