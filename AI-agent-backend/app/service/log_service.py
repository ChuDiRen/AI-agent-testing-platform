# Copyright (c) 2025 左岚. All rights reserved.
"""
日志Service
处理日志相关的业务逻辑
"""

import math
from datetime import datetime
from typing import Optional

from sqlalchemy import func, and_, or_, desc
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.dto.log_dto import (
    LogQueryRequest,
    LogResponse,
    LogListResponse,
    LogStatsResponse,
    LogLevel
)
from app.entity.system_log import SystemLog

logger = get_logger(__name__)


class LogService:
    """
    日志服务类
    提供日志相关的业务逻辑
    """

    def __init__(self, db: Session):
        self.db = db

    def query_logs(self, query_request: LogQueryRequest) -> LogListResponse:
        """
        查询日志列表
        
        Args:
            query_request: 查询请求参数
            
        Returns:
            日志列表响应
        """
        try:
            # 构建查询条件
            query = self.db.query(SystemLog)
            
            # 日志级别过滤
            if query_request.level:
                query = query.filter(SystemLog.level == query_request.level.value)
            
            # 时间范围过滤
            if query_request.start_time:
                query = query.filter(SystemLog.timestamp >= query_request.start_time)
            if query_request.end_time:
                query = query.filter(SystemLog.timestamp <= query_request.end_time)
            
            # 关键词搜索
            if query_request.keyword:
                keyword = f"%{query_request.keyword}%"
                query = query.filter(
                    or_(
                        SystemLog.message.like(keyword),
                        SystemLog.details.like(keyword)
                    )
                )
            
            # 模块过滤
            if query_request.module:
                query = query.filter(SystemLog.module == query_request.module)
            
            # 用户过滤
            if query_request.user:
                query = query.filter(SystemLog.user == query_request.user)
            
            # 获取总数
            total = query.count()
            
            # 分页
            offset = (query_request.page - 1) * query_request.size
            logs = query.order_by(desc(SystemLog.timestamp)).offset(offset).limit(query_request.size).all()
            
            # 转换为响应格式
            log_responses = []
            for log in logs:
                log_responses.append(LogResponse(
                    id=log.id,
                    timestamp=log.timestamp,
                    level=LogLevel(log.level),
                    module=log.module,
                    message=log.message,
                    user=log.user,
                    ip_address=log.ip_address,
                    user_agent=log.user_agent,
                    details=log.details
                ))
            
            # 计算总页数
            pages = math.ceil(total / query_request.size) if total > 0 else 0
            
            return LogListResponse(
                items=log_responses,
                total=total,
                page=query_request.page,
                size=query_request.size,
                pages=pages
            )
            
        except Exception as e:
            logger.error(f"Error querying logs: {str(e)}")
            raise Exception("查询日志失败")

    def get_log_by_id(self, log_id: int) -> Optional[LogResponse]:
        """
        根据ID获取日志详情
        
        Args:
            log_id: 日志ID
            
        Returns:
            日志详情
        """
        try:
            log = self.db.query(SystemLog).filter(SystemLog.id == log_id).first()
            if not log:
                return None
            
            return LogResponse(
                id=log.id,
                timestamp=log.timestamp,
                level=LogLevel(log.level),
                module=log.module,
                message=log.message,
                user=log.user,
                ip_address=log.ip_address,
                user_agent=log.user_agent,
                details=log.details
            )
            
        except Exception as e:
            logger.error(f"Error getting log by id {log_id}: {str(e)}")
            raise Exception("获取日志详情失败")

    def get_log_stats(self) -> LogStatsResponse:
        """
        获取日志统计信息
        
        Returns:
            日志统计信息
        """
        try:
            # 总日志数
            total_count = self.db.query(func.count(SystemLog.id)).scalar() or 0
            
            # 各级别日志数量
            debug_count = self.db.query(func.count(SystemLog.id)).filter(SystemLog.level == 'DEBUG').scalar() or 0
            info_count = self.db.query(func.count(SystemLog.id)).filter(SystemLog.level == 'INFO').scalar() or 0
            warning_count = self.db.query(func.count(SystemLog.id)).filter(SystemLog.level == 'WARNING').scalar() or 0
            error_count = self.db.query(func.count(SystemLog.id)).filter(SystemLog.level == 'ERROR').scalar() or 0
            critical_count = self.db.query(func.count(SystemLog.id)).filter(SystemLog.level == 'CRITICAL').scalar() or 0
            
            # 今日日志数
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            today_count = self.db.query(func.count(SystemLog.id)).filter(
                and_(
                    SystemLog.timestamp >= today_start,
                    SystemLog.timestamp <= today_end
                )
            ).scalar() or 0
            
            return LogStatsResponse(
                total_count=total_count,
                debug_count=debug_count,
                info_count=info_count,
                warning_count=warning_count,
                error_count=error_count,
                critical_count=critical_count,
                today_count=today_count
            )
            
        except Exception as e:
            logger.error(f"Error getting log stats: {str(e)}")
            raise Exception("获取日志统计失败")

    def clear_logs(self, before_date: Optional[datetime] = None) -> int:
        """
        清空日志
        
        Args:
            before_date: 清空指定日期之前的日志，如果为None则清空所有日志
            
        Returns:
            删除的日志数量
        """
        try:
            query = self.db.query(SystemLog)
            
            if before_date:
                query = query.filter(SystemLog.timestamp < before_date)
            
            # 获取要删除的数量
            count = query.count()
            
            # 删除日志
            query.delete()
            self.db.commit()
            
            logger.info(f"Cleared {count} logs")
            return count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error clearing logs: {str(e)}")
            raise Exception("清空日志失败")

    def create_log(
        self,
        level: str,
        module: str,
        message: str,
        user: Optional[str] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_url: Optional[str] = None,
        details: Optional[str] = None
    ) -> SystemLog:
        """
        创建日志记录
        
        Args:
            level: 日志级别
            module: 模块名称
            message: 日志消息
            user: 用户名
            user_id: 用户ID
            ip_address: IP地址
            user_agent: 用户代理
            request_method: 请求方法
            request_url: 请求URL
            details: 详细信息
            
        Returns:
            创建的日志记录
        """
        try:
            log = SystemLog.create_log(
                level=level,
                module=module,
                message=message,
                user=user,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_url=request_url,
                details=details
            )
            
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            
            return log
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating log: {str(e)}")
            raise Exception("创建日志失败")
