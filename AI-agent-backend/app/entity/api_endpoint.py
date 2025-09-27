# Copyright (c) 2025 左岚. All rights reserved.
"""
API端点实体
定义API接口管理的数据模型
"""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship

from .base import BaseEntity


class ApiMethod(str, Enum):
    """API请求方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ApiStatus(str, Enum):
    """API状态枚举"""
    ACTIVE = "active"  # 激活
    INACTIVE = "inactive"  # 未激活
    DEPRECATED = "deprecated"  # 已废弃
    MAINTENANCE = "maintenance"  # 维护中


class ApiEndpoint(BaseEntity):
    """
    API端点实体类
    定义API接口的基本信息和统计数据
    """
    __tablename__ = "api_endpoint"
    __allow_unmapped__ = True  # 允许未映射的注解

    # API路径 - 必填，最大500个字符
    path = Column(String(500), nullable=False, comment="API路径")

    # API方法 - 必填，使用枚举值
    method = Column(String(10), nullable=False, comment="HTTP方法")

    # API名称 - 必填，最大100个字符
    name = Column(String(100), nullable=False, comment="API名称")

    # API描述 - 可选，文本类型
    description = Column(Text, nullable=True, comment="API描述")

    # API状态 - 必填，使用枚举值
    status = Column(String(20), nullable=False, default=ApiStatus.ACTIVE.value, comment="API状态")

    # 所属模块 - 可选，最大100个字符
    module = Column(String(100), nullable=True, comment="所属模块")

    # 权限标识 - 可选，最大100个字符
    permission = Column(String(100), nullable=True, comment="权限标识")

    # API版本 - 可选，最大20个字符
    version = Column(String(20), nullable=True, default="v1", comment="API版本")

    # 请求参数示例 - JSON格式存储
    request_example = Column(JSON, nullable=True, comment="请求参数示例")

    # 响应示例 - JSON格式存储
    response_example = Column(JSON, nullable=True, comment="响应示例")

    # 访问统计
    total_calls = Column(Integer, default=0, comment="总调用次数")
    success_calls = Column(Integer, default=0, comment="成功调用次数")
    error_calls = Column(Integer, default=0, comment="错误调用次数")

    # 性能统计
    avg_response_time = Column(Float, default=0.0, comment="平均响应时间(ms)")
    max_response_time = Column(Float, default=0.0, comment="最大响应时间(ms)")
    min_response_time = Column(Float, default=0.0, comment="最小响应时间(ms)")

    # 最后调用时间
    last_called_at = Column(DateTime, nullable=True, comment="最后调用时间")

    # 创建者ID - 外键关联用户表
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False, comment="创建者ID")

    # 关联关系
    # API-创建者关联
    creator = relationship("User", foreign_keys=[created_by_id])

    def __init__(self, path: str, method: str, name: str, description: str = None,
                 module: str = None, permission: str = None, version: str = "v1",
                 request_example: Dict[str, Any] = None, response_example: Dict[str, Any] = None,
                 created_by_id: int = None):
        """
        初始化API端点

        Args:
            path: API路径
            method: HTTP方法
            name: API名称
            description: API描述
            module: 所属模块
            permission: 权限标识
            version: API版本
            request_example: 请求参数示例
            response_example: 响应示例
            created_by_id: 创建者ID
        """
        self.path = path
        self.method = method
        self.name = name
        self.description = description
        self.status = ApiStatus.ACTIVE.value
        self.module = module
        self.permission = permission
        self.version = version
        self.request_example = request_example or {}
        self.response_example = response_example or {}
        self.created_by_id = created_by_id
        self.total_calls = 0
        self.success_calls = 0
        self.error_calls = 0
        self.avg_response_time = 0.0
        self.max_response_time = 0.0
        self.min_response_time = 0.0

    def is_active(self) -> bool:
        """判断API是否激活"""
        return self.status == ApiStatus.ACTIVE.value

    def is_deprecated(self) -> bool:
        """判断API是否已废弃"""
        return self.status == ApiStatus.DEPRECATED.value

    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_calls == 0:
            return 0.0
        return (self.success_calls / self.total_calls) * 100

    def update_stats(self, success: bool, response_time: float):
        """更新统计数据"""
        self.total_calls += 1
        self.last_called_at = datetime.utcnow()
        
        if success:
            self.success_calls += 1
        else:
            self.error_calls += 1
        
        # 更新响应时间统计
        if self.total_calls == 1:
            self.avg_response_time = response_time
            self.max_response_time = response_time
            self.min_response_time = response_time
        else:
            # 计算新的平均响应时间
            total_time = self.avg_response_time * (self.total_calls - 1) + response_time
            self.avg_response_time = total_time / self.total_calls
            
            # 更新最大最小响应时间
            if response_time > self.max_response_time:
                self.max_response_time = response_time
            if response_time < self.min_response_time:
                self.min_response_time = response_time

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "id": self.id,
            "path": self.path,
            "method": self.method,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "module": self.module,
            "permission": self.permission,
            "version": self.version,
            "request_example": self.request_example,
            "response_example": self.response_example,
            "total_calls": self.total_calls,
            "success_calls": self.success_calls,
            "error_calls": self.error_calls,
            "success_rate": self.get_success_rate(),
            "avg_response_time": self.avg_response_time,
            "max_response_time": self.max_response_time,
            "min_response_time": self.min_response_time,
            "last_called_at": self.last_called_at.isoformat() if self.last_called_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by_id": self.created_by_id
        }
