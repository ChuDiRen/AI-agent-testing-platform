"""
请求历史Service
提供请求历史的查询、收藏、统计等功能
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_

from apitest.model.ApiRequestHistoryModel import ApiRequestHistory


class RequestHistoryService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                     api_id: Optional[int] = None, request_method: Optional[str] = None,
                     request_url: Optional[str] = None, is_success: Optional[int] = None,
                     is_favorite: Optional[int] = None, start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None) -> tuple[List[ApiRequestHistory], int]:
        """分页查询请求历史"""
        statement = select(ApiRequestHistory)
        
        # 条件筛选
        if project_id:
            statement = statement.where(ApiRequestHistory.project_id == project_id)
        if api_id:
            statement = statement.where(ApiRequestHistory.api_id == api_id)
        if request_method:
            statement = statement.where(ApiRequestHistory.request_method == request_method)
        if request_url:
            statement = statement.where(ApiRequestHistory.request_url.contains(request_url))
        if is_success is not None:
            statement = statement.where(ApiRequestHistory.is_success == is_success)
        if is_favorite is not None:
            statement = statement.where(ApiRequestHistory.is_favorite == is_favorite)
        if start_time:
            statement = statement.where(ApiRequestHistory.create_time >= start_time)
        if end_time:
            statement = statement.where(ApiRequestHistory.create_time <= end_time)
        
        # 按时间倒序
        statement = statement.order_by(ApiRequestHistory.create_time.desc())
        
        # 查询总数
        count_statement = select(ApiRequestHistory)
        if project_id:
            count_statement = count_statement.where(ApiRequestHistory.project_id == project_id)
        total = len(self.session.exec(count_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[ApiRequestHistory]:
        """根据ID查询历史详情"""
        return self.session.get(ApiRequestHistory, id)
    
    def query_recent(self, project_id: int, limit: int = 10) -> List[ApiRequestHistory]:
        """查询最近的请求历史"""
        statement = select(ApiRequestHistory).where(
            ApiRequestHistory.project_id == project_id
        ).order_by(ApiRequestHistory.create_time.desc()).limit(limit)
        
        return self.session.exec(statement).all()
    
    def query_favorites(self, project_id: int) -> List[ApiRequestHistory]:
        """查询收藏的请求历史"""
        statement = select(ApiRequestHistory).where(
            and_(
                ApiRequestHistory.project_id == project_id,
                ApiRequestHistory.is_favorite == 1
            )
        ).order_by(ApiRequestHistory.create_time.desc())
        
        return self.session.exec(statement).all()
    
    def create(self, **kwargs) -> ApiRequestHistory:
        """新增请求历史记录"""
        data = ApiRequestHistory(
            **kwargs,
            create_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def delete(self, id: int) -> bool:
        """删除历史记录"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def batch_delete(self, ids: List[int]) -> int:
        """批量删除历史记录"""
        deleted_count = 0
        for id in ids:
            data = self.get_by_id(id)
            if data:
                self.session.delete(data)
                deleted_count += 1
        
        self.session.commit()
        return deleted_count
    
    def toggle_favorite(self, id: int) -> Optional[int]:
        """切换收藏状态"""
        data = self.get_by_id(id)
        if not data:
            return None
        
        data.is_favorite = 0 if data.is_favorite == 1 else 1
        self.session.add(data)
        self.session.commit()
        return data.is_favorite
    
    def clear(self, project_id: int, keep_favorites: bool = False, days: Optional[int] = None) -> int:
        """清空历史记录"""
        statement = select(ApiRequestHistory).where(
            ApiRequestHistory.project_id == project_id
        )
        
        # 保留收藏
        if keep_favorites:
            statement = statement.where(ApiRequestHistory.is_favorite == 0)
        
        # 保留最近N天
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            statement = statement.where(ApiRequestHistory.create_time < cutoff_date)
        
        records = self.session.exec(statement).all()
        deleted_count = len(records)
        
        for record in records:
            self.session.delete(record)
        
        self.session.commit()
        return deleted_count
    
    def get_statistics(self, project_id: int, days: int = 7) -> Dict[str, Any]:
        """获取请求历史统计"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        statement = select(ApiRequestHistory).where(
            and_(
                ApiRequestHistory.project_id == project_id,
                ApiRequestHistory.create_time >= cutoff_date
            )
        )
        records = self.session.exec(statement).all()
        
        # 统计数据
        total = len(records)
        success_count = sum(1 for r in records if r.is_success == 1)
        fail_count = total - success_count
        avg_response_time = sum(r.response_time or 0 for r in records) / total if total > 0 else 0
        
        # 按方法统计
        method_stats = {}
        for record in records:
            method = record.request_method
            if method not in method_stats:
                method_stats[method] = 0
            method_stats[method] += 1
        
        return {
            "total": total,
            "success_count": success_count,
            "fail_count": fail_count,
            "success_rate": round(success_count / total * 100, 2) if total > 0 else 0,
            "avg_response_time": round(avg_response_time, 2),
            "method_stats": method_stats
        }
