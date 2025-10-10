# Copyright (c) 2025 左岚. All rights reserved.
"""
数据驱动测试数据模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ApiEngineDDT(Base):
    """数据驱动测试数据表"""
    __tablename__ = "t_plugin_api_engine_ddt"

    ddt_id = Column(Integer, primary_key=True, autoincrement=True, comment="DDT数据ID")
    case_id = Column(Integer, ForeignKey("t_plugin_api_engine_case.case_id"), nullable=False, comment="关联用例ID")
    name = Column(String(200), nullable=False, comment="数据集名称")
    description = Column(Text, nullable=True, comment="数据集描述")

    # 数据源类型: manual(手动录入) / file(文件上传) / database(数据库查询) / api(API接口)
    data_source_type = Column(String(20), default='manual', comment="数据源类型")

    # 手动录入的数据
    data_content = Column(JSON, nullable=True, comment="测试数据内容(JSON数组)")

    # 文件相关信息
    file_path = Column(String(500), nullable=True, comment="文件路径")
    file_type = Column(String(20), nullable=True, comment="文件类型")

    # 数据库查询信息
    database_query = Column(Text, nullable=True, comment="数据库查询SQL")
    database_config = Column(JSON, nullable=True, comment="数据库配置")

    # API接口信息
    api_url = Column(String(500), nullable=True, comment="API接口URL")
    api_headers = Column(JSON, nullable=True, comment="API请求头")
    api_params = Column(JSON, nullable=True, comment="API请求参数")

    # 执行配置
    execution_mode = Column(String(20), default='sequential', comment="执行模式:sequential/parallel")
    max_parallel = Column(Integer, default=5, comment="最大并行数")

    # 失败处理
    failure_strategy = Column(String(20), default='continue', comment="失败处理策略:continue/stop/retry")
    max_retries = Column(Integer, default=0, comment="最大重试次数")

    # 状态字段
    is_active = Column(String(10), default='yes', comment="是否启用:yes/no")
    sort_order = Column(Integer, default=0, comment="排序序号")

    # 时间字段
    created_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建人ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    case = relationship("ApiEngineCase", back_populates="ddt_datasets")
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<ApiEngineDDT(ddt_id={self.ddt_id}, name='{self.name}', case_id={self.case_id})>"


class ApiEngineDDTExecution(Base):
    """数据驱动测试执行记录表"""
    __tablename__ = "t_plugin_api_engine_ddt_execution"

    execution_id = Column(Integer, primary_key=True, autoincrement=True, comment="执行记录ID")
    ddt_id = Column(Integer, ForeignKey("t_plugin_api_engine_ddt.ddt_id"), nullable=False, comment="DDT数据ID")
    case_id = Column(Integer, ForeignKey("t_plugin_api_engine_case.case_id"), nullable=False, comment="用例ID")

    # 执行批次信息
    batch_id = Column(String(100), nullable=False, comment="执行批次ID")
    data_index = Column(Integer, nullable=False, comment="数据索引")
    data_row = Column(JSON, nullable=True, comment="数据行内容")

    # 执行状态
    status = Column(String(20), default='pending', comment="执行状态:pending/running/success/failed/skipped")

    # 执行结果
    execution_result = Column(JSON, nullable=True, comment="执行结果")
    error_message = Column(Text, nullable=True, comment="错误信息")

    # 性能指标
    execution_time = Column(Integer, nullable=True, comment="执行时间(毫秒)")
    memory_usage = Column(Integer, nullable=True, comment="内存使用(字节)")

    # 时间信息
    started_at = Column(DateTime, nullable=True, comment="开始时间")
    finished_at = Column(DateTime, nullable=True, comment="结束时间")

    # 执行人
    executed_by = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="执行人ID")

    # 关系
    ddt = relationship("ApiEngineDDT")
    case = relationship("ApiEngineCase")
    executor = relationship("User", foreign_keys=[executed_by])

    def __repr__(self):
        return f"<ApiEngineDDTExecution(execution_id={self.execution_id}, ddt_id={self.ddt_id}, status='{self.status}')>"