# Copyright (c) 2025 左岚. All rights reserved.
"""
审计日志Repository
提供审计日志的数据访问功能
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.entity.audit_log import AuditLog
from app.repository.base import BaseRepository

logger = get_logger(__name__)


class AuditLogRepository(BaseRepository[AuditLog]):
    """
    审计日志Repository
    提供审计日志的CRUD操作和查询功能
    """

    def __init__(self, db: Session):
        super().__init__(db, AuditLog)
        self.logger = get_logger(self.__class__.__name__)

    def create_audit_log(
        self, user_id: Optional[int], username: Optional[str], operation_type: str,
        resource_type: str, resource_id: Optional[str], resource_name: Optional[str],
        operation_desc: str, request_method: Optional[str], request_url: Optional[str],
        request_params: Optional[str], response_status: Optional[int],
        response_message: Optional[str], ip_address: Optional[str],
        user_agent: Optional[str], execution_time: Optional[int],
        is_success: int = 1, error_message: Optional[str] = None,
        before_data: Optional[str] = None, after_data: Optional[str] = None
    ) -> AuditLog:
        """
        创建审计日志记录
        
        Args:
            user_id: 操作用户ID
            username: 操作用户名
            operation_type: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            operation_desc: 操作描述
            request_method: 请求方法
            request_url: 请求URL
            request_params: 请求参数
            response_status: 响应状态码
            response_message: 响应消息
            ip_address: IP地址
            user_agent: 用户代理
            execution_time: 执行时间
            is_success: 是否成功
            error_message: 错误信息
            before_data: 操作前数据
            after_data: 操作后数据
            
        Returns:
            创建的审计日志对象
        """
        try:
            audit_log = AuditLog(
                USER_ID=user_id,
                USERNAME=username,
                OPERATION_TYPE=operation_type,
                RESOURCE_TYPE=resource_type,
                RESOURCE_ID=resource_id,
                RESOURCE_NAME=resource_name,
                OPERATION_DESC=operation_desc,
                REQUEST_METHOD=request_method,
                REQUEST_URL=request_url,
                REQUEST_PARAMS=request_params,
                RESPONSE_STATUS=response_status,
                RESPONSE_MESSAGE=response_message,
                IP_ADDRESS=ip_address,
                USER_AGENT=user_agent,
                EXECUTION_TIME=execution_time,
                OPERATION_TIME=datetime.utcnow(),
                IS_SUCCESS=is_success,
                ERROR_MESSAGE=error_message,
                BEFORE_DATA=before_data,
                AFTER_DATA=after_data
            )
            
            return self.create(audit_log)
            
        except Exception as e:
            self.logger.error(f"Create audit log error: {str(e)}")
            raise

    def get_audit_logs_by_user(
        self, user_id: int, page: int = 1, size: int = 20
    ) -> tuple[List[AuditLog], int]:
        """
        根据用户ID获取审计日志
        
        Args:
            user_id: 用户ID
            page: 页码
            size: 每页大小
            
        Returns:
            审计日志列表和总数
        """
        try:
            query = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.user_id == user_id,
                    AuditLog.is_deleted == 0
                )
            ).order_by(desc(AuditLog.OPERATION_TIME))
            
            total = query.count()
            logs = query.offset((page - 1) * size).limit(size).all()
            
            return logs, total
            
        except Exception as e:
            self.logger.error(f"Get audit logs by user error: {str(e)}")
            return [], 0

    def get_audit_logs_by_operation_type(
        self, operation_type: str, page: int = 1, size: int = 20
    ) -> tuple[List[AuditLog], int]:
        """
        根据操作类型获取审计日志
        
        Args:
            operation_type: 操作类型
            page: 页码
            size: 每页大小
            
        Returns:
            审计日志列表和总数
        """
        try:
            query = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.OPERATION_TYPE == operation_type,
                    AuditLog.is_deleted == 0
                )
            ).order_by(desc(AuditLog.OPERATION_TIME))
            
            total = query.count()
            logs = query.offset((page - 1) * size).limit(size).all()
            
            return logs, total
            
        except Exception as e:
            self.logger.error(f"Get audit logs by operation type error: {str(e)}")
            return [], 0

    def get_audit_logs_by_resource_type(
        self, resource_type: str, page: int = 1, size: int = 20
    ) -> tuple[List[AuditLog], int]:
        """
        根据资源类型获取审计日志
        
        Args:
            resource_type: 资源类型
            page: 页码
            size: 每页大小
            
        Returns:
            审计日志列表和总数
        """
        try:
            query = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.RESOURCE_TYPE == resource_type,
                    AuditLog.is_deleted == 0
                )
            ).order_by(desc(AuditLog.OPERATION_TIME))
            
            total = query.count()
            logs = query.offset((page - 1) * size).limit(size).all()
            
            return logs, total
            
        except Exception as e:
            self.logger.error(f"Get audit logs by resource type error: {str(e)}")
            return [], 0

    def get_audit_logs_by_time_range(
        self, start_time: datetime, end_time: datetime,
        page: int = 1, size: int = 20
    ) -> tuple[List[AuditLog], int]:
        """
        根据时间范围获取审计日志
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            page: 页码
            size: 每页大小
            
        Returns:
            审计日志列表和总数
        """
        try:
            query = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).order_by(desc(AuditLog.OPERATION_TIME))
            
            total = query.count()
            logs = query.offset((page - 1) * size).limit(size).all()
            
            return logs, total
            
        except Exception as e:
            self.logger.error(f"Get audit logs by time range error: {str(e)}")
            return [], 0

    def search_audit_logs(
        self, filters: Dict[str, Any], page: int = 1, size: int = 20
    ) -> tuple[List[AuditLog], int]:
        """
        搜索审计日志
        
        Args:
            filters: 搜索条件字典
            page: 页码
            size: 每页大小
            
        Returns:
            审计日志列表和总数
        """
        try:
            query = self.db.query(AuditLog).filter(AuditLog.is_deleted == 0)
            
            # 用户ID过滤
            if filters.get('user_id'):
                query = query.filter(AuditLog.user_id == filters['user_id'])
            
            # 用户名过滤
            if filters.get('username'):
                query = query.filter(AuditLog.username.like(f"%{filters['username']}%"))
            
            # 操作类型过滤
            if filters.get('operation_type'):
                query = query.filter(AuditLog.OPERATION_TYPE == filters['operation_type'])
            
            # 资源类型过滤
            if filters.get('resource_type'):
                query = query.filter(AuditLog.RESOURCE_TYPE == filters['resource_type'])
            
            # IP地址过滤
            if filters.get('ip_address'):
                query = query.filter(AuditLog.IP_ADDRESS == filters['ip_address'])
            
            # 成功状态过滤
            if filters.get('is_success') is not None:
                query = query.filter(AuditLog.IS_SUCCESS == filters['is_success'])
            
            # 时间范围过滤
            if filters.get('start_time'):
                query = query.filter(AuditLog.OPERATION_TIME >= filters['start_time'])
            
            if filters.get('end_time'):
                query = query.filter(AuditLog.OPERATION_TIME <= filters['end_time'])
            
            # 关键词搜索
            if filters.get('keyword'):
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    or_(
                        AuditLog.OPERATION_DESC.like(keyword),
                        AuditLog.RESOURCE_NAME.like(keyword),
                        AuditLog.REQUEST_URL.like(keyword)
                    )
                )
            
            query = query.order_by(desc(AuditLog.OPERATION_TIME))
            
            total = query.count()
            logs = query.offset((page - 1) * size).limit(size).all()
            
            return logs, total
            
        except Exception as e:
            self.logger.error(f"Search audit logs error: {str(e)}")
            return [], 0

    def get_operation_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        获取操作统计信息
        
        Args:
            days: 统计天数
            
        Returns:
            统计信息字典
        """
        try:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=days)
            
            # 总操作数
            total_operations = self.db.query(func.count(AuditLog.LOG_ID)).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).scalar()
            
            # 成功操作数
            success_operations = self.db.query(func.count(AuditLog.LOG_ID)).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.IS_SUCCESS == 1,
                    AuditLog.is_deleted == 0
                )
            ).scalar()
            
            # 失败操作数
            failed_operations = total_operations - success_operations
            
            # 按操作类型统计
            operation_type_stats = self.db.query(
                AuditLog.OPERATION_TYPE,
                func.count(AuditLog.LOG_ID).label('count')
            ).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).group_by(AuditLog.OPERATION_TYPE).all()
            
            # 按资源类型统计
            resource_type_stats = self.db.query(
                AuditLog.RESOURCE_TYPE,
                func.count(AuditLog.LOG_ID).label('count')
            ).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.is_deleted == 0
                )
            ).group_by(AuditLog.RESOURCE_TYPE).all()
            
            # 活跃用户统计
            active_users = self.db.query(
                func.count(func.distinct(AuditLog.user_id))
            ).filter(
                and_(
                    AuditLog.OPERATION_TIME >= start_time,
                    AuditLog.OPERATION_TIME <= end_time,
                    AuditLog.user_id.isnot(None),
                    AuditLog.is_deleted == 0
                )
            ).scalar()
            
            return {
                'total_operations': total_operations or 0,
                'success_operations': success_operations or 0,
                'failed_operations': failed_operations or 0,
                'success_rate': round((success_operations / total_operations * 100), 2) if total_operations > 0 else 0,
                'active_users': active_users or 0,
                'operation_type_stats': [
                    {'type': stat.OPERATION_TYPE, 'count': stat.count}
                    for stat in operation_type_stats
                ],
                'resource_type_stats': [
                    {'type': stat.RESOURCE_TYPE, 'count': stat.count}
                    for stat in resource_type_stats
                ],
                'period': f'{days}天',
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Get operation statistics error: {str(e)}")
            return {}

    def cleanup_old_logs(self, days: int = 90) -> int:
        """
        清理旧的审计日志
        
        Args:
            days: 保留天数
            
        Returns:
            清理的记录数
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # 软删除旧记录
            updated_count = self.db.query(AuditLog).filter(
                and_(
                    AuditLog.OPERATION_TIME < cutoff_time,
                    AuditLog.is_deleted == 0
                )
            ).update({
                'is_deleted': 1,
                'updated_at': datetime.utcnow()
            })
            
            self.db.commit()
            
            self.logger.info(f"Cleaned up {updated_count} old audit logs")
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Cleanup old logs error: {str(e)}")
            self.db.rollback()
            return 0