"""
Tool CRUD 操作
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tool
from app.crud.base import CRUDBase
from app.schemas import ToolCreate, ToolUpdate


class CRUDTool(CRUDBase[Tool, ToolCreate, ToolUpdate]):
    """Tool CRUD 操作类"""

    async def get_by_type(
        self, db: AsyncSession, *, tool_type: str, skip: int = 0, limit: int = 100
    ) -> List[Tool]:
        """根据类型获取工具列表"""
        result = await db.execute(
            select(Tool)
            .where(Tool.type == tool_type)
            .offset(skip)
            .limit(limit)
            .order_by(Tool.id.desc())
        )
        return result.scalars().all()


# 创建 Tool CRUD 实例
tool = CRUDTool(Tool)


# 导出
__all__ = ["tool"]
