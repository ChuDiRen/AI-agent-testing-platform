"""
Web测试执行历史Service层
按照ApiTest标准实现
"""
import json
import uuid
from datetime import datetime, timedelta
from typing import Tuple, List, Optional

from core.logger import get_logger
from sqlmodel import Session, select, and_, or_, func

from ..model.WebHistoryModel import WebHistory, WebHistoryCase, WebExecutionStatus
from ..schemas.WebHistorySchema import (
    WebHistoryQuery, WebHistoryCreate, WebHistoryUpdate, 
    WebHistoryResponse, WebHistoryCaseResponse
)

logger = get_logger(__name__)


class WebHistoryService:
    """Web测试执行历史服务类 - 使用静态方法模式"""
    
    @staticmethod
    def generate_execution_id() -> str:
        """生成执行ID"""
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        # 简单的递增序号，实际应该从数据库获取当日序号
        return f"exec_{date_str}_{uuid.uuid4().hex[:6]}"
    
    @staticmethod
    def query_by_page(session: Session, query: WebHistoryQuery) -> Tuple[List[WebHistory], int]:
        """分页查询执行历史"""
        offset = (query.page - 1) * query.pageSize
        statement = select(WebHistory)
        
        # 应用过滤条件
        if query.project_id:
            statement = statement.where(WebHistory.project_id == query.project_id)
        if query.status:
            statement = statement.where(WebHistory.status == query.status)
        if query.env:
            statement = statement.where(WebHistory.env == query.env)
        if query.executor:
            statement = statement.where(WebHistory.executor.contains(query.executor))
        if query.start_date:
            statement = statement.where(WebHistory.start_time >= query.start_date)
        if query.end_date:
            statement = statement.where(WebHistory.start_time <= query.end_date)
        
        # 排序
        statement = statement.order_by(WebHistory.start_time.desc())
        
        # 分页
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()
        
        # 统计总数
        count_statement = select(func.count()).select_from(statement.subquery())
        total = session.exec(count_statement).one()
        
        return list(datas), total
    
    @staticmethod
    def query_by_id(session: Session, execution_id: str) -> Optional[WebHistory]:
        """根据ID查询执行历史"""
        return session.get(WebHistory, execution_id)
    
    @staticmethod
    def create(session: Session, history_data: WebHistoryCreate) -> WebHistory:
        """创建执行历史记录"""
        try:
            execution_id = WebHistoryService.generate_execution_id()
            
            # 转换列表字段为JSON
            browsers_json = json.dumps(history_data.browsers or [], ensure_ascii=False)
            case_ids_json = json.dumps(history_data.case_ids or [], ensure_ascii=False)
            
            history = WebHistory(
                id=execution_id,
                project_id=history_data.project_id,
                project_name=history_data.project_name,
                env=history_data.env,
                status=history_data.status,
                total=history_data.total,
                passed=history_data.passed,
                failed=history_data.failed,
                pass_rate=history_data.pass_rate,
                duration=history_data.duration,
                executor=history_data.executor,
                browsers=browsers_json,
                threads=history_data.threads,
                case_ids=case_ids_json,
                error_summary=history_data.error_summary,
                start_time=datetime.now()
            )
            
            session.add(history)
            session.commit()
            session.refresh(history)
            logger.info(f"创建Web执行历史成功，ID: {history.id}")
            return history
        except Exception as e:
            session.rollback()
            logger.error(f"创建Web执行历史失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def update(session: Session, execution_id: str, history_data: WebHistoryUpdate) -> bool:
        """更新执行历史记录"""
        try:
            history = session.get(WebHistory, execution_id)
            if not history:
                return False
            
            # 更新字段
            update_data = history_data.dict(exclude_unset=True, exclude={'id'})
            
            # 处理列表字段
            if 'browsers' in update_data and update_data['browsers']:
                update_data['browsers'] = json.dumps(update_data['browsers'], ensure_ascii=False)
            
            for field, value in update_data.items():
                if value is not None:
                    setattr(history, field, value)
            
            history.update_time = datetime.now()
            session.commit()
            logger.info(f"更新Web执行历史成功，ID: {execution_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"更新Web执行历史失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def delete(session: Session, execution_id: str) -> bool:
        """删除执行历史记录"""
        try:
            history = session.get(WebHistory, execution_id)
            if not history:
                return False
            
            # 先删除相关的用例详情
            case_statement = select(WebHistoryCase).where(WebHistoryCase.execution_id == execution_id)
            cases = session.exec(case_statement).all()
            for case in cases:
                session.delete(case)
            
            # 删除历史记录
            session.delete(history)
            session.commit()
            logger.info(f"删除Web执行历史成功，ID: {execution_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"删除Web执行历史失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def batch_delete(session: Session, execution_ids: List[str]) -> int:
        """批量删除执行历史记录"""
        try:
            count = 0
            for execution_id in execution_ids:
                if WebHistoryService.delete(session, execution_id):
                    count += 1
            logger.info(f"批量删除Web执行历史成功，删除数量: {count}")
            return count
        except Exception as e:
            logger.error(f"批量删除Web执行历史失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def query_cases_by_execution(session: Session, execution_id: str) -> List[WebHistoryCase]:
        """查询执行历史下的用例详情"""
        try:
            statement = select(WebHistoryCase).where(
                WebHistoryCase.execution_id == execution_id
            ).order_by(WebHistoryCase.create_time)
            
            return session.exec(statement).all()
        except Exception as e:
            logger.error(f"查询执行历史用例详情失败: {e}", exc_info=True)
            return []
    
    @staticmethod
    def create_case_detail(session: Session, execution_id: str, case_data: dict) -> WebHistoryCase:
        """创建用例执行详情"""
        try:
            case = WebHistoryCase(
                execution_id=execution_id,
                case_id=case_data.get('case_id'),
                case_name=case_data.get('case_name'),
                status=case_data.get('status', WebExecutionStatus.RUNNING),
                duration=case_data.get('duration', 0),
                error_message=case_data.get('error_message'),
                start_time=case_data.get('start_time'),
                end_time=case_data.get('end_time'),
                screenshot_path=case_data.get('screenshot_path'),
                step_results=json.dumps(case_data.get('step_results', []), ensure_ascii=False)
            )
            
            session.add(case)
            session.commit()
            session.refresh(case)
            return case
        except Exception as e:
            session.rollback()
            logger.error(f"创建用例执行详情失败: {e}", exc_info=True)
            raise e
    
    @staticmethod
    def get_statistics(session: Session, project_id: Optional[int] = None, days: int = 7) -> dict:
        """获取执行统计信息"""
        try:
            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # 基础查询条件
            base_condition = and_(WebHistory.start_time >= start_time, WebHistory.start_time <= end_time)
            if project_id:
                base_condition = and_(base_condition, WebHistory.project_id == project_id)
            
            # 总执行次数
            total_statement = select(func.count()).select_from(WebHistory).where(base_condition)
            total_executions = session.exec(total_statement).one()
            
            # 按状态统计
            status_stats = {}
            for status in WebExecutionStatus:
                status_statement = select(func.count()).where(
                    and_(base_condition, WebHistory.status == status.value)
                )
                count = session.exec(status_statement).one()
                if count > 0:
                    status_stats[status.value] = count
            
            # 按环境统计
            env_stats = {}
            for env in WebEnvironment:
                env_statement = select(func.count()).where(
                    and_(base_condition, WebHistory.env == env.value)
                )
                count = session.exec(env_statement).one()
                if count > 0:
                    env_stats[env.value] = count
            
            # 计算平均通过率
            avg_pass_rate_statement = select(func.avg(WebHistory.pass_rate)).where(base_condition)
            avg_pass_rate = session.exec(avg_pass_rate_statement).one() or 0
            
            return {
                'total_executions': total_executions,
                'status_stats': status_stats,
                'env_stats': env_stats,
                'avg_pass_rate': round(avg_pass_rate, 2),
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
                'env_stats': {},
                'avg_pass_rate': 0,
                'date_range': {}
            }
