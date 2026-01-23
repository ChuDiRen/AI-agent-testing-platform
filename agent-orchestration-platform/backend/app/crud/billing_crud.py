"""
Cost Quota CRUD 操作
"""
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.billing import CostQuota, UsageAlert, Invoice
from app.crud.base import CRUDBase
from app.schemas.billing_schema import CostQuotaCreate, CostQuotaUpdate, CostQuotaResponse


class CRUDCostQuota(CRUDBase[CostQuota, CostQuotaCreate, CostQuotaUpdate]):
    """Cost Quota CRUD 操作类"""

    async def get_by_agent(
        self, db: AsyncSession, *, agent_id: int
    ) -> Optional[CostQuota]:
        """根据 Agent ID 获取配额"""
        result = await db.execute(
            select(CostQuota).where(CostQuota.agent_id == agent_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> Optional[CostQuota]:
        """根据用户 ID 获取配额"""
        result = await db.execute(
            select(CostQuota).where(CostQuota.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_active_quotas(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[CostQuota]:
        """获取启用的配额列表"""
        result = await db.execute(
            select(CostQuota)
            .where(CostQuota.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(CostQuota.id.desc())
        )
        return result.scalars().all()

    async def update_current_usage(
        self, db: AsyncSession, *, quota_id: int, usage_delta: float
    ) -> CostQuota:
        """更新当前使用量"""
        db_quota = await self.get(db, id=quota_id)
        new_usage = db_quota.current_usage + usage_delta

        await self.update(
            db, db_obj=db_quota, obj_in={"current_usage": new_usage}
        )

        # 检查预警
        if db_quota.alert_enabled and db_quota.alert_threshold > 0:
            percent_used = new_usage / db_quota.monthly_limit
            await self._check_alert(db, db_quota, percent_used)

        return await self.get(db, id=db_quota.id)

    async def _check_alert(
        self, db: AsyncSession, db_quota: CostQuota, percent_used: float
    ):
        """检查并创建预警记录"""
        db_quota.is_warning = percent_used >= db_quota.alert_threshold
        db_quota.is_critical = percent_used >= 1.0

        if db_quota.is_warning or db_quota.is_critical:
            await self._create_alert(db, db_quota, percent_used)

    async def _create_alert(
        self, db: AsyncSession, db_quota: CostQuota, percent_used: float
    ):
        """创建预警记录"""
        status = "critical" if percent_used >= 1.0 else "warning"

        alert = UsageAlert(
            quota_id=db_quota.id,
            agent_id=db_quota.agent_id,
            user_id=db_quota.user_id,
            usage_type="monthly",
            current_usage=db_quota.current_usage,
            threshold=db_quota.alert_threshold,
            status=status,
            alert_sent=False,
            message=f"已使用 {percent_used*100:.1f}% 限额"
        )

        db.add(alert)
        await db.commit()

    async def reset_monthly_usage(self, db: AsyncSession) -> None:
        """重置每月使用量（定时任务）"""
        # TODO: 实现定时任务，每月 1 号重置所有配额
        pass


# 创建 Cost Quota CRUD 实例
cost_quota = CRUDCostQuota(CostQuota)


# 导出
__all__ = ["cost_quota"]
