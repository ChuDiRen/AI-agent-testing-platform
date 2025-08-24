# Copyright (c) 2025 左岚. All rights reserved.
"""
审计日志实体
记录用户操作行为和权限变更
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from app.entity.base import BaseEntity


class AuditLog(BaseEntity):
    """
    审计日志表 - t_audit_log
    记录系统中所有重要操作的审计信息
    """
    __tablename__ = "audit_log"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 使用Base类的id作为主键，没有别名
    USER_ID = Column(Integer, nullable=True, comment="操作用户ID")
    USERNAME = Column(String(50), nullable=True, comment="操作用户名")
    OPERATION_TYPE = Column(String(50), nullable=False, comment="操作类型(CREATE/UPDATE/DELETE/LOGIN/LOGOUT)")
    RESOURCE_TYPE = Column(String(50), nullable=False, comment="资源类型(USER/ROLE/MENU/DEPT)")
    RESOURCE_ID = Column(String(100), nullable=True, comment="资源ID")
    RESOURCE_NAME = Column(String(200), nullable=True, comment="资源名称")
    OPERATION_DESC = Column(String(500), nullable=True, comment="操作描述")
    REQUEST_METHOD = Column(String(10), nullable=True, comment="请求方法(GET/POST/PUT/DELETE)")
    REQUEST_URL = Column(String(500), nullable=True, comment="请求URL")
    REQUEST_PARAMS = Column(Text, nullable=True, comment="请求参数(JSON格式)")
    RESPONSE_STATUS = Column(Integer, nullable=True, comment="响应状态码")
    RESPONSE_MESSAGE = Column(Text, nullable=True, comment="响应消息")
    IP_ADDRESS = Column(String(50), nullable=True, comment="客户端IP地址")
    USER_AGENT = Column(String(500), nullable=True, comment="用户代理")
    EXECUTION_TIME = Column(Integer, nullable=True, comment="执行时间(毫秒)")
    OPERATION_TIME = Column(DateTime, default=datetime.utcnow, nullable=False, comment="操作时间")
    IS_SUCCESS = Column(Integer, default=1, comment="是否成功(0:失败,1:成功)")
    ERROR_MESSAGE = Column(Text, nullable=True, comment="错误信息")
    BEFORE_DATA = Column(Text, nullable=True, comment="操作前数据(JSON格式)")
    AFTER_DATA = Column(Text, nullable=True, comment="操作后数据(JSON格式)")

    # 创建索引以提高查询性能
    __table_args__ = (
        Index('idx_audit_user_id', 'USER_ID'),
        Index('idx_audit_operation_type', 'OPERATION_TYPE'),
        Index('idx_audit_resource_type', 'RESOURCE_TYPE'),
        Index('idx_audit_operation_time', 'OPERATION_TIME'),
        Index('idx_audit_ip_address', 'IP_ADDRESS'),
        Index('idx_audit_is_success', 'IS_SUCCESS'),
        {'comment': '审计日志表'}
    )

    @classmethod
    def get_primary_key_name(cls) -> str:
        """获取主键字段名"""
        return "LOG_ID"

    def get_primary_key_value(self):
        """获取主键值"""
        return self.LOG_ID

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'log_id': self.LOG_ID,
            'user_id': self.USER_ID,
            'username': self.USERNAME,
            'operation_type': self.OPERATION_TYPE,
            'resource_type': self.RESOURCE_TYPE,
            'resource_id': self.RESOURCE_ID,
            'resource_name': self.RESOURCE_NAME,
            'operation_desc': self.OPERATION_DESC,
            'request_method': self.REQUEST_METHOD,
            'request_url': self.REQUEST_URL,
            'request_params': self.REQUEST_PARAMS,
            'response_status': self.RESPONSE_STATUS,
            'response_message': self.RESPONSE_MESSAGE,
            'ip_address': self.IP_ADDRESS,
            'user_agent': self.USER_AGENT,
            'execution_time': self.EXECUTION_TIME,
            'operation_time': self.OPERATION_TIME.isoformat() if self.OPERATION_TIME else None,
            'is_success': self.IS_SUCCESS,
            'error_message': self.ERROR_MESSAGE,
            'before_data': self.BEFORE_DATA,
            'after_data': self.AFTER_DATA
        }

    def __repr__(self) -> str:
        return f"<AuditLog(LOG_ID={self.LOG_ID}, USER_ID={self.USER_ID}, OPERATION_TYPE={self.OPERATION_TYPE})>"