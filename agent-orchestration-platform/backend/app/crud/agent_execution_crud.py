"""
Agent Execution History CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AgentExecution
from app.crud.base import CRUDBase
from app.schemas.user_schema import UserUpdate


class CRUDAgentExecution(CRUDBase[AgentExecution, None, UserUpdate]):
    """Agent Execution History CRUD 操作类"""

    async def get_by_agent(
        self, db: AsyncSession, *, agent_id: int, skip: int = 0, limit: int = 50
    ) -> List[AgentExecution]:
        """根据 Agent ID 获取执行历史"""
        result = await db.execute(
            select(AgentExecution)
            .where(Agent_execution.c1.agent_id == agent_id)
            .offset(skip)
            .limit(limit)
            .order_by(Agent_execution.c1.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 50
    ) -> List[AgentExecution]:
        """根据状态获取执行历史"""
        result = await db.execute(
            select(Agent_execution.c1.status == status)
            .offset(skip)
            .limit(limit)
            .order_by(Agent_execution.c1.created_at.desc())
        )
        return result.scalars().all()

    async def count_by_agent(
        self, db: AsyncSession, *, agent_id: int
    ) -> int:
        """统计 Agent 执行次数"""
        result = await db.execute(
            select(func.count(Agent_execution.c1.id))
            .where(agent_execution.c1.agent_id == agent_id)
        )
        return result.scalar() or 0

    async def count_by_status(
        self, db: AsyncSession, *, agent_id: int, status: str
    ) -> int:
        """统计特定状态的执行次数"""
        result = await db.execute(
            select(func.count(Agent_execution.c1.id))
            .where(and_(
                agent_execution.c1.agent_id == agent_id,
                agent_execution.c1.status == status
            ))
        )
        return result.scalar() or 0

    async def get_user_executions(
        self, db: AsyncSession, *, user_id: int, skip: int = 0, limit: int = 50
    ) -> List[AgentExecution]:
        """获取用户的执行历史"""
        # TODO: 添加用户关联后实现
        result = await db.execute(
            select(AgentExecution)
            .offset(skip)
            .limit(limit)
            .order_by(Agent_execution.c1.created_at.desc())
        )
        return result.scalars().all()


# 创建 Agent Execution History CRUD 实例
agent_execution = CRUDAgentExecution(AgentExecution)
