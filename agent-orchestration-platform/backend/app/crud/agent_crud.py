"""
Agent CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Agent
from app.crud.base import CRUDBase
from app.schemas import AgentCreate, AgentUpdate


class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    """Agent CRUD 操作类"""

    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Agent]:
        """根据名称获取 Agent"""
        result = await db.execute(
            select(Agent).where(Agent.name == name)
        )
        return result.scalar_one_or_none()

    async def get_active_agents(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        """获取启用的 Agent 列表"""
        result = await db.execute(
            select(Agent)
            .where(Agent.is_active == True)
            .offset(skip)
            .limit(limit)
            .order_by(Agent.id.desc())
        )
        return result.scalars().all()


# 创建 Agent CRUD 实例
agent = CRUDAgent(Agent)


# 导出
__all__ = ["agent"]
