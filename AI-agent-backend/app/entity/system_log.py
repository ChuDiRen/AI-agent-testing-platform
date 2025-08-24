# Copyright (c) 2025 左岚. All rights reserved.
"""
系统日志实体类
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.sql import func

from app.db.base import Base


class SystemLog(Base):
    """
    系统日志实体类
    
    用于记录系统运行过程中的各种日志信息
    """
    
    __tablename__ = "system_logs"
    
    # 基础字段
    id = Column(Integer, primary_key=True, index=True, comment="日志ID")
    timestamp = Column(DateTime, default=func.now(), nullable=False, comment="时间戳")
    level = Column(String(20), nullable=False, comment="日志级别")
    module = Column(String(100), nullable=False, comment="模块名称")
    message = Column(Text, nullable=False, comment="日志消息")
    
    # 用户相关
    user = Column(String(100), nullable=True, comment="用户名")
    user_id = Column(Integer, nullable=True, comment="用户ID")
    
    # 请求相关
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(Text, nullable=True, comment="用户代理")
    request_method = Column(String(10), nullable=True, comment="请求方法")
    request_url = Column(String(500), nullable=True, comment="请求URL")
    
    # 详细信息
    details = Column(Text, nullable=True, comment="详细信息")
    stack_trace = Column(Text, nullable=True, comment="堆栈跟踪")
    
    # 创建时间
    create_time = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    
    # 创建索引
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_level', 'level'),
        Index('idx_module', 'module'),
        Index('idx_user', 'user'),
        Index('idx_create_time', 'create_time'),
        {'comment': '系统日志表'}
    )
    
    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            日志信息字典
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "level": self.level,
            "module": self.module,
            "message": self.message,
            "user": self.user,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_method": self.request_method,
            "request_url": self.request_url,
            "details": self.details,
            "stack_trace": self.stack_trace,
            "create_time": self.create_time.isoformat() if self.create_time else None
        }
    
    def __repr__(self):
        """
        字符串表示
        """
        return f"<SystemLog(id={self.id}, level='{self.level}', module='{self.module}', message='{self.message[:50]}...')>"
    
    @classmethod
    def create_log(
        cls,
        level: str,
        module: str,
        message: str,
        user: Optional[str] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_url: Optional[str] = None,
        details: Optional[str] = None,
        stack_trace: Optional[str] = None
    ) -> "SystemLog":
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
            stack_trace: 堆栈跟踪
            
        Returns:
            系统日志实例
        """
        return cls(
            level=level,
            module=module,
            message=message,
            user=user,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_url=request_url,
            details=details,
            stack_trace=stack_trace
        )
