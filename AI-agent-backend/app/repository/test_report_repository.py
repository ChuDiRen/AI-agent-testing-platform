# Copyright (c) 2025 左岚. All rights reserved.
"""
测试报告Repository
处理测试报告相关的数据访问操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.entity.test_report import TestReport, ReportStatus, ReportType
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class TestReportRepository(BaseRepository[TestReport]):
    """测试报告Repository类"""

    def __init__(self, db: Session):
        super().__init__(db, TestReport)

    def find_by_type(self, report_type: str, skip: int = 0, limit: int = 100) -> List[TestReport]:
        """根据类型查找报告"""
        try:
            reports = self.db.query(TestReport).filter(
                and_(TestReport.report_type == report_type, TestReport.is_deleted == 0)
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(reports)} reports of type '{report_type}'")
            return reports
        except Exception as e:
            logger.error(f"Error finding reports by type '{report_type}': {str(e)}")
            raise

    def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[TestReport]:
        """根据状态查找报告"""
        try:
            reports = self.db.query(TestReport).filter(
                and_(TestReport.status == status, TestReport.is_deleted == 0)
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(reports)} reports with status '{status}'")
            return reports
        except Exception as e:
            logger.error(f"Error finding reports by status '{status}': {str(e)}")
            raise

    def search(self, keyword: str = None, report_type: str = None, status: str = None,
               test_case_id: int = None, agent_id: int = None, created_by_id: int = None,
               start_date: datetime = None, end_date: datetime = None,
               skip: int = 0, limit: int = 100) -> tuple[List[TestReport], int]:
        """搜索测试报告"""
        try:
            query = self.db.query(TestReport).filter(TestReport.is_deleted == 0)
            
            # 关键词搜索
            if keyword:
                keyword_filter = or_(
                    TestReport.name.ilike(f'%{keyword}%'),
                    TestReport.description.ilike(f'%{keyword}%'),
                    TestReport.summary.ilike(f'%{keyword}%')
                )
                query = query.filter(keyword_filter)
            
            # 类型筛选
            if report_type:
                query = query.filter(TestReport.report_type == report_type)
            
            # 状态筛选
            if status:
                query = query.filter(TestReport.status == status)
            
            # 测试用例筛选
            if test_case_id:
                query = query.filter(TestReport.test_case_id == test_case_id)
            
            # 代理筛选
            if agent_id:
                query = query.filter(TestReport.agent_id == agent_id)
            
            # 创建者筛选
            if created_by_id:
                query = query.filter(TestReport.created_by_id == created_by_id)
            
            # 时间范围筛选
            if start_date:
                query = query.filter(TestReport.created_at >= start_date)
            if end_date:
                query = query.filter(TestReport.created_at <= end_date)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            reports = query.order_by(desc(TestReport.created_at)).offset(skip).limit(limit).all()
            
            logger.debug(f"Search found {len(reports)} reports (total: {total})")
            return reports, total
            
        except Exception as e:
            logger.error(f"Error searching reports: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """获取测试报告统计信息"""
        try:
            # 基本统计
            total_reports = self.count()
            
            # 按状态统计
            status_counts = {}
            for status in ReportStatus:
                count = self.db.query(func.count(TestReport.id)).filter(
                    and_(TestReport.status == status.value, TestReport.is_deleted == 0)
                ).scalar()
                status_counts[status.value] = count
            
            # 按类型统计
            type_counts = {}
            for report_type in ReportType:
                count = self.db.query(func.count(TestReport.id)).filter(
                    and_(TestReport.report_type == report_type.value, TestReport.is_deleted == 0)
                ).scalar()
                type_counts[report_type.value] = count
            
            # 平均生成时间
            avg_generation_time = self.db.query(func.avg(TestReport.duration)).filter(
                and_(TestReport.duration.isnot(None), TestReport.is_deleted == 0)
            ).scalar() or 0.0
            
            # 总覆盖测试用例数
            total_test_cases_covered = self.db.query(func.sum(TestReport.total_cases)).filter(
                TestReport.is_deleted == 0
            ).scalar() or 0
            
            # 整体通过率
            total_passed = self.db.query(func.sum(TestReport.passed_cases)).filter(
                TestReport.is_deleted == 0
            ).scalar() or 0
            overall_pass_rate = (total_passed / total_test_cases_covered * 100) \
                              if total_test_cases_covered > 0 else 0.0
            
            # 最近报告
            recent_reports = self.db.query(TestReport).filter(
                TestReport.is_deleted == 0
            ).order_by(desc(TestReport.created_at)).limit(5).all()
            
            recent_reports_data = [
                {
                    "id": report.id,
                    "name": report.name,
                    "type": report.report_type,
                    "status": report.status,
                    "pass_rate": report.pass_rate,
                    "created_at": report.created_at.isoformat() if report.created_at else None
                }
                for report in recent_reports
            ]
            
            statistics = {
                "total_reports": total_reports,
                "generating_reports": status_counts.get(ReportStatus.GENERATING.value, 0),
                "completed_reports": status_counts.get(ReportStatus.COMPLETED.value, 0),
                "failed_reports": status_counts.get(ReportStatus.FAILED.value, 0),
                "archived_reports": status_counts.get(ReportStatus.ARCHIVED.value, 0),
                "reports_by_type": type_counts,
                "reports_by_status": status_counts,
                "avg_generation_time": round(avg_generation_time, 2),
                "total_test_cases_covered": total_test_cases_covered,
                "overall_pass_rate": round(overall_pass_rate, 2),
                "recent_reports": recent_reports_data
            }
            
            logger.debug("Generated test report statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting test report statistics: {str(e)}")
            raise