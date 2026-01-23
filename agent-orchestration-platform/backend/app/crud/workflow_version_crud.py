"""
Workflow Version CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import WorkflowVersion, Workflow
from app.crud.base import CRUDBase
from app.schemas import WorkflowUpdate


class CRUDWorkflowVersion(CRUDBase[WorkflowVersion, None, WorkflowUpdate]):
    """Workflow Version CRUD 操作类"""

    async def get_by_workflow(
        self, db: AsyncSession, *, workflow_id: int, skip: int = 0, limit: int = 100
    ) -> List[WorkflowVersion]:
        """根据 Workflow ID 获取版本历史"""
        result = await db.execute(
            select(WorkflowVersion)
            .where(WorkflowVersion.workflow_id == workflow_id)
            .offset(skip)
            .limit(limit)
            .order_by(WorkflowVersion.id.desc())
        )
        return result.scalars().all()

    async def get_latest_version(
        self, db: AsyncSession, *, workflow_id: int
    ) -> Optional[WorkflowVersion]:
        """获取 Workflow 最新版本"""
        result = await db.execute(
            select(WorkflowVersion)
            .where(and_(
                WorkflowVersion.workflow_id == workflow_id,
                WorkflowVersion.is_published == True
            ))
            .order_by(WorkflowVersion.id.desc())
            .first()
        )
        return result.scalar_one_or_none()

    async def count_total_versions(
        self, db: AsyncSession, *, workflow_id: int
    ) -> int:
        """统计总版本数"""
        result = await db.execute(
            select(func.count(WorkflowVersion.id))
            .where(WorkflowVersion.workflow_id == workflow_id)
        )
        return result.scalar() or 0


# 创建 Workflow Version CRUD 实例
workflow_version = CRUDWorkflowVersion(WorkflowVersion)
