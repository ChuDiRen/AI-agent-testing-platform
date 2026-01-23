"""
Billing API 端点 - 成本配额管理和计费
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.db.session import get_db
from app.models import Usage, Agent, Execution, CostQuota, UsageAlert, Invoice
from app.schemas import (
    UsageStatsResponse,
    CostQuotaCreate,
    CostQuotaUpdate,
    CostQuotaResponse,
    UsageAlertResponse,
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse
)
from app.crud.billing_crud import cost_quota
from app.core.resp_model import RespModel


router = APIRouter(prefix="/Billing", tags=["计费统计"])


# ========== Usage Statistics ==========

@router.get("/usage", response_model=RespModel)
async def get_usage_stats(
    agent_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取使用量统计"""
    # 构建查询条件
    conditions = []
    if agent_id:
        conditions.append(Usage.agent_id == agent_id)
    if start_date:
        conditions.append(Usage.recorded_at >= start_date)
    if end_date:
        conditions.append(Usage.recorded_at <= end_date)

    # 查询数据
    query = select(
        func.count(Usage.id).label("total_executions"),
        func.sum(Usage.tokens_used).label("total_tokens"),
        func.sum(Usage.cost).label("total_cost"),
        func.avg(Usage.execution_time).label("avg_execution_time")
    )

    if conditions:
        query = query.where(and_(*conditions))

    result = await db.execute(query)
    row = result.first()

    return RespModel.ok_resp(data={
        "total_executions": row.total_executions or 0,
        "total_tokens": int(row.total_tokens or 0),
        "total_cost": float(row.total_cost or 0),
        "avg_execution_time": float(row.avg_execution_time or 0)
    })


@router.get("/agent-breakdown", response_model=RespModel)
async def get_agent_breakdown(
    start_date: datetime = Query(default_factory=lambda: datetime.now() - timedelta(days=30)),
    end_date: datetime = Query(default_factory=datetime.now),
    db: AsyncSession = Depends(get_db)
):
    """获取 Agent 使用量统计（按 Agent 分组）"""
    query = (
        select(
            Agent.name.label("agent_name"),
            func.count(Usage.id).label("executions"),
            func.sum(Usage.tokens_used).label("tokens"),
            func.sum(Usage.cost).label("cost")
        )
        .join(Usage, Usage.agent_id == Agent.id)
        .where(and_(
            Usage.recorded_at >= start_date,
            Usage.recorded_at <= end_date
        ))
        .group_by(Agent.id, Agent.name)
        .order_by(func.sum(Usage.cost).desc())
    )

    result = await db.execute(query)
    rows = result.all()

    breakdown = [
        {
            "agent_name": row.agent_name,
            "executions": row.executions,
            "tokens_used": int(row.tokens or 0),
            "cost": float(row.cost or 0)
        }
        for row in rows
    ]

    return RespModel.ok_resp(data=breakdown)


@router.get("/usage/history", response_model=RespModel)
async def get_usage_history(
    agent_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """获取使用量历史记录"""
    query = select(Usage, Agent.name).join(
        Agent, Usage.agent_id == Agent.id
    ).order_by(Usage.recorded_at.desc())

    if agent_id:
        query = query.where(Usage.agent_id == agent_id)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    history = [
        {
            "id": row.Usage.id,
            "execution_id": row.Usage.execution_id,
            "agent_name": row.name,
            "tokens_used": row.Usage.tokens_used,
            "execution_time": row.Usage.execution_time,
            "api_calls": row.Usage.api_calls,
            "cost": row.Usage.cost,
            "recorded_at": row.Usage.recorded_at.isoformat()
        }
        for row in rows
    ]

    total = await db.execute(select(func.count(Usage.id)))
    return RespModel.ok_resp_list(data=history, total=total.scalar() or 0)


# ========== Cost Quota Management ==========

@router.post("/quotas", response_model=RespModel)
async def create_cost_quota(
    quota_in: CostQuotaCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建成本配额"""
    quota = await cost_quota.create(db, obj_in=quota_in)
    return RespModel.ok_resp(data=quota)


@router.get("/quotas/{quota_id}", response_model=RespModel)
async def get_cost_quota(
    quota_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个成本配额"""
    quota = await cost_quota.get(db, id=quota_id)
    if not quota:
        return RespModel.error_resp(message="配额不存在")
    return RespModel.ok_resp(data=quota)


@router.get("/quotas", response_model=RespModel)
async def list_cost_quotas(
    agent_id: Optional[int] = None,
    user_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取成本配额列表"""
    if agent_id:
        quota = await cost_quota.get_by_agent(db, agent_id=agent_id)
        if quota:
            return RespModel.ok_resp_list(data=[quota], total=1)
        return RespModel.ok_resp_list(data=[], total=0)
    elif user_id:
        quota = await cost_quota.get_by_user(db, user_id=user_id)
        if quota:
            return RespModel.ok_resp_list(data=[quota], total=1)
        return RespModel.ok_resp_list(data=[], total=0)
    else:
        quotas = await cost_quota.get_active_quotas(db, skip=skip, limit=limit)
        return RespModel.ok_resp_list(data=quotas)


@router.put("/quotas/{quota_id}", response_model=RespModel)
async def update_cost_quota(
    quota_id: int,
    quota_in: CostQuotaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新成本配额"""
    db_quota = await cost_quota.get(db, id=quota_id)
    if not db_quota:
        return RespModel.error_resp(message="配额不存在")

    quota = await cost_quota.update(db, db_obj=db_quota, obj_in=quota_in)
    return RespModel.ok_resp(data=quota)


@router.delete("/quotas/{quota_id}", response_model=RespModel)
async def delete_cost_quota(
    quota_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除成本配额"""
    db_quota = await cost_quota.get(db, id=quota_id)
    if not db_quota:
        return RespModel.error_resp(message="配额不存在")

    await cost_quota.remove(db, id=quota_id)
    return RespModel.ok_resp(message="配额删除成功")


@router.post("/quotas/{quota_id}/usage", response_model=RespModel)
async def update_quota_usage(
    quota_id: int,
    usage_delta: float,
    db: AsyncSession = Depends(get_db)
):
    """更新配额使用量"""
    quota = await cost_quota.update_current_usage(db, quota_id=quota_id, usage_delta=usage_delta)
    return RespModel.ok_resp(data=quota)


# ========== Invoice Management ==========

@router.post("/invoices", response_model=RespModel)
async def create_invoice(
    invoice_in: InvoiceCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建发票"""
    invoice = Invoice(**invoice_in.model_dump())
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return RespModel.ok_resp(data=invoice)


@router.get("/invoices/{invoice_id}", response_model=RespModel)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个发票"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        return RespModel.error_resp(message="发票不存在")
    return RespModel.ok_resp(data=invoice)


@router.get("/invoices", response_model=RespModel)
async def list_invoices(
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取发票列表"""
    query = select(Invoice)

    if user_id:
        query = query.where(Invoice.user_id == user_id)
    if status:
        query = query.where(Invoice.status == status)

    query = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    invoices = result.scalars().all()

    # 获取总数
    count_query = select(func.count(Invoice.id))
    if user_id:
        count_query = count_query.where(Invoice.user_id == user_id)
    if status:
        count_query = count_query.where(Invoice.status == status)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return RespModel.ok_resp_list(data=invoices, total=total)


@router.put("/invoices/{invoice_id}", response_model=RespModel)
async def update_invoice(
    invoice_id: int,
    invoice_in: InvoiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新发票状态"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    db_invoice = result.scalar_one_or_none()
    if not db_invoice:
        return RespModel.error_resp(message="发票不存在")

    update_data = invoice_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_invoice, field, value)

    await db.commit()
    await db.refresh(db_invoice)
    return RespModel.ok_resp(data=db_invoice)


# ========== Alert Management ==========

@router.get("/alerts", response_model=RespModel)
async def list_usage_alerts(
    quota_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """获取预警记录列表"""
    query = select(UsageAlert)

    if quota_id:
        query = query.where(UsageAlert.quota_id == quota_id)
    if status:
        query = query.where(UsageAlert.status == status)

    query = query.order_by(UsageAlert.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    alerts = result.scalars().all()

    # 获取总数
    count_query = select(func.count(UsageAlert.id))
    if quota_id:
        count_query = count_query.where(UsageAlert.quota_id == quota_id)
    if status:
        count_query = count_query.where(UsageAlert.status == status)

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    return RespModel.ok_resp_list(data=alerts, total=total)


@router.get("/dashboard", response_model=RespModel)
async def get_billing_dashboard(
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取计费仪表板数据"""
    # 总使用量
    total_usage = await db.execute(
        select(func.sum(Usage.cost))
    )
    total_cost = total_usage.scalar() or 0

    # 本月使用量
    from sqlalchemy import cast
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_usage = await db.execute(
        select(func.sum(Usage.cost)).where(Usage.recorded_at >= start_of_month)
    )
    monthly_cost = monthly_usage.scalar() or 0

    # 总执行次数
    total_executions = await db.execute(
        select(func.count(Execution.id))
    )
    executions_count = total_executions.scalar() or 0

    # 活跃配额数
    active_quotas = await db.execute(
        select(func.count(CostQuota.id)).where(CostQuota.is_active == True)
    )
    quotas_count = active_quotas.scalar() or 0

    # 未处理预警数
    pending_alerts = await db.execute(
        select(func.count(UsageAlert.id)).where(UsageAlert.alert_sent == False)
    )
    alerts_count = pending_alerts.scalar() or 0

    return RespModel.ok_resp(data={
        "total_cost": float(total_cost),
        "monthly_cost": float(monthly_cost),
        "total_executions": executions_count,
        "active_quotas": quotas_count,
        "pending_alerts": alerts_count
    })
