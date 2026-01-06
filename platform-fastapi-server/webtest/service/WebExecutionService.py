"""
Web执行Service层 - 按照ApiTest标准实现
"""
import json
import uuid
from datetime import datetime
from typing import Tuple, List, Optional, Dict, Any

from core.logger import get_logger
from sqlmodel import Session, select, func, and_

from ..model.WebExecutionModel import WebExecution, WebExecutionResult
from ..schemas.WebExecutionSchema import (
    WebExecutionRequest, WebExecutionStatus, WebExecutionQuery,
    WebExecutionDetail, WebReportInfo
)

logger = get_logger(__name__)


class WebExecutionService:
    """Web执行服务类 - 使用静态方法模式"""
    
    @staticmethod
    def generate_execution_id() -> str:
        """生成执行ID"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d_%H%M%S")
        return f"exec_{date_str}_{uuid.uuid4().hex[:6]}"
    
    @staticmethod
    def start_execution(session: Session, request: WebExecutionRequest) -> str:
        """启动执行"""
        try:
            execution_id = WebExecutionService.generate_execution_id()
            
            # 创建执行记录
            execution = WebExecution(
                execution_id=execution_id,
                project_id=request.project_id,
                execution_name=request.execution_name,
                execution_type=request.execution_type,
                trigger_type='manual',
                case_ids=json.dumps(request.case_ids),
                total_cases=len(request.case_ids),
                status='pending',
                browser_type=request.browser_type,
                environment=request.environment,
                parallel_count=request.parallel_count,
                retry_count=request.retry_count,
                timeout=request.timeout,
                generate_report=request.generate_report,
                take_screenshot=request.take_screenshot,
                start_time=datetime.now()
            )
            
            session.add(execution)
            session.commit()
            session.refresh(execution)
            logger.info(f"启动Web执行成功，ID: {execution_id}")
            return execution_id
        except Exception as e:
            session.rollback()
            logger.error(f"启动Web执行失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def stop_execution(session: Session, execution_id: str) -> bool:
        """停止执行"""
        try:
            execution = session.exec(select(WebExecution).where(WebExecution.execution_id == execution_id)).first()
            if not execution:
                return False
            
            if execution.status in ['completed', 'failed', 'stopped']:
                return False
            
            execution.status = 'stopped'
            execution.end_time = datetime.now()
            execution.update_time = datetime.now()
            
            session.commit()
            logger.info(f"停止Web执行成功，ID: {execution_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"停止Web执行失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_execution_status(session: Session, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态"""
        try:
            execution = session.exec(select(WebExecution).where(WebExecution.execution_id == execution_id)).first()
            if not execution:
                return None
            
            # 计算进度
            progress = 0.0
            if execution.total_cases > 0:
                completed = (execution.passed_cases or 0) + (execution.failed_cases or 0) + (execution.skipped_cases or 0)
                progress = (completed / execution.total_cases) * 100
            
            return {
                "execution_id": execution.execution_id,
                "project_id": execution.project_id,
                "execution_name": execution.execution_name,
                "status": execution.status,
                "progress": round(progress, 2),
                "total_cases": execution.total_cases,
                "passed_cases": execution.passed_cases or 0,
                "failed_cases": execution.failed_cases or 0,
                "skipped_cases": execution.skipped_cases or 0,
                "error_cases": execution.error_cases or 0,
                "running_cases": execution.running_cases or 0,
                "start_time": execution.start_time,
                "end_time": execution.end_time,
                "duration": execution.duration,
                "current_case": execution.current_case,
                "error_message": execution.error_message,
                "browser_type": execution.browser_type,
                "environment": execution.environment
            }
        except Exception as e:
            logger.error(f"获取执行状态失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def query_by_page(session: Session, query: WebExecutionQuery) -> Tuple[List[WebExecution], int]:
        """分页查询执行记录"""
        offset = (query.page - 1) * query.pageSize
        statement = select(WebExecution)
        
        # 应用过滤条件
        if query.project_id:
            statement = statement.where(WebExecution.project_id == query.project_id)
        if query.execution_name:
            statement = statement.where(WebExecution.execution_name.contains(query.execution_name))
        if query.status:
            statement = statement.where(WebExecution.status == query.status)
        if query.execution_type:
            statement = statement.where(WebExecution.execution_type == query.execution_type)
        
        # 排序
        statement = statement.order_by(WebExecution.start_time.desc())
        
        # 分页
        statement = statement.limit(query.pageSize).offset(offset)
        executions = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(count_statement).one()
        
        return list(executions), total
    
    @staticmethod
    def query_by_id(session: Session, execution_id: str) -> Optional[WebExecution]:
        """根据ID查询执行记录"""
        return session.exec(select(WebExecution).where(WebExecution.execution_id == execution_id)).first()
    
    @staticmethod
    def get_execution_results(session: Session, execution_id: str) -> List[WebExecutionResult]:
        """获取执行结果"""
        try:
            statement = select(WebExecutionResult).where(
                WebExecutionResult.execution_id == execution_id
            ).order_by(WebExecutionResult.case_id)
            
            return session.exec(statement).all()
        except Exception as e:
            logger.error(f"获取执行结果失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def get_report_info(session: Session, execution_id: str) -> Optional[WebReportInfo]:
        """获取报告信息"""
        try:
            execution = WebExecutionService.query_by_id(session, execution_id)
            if not execution:
                return None
            
            # 检查是否有报告
            report_url = f"/reports/web/{execution_id}.html"
            is_available = execution.status == 'completed' and execution.generate_report
            
            return WebReportInfo(
                execution_id=execution_id,
                report_url=report_url,
                report_format="html",
                is_available=is_available,
                generate_time=execution.end_time
            )
        except Exception as e:
            logger.error(f"获取报告信息失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def delete_execution(session: Session, execution_id: str) -> bool:
        """删除执行记录"""
        try:
            execution = WebExecutionService.query_by_id(session, execution_id)
            if not execution:
                return False
            
            # 删除相关的结果记录
            results = WebExecutionService.get_execution_results(session, execution_id)
            for result in results:
                session.delete(result)
            
            # 删除执行记录
            session.delete(execution)
            session.commit()
            logger.info(f"删除Web执行记录成功，ID: {execution_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除Web执行记录失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def batch_delete_executions(session: Session, execution_ids: List[str]) -> int:
        """批量删除执行记录"""
        try:
            count = 0
            for execution_id in execution_ids:
                if WebExecutionService.delete_execution(session, execution_id):
                    count += 1
            logger.info(f"批量删除Web执行记录成功，删除数量: {count}")
            return count
        except Exception as e:
            logger.error(f"批量删除Web执行记录失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_statistics(session: Session, project_id: Optional[int] = None, days: int = 7) -> Dict[str, Any]:
        """获取执行统计信息"""
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 基础查询条件
            base_condition = and_(WebExecution.start_time >= start_time, WebExecution.start_time <= end_time)
            if project_id:
                base_condition = and_(base_condition, WebExecution.project_id == project_id)
            
            # 总执行次数
            total_statement = select(func.count()).select_from(WebExecution).where(base_condition)
            total_executions = session.exec(total_statement).one()
            
            # 按状态统计
            status_stats = {}
            for status in ['pending', 'running', 'completed', 'failed', 'stopped']:
                status_statement = select(func.count()).where(and_(base_condition, WebExecution.status == status))
                count = session.exec(status_statement).one()
                if count > 0:
                    status_stats[status] = count
            
            # 按浏览器统计
            browser_stats = {}
            browsers = ['chrome', 'firefox', 'safari', 'edge']
            for browser in browsers:
                browser_statement = select(func.count()).where(and_(base_condition, WebExecution.browser_type == browser))
                count = session.exec(browser_statement).one()
                if count > 0:
                    browser_stats[browser] = count
            
            # 计算平均执行时间
            avg_duration_statement = select(func.avg(WebExecution.duration)).where(and_(base_condition, WebExecution.duration.is_not(None)))
            avg_duration = session.exec(avg_duration_statement).one() or 0
            
            # 计算通过率
            passed_statement = select(func.sum(WebExecution.passed_cases)).where(base_condition)
            total_cases_statement = select(func.sum(WebExecution.total_cases)).where(base_condition)
            passed_cases = session.exec(passed_statement).one() or 0
            total_cases = session.exec(total_cases_statement).one() or 0
            pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
            
            return {
                'total_executions': total_executions,
                'status_stats': status_stats,
                'browser_stats': browser_stats,
                'avg_duration': round(avg_duration, 2),
                'pass_rate': round(pass_rate, 2),
                'date_range': {
                    'start_date': start_time.isoformat(),
                    'end_date': end_time.isoformat()
                }
            }
        except Exception as e:
            logger.error(f"获取执行统计信息失败: {e}", exc_info=True)
            return {
                'total_executions': 0,
                'status_stats': {},
                'browser_stats': {},
                'avg_duration': 0,
                'pass_rate': 0,
                'date_range': {}
            }
    
    @staticmethod
    def update_execution_status(session: Session, execution_id: str, status: str) -> bool:
        """更新执行状态"""
        try:
            execution = WebExecutionService.query_by_id(session, execution_id)
            if not execution:
                return False
            
            execution.status = status
            if status in ['completed', 'failed', 'stopped']:
                execution.end_time = datetime.now()
                if execution.start_time:
                    execution.duration = int((execution.end_time - execution.start_time).total_seconds())
            
            execution.update_time = datetime.now()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"更新执行状态失败: {e}", exc_info=True)
            return False
    
    @staticmethod
    def get_execution_status(session: Session, execution_id: str) -> Optional[WebExecutionStatus]:
        """获取执行状态"""
        try:
            # 查询执行记录
            statement = select(WebExecution).where(WebExecution.execution_id == execution_id)
            execution = session.exec(statement).first()
            
            if not execution:
                return None
            
            # 查询执行结果统计
            result_statement = select(
                func.count(WebExecutionResult.id),
                func.sum(func.case((WebExecutionResult.status == 'passed', 1), else_=0)),
                func.sum(func.case((WebExecutionResult.status == 'failed', 1), else_=0)),
                func.sum(func.case((WebExecutionResult.status == 'skipped', 1), else_=0)),
                func.sum(func.case((WebExecutionResult.status == 'error', 1), else_=0)),
                func.sum(func.case((WebExecutionResult.status == 'running', 1), else_=0))
            ).where(WebExecutionResult.execution_id == execution_id)
            
            result_stats = session.exec(result_statement).first() or (0, 0, 0, 0, 0, 0)
            total, passed, failed, skipped, error, running = result_stats
            
            # 计算进度
            progress = 0.0
            if execution.total_cases > 0:
                completed = passed + failed + skipped + error
                progress = (completed / execution.total_cases) * 100
            
            return WebExecutionStatus(
                execution_id=execution.execution_id,
                project_id=execution.project_id,
                execution_name=execution.execution_name,
                status=execution.status,
                progress=progress,
                total_cases=execution.total_cases,
                passed_cases=passed or 0,
                failed_cases=failed or 0,
                skipped_cases=skipped or 0,
                error_cases=error or 0,
                running_cases=running or 0,
                start_time=execution.start_time,
                end_time=execution.end_time,
                duration=execution.duration,
                browser_type=execution.browser_type,
                environment=execution.environment,
                error_message=execution.error_message
            )
        except Exception as e:
            logger.error(f"获取执行状态失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def query_executions_by_page(session: Session, query: WebExecutionQuery) -> Tuple[List[WebExecution], int]:
        """分页查询执行记录"""
        try:
            # 构建查询条件
            statement = select(WebExecution)
            
            # 添加过滤条件
            if query.project_id:
                statement = statement.where(WebExecution.project_id == query.project_id)
            if query.execution_name:
                statement = statement.where(WebExecution.execution_name.contains(query.execution_name))
            if query.status:
                statement = statement.where(WebExecution.status == query.status)
            if query.execution_type:
                statement = statement.where(WebExecution.execution_type == query.execution_type)
            if query.trigger_type:
                statement = statement.where(WebExecution.trigger_type == query.trigger_type)
            if query.start_date:
                statement = statement.where(WebExecution.create_time >= query.start_date)
            if query.end_date:
                statement = statement.where(WebExecution.create_time <= query.end_date)
            
            # 计算总数
            count_statement = select(func.count()).select_from(statement.subquery())
            total = session.exec(count_statement).one()
            
            # 分页查询
            statement = statement.offset((query.page - 1) * query.pageSize).limit(query.pageSize)
            statement = statement.order_by(WebExecution.create_time.desc())
            executions = session.exec(statement).all()
            
            return list(executions), total
        except Exception as e:
            logger.error(f"分页查询执行记录失败: {e}", exc_info=True)
            return [], 0
    
    @staticmethod
    def get_execution_detail(session: Session, execution_id: int) -> Optional[WebExecutionDetail]:
        """获取执行详情"""
        try:
            # 查询执行记录
            execution = session.get(WebExecution, execution_id)
            if not execution:
                return None
            
            # 查询执行结果
            result_statement = select(WebExecutionResult).where(
                WebExecutionResult.execution_id == execution.execution_id
            ).order_by(WebExecutionResult.create_time)
            results = session.exec(result_statement).all()
            
            # 统计信息
            statistics = {
                "total_cases": execution.total_cases,
                "passed_cases": execution.passed_cases,
                "failed_cases": execution.failed_cases,
                "skipped_cases": execution.skipped_cases,
                "error_cases": execution.error_cases,
                "success_rate": (execution.passed_cases / execution.total_cases * 100) if execution.total_cases > 0 else 0
            }
            
            return WebExecutionDetail(
                execution_info=execution,
                case_results=list(results),
                statistics=statistics
            )
        except Exception as e:
            logger.error(f"获取执行详情失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_report_info(session: Session, execution_id: str) -> Optional[WebReportInfo]:
        """获取报告信息"""
        try:
            # 查询执行记录
            statement = select(WebExecution).where(WebExecution.execution_id == execution_id)
            execution = session.exec(statement).first()
            
            if not execution:
                return None
            
            # 检查报告是否存在
            is_available = execution.report_path is not None
            file_size = 0
            
            if is_available and execution.report_path:
                # TODO: 检查文件是否存在并获取大小
                pass
            
            return WebReportInfo(
                execution_id=execution_id,
                report_url=f"/reports/web/{execution_id}/index.html" if is_available else "",
                report_format="html",
                is_available=is_available,
                generate_time=execution.end_time,
                file_size=file_size
            )
        except Exception as e:
            logger.error(f"获取报告信息失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_execution_results(session: Session, execution_id: str, page: int = 1, pageSize: int = 10) -> Tuple[List[WebExecutionResult], int]:
        """获取执行结果"""
        try:
            # 计算总数
            count_statement = select(func.count(WebExecutionResult.id)).where(
                WebExecutionResult.execution_id == execution_id
            )
            total = session.exec(count_statement).one()
            
            # 分页查询
            statement = select(WebExecutionResult).where(
                WebExecutionResult.execution_id == execution_id
            ).offset((page - 1) * pageSize).limit(pageSize)
            statement = statement.order_by(WebExecutionResult.create_time)
            results = session.exec(statement).all()
            
            return list(results), total
        except Exception as e:
            logger.error(f"获取执行结果失败: {e}", exc_info=True)
            return [], 0
    
    @staticmethod
    def get_execution_statistics(session: Session, project_id: int, days: int = 30) -> Dict[str, Any]:
        """获取执行统计"""
        try:
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            
            # 查询统计数据
            statement = select(
                func.count(WebExecution.id),
                func.sum(func.case((WebExecution.status == 'completed', 1), else_=0)),
                func.sum(func.case((WebExecution.status == 'failed', 1), else_=0)),
                func.sum(WebExecution.total_cases),
                func.sum(WebExecution.passed_cases),
                func.sum(WebExecution.failed_cases)
            ).where(
                WebExecution.project_id == project_id,
                WebExecution.create_time >= start_date,
                WebExecution.create_time <= end_date
            )
            
            stats = session.exec(statement).first() or (0, 0, 0, 0, 0, 0)
            total, completed, failed, total_cases, passed_cases, failed_cases = stats
            
            # 计算成功率
            success_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
            
            return {
                "period_days": days,
                "total_executions": total,
                "completed_executions": completed or 0,
                "failed_executions": failed or 0,
                "total_cases": total_cases or 0,
                "passed_cases": passed_cases or 0,
                "failed_cases": failed_cases or 0,
                "success_rate": success_rate
            }
        except Exception as e:
            logger.error(f"获取执行统计失败: {e}", exc_info=True)
            return {}
    
    @staticmethod
    def retry_failed_cases(session: Session, execution_id: str) -> Optional[str]:
        """重试失败的用例"""
        try:
            # 查询原执行记录
            original_statement = select(WebExecution).where(WebExecution.execution_id == execution_id)
            original_execution = session.exec(original_statement).first()
            
            if not original_execution:
                return None
            
            # 查询失败的用例
            failed_statement = select(WebExecutionResult).where(
                WebExecutionResult.execution_id == execution_id,
                WebExecutionResult.status.in_(['failed', 'error'])
            )
            failed_results = session.exec(failed_statement).all()
            
            if not failed_results:
                return None
            
            # 提取失败的用例ID
            failed_case_ids = [result.case_id for result in failed_results]
            
            # 创建新的执行记录
            new_execution_id = f"retry_{uuid.uuid4().hex[:8]}"
            retry_request = WebExecutionRequest(
                project_id=original_execution.project_id,
                execution_name=f"重试_{original_execution.execution_name}",
                execution_type='single',
                case_ids=failed_case_ids,
                browser_type=original_execution.browser_type,
                environment=original_execution.environment
            )
            
            WebExecutionService.create_execution(session, new_execution_id, retry_request)
            logger.info(f"创建重试执行成功，新执行ID: {new_execution_id}")
            return new_execution_id
        except Exception as e:
            logger.error(f"重试失败用例失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def start_execution(session: Session, request: WebExecutionRequest) -> str:
        """启动执行"""
        try:
            import uuid
            execution_id = f"exec_{uuid.uuid4().hex[:8]}"
            
            # 创建执行记录
            execution = WebExecutionService.create_execution(session, execution_id, request)
            
            # 更新状态为运行中
            execution.status = 'running'
            execution.start_time = datetime.now()
            session.commit()
            
            # TODO: 异步启动执行引擎
            # 这里应该调用测试执行引擎来实际运行测试
            # 可以使用 Celery、BackgroundTasks 或其他异步任务队列
            
            logger.info(f"启动Web执行成功，执行ID: {execution_id}")
            return execution_id
        except Exception as e:
            session.rollback()
            logger.error(f"启动Web执行失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update_execution_result(session: Session, execution_id: str, case_id: int, 
                              status: str, error_message: str = None, 
                              screenshot_path: str = None, execution_time: float = None) -> bool:
        """更新执行结果"""
        try:
            # 创建或更新执行结果
            result = WebExecutionResult(
                execution_id=execution_id,
                case_id=case_id,
                status=status,
                error_message=error_message,
                screenshot_path=screenshot_path,
                execution_time=execution_time or 0.0,
                start_time=datetime.now(),
                end_time=datetime.now()
            )
            
            session.add(result)
            
            # 更新执行记录的统计信息
            execution_statement = select(WebExecution).where(WebExecution.execution_id == execution_id)
            execution = session.exec(execution_statement).first()
            
            if execution:
                if status == 'passed':
                    execution.passed_cases += 1
                elif status == 'failed':
                    execution.failed_cases += 1
                elif status == 'skipped':
                    execution.skipped_cases += 1
                elif status == 'error':
                    execution.error_cases += 1
                
                # 检查是否所有用例都执行完成
                total_completed = execution.passed_cases + execution.failed_cases + execution.skipped_cases + execution.error_cases
                if total_completed >= execution.total_cases:
                    execution.status = 'completed'
                    execution.end_time = datetime.now()
                    if execution.start_time:
                        execution.duration = int((execution.end_time - execution.start_time).total_seconds())
            
            session.commit()
            logger.info(f"更新执行结果成功，执行ID: {execution_id}, 用例ID: {case_id}, 状态: {status}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"更新执行结果失败: {e}", exc_info=True)
            return False
    
    @staticmethod
    def complete_execution(session: Session, execution_id: str, success: bool = True, 
                          error_message: str = None) -> bool:
        """完成执行"""
        try:
            statement = select(WebExecution).where(WebExecution.execution_id == execution_id)
            execution = session.exec(statement).first()
            
            if not execution:
                return False
            
            execution.status = 'completed' if success else 'failed'
            execution.end_time = datetime.now()
            if execution.start_time:
                execution.duration = int((execution.end_time - execution.start_time).total_seconds())
            
            if error_message:
                execution.error_message = error_message
            
            session.commit()
            logger.info(f"完成Web执行，执行ID: {execution_id}, 状态: {execution.status}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"完成Web执行失败: {e}", exc_info=True)
            return False
    
    @staticmethod
    def generate_execution_report(session: Session, execution_id: str) -> Optional[str]:
        """生成执行报告"""
        try:
            # 查询执行记录和结果
            execution_statement = select(WebExecution).where(WebExecution.execution_id == execution_id)
            execution = session.exec(execution_statement).first()
            
            if not execution:
                return None
            
            result_statement = select(WebExecutionResult).where(
                WebExecutionResult.execution_id == execution_id
            ).order_by(WebExecutionResult.create_time)
            results = session.exec(result_statement).all()
            
            # TODO: 生成HTML报告
            # 1. 创建报告模板
            # 2. 填充执行数据
            # 3. 生成图表和统计
            # 4. 保存报告文件
            
            # 模拟报告生成
            import os
            from datetime import datetime
            
            report_dir = "reports/web"
            os.makedirs(report_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"report_{execution_id}_{timestamp}.html"
            report_path = os.path.join(report_dir, report_filename)
            
            # 生成简单的HTML报告
            html_content = WebExecutionService._generate_html_report(execution, list(results))
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 更新执行记录的报告路径
            execution.report_path = report_path
            session.commit()
            
            logger.info(f"生成执行报告成功，执行ID: {execution_id}, 报告路径: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"生成执行报告失败: {e}", exc_info=True)
            return None
    
    @staticmethod
    def _generate_html_report(execution: WebExecution, results: List[WebExecutionResult]) -> str:
        """生成HTML报告内容"""
        try:
            from datetime import datetime
            
            # 计算统计信息
            total_cases = len(results)
            passed_cases = len([r for r in results if r.status == 'passed'])
            failed_cases = len([r for r in results if r.status == 'failed'])
            skipped_cases = len([r for r in results if r.status == 'skipped'])
            error_cases = len([r for r in results if r.status == 'error'])
            success_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
            
            html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web测试执行报告 - {execution.execution_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 20px; }}
        .summary-item {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; flex: 1; }}
        .passed {{ background-color: #d4edda; color: #155724; }}
        .failed {{ background-color: #f8d7da; color: #721c24; }}
        .skipped {{ background-color: #fff3cd; color: #856404; }}
        .error {{ background-color: #f8d7da; color: #721c24; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .status-passed {{ color: #28a745; font-weight: bold; }}
        .status-failed {{ color: #dc3545; font-weight: bold; }}
        .status-skipped {{ color: #ffc107; font-weight: bold; }}
        .status-error {{ color: #dc3545; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Web测试执行报告</h1>
        <p><strong>执行名称:</strong> {execution.execution_name}</p>
        <p><strong>执行ID:</strong> {execution.execution_id}</p>
        <p><strong>执行时间:</strong> {execution.start_time or 'N/A'} - {execution.end_time or 'N/A'}</p>
        <p><strong>执行时长:</strong> {execution.duration or 0} 秒</p>
        <p><strong>浏览器类型:</strong> {execution.browser_type or 'N/A'}</p>
        <p><strong>执行环境:</strong> {execution.environment or 'N/A'}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <h3>总用例数</h3>
            <p>{total_cases}</p>
        </div>
        <div class="summary-item passed">
            <h3>通过</h3>
            <p>{passed_cases}</p>
        </div>
        <div class="summary-item failed">
            <h3>失败</h3>
            <p>{failed_cases}</p>
        </div>
        <div class="summary-item skipped">
            <h3>跳过</h3>
            <p>{skipped_cases}</p>
        </div>
        <div class="summary-item error">
            <h3>错误</h3>
            <p>{error_cases}</p>
        </div>
        <div class="summary-item">
            <h3>成功率</h3>
            <p>{success_rate:.1f}%</p>
        </div>
    </div>
    
    <h2>执行结果详情</h2>
    <table>
        <thead>
            <tr>
                <th>用例ID</th>
                <th>状态</th>
                <th>执行时间(秒)</th>
                <th>开始时间</th>
                <th>结束时间</th>
                <th>错误信息</th>
                <th>截图</th>
            </tr>
        </thead>
        <tbody>
"""
            
            for result in results:
                status_class = f"status-{result.status}"
                screenshot_link = f"<a href='{result.screenshot_path}' target='_blank'>查看</a>" if result.screenshot_path else "无"
                error_msg = result.error_message or ""
                
                html_template += f"""
            <tr>
                <td>{result.case_id}</td>
                <td class="{status_class}">{result.status}</td>
                <td>{result.execution_time:.2f}</td>
                <td>{result.start_time or 'N/A'}</td>
                <td>{result.end_time or 'N/A'}</td>
                <td>{error_msg}</td>
                <td>{screenshot_link}</td>
            </tr>
"""
            
            html_template += """
        </tbody>
    </table>
    
    <div style="margin-top: 30px; text-align: center; color: #666;">
        <p>报告生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
</body>
</html>
"""
            
            return html_template
        except Exception as e:
            logger.error(f"生成HTML报告内容失败: {e}", exc_info=True)
            return f"<html><body><h1>报告生成失败</h1><p>错误: {e}</p></body></html>"
