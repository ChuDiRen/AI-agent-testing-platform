"""
机器人配置信息 CRUD 操作
从 Flask 迁移到 FastAPI
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.robot_config import RobotConfig
from app.schemas.robot_config import RobotConfigCreate, RobotConfigUpdate


class CRUDRobotConfig(CRUDBase[RobotConfig, RobotConfigCreate, RobotConfigUpdate]):
    """机器人配置信息 CRUD"""
    
    async def get_by_robot_type(self, db: AsyncSession, *, robot_type: str) -> List[RobotConfig]:
        """根据机器人类型获取配置"""
        result = await db.execute(select(RobotConfig).where(RobotConfig.robot_type == robot_type))
        return result.scalars().all()
    
    async def get_by_name(self, db: AsyncSession, *, robot_name: str) -> Optional[RobotConfig]:
        """根据机器人名称获取配置"""
        result = await db.execute(select(RobotConfig).where(RobotConfig.robot_name == robot_name))
        return result.scalars().first()
    
    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        page: int = 1, 
        page_size: int = 10,
        robot_type: Optional[str] = None,
        robot_name: Optional[str] = None
    ) -> tuple[List[RobotConfig], int]:
        """根据筛选条件获取机器人配置列表"""
        query = select(RobotConfig)
        
        # 添加筛选条件
        if robot_type:
            query = query.where(RobotConfig.robot_type == robot_type)
        
        if robot_name:
            query = query.where(RobotConfig.robot_name.like(f"%{robot_name}%"))
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return items, total


robot_config_crud = CRUDRobotConfig(RobotConfig)
