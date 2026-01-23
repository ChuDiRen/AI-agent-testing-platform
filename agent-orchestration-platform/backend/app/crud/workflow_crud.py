"""
Workflow CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Workflow
from app.crud.base import CRUDBase
from app.schemas import WorkflowCreate, WorkflowUpdate


class CRUDWorkflow(CRUDBase[Workflow, WorkflowCreate, WorkflowUpdate]):
    """Workflow CRUD 操作类"""

    async def get_published(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Workflow]:
        """获取已发布的工作流列表"""
        result = await db.execute(
            select(Workflow)
            .where(Workflow.is_published == True)
            .offset(skip)
            .limit(limit)
            .order_by(Workflow.id.desc())
        )
        return result.scalars().all()


# 创建 Workflow CRUD 实例
workflow = CRUDWorkflow(Workflow)


# 导出
__all__ = ["workflow"]
