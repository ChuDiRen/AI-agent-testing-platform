"""
接口历史Service
提供历史记录的CRUD、查询、统计等功能
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_, desc

from apitest.model.ApiHistoryModel import ApiHistory


class HistoryService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                     api_id: Optional[int] = None, case_id: Optional[int] = None,
                     execution_status: Optional[str] = None, 
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None) -> tuple[List[ApiHistory], int]:
        """分页查询历史记录"""
        statement = select(ApiHistory)
        
        # 条件筛选
        if project_id:
            statement = statement.where(ApiHistory.project_id == project_id)
        if api_id:
            statement = statement.where(ApiHistory.api_info_id == api_id)
        if case_id:
            statement = statement.where(ApiHistory.case_info_id == case_id)
        if execution_status:
            statement = statement.where(ApiHistory.test_status == execution_status)
        if start_time:
            statement = statement.where(ApiHistory.create_time >= start_time)
        if end_time:
            statement = statement.where(ApiHistory.create_time <= end_time)
        
        # 排序
        statement = statement.order_by(desc(ApiHistory.create_time))
        
        # 查询总数
        total_statement = select(ApiHistory)
        if project_id:
            total_statement = total_statement.where(ApiHistory.project_id == project_id)
        if api_id:
            total_statement = total_statement.where(ApiHistory.api_info_id == api_id)
        if case_id:
            total_statement = total_statement.where(ApiHistory.case_info_id == case_id)
        if execution_status:
            total_statement = total_statement.where(ApiHistory.test_status == execution_status)
        if start_time:
            total_statement = total_statement.where(ApiHistory.create_time >= start_time)
        if end_time:
            total_statement = total_statement.where(ApiHistory.create_time <= end_time)
        
        total = len(self.session.exec(total_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[ApiHistory]:
        """根据ID查询历史记录"""
        return self.session.get(ApiHistory, id)
    
    def create(self, **kwargs) -> ApiHistory:
        """创建历史记录"""
        data = ApiHistory(
            **kwargs,
            create_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新历史记录"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除历史记录"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def query_by_project(self, project_id: int, limit: int = 100) -> List[ApiHistory]:
        """查询项目的历史记录"""
        statement = select(ApiHistory).where(
            ApiHistory.project_id == project_id
        ).order_by(desc(ApiHistory.create_time)).limit(limit)
        
        return self.session.exec(statement).all()
    
    def query_by_api(self, api_id: int, limit: int = 50) -> List[ApiHistory]:
        """查询指定接口的历史记录"""
        statement = select(ApiHistory).where(
            ApiHistory.api_info_id == api_id
        ).order_by(desc(ApiHistory.create_time)).limit(limit)
        
        return self.session.exec(statement).all()
    
    def query_by_case(self, case_id: int, limit: int = 50) -> List[ApiHistory]:
        """查询指定用例的历史记录"""
        statement = select(ApiHistory).where(
            ApiHistory.case_info_id == case_id
        ).order_by(desc(ApiHistory.create_time)).limit(limit)
        
        return self.session.exec(statement).all()
    
    def batch_delete(self, history_ids: List[int]) -> int:
        """批量删除历史记录"""
        deleted_count = 0
        for history_id in history_ids:
            if self.delete(history_id):
                deleted_count += 1
        
        return deleted_count
    
    def clean_old_records(self, project_id: int, days: int = 30) -> int:
        """清理旧的历史记录"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        old_records = self.session.exec(
            select(ApiHistory).where(
                and_(
                    ApiHistory.project_id == project_id,
                    ApiHistory.create_time < cutoff_date
                )
            )
        ).all()
        
        deleted_count = 0
        for record in old_records:
            self.session.delete(record)
            deleted_count += 1
        
        if deleted_count > 0:
            self.session.commit()
        
        return deleted_count
    
    def get_statistics(self, project_id: int, days: int = 7) -> Dict[str, Any]:
        """获取历史统计信息"""
        start_date = datetime.now() - timedelta(days=days)
        
        # 总执行次数
        total_statement = select(ApiHistory).where(
            and_(
                ApiHistory.project_id == project_id,
                ApiHistory.create_time >= start_date
            )
        )
        total_executions = len(self.session.exec(total_statement).all())
        
        # 成功/失败统计
        success_count = len(self.session.exec(
            select(ApiHistory).where(
                and_(
                    ApiHistory.project_id == project_id,
                    ApiHistory.create_time >= start_date,
                    ApiHistory.test_status == 'success'
                )
            )
        ).all())
        
        failure_count = len(self.session.exec(
            select(ApiHistory).where(
                and_(
                    ApiHistory.project_id == project_id,
                    ApiHistory.create_time >= start_date,
                    ApiHistory.test_status == 'failed'
                )
            )
        ).all())
        
        # 按日期统计
        daily_stats = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            next_date = date + timedelta(days=1)
            
            day_count = len(self.session.exec(
                select(ApiHistory).where(
                    and_(
                        ApiHistory.project_id == project_id,
                        ApiHistory.create_time >= date,
                        ApiHistory.create_time < next_date
                    )
                )
            ).all())
            
            daily_stats.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': day_count
            })
        
        # 平均响应时间
        avg_response_time = 0
        response_times = self.session.exec(
            select(ApiHistory.response_time).where(
                and_(
                    ApiHistory.project_id == project_id,
                    ApiHistory.create_time >= start_date,
                    ApiHistory.response_time > 0
                )
            )
        ).all()
        
        if response_times:
            avg_response_time = sum(rt[0] for rt in response_times) / len(response_times)
        
        return {
            'total_executions': total_executions,
            'success_count': success_count,
            'failure_count': failure_count,
            'success_rate': round(success_count / total_executions * 100, 2) if total_executions > 0 else 0,
            'avg_response_time': round(avg_response_time, 2),
            'daily_stats': daily_stats
        }
