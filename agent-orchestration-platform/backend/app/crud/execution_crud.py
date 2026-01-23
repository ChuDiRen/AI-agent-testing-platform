"""
Execution CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Execution
from app.crud.base import CRUDBase
from app.schemas import ExecutionCreate, ExecutionUpdate


class CRUDExecution(CRUDBase[Execution, ExecutionCreate, ExecutionUpdate]):
    """Execution CRUD 操作类"""

    async def get_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Execution]:
        """根据状态获取执行记录"""
        result = await db.execute(
            select(Execution)
            .where(Execution.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Execution.id.desc())
        )
        return result.scalars().all()

    async def get_by_workflow(
        self, db: AsyncSession, *, workflow_id: int, skip: int = 0, limit: int = 100
    ) -> List[Execution]:
        """根据 Workflow ID 获取执行记录"""
        result = await db.execute(
            select(Execution)
            .where(Execution.workflow_id == workflow_id)
            .offset(skip)
            .limit(limit)
            .order_by(Execution.id.desc())
        )
        return result.scalars().all()


# 创建 Execution CRUD 实例
execution = CRUDExecution(Execution)


# 导出
__all__ = ["execution"]
