"""
Cost Quota Schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date


class CostQuotaBase(BaseModel):
    """配额基础模型"""
    monthly_limit: float = Field(..., ge=0, description="每月限额（元）")
    reset_day: int = Field(1, description="每月重置日期（1-31）")
    alert_threshold: float = Field(0.8, ge=0, le=1.0, description="预警阈值（百分比）")
    overage_enabled: bool = False
    overage_rate: float = Field(1.5, ge=1.0, description="超额费率倍数")


class CostQuotaCreate(CostQuotaBase):
    """创建配额"""
    agent_id: int
    user_id: int


class CostQuotaUpdate(CostQuotaBase):
    """更新配额"""
    monthly_limit: Optional[float] = None
    current_usage: Optional[float] = None
    alert_threshold: Optional[float] = None
    overage_enabled: Optional[bool] = None
    overage_rate: Optional[float] = None
    is_active: Optional[bool] = None


class CostQuotaResponse(CostQuotaBase):
    """配额响应"""
    id: int
    agent_id: int
    user_id: int
    monthly_limit: float
    current_usage: float
    reset_day: int
    alert_threshold: float
    alert_enabled: bool
    overage_enabled: bool
    overage_rate: float
    is_active: bool
    created_at: str
    updated_at: str
    current_percent: float = Field(0.0, description="当前使用百分比")
    is_warning: bool = Field(False, description="是否预警")
    is_critical: bool = Field(False, description="是否严重超限")


class UsageAlertResponse(BaseModel):
    """预警记录响应"""
    id: int
    quota_id: int
    agent_id: int
    user_id: int
    usage_type: str
    current_usage: float
    threshold: float
    status: str
    message: str
    alert_sent: bool
    created_at: str


class InvoiceCreate(BaseModel):
    """创建发票"""
    user_id: int
    billing_period: str
    start_date: date
    end_date: date
    total_cost: float = Field(..., ge=0, description="总成本")
    notes: Optional[str] = None


class InvoiceUpdate(BaseModel):
    """更新发票"""
    status: Optional[str] = None
    paid_amount: Optional[float] = None
    invoice_url: Optional[str] = None


class InvoiceResponse(BaseModel):
    """发票响应"""
    id: int
    user_id: int
    billing_period: str
    start_date: date
    end_date: date
    total_cost: float
    paid_amount: float
    status: str
    invoice_url: Optional[str] = None
    created_at: str
    updated_at: str


# 导出所有 Schema
__all__ = [
    "CostQuotaBase",
    "CostQuotaCreate",
    "CostQuotaUpdate",
    "CostQuotaResponse",
    "UsageAlertResponse",
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceResponse"
]
