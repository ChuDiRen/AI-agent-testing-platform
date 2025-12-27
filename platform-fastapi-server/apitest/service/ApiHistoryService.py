"""
接口历史Service - 已重构为静态方法模式
提供历史记录的CRUD、查询、统计等功能
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select, and_, desc

from apitest.model.ApiHistoryModel import ApiHistory
from apitest.schemas.ApiHistorySchema import ApiTestHistoryQuery


class HistoryService:
    """接口历史服务类 - 使用静态方法模式"""

    @staticmethod
    def query_by_page(session: Session, query: ApiTestHistoryQuery) -> Tuple[List[ApiHistory], int]:
        """分页查询历史记录"""
        offset = (query.page - 1) * query.pageSize
        statement = select(ApiHistory)

        # 应用过滤条件
        if query.project_id:
            statement = statement.where(ApiHistory.project_id == query.project_id)
        if hasattr(query, 'api_id') and query.api_id:
            statement = statement.where(ApiHistory.api_info_id == query.api_id)
        if hasattr(query, 'case_id') and query.case_id:
            statement = statement.where(ApiHistory.case_info_id == query.case_id)
        if hasattr(query, 'test_status') and query.test_status:
            statement = statement.where(ApiHistory.test_status == query.test_status)
        if hasattr(query, 'start_time') and query.start_time:
            statement = statement.where(ApiHistory.create_time >= query.start_time)
        if hasattr(query, 'end_time') and query.end_time:
            statement = statement.where(ApiHistory.create_time <= query.end_time)

        # 排序
        statement = statement.order_by(desc(ApiHistory.create_time))
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()

        # 统计总数
        count_statement = select(ApiHistory)
        if query.project_id:
            count_statement = count_statement.where(ApiHistory.project_id == query.project_id)
        if hasattr(query, 'api_id') and query.api_id:
            count_statement = count_statement.where(ApiHistory.api_info_id == query.api_id)
        if hasattr(query, 'case_id') and query.case_id:
            count_statement = count_statement.where(ApiHistory.case_info_id == query.case_id)
        if hasattr(query, 'test_status') and query.test_status:
            count_statement = count_statement.where(ApiHistory.test_status == query.test_status)
        if hasattr(query, 'start_time') and query.start_time:
            count_statement = count_statement.where(ApiHistory.create_time >= query.start_time)
        if hasattr(query, 'end_time') and query.end_time:
            count_statement = count_statement.where(ApiHistory.create_time <= query.end_time)
        total = len(session.exec(count_statement).all())

        return list(datas), total

    @staticmethod
    def query_by_id(session: Session, id: int) -> Optional[ApiHistory]:
        """根据ID查询历史记录"""
        return session.get(ApiHistory, id)

    @staticmethod
    def create(session: Session, history_data: Dict[str, Any]) -> ApiHistory:
        """创建历史记录"""
        data = ApiHistory(
            **history_data,
            create_time=datetime.now()
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @staticmethod
    def update(session: Session, history_data: Dict[str, Any]) -> Optional[ApiHistory]:
        """更新历史记录"""
        statement = select(ApiHistory).where(ApiHistory.id == history_data.get('id'))
        db_history = session.exec(statement).first()
        if not db_history:
            return None

        update_data = {k: v for k, v in history_data.items() if k != 'id' and v is not None}
        for key, value in update_data.items():
            setattr(db_history, key, value)

        session.commit()
        return db_history

    @staticmethod
    def delete(session: Session, id: int) -> bool:
        """删除历史记录"""
        history = session.get(ApiHistory, id)
        if not history:
            return False

        session.delete(history)
        session.commit()
        return True

    @staticmethod
    def query_by_project(session: Session, project_id: int, limit: int = 100) -> List[ApiHistory]:
        """查询项目的历史记录"""
        statement = select(ApiHistory).where(
            ApiHistory.project_id == project_id
        ).order_by(desc(ApiHistory.create_time)).limit(limit)

        return list(session.exec(statement).all())

    @staticmethod
    def query_by_api(session: Session, api_id: int, limit: int = 50) -> List[ApiHistory]:
        """查询指定接口的历史记录"""
        statement = select(ApiHistory).where(
            ApiHistory.api_info_id == api_id
        ).order_by(desc(ApiHistory.create_time)).limit(limit)

        return list(session.exec(statement).all())

    @staticmethod
    def query_by_case(session: Session, case_id: int, limit: int = 50) -> List[ApiHistory]:
        """查询指定用例的历史记录"""
        statement = select(ApiHistory).where(
            ApiHistory.case_info_id == case_id
        ).order_by(desc(ApiHistory.create_time)).limit(limit)

        return list(session.exec(statement).all())

    @staticmethod
    def batch_delete(session: Session, history_ids: List[int]) -> int:
        """批量删除历史记录"""
        deleted_count = 0
        for history_id in history_ids:
            history = session.get(ApiHistory, history_id)
            if history:
                session.delete(history)
                deleted_count += 1

        if deleted_count > 0:
            session.commit()

        return deleted_count

    @staticmethod
    def clean_old_records(session: Session, project_id: int, days: int = 30) -> int:
        """清理旧的历史记录"""
        cutoff_date = datetime.now() - timedelta(days=days)

        old_records = session.exec(
            select(ApiHistory).where(
                and_(
                    ApiHistory.project_id == project_id,
                    ApiHistory.create_time < cutoff_date
                )
            )
        ).all()

        deleted_count = 0
        for record in old_records:
            session.delete(record)
            deleted_count += 1

        if deleted_count > 0:
            session.commit()

        return deleted_count

    @staticmethod
    def get_statistics(session: Session, project_id: int, days: int = 7) -> Dict[str, Any]:
        """获取历史统计信息"""
        start_date = datetime.now() - timedelta(days=days)

        # 总执行次数
        total_statement = select(ApiHistory).where(
            and_(
                ApiHistory.project_id == project_id,
                ApiHistory.create_time >= start_date
            )
        )
        total_executions = len(session.exec(total_statement).all())

        # 成功/失败统计
        success_count = len(session.exec(
            select(ApiHistory).where(
                and_(
                    ApiHistory.project_id == project_id,
                    ApiHistory.create_time >= start_date,
                    ApiHistory.test_status == 'success'
                )
            )
        ).all())

        failure_count = len(session.exec(
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

            day_count = len(session.exec(
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
        response_times = session.exec(
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
