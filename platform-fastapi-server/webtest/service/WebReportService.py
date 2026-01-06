"""
Web测试报告Service层
按照ApiTest标准实现
"""
import json
import uuid
import os
from datetime import datetime, timedelta
from typing import Tuple, List, Optional, Dict, Any

from core.logger import get_logger
from sqlmodel import Session, select, and_, or_, func

from ..model.WebReportModel import WebReport, WebReportTemplate, WebReportStatus, WebReportFormat
from ..schemas.WebReportSchema import (
    WebReportQuery, WebReportCreate, WebReportUpdate, 
    WebReportResponse, WebReportTemplateResponse, WebReportGenerateRequest,
    WebReportStatistics
)

logger = get_logger(__name__)


class WebReportService:
    """Web测试报告服务类 - 使用静态方法模式"""
    
    @staticmethod
    def generate_report_id() -> str:
        """生成报告ID"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        return f"report_{date_str}_{uuid.uuid4().hex[:6]}"
    
    @staticmethod
    def query_by_page(session: Session, query: WebReportQuery) -> Tuple[List[WebReport], int]:
        """分页查询报告"""
        offset = (query.page - 1) * query.pageSize
        statement = select(WebReport)
        
        # 应用过滤条件
        if query.execution_id:
            statement = statement.where(WebReport.execution_id == query.execution_id)
        if query.project_id:
            statement = statement.where(WebReport.project_id == query.project_id)
        if query.status:
            statement = statement.where(WebReport.status == query.status)
        if query.format:
            statement = statement.where(WebReport.format == query.format)
        if query.start_date:
            statement = statement.where(WebReport.generate_time >= query.start_date)
        if query.end_date:
            statement = statement.where(WebReport.generate_time <= query.end_date)
        
        # 排序
        statement = statement.order_by(WebReport.generate_time.desc())
        
        # 分页
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(count_statement).one()
        
        return list(datas), total
    
    @staticmethod
    def query_by_id(session: Session, report_id: str) -> Optional[WebReport]:
        """根据ID查询报告"""
        return session.get(WebReport, report_id)
    
    @staticmethod
    def query_by_execution_id(session: Session, execution_id: str) -> Optional[WebReport]:
        """根据执行ID查询报告"""
        statement = select(WebReport).where(WebReport.execution_id == execution_id)
        return session.exec(statement).first()
    
    @staticmethod
    def create(session: Session, report_data: WebReportCreate) -> WebReport:
        """创建报告记录"""
        try:
            report_id = WebReportService.generate_report_id()
            
            # 转换字典字段为JSON
            summary_json = json.dumps(report_data.summary_data or {}, ensure_ascii=False)
            detail_json = json.dumps(report_data.detail_data or {}, ensure_ascii=False)
            chart_json = json.dumps(report_data.chart_data or {}, ensure_ascii=False)
            
            report = WebReport(
                id=report_id,
                execution_id=report_data.execution_id,
                project_id=report_data.project_id,
                project_name=report_data.project_name,
                report_name=report_data.report_name,
                status=WebReportStatus.GENERATING,
                format=report_data.format,
                summary_data=summary_json,
                detail_data=detail_json,
                chart_data=chart_json,
                error_summary=report_data.error_summary,
                generate_time=datetime.now()
            )
            
            session.add(report)
            session.commit()
            session.refresh(report)
            logger.info(f"创建Web报告成功，ID: {report.id}")
            return report
        except Exception as e:
            session.rollback()
            logger.error(f"创建Web报告失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update(session: Session, report_id: str, report_data: WebReportUpdate) -> bool:
        """更新报告记录"""
        try:
            report = session.get(WebReport, report_id)
            if not report:
                return False
            
            # 更新字段
            update_data = report_data.dict(exclude_unset=True, exclude={'id'})
            
            for field, value in update_data.items():
                if value is not None:
                    setattr(report, field, value)
            
            report.update_time = datetime.now()
            session.commit()
            logger.info(f"更新Web报告成功，ID: {report_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"更新Web报告失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def delete(session: Session, report_id: str) -> bool:
        """删除报告记录"""
        try:
            report = session.get(WebReport, report_id)
            if not report:
                return False
            
            # 删除文件
            if report.file_path and os.path.exists(report.file_path):
                try:
                    os.remove(report.file_path)
                    logger.info(f"删除报告文件: {report.file_path}")
                except Exception as e:
                    logger.warning(f"删除报告文件失败: {e}")
            
            # 删除数据库记录
            session.delete(report)
            session.commit()
            logger.info(f"删除Web报告成功，ID: {report_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除Web报告失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def batch_delete(session: Session, report_ids: List[str]) -> int:
        """批量删除报告记录"""
        try:
            count = 0
            for report_id in report_ids:
                if WebReportService.delete(session, report_id):
                    count += 1
            logger.info(f"批量删除Web报告成功，删除数量: {count}")
            return count
        except Exception as e:
            logger.error(f"批量删除Web报告失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def generate_report(session: Session, request: WebReportGenerateRequest) -> WebReport:
        """生成报告"""
        try:
            # 检查是否已存在相同执行ID的报告
            existing_report = WebReportService.query_by_execution_id(session, request.execution_id)
            if existing_report:
                logger.warning(f"执行ID {request.execution_id} 已存在报告，返回现有报告")
                return existing_report
            
            # 获取执行历史数据
            from .WebHistoryService import WebHistoryService
            history = WebHistoryService.query_by_id(session, request.execution_id)
            if not history:
                raise ValueError(f"执行记录不存在: {request.execution_id}")
            
            # 获取用例详情
            cases = WebHistoryService.query_cases_by_execution(session, request.execution_id)
            
            # 构建报告数据
            summary_data = {
                "id": history.id,
                "project_name": history.project_name,
                "start_time": history.start_time.isoformat(),
                "duration": history.duration,
                "executor": history.executor,
                "total": history.total,
                "passed": history.passed,
                "failed": history.failed,
                "skipped": 0,
                "pass_rate": history.pass_rate,
                "env": history.env,
                "browsers": json.loads(history.browsers) if history.browsers else [],
                "threads": history.threads
            }
            
            # 构建详细用例数据
            detail_data = {
                "cases": []
            }
            
            for case in cases:
                case_data = {
                    "name": case.case_name,
                    "status": case.status,
                    "duration": case.duration,
                    "browser": "chromium",  # 默认浏览器
                    "screenshot": bool(case.screenshot_path),
                    "error": case.error_message,
                    "steps": json.loads(case.step_results) if case.step_results else []
                }
                detail_data["cases"].append(case_data)
            
            # 构建图表数据
            chart_data = {
                "status_chart": {
                    "passed": history.passed,
                    "failed": history.failed,
                    "skipped": 0
                },
                "browser_chart": {
                    "chromium": history.total  # 简化处理
                },
                "duration_chart": {
                    "total": history.duration,
                    "avg": history.duration / max(history.total, 1)
                }
            }
            
            # 创建报告记录
            report_create = WebReportCreate(
                execution_id=request.execution_id,
                project_id=history.project_id,
                project_name=history.project_name,
                report_name=f"{history.project_name} - {history.start_time.strftime('%Y%m%d_%H%M%S')}报告",
                format=request.format,
                summary_data=summary_data,
                detail_data=detail_data,
                chart_data=chart_data
            )
            
            report = WebReportService.create(session, report_create)
            
            # 异步生成报告文件
            # 这里应该启动后台任务来生成实际的报告文件
            # 暂时标记为完成状态
            WebReportService.update(session, report.id, WebReportUpdate(
                id=report.id,
                status=WebReportStatus.COMPLETED,
                view_url=f"/reports/web/{report.id}.html",
                allure_url=f"/allure-report/{request.execution_id}/index.html"
            ))
            
            return report
        except Exception as e:
            logger.error(f"生成报告失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_download_url(session: Session, report_id: str) -> Optional[str]:
        """获取下载链接"""
        try:
            report = WebReportService.query_by_id(session, report_id)
            if not report or report.status != WebReportStatus.COMPLETED:
                return None
            
            if report.download_url:
                return report.download_url
            
            # 生成下载链接
            download_url = f"/api/web/report/download/{report_id}"
            WebReportService.update(session, report_id, WebReportUpdate(
                id=report_id,
                download_url=download_url
            ))
            
            return download_url
        except Exception as e:
            logger.error(f"获取下载链接失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_statistics(session: Session, project_id: Optional[int] = None, days: int = 30) -> WebReportStatistics:
        """获取报告统计信息"""
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 基础查询条件
            base_condition = and_(WebReport.generate_time >= start_time, WebReport.generate_time <= end_time)
            if project_id:
                base_condition = and_(base_condition, WebReport.project_id == project_id)
            
            # 总报告数
            total_statement = select(func.count()).select_from(WebReport).where(base_condition)
            total_reports = session.exec(total_statement).one()
            
            # 按状态统计
            completed_statement = select(func.count()).where(and_(base_condition, WebReport.status == WebReportStatus.COMPLETED))
            completed_reports = session.exec(completed_statement).one()
            
            generating_statement = select(func.count()).where(and_(base_condition, WebReport.status == WebReportStatus.GENERATING))
            generating_reports = session.exec(generating_statement).one()
            
            failed_statement = select(func.count()).where(and_(base_condition, WebReport.status == WebReportStatus.FAILED))
            failed_reports = session.exec(failed_statement).one()
            
            # 按格式统计
            format_stats = {}
            for fmt in WebReportFormat:
                format_statement = select(func.count()).where(and_(base_condition, WebReport.format == fmt.value))
                count = session.exec(format_statement).one()
                if count > 0:
                    format_stats[fmt.value] = count
            
            # 平均文件大小
            avg_size_statement = select(func.avg(WebReport.file_size)).where(and_(base_condition, WebReport.file_size.is_not(None)))
            avg_file_size = session.exec(avg_size_statement).one() or 0
            
            # 最新报告
            latest_statement = select(WebReport).where(base_condition).order_by(WebReport.generate_time.desc()).limit(1)
            latest_report = session.exec(latest_statement).first()
            
            return WebReportStatistics(
                total_reports=total_reports,
                completed_reports=completed_reports,
                generating_reports=generating_reports,
                failed_reports=failed_reports,
                format_stats=format_stats,
                avg_file_size=round(avg_file_size / 1024, 2),  # 转换为KB
                latest_report=latest_report
            )
        except Exception as e:
            logger.error(f"获取报告统计信息失败: {e}", exc_info=True)
            return WebReportStatistics(
                total_reports=0,
                completed_reports=0,
                generating_reports=0,
                failed_reports=0,
                format_stats={},
                avg_file_size=0.0
            )
    
    @staticmethod
    def query_templates(session: Session, active_only: bool = True) -> List[WebReportTemplate]:
        """查询报告模板"""
        try:
            statement = select(WebReportTemplate)
            if active_only:
                statement = statement.where(WebReportTemplate.is_active == True)
            statement = statement.order_by(WebReportTemplate.is_default.desc(), WebReportTemplate.name)
            
            return session.exec(statement).all()
        except Exception as e:
            logger.error(f"查询报告模板失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_default_template(session: Session, format_type: WebReportFormat) -> Optional[WebReportTemplate]:
        """获取默认模板"""
        try:
            statement = select(WebReportTemplate).where(
                and_(WebReportTemplate.template_type == format_type, WebReportTemplate.is_default == True)
            )
            return session.exec(statement).first()
        except Exception as e:
            logger.error(f"获取默认模板失败: {e}", exc_info=True)
            return None
