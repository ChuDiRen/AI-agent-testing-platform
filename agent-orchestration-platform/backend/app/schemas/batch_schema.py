"""
批量操作相关 Schemas
"""
from typing import Optional
from pydantic import BaseModel, Field


class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: list[int] = Field(..., min_items=1, description="要删除的 ID 列表")
    reason: Optional[str] = Field(None, description="删除原因")


class BatchPublishRequest(BaseModel):
    """批量发布请求"""
    ids: list[int] = Field(..., min_items=1, description="要发布的 Workflow ID 列表")


class ImportWorkflowRequest(BaseModel):
    """导入 Workflow 请求"""
    data: dict = Field(..., description="Workflow 数据")


class ExportWorkflowsRequest(BaseModel):
    """导出 Workflows 请求"""
    ids: list[int] = Field(..., min_items=1, description="要导出的 Workflow ID 列表")
    format: str = Field("json", description="导出格式：json, yaml")


class LoopNodeSchema(BaseModel):
    """循环节点 Schema"""
    type: str = Field("loop", description="节点类型: loop")
    iterations: int = Field(..., ge=1, description="循环次数")
    condition: str = Field(..., description="循环条件表达式")
    action: str = Field(..., description="每次循环执行的操作")


class SubgraphNodeSchema(BaseModel):
    """子图节点 Schema"""
    type: str = Field("subgraph", description="节点类型: subgraph")
    sub_workflow_id: int = Field(..., description="子 Workflow ID")
    condition: str = Field(..., description="触发条件表达式")


class ConditionNodeSchema(BaseModel):
    """条件节点 Schema"""
    type: str = Field("condition", description="节点类型: condition")
    condition: str = Field(..., description="条件表达式")
    true_action: str = Field(..., description="条件为真时执行的操作")
    false_action: Optional[str] = Field(None, description="条件为假时执行的操作")


class CostQuotaRequest(BaseModel):
    """成本配额管理请求"""
    agent_id: int = Field(..., description="Agent ID")
    monthly_limit: float = Field(..., description="每月成本限制")
    alert_threshold: float = Field(..., description="预警阈值（百分比）")
    notification_enabled: bool = Field(True, description="是否启用通知")


# 导出所有 Schema
__all__ = [
    "BatchDeleteRequest",
    "BatchPublishRequest",
    "ImportWorkflowRequest",
    "ExportWorkflowsRequest",
    "LoopNodeSchema",
    "SubgraphNodeSchema",
    "ConditionNodeSchema",
    "CostQuotaRequest"
]
