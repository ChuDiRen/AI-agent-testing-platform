"""
操作日志服务 - 记录用户操作和系统事件
"""
from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select

from models.operation_log import OperationLog, OperationType
from core.logger import setup_logger

logger = setup_logger(__name__)


class OperationLogService:
    """操作日志服务"""

    def __init__(self, db: Session):
        self.db = db

    def log_operation(
        self,
        user_id: Optional[int],
        operation_type: OperationType,
        module: str,
        operation_name: str,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> OperationLog:
        """
        记录操作日志

        Args:
            user_id: 用户ID
            operation_type: 操作类型
            module: 模块名称
            operation_name: 操作名称
            details: 操作详情
            ip_address: IP地址
            user_agent: 用户代理
            status: 状态
            error_message: 错误信息

        Returns:
            操作日志记录
        """
        log = OperationLog(
            user_id=user_id,
            operation_type=operation_type,
            module=module,
            operation_name=operation_name,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message
        )

        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)

        logger.info(
            f"操作日志: user_id={user_id}, operation={operation_name}, "
            f"module={module}, status={status}"
        )

        return log

    def get_user_logs(
        self,
        user_id: int,
        operation_type: Optional[OperationType] = None,
        module: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[OperationLog]:
        """
        获取用户操作日志

        Args:
            user_id: 用户ID
            operation_type: 操作类型
            module: 模块名称
            skip: 跳过数量
            limit: 返回数量

        Returns:
            操作日志列表
        """
        query = select(OperationLog).where(OperationLog.user_id == user_id)

        if operation_type:
            query = query.where(OperationLog.operation_type == operation_type)
        if module:
            query = query.where(OperationLog.module == module)

        return self.db.exec(
            query.order_by(OperationLog.create_time.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_logs(
        self,
        operation_type: Optional[OperationType] = None,
        module: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[OperationLog]:
        """
        获取操作日志（支持多条件过滤）

        Args:
            operation_type: 操作类型
            module: 模块名称
            status: 状态
            start_date: 开始日期
            end_date: 结束日期
            skip: 跳过数量
            limit: 返回数量

        Returns:
            操作日志列表
        """
        query = select(OperationLog)

        if operation_type:
            query = query.where(OperationLog.operation_type == operation_type)
        if module:
            query = query.where(OperationLog.module == module)
        if status:
            query = query.where(OperationLog.status == status)
        if start_date:
            query = query.where(OperationLog.create_time >= start_date)
        if end_date:
            query = query.where(OperationLog.create_time <= end_date)

        return self.db.exec(
            query.order_by(OperationLog.create_time.desc())
            .offset(skip)
            .limit(limit)
        ).all()

    def get_operation_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        获取操作统计

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            统计字典
        """
        query = select(OperationLog)

        if start_date:
            query = query.where(OperationLog.create_time >= start_date)
        if end_date:
            query = query.where(OperationLog.create_time <= end_date)

        logs = self.db.exec(query).all()

        # 统计
        total = len(logs)
        success_count = sum(1 for log in logs if log.status == "success")
        error_count = sum(1 for log in logs if log.status == "error")

        # 按操作类型统计
        operation_type_stats = {}
        for log in logs:
            op_type = log.operation_type.value
            operation_type_stats[op_type] = operation_type_stats.get(op_type, 0) + 1

        # 按模块统计
        module_stats = {}
        for log in logs:
            mod = log.module
            module_stats[mod] = module_stats.get(mod, 0) + 1

        # 按用户统计
        user_stats = {}
        for log in logs:
            uid = log.user_id
            if uid:
                user_stats[uid] = user_stats.get(uid, 0) + 1

        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "summary": {
                "total": total,
                "success": success_count,
                "error": error_count,
                "success_rate": success_count / total if total > 0 else 0.0
            },
            "by_operation_type": operation_type_stats,
            "by_module": module_stats,
            "top_users": sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        }

    def count_logs(
        self,
        operation_type: Optional[OperationType] = None,
        module: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        统计日志数量

        Args:
            operation_type: 操作类型
            module: 模块名称
            status: 状态
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            日志数量
        """
        query = select(OperationLog)

        if operation_type:
            query = query.where(OperationLog.operation_type == operation_type)
        if module:
            query = query.where(OperationLog.module == module)
        if status:
            query = query.where(OperationLog.status == status)
        if start_date:
            query = query.where(OperationLog.create_time >= start_date)
        if end_date:
            query = query.where(OperationLog.create_time <= end_date)

        return len(self.db.exec(query).all())
