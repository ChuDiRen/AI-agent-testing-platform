# Copyright (c) 2025 左岚. All rights reserved.
"""测试报告服务"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
import json

from app.models.report import TestReport, TestExecution
from app.models.testcase import TestCase
from app.schemas.report import (
    TestReportCreate, TestReportUpdate, TestReportStatistics,
    TestExecutionCreate, TestExecutionUpdate, ReportGenerateRequest
)
from app.schemas.pagination import PaginationParams


class ReportService:
    """测试报告服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_report(self, report_data: TestReportCreate, created_by_id: int) -> TestReport:
        """创建测试报告"""
        report = TestReport(
            **report_data.model_dump(),
            created_by_id=created_by_id,
            status="generating"
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report
    
    async def get_report(self, report_id: int) -> Optional[TestReport]:
        """获取测试报告"""
        result = await self.db.execute(
            select(TestReport).where(TestReport.report_id == report_id)
        )
        return result.scalar_one_or_none()
    
    async def get_reports_paginated(
        self,
        pagination: PaginationParams,
        keyword: Optional[str] = None,
        report_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Tuple[List[TestReport], int]:
        """分页获取测试报告列表"""
        # 构建查询
        query = select(TestReport)
        count_query = select(func.count(TestReport.report_id))
        
        # 添加过滤条件
        conditions = []
        if keyword:
            conditions.append(
                or_(
                    TestReport.name.like(f"%{keyword}%"),
                    TestReport.description.like(f"%{keyword}%")
                )
            )
        if report_type:
            conditions.append(TestReport.report_type == report_type)
        if status:
            conditions.append(TestReport.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # 排序
        query = query.order_by(TestReport.created_at.desc())
        
        # 分页
        query = query.offset((pagination.page - 1) * pagination.page_size).limit(pagination.page_size)
        
        # 执行查询
        result = await self.db.execute(query)
        reports = result.scalars().all()
        
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        return list(reports), total
    
    async def update_report(self, report_id: int, report_data: TestReportUpdate) -> Optional[TestReport]:
        """更新测试报告"""
        report = await self.get_report(report_id)
        if not report:
            return None
        
        update_data = report_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(report, key, value)
        
        await self.db.commit()
        await self.db.refresh(report)
        return report
    
    async def delete_report(self, report_id: int) -> bool:
        """删除测试报告"""
        report = await self.get_report(report_id)
        if not report:
            return False
        
        await self.db.delete(report)
        await self.db.commit()
        return True
    
    async def get_statistics(self, report_type: Optional[str] = None) -> TestReportStatistics:
        """获取统计信息"""
        # 基础查询
        query = select(TestReport)
        if report_type:
            query = query.where(TestReport.report_type == report_type)
        
        result = await self.db.execute(query)
        reports = result.scalars().all()
        
        # 统计数据
        total_reports = len(reports)
        generating_reports = sum(1 for r in reports if r.status == "generating")
        completed_reports = sum(1 for r in reports if r.status == "completed")
        failed_reports = sum(1 for r in reports if r.status == "failed")
        
        # 计算平均通过率
        completed = [r for r in reports if r.status == "completed"]
        average_pass_rate = sum(r.pass_rate for r in completed) / len(completed) if completed else 0.0
        
        # 测试用例统计
        total_test_cases = sum(r.total_cases for r in reports)
        passed_test_cases = sum(r.passed_cases for r in reports)
        failed_test_cases = sum(r.failed_cases for r in reports)
        
        return TestReportStatistics(
            total_reports=total_reports,
            generating_reports=generating_reports,
            completed_reports=completed_reports,
            failed_reports=failed_reports,
            average_pass_rate=round(average_pass_rate, 2),
            total_test_cases=total_test_cases,
            passed_test_cases=passed_test_cases,
            failed_test_cases=failed_test_cases
        )
    
    async def generate_report(self, request: ReportGenerateRequest, created_by_id: int) -> TestReport:
        """生成测试报告"""
        # 创建报告
        report = TestReport(
            name=request.name,
            description=request.description,
            report_type=request.report_type,
            created_by_id=created_by_id,
            status="generating",
            start_time=datetime.now(),
            total_cases=len(request.testcase_ids)
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        
        # 创建执行记录
        executions = []
        for testcase_id in request.testcase_ids:
            execution = TestExecution(
                report_id=report.report_id,
                testcase_id=testcase_id,
                status="pending",
                environment=request.environment
            )
            executions.append(execution)
            self.db.add(execution)
        
        await self.db.commit()
        
        # 模拟执行测试用例
        await self._execute_testcases(report, executions, request.config)
        
        return report
    
    async def _execute_testcases(
        self, 
        report: TestReport, 
        executions: List[TestExecution],
        config: Optional[Dict[str, Any]] = None
    ):
        """执行测试用例（模拟）"""
        import random
        
        passed = 0
        failed = 0
        skipped = 0
        
        for execution in executions:
            # 模拟执行
            execution.status = "running"
            execution.start_time = datetime.now()
            await self.db.commit()
            
            # 随机生成结果（80%通过率）
            result = random.choices(
                ["passed", "failed", "skipped"],
                weights=[0.8, 0.15, 0.05]
            )[0]
            
            execution.status = result
            execution.end_time = datetime.now()
            execution.duration = random.uniform(0.5, 5.0)
            
            if result == "passed":
                passed += 1
                execution.actual_result = "测试通过"
            elif result == "failed":
                failed += 1
                execution.actual_result = "测试失败"
                execution.error_message = "断言失败: 预期结果与实际结果不符"
            else:
                skipped += 1
                execution.actual_result = "测试跳过"
            
            await self.db.commit()
        
        # 更新报告统计
        report.status = "completed"
        report.end_time = datetime.now()
        report.duration = (report.end_time - report.start_time).total_seconds()
        report.passed_cases = passed
        report.failed_cases = failed
        report.skipped_cases = skipped
        report.executed_cases = passed + failed + skipped
        report.remaining_cases = report.total_cases - report.executed_cases
        report.pass_rate = round((passed / report.total_cases * 100) if report.total_cases > 0 else 0, 2)
        report.execution_rate = round((report.executed_cases / report.total_cases * 100) if report.total_cases > 0 else 0, 2)
        
        # 生成报告摘要
        report.summary = f"共执行 {report.total_cases} 个测试用例，通过 {passed} 个，失败 {failed} 个，跳过 {skipped} 个。通过率: {report.pass_rate}%"
        
        await self.db.commit()
    
    async def get_report_executions(self, report_id: int) -> List[TestExecution]:
        """获取报告的执行记录"""
        result = await self.db.execute(
            select(TestExecution)
            .where(TestExecution.report_id == report_id)
            .order_by(TestExecution.created_at)
        )
        return list(result.scalars().all())
    
    async def export_report(self, report_id: int, format: str = "excel") -> Optional[str]:
        """导出报告"""
        report = await self.get_report(report_id)
        if not report:
            return None
        
        # 这里返回模拟的文件路径，实际应该生成真实的Excel/PDF文件
        file_path = f"exports/report_{report_id}.{format}"
        report.file_path = file_path
        await self.db.commit()
        
        return file_path

