"""
Cost Quota 数据模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class CostQuota(Base):
    """成本配额模型"""

    __tablename__ = "cost_quotas"

    id = Column(Integer, primary_key=True, index=True, comment="配额 ID")
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, comment="Agent ID")
    user_id = Column(Integer, ForeignKey("users.id"), comment="用户 ID")
    monthly_limit = Column(Float, default=100.0, comment="每月限额（元）")
    current_usage = Column(Float, default=0.0, comment="当月已用（元）")
    reset_day = Column(Integer, default=1, comment="重置日期（每月的哪一天）")
    alert_threshold = Column(Float, default=0.8, comment="预警阈值（百分比）")
    alert_enabled = Column(Boolean, default=True, comment="是否启用预警")
    overage_enabled = Column(Boolean, default=False, comment="是否启用超额扣费")
    overage_rate = Column(Float, default=1.5, comment="超额费率倍数")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    agent = relationship("Agent", back_populates="quotas")
    user = relationship("User", back_populates="quotas")
    # alerts = relationship("UsageAlert", back_populates="quota")  # 暂时注释，避免错误


class UsageAlert(Base):
    """使用量预警记录"""

    __tablename__ = "usage_alerts"

    id = Column(Integer, primary_key=True, index=True, comment="预警 ID")
    quota_id = Column(Integer, ForeignKey("cost_quotas.id"), nullable=False, comment="配额 ID")
    agent_id = Column(Integer, ForeignKey("agents.id"), comment="Agent ID")
    user_id = Column(Integer, comment="用户 ID")
    usage_type = Column(String(50), default="monthly", comment="使用类型: monthly, daily")
    current_usage = Column(Float, default=0.0, comment="当前使用量")
    threshold = Column(Float, default=0.8, comment="预警阈值（百分比）")
    status = Column(String(20), default="ok", comment="状态: ok, warning, critical, overage")
    alert_sent = Column(Boolean, default=False, comment="是否已发送预警")
    message = Column(Text, comment="预警消息")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    # 关联关系
    # quota = relationship("CostQuota", back_populates="alerts")  # 暂时注释，避免错误


class Invoice(Base):
    """发票模型"""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True, comment="发票 ID")
    user_id = Column(Integer, ForeignKey("users.id"), comment="用户 ID")
    billing_period = Column(String(100), comment="计费周期")
    start_date = Column(Date, comment="开始日期")
    end_date = Column(Date, comment="结束日期")
    total_cost = Column(Float, default=0.0, comment="总成本")
    paid_amount = Column(Float, default=0.0, comment="已付金额")
    status = Column(String(20), default="pending", comment="状态: pending, paid, overdue")
    invoice_url = Column(String(500), comment="发票文件 URL")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关联关系
    user = relationship("User", back_populates="invoices")


# 导出所有模型
__all__ = ["CostQuota", "UsageAlert", "Invoice"]
