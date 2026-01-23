"""
数据库模型 - Agent 模型
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Agent(Base):
    """Agent 模型"""

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True, comment="Agent ID")
    name = Column(String(100), nullable=False, comment="Agent 名称")
    description = Column(Text, comment="Agent 描述")
    type = Column(String(50), default="chat", comment="Agent 类型")
    model = Column(String(50), nullable=False, comment="模型名称")
    temperature = Column(Float, default=0.7, comment="温度参数")
    max_tokens = Column(Integer, default=2048, comment="最大 Token 数")
    prompt_template = Column(Text, comment="Prompt 模板")
    system_prompt = Column(Text, comment="系统提示词")
    tools = Column(Text, comment="关联工具列表 (JSON)")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人 ID")

    # 关联关系
    executions = relationship("Execution", back_populates="agent")
    executions_history = relationship("AgentExecution", back_populates="agent")
    quotas = relationship("CostQuota", back_populates="agent")


class Tool(Base):
    """Tool/MCP 工具模型"""

    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, index=True, comment="Tool ID")
    name = Column(String(100), nullable=False, comment="工具名称")
    description = Column(Text, comment="工具描述")
    type = Column(String(50), comment="工具类型: http, mcp, builtin")
    config = Column(Text, comment="工具配置 (JSON)")
    endpoint_url = Column(String(500), comment="HTTP 工具端点")
    mcp_server = Column(String(500), comment="MCP 服务器地址")
    is_active = Column(Boolean, default=True, comment="是否启用")
    test_status = Column(String(20), default="untested", comment="测试状态: untested, passed, failed")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")


class Workflow(Base):
    """Workflow 模型"""

    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True, comment="Workflow ID")
    name = Column(String(100), nullable=False, comment="Workflow 名称")
    description = Column(Text, comment="Workflow 描述")
    graph_data = Column(Text, nullable=False, comment="工作流图数据 (JSON)")
    is_published = Column(Boolean, default=False, comment="是否发布")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人 ID")

    # 关联关系
    executions = relationship("Execution", back_populates="workflow")
    # versions = relationship("WorkflowVersion", back_populates="workflow")  # 暂时注释，避免循环导入


# 从其他模块导入
from app.models.user import User
from app.models.execution import Execution
from app.models.usage import Usage
from app.models.billing import CostQuota, UsageAlert, Invoice
from app.models.workflow_version import WorkflowVersion
from app.models.agent_execution import AgentExecution

# 导出所有模型
__all__ = [
    "User",
    "Agent",
    "Tool",
    "Workflow",
    "WorkflowVersion",
    "Execution",
    "AgentExecution",
    "Usage",
    "CostQuota",
    "UsageAlert",
    "Invoice"
]
