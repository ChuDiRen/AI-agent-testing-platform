"""
Pydantic Schemas - 请求/响应模型
"""
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

# 从其他模块导入
from app.schemas.user_schema import LoginRequest, RegisterRequest, TokenResponse, UserCreate, UserUpdate, UserResponse
from app.schemas.batch_schema import (
    BatchDeleteRequest,
    BatchPublishRequest,
    ImportWorkflowRequest,
    ExportWorkflowsRequest,
    LoopNodeSchema,
    SubgraphNodeSchema,
    CostQuotaRequest
)
from app.schemas.billing_schema import (
    CostQuotaBase,
    CostQuotaCreate,
    CostQuotaUpdate,
    CostQuotaResponse,
    UsageAlertResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse
)


# ========== Agent Schemas ==========

class AgentBase(BaseModel):
    """Agent 基础模型"""
    name: str = Field(..., description="Agent 名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Agent 描述")
    type: str = Field(default="chat", description="Agent 类型")
    model: str = Field(default="gpt-3.5-turbo", description="模型名称")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(2048, ge=1, le=128000, description="最大 Token 数")
    prompt_template: Optional[str] = Field(None, description="Prompt 模板")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    tools: Optional[str] = Field(None, description="关联工具列表 (JSON)")


class AgentCreate(AgentBase):
    """创建 Agent"""
    created_by: int = Field(..., description="创建人 ID")


class AgentUpdate(BaseModel):
    """更新 Agent"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=128000)
    prompt_template: Optional[str] = None
    system_prompt: Optional[str] = None
    tools: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    """Agent 响应模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========== Tool Schemas ==========

class ToolBase(BaseModel):
    """Tool 基础模型"""
    name: str = Field(..., description="工具名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="工具描述")
    type: str = Field(..., description="工具类型: http, mcp, builtin")


class ToolCreate(ToolBase):
    """创建 Tool"""
    config: Optional[str] = Field(None, description="工具配置 (JSON)")
    endpoint_url: Optional[str] = Field(None, description="HTTP 工具端点")
    mcp_server: Optional[str] = Field(None, description="MCP 服务器地址")


class ToolUpdate(BaseModel):
    """更新 Tool"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    type: Optional[str] = None
    config: Optional[str] = None
    endpoint_url: Optional[str] = None
    mcp_server: Optional[str] = None
    is_active: Optional[bool] = None


class ToolResponse(ToolBase):
    """Tool 响应模型"""
    id: int
    config: Optional[str] = None
    endpoint_url: Optional[str] = None
    mcp_server: Optional[str] = None
    is_active: bool
    test_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========== Workflow Schemas ==========

class WorkflowBase(BaseModel):
    """Workflow 基础模型"""
    name: str = Field(..., description="Workflow 名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Workflow 描述")


class WorkflowCreate(WorkflowBase):
    """创建 Workflow"""
    graph_data: str = Field(..., description="工作流图数据 (JSON)")
    created_by: int = Field(..., description="创建人 ID")


class WorkflowUpdate(BaseModel):
    """更新 Workflow"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    graph_data: Optional[str] = None
    is_published: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    """Workflow 响应模型"""
    id: int
    graph_data: str
    is_published: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========== Execution Schemas ==========

class ExecutionCreate(BaseModel):
    """创建 Execution"""
    workflow_id: int = Field(..., description="Workflow ID")
    agent_id: int = Field(..., description="Agent ID")
    input_data: Optional[str] = Field(None, description="输入数据 (JSON)")


class ExecutionUpdate(BaseModel):
    """更新 Execution"""
    status: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None


class ExecutionResponse(BaseModel):
    """Execution 响应模型"""
    id: int
    workflow_id: int
    agent_id: int
    status: str
    input_data: Optional[str] = None
    output_data: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        # 添加序列化配置
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ========== Usage Schemas ==========

class UsageResponse(BaseModel):
    """Usage 响应模型"""
    id: int
    execution_id: int
    agent_id: int
    user_id: Optional[int] = None
    tokens_used: int
    execution_time: Optional[int] = None
    api_calls: int
    cost: float
    recorded_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UsageStatsResponse(BaseModel):
    """Usage 统计响应模型"""
    total_executions: int
    total_tokens: int
    total_cost: float
    avg_execution_time: float
    agent_breakdown: List[Dict[str, Any]]


# 导出所有 Schema
__all__ = [
    # Agent Schemas
    "AgentCreate", "AgentUpdate", "AgentResponse",
    # Tool Schemas
    "ToolCreate", "ToolUpdate", "ToolResponse",
    # Workflow Schemas
    "WorkflowCreate", "WorkflowUpdate", "WorkflowResponse",
    # Execution Schemas
    "ExecutionCreate", "ExecutionUpdate", "ExecutionResponse",
    # Usage Schemas
    "UsageResponse", "UsageStatsResponse",
    # User Schemas
    "LoginRequest", "RegisterRequest", "TokenResponse", "UserCreate", "UserUpdate", "UserResponse",
    # Batch Schemas
    "BatchDelete", "BatchPublish", "ImportWorkflow", "ExportWorkflow", "LoopNode", "Subgraph",
    # Billing Schemas
    "CostQuotaBase",
    "CostQuotaCreate",
    "CostQuotaUpdate",
    "CostQuotaResponse",
    "UsageAlertResponse",
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceResponse"
]
