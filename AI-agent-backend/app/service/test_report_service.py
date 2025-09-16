# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告服务
处理测试报告相关的业务逻辑
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.entity.test_report import TestReport, ReportStatus, ReportType
from app.dto.test_report_dto import (
    TestReportCreateRequest, TestReportUpdateRequest, TestReportSearchRequest,
    TestReportResponse, TestReportListResponse, TestReportStatisticsResponse
)
from app.utils.exceptions import BusinessException

logger = logging.getLogger(__name__)


class TestReportService:
    """测试报告服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_report(self, request: TestReportCreateRequest, created_by_id: int) -> TestReportResponse:
        """创建测试报告"""
        try:
            # 创建测试报告实体
            test_report = TestReport(
                name=request.name,
                description=request.description,
                report_type=request.report_type.value,
                test_case_id=request.test_case_id,
                agent_id=request.agent_id,
                created_by_id=created_by_id,
                extra_data=request.metadata or {}
            )

            self.db.add(test_report)
            self.db.commit()
            self.db.refresh(test_report)

            logger.info(f"Created test report: {test_report.id}")
            return self._convert_to_response(test_report)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating test report: {str(e)}")
            raise BusinessException(f"创建测试报告失败: {str(e)}")

    def get_report_list(self, request: TestReportSearchRequest) -> TestReportListResponse:
        """获取测试报告列表"""
        try:
            # 构建查询条件
            query = self.db.query(TestReport)

            # 应用筛选条件
            if request.keyword:
                query = query.filter(
                    or_(
                        TestReport.name.contains(request.keyword),
                        TestReport.description.contains(request.keyword)
                    )
                )

            if request.report_type:
                query = query.filter(TestReport.report_type == request.report_type.value)

            if request.status:
                query = query.filter(TestReport.status == request.status.value)

            if request.test_case_id:
                query = query.filter(TestReport.test_case_id == request.test_case_id)

            if request.agent_id:
                query = query.filter(TestReport.agent_id == request.agent_id)

            if request.created_by_id:
                query = query.filter(TestReport.created_by_id == request.created_by_id)

            if request.start_date:
                query = query.filter(TestReport.created_at >= request.start_date)

            if request.end_date:
                query = query.filter(TestReport.created_at <= request.end_date)

            # 获取总数
            total = query.count()

            # 排序和分页
            query = query.order_by(TestReport.created_at.desc())
            offset = (request.page - 1) * request.page_size
            reports = query.offset(offset).limit(request.page_size).all()

            # 转换为响应对象
            report_responses = [self._convert_to_response(report) for report in reports]

            return TestReportListResponse(
                reports=report_responses,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=(total + request.page_size - 1) // request.page_size
            )

        except Exception as e:
            logger.error(f"Error getting report list: {str(e)}")
            raise BusinessException(f"获取测试报告列表失败: {str(e)}")

    def get_statistics(self) -> TestReportStatisticsResponse:
        """获取测试报告统计信息"""
        try:
            # 基础统计
            total_reports = self.db.query(TestReport).count()
            generating_reports = self.db.query(TestReport).filter(
                TestReport.status == ReportStatus.GENERATING.value
            ).count()
            completed_reports = self.db.query(TestReport).filter(
                TestReport.status == ReportStatus.COMPLETED.value
            ).count()
            failed_reports = self.db.query(TestReport).filter(
                TestReport.status == ReportStatus.FAILED.value
            ).count()
            archived_reports = self.db.query(TestReport).filter(
                TestReport.status == ReportStatus.ARCHIVED.value
            ).count()

            # 按类型统计
            reports_by_type = {}
            for report_type in ReportType:
                count = self.db.query(TestReport).filter(
                    TestReport.report_type == report_type.value
                ).count()
                reports_by_type[report_type.value] = count

            # 按状态统计
            reports_by_status = {
                ReportStatus.GENERATING.value: generating_reports,
                ReportStatus.COMPLETED.value: completed_reports,
                ReportStatus.FAILED.value: failed_reports,
                ReportStatus.ARCHIVED.value: archived_reports
            }

            # 计算平均生成时间
            avg_generation_time = self.db.query(func.avg(TestReport.duration)).filter(
                TestReport.duration.isnot(None)
            ).scalar() or 0.0

            # 计算总覆盖测试用例数和整体通过率
            total_test_cases_covered = self.db.query(func.sum(TestReport.total_cases)).scalar() or 0
            total_passed_cases = self.db.query(func.sum(TestReport.passed_cases)).scalar() or 0
            overall_pass_rate = (total_passed_cases / total_test_cases_covered * 100) if total_test_cases_covered > 0 else 0.0

            # 获取最近报告
            recent_reports_query = self.db.query(TestReport).order_by(
                TestReport.created_at.desc()
            ).limit(5)
            recent_reports = []
            for report in recent_reports_query:
                recent_reports.append({
                    "id": report.id,
                    "name": report.name,
                    "status": report.status,
                    "pass_rate": report.pass_rate,
                    "created_at": report.created_at.isoformat() if report.created_at else ""
                })

            return TestReportStatisticsResponse(
                total_reports=total_reports,
                generating_reports=generating_reports,
                completed_reports=completed_reports,
                failed_reports=failed_reports,
                archived_reports=archived_reports,
                reports_by_type=reports_by_type,
                reports_by_status=reports_by_status,
                avg_generation_time=avg_generation_time,
                total_test_cases_covered=total_test_cases_covered,
                overall_pass_rate=round(overall_pass_rate, 2),
                recent_reports=recent_reports
            )

        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            raise BusinessException(f"获取统计信息失败: {str(e)}")

    def _convert_to_response(self, test_report: TestReport) -> TestReportResponse:
        """转换为响应对象"""
        return TestReportResponse(
            id=test_report.id,
            name=test_report.name,
            description=test_report.description,
            report_type=test_report.report_type,
            status=test_report.status,
            test_case_id=test_report.test_case_id,
            agent_id=test_report.agent_id,
            created_by_id=test_report.created_by_id,
            start_time=test_report.start_time,
            end_time=test_report.end_time,
            duration=test_report.duration,
            total_cases=test_report.total_cases,
            passed_cases=test_report.passed_cases,
            failed_cases=test_report.failed_cases,
            skipped_cases=test_report.skipped_cases,
            blocked_cases=test_report.blocked_cases,
            executed_cases=test_report.get_executed_cases(),
            remaining_cases=test_report.get_remaining_cases(),
            pass_rate=test_report.pass_rate,
            execution_rate=test_report.get_execution_rate(),
            content=test_report.content,
            file_path=test_report.file_path,
            summary=test_report.summary,
            issues=test_report.issues,
            metadata=test_report.extra_data or {},
            created_at=test_report.created_at,
            updated_at=test_report.updated_at
        )
