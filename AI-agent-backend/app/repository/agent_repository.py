# Copyright (c) 2025 左岚. All rights reserved.
"""
AI代理Repository
处理AI代理相关的数据访问操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session, joinedload

from app.entity.agent import Agent, AgentStatus, AgentType
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class AgentRepository(BaseRepository[Agent]):
    """AI代理Repository类"""

    def __init__(self, db: Session):
        super().__init__(db, Agent)

    def find_by_name(self, name: str) -> Optional[Agent]:
        """
        根据名称查找代理
        
        Args:
            name: 代理名称
            
        Returns:
            代理对象或None
        """
        try:
            agent = self.db.query(Agent).filter(
                and_(
                    Agent.name == name,
                    Agent.is_deleted == 0
                )
            ).first()
            
            logger.debug(f"Found agent by name '{name}': {agent is not None}")
            return agent
            
        except Exception as e:
            logger.error(f"Error finding agent by name '{name}': {str(e)}")
            raise

    def find_by_type(self, agent_type: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        根据类型查找代理
        
        Args:
            agent_type: 代理类型
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            代理列表
        """
        try:
            agents = self.db.query(Agent).filter(
                and_(
                    Agent.type == agent_type,
                    Agent.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(agents)} agents of type '{agent_type}'")
            return agents
            
        except Exception as e:
            logger.error(f"Error finding agents by type '{agent_type}': {str(e)}")
            raise

    def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        根据状态查找代理
        
        Args:
            status: 代理状态
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            代理列表
        """
        try:
            agents = self.db.query(Agent).filter(
                and_(
                    Agent.status == status,
                    Agent.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(agents)} agents with status '{status}'")
            return agents
            
        except Exception as e:
            logger.error(f"Error finding agents by status '{status}': {str(e)}")
            raise

    def find_by_creator(self, created_by_id: int, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        根据创建者查找代理
        
        Args:
            created_by_id: 创建者ID
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            代理列表
        """
        try:
            agents = self.db.query(Agent).filter(
                and_(
                    Agent.created_by_id == created_by_id,
                    Agent.is_deleted == 0
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(agents)} agents created by user {created_by_id}")
            return agents
            
        except Exception as e:
            logger.error(f"Error finding agents by creator {created_by_id}: {str(e)}")
            raise

    def search(self, keyword: str = None, agent_type: str = None, status: str = None,
               created_by_id: int = None, start_date: datetime = None, end_date: datetime = None,
               skip: int = 0, limit: int = 100) -> tuple[List[Agent], int]:
        """
        搜索代理
        
        Args:
            keyword: 搜索关键词
            agent_type: 代理类型筛选
            status: 状态筛选
            created_by_id: 创建者ID筛选
            start_date: 创建时间开始
            end_date: 创建时间结束
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            (代理列表, 总数量)
        """
        try:
            query = self.db.query(Agent).filter(Agent.is_deleted == 0)
            
            # 关键词搜索
            if keyword:
                keyword_filter = or_(
                    Agent.name.ilike(f'%{keyword}%'),
                    Agent.description.ilike(f'%{keyword}%')
                )
                query = query.filter(keyword_filter)
            
            # 类型筛选
            if agent_type:
                query = query.filter(Agent.type == agent_type)
            
            # 状态筛选
            if status:
                query = query.filter(Agent.status == status)
            
            # 创建者筛选
            if created_by_id:
                query = query.filter(Agent.created_by_id == created_by_id)
            
            # 时间范围筛选
            if start_date:
                query = query.filter(Agent.created_at >= start_date)
            if end_date:
                query = query.filter(Agent.created_at <= end_date)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            agents = query.order_by(desc(Agent.created_at)).offset(skip).limit(limit).all()
            
            logger.debug(f"Search found {len(agents)} agents (total: {total})")
            return agents, total
            
        except Exception as e:
            logger.error(f"Error searching agents: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """
        获取代理统计信息
        
        Returns:
            统计信息字典
        """
        try:
            # 基本统计
            total_agents = self.count()
            active_agents = self.db.query(func.count(Agent.id)).filter(
                and_(Agent.status == AgentStatus.ACTIVE.value, Agent.is_deleted == 0)
            ).scalar()
            running_agents = self.db.query(func.count(Agent.id)).filter(
                and_(Agent.status == AgentStatus.RUNNING.value, Agent.is_deleted == 0)
            ).scalar()
            error_agents = self.db.query(func.count(Agent.id)).filter(
                and_(Agent.status == AgentStatus.ERROR.value, Agent.is_deleted == 0)
            ).scalar()
            
            # 运行统计
            total_runs = self.db.query(func.sum(Agent.run_count)).filter(
                Agent.is_deleted == 0
            ).scalar() or 0
            total_success = self.db.query(func.sum(Agent.success_count)).filter(
                Agent.is_deleted == 0
            ).scalar() or 0
            total_errors = self.db.query(func.sum(Agent.error_count)).filter(
                Agent.is_deleted == 0
            ).scalar() or 0
            
            # 成功率计算
            overall_success_rate = (total_success / total_runs * 100) if total_runs > 0 else 0.0
            
            # 按类型统计
            agents_by_type = {}
            for agent_type in AgentType:
                count = self.db.query(func.count(Agent.id)).filter(
                    and_(Agent.type == agent_type.value, Agent.is_deleted == 0)
                ).scalar()
                agents_by_type[agent_type.value] = count
            
            # 按状态统计
            agents_by_status = {}
            for status in AgentStatus:
                count = self.db.query(func.count(Agent.id)).filter(
                    and_(Agent.status == status.value, Agent.is_deleted == 0)
                ).scalar()
                agents_by_status[status.value] = count
            
            # 最近活动
            recent_activity = self.db.query(Agent).filter(
                and_(Agent.last_run_time.isnot(None), Agent.is_deleted == 0)
            ).order_by(desc(Agent.last_run_time)).limit(10).all()
            
            recent_activity_data = [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "type": agent.type,
                    "status": agent.status,
                    "last_run_time": agent.last_run_time.isoformat() if agent.last_run_time else None,
                    "success_rate": agent.get_success_rate()
                }
                for agent in recent_activity
            ]
            
            statistics = {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "running_agents": running_agents,
                "error_agents": error_agents,
                "total_runs": total_runs,
                "total_success": total_success,
                "total_errors": total_errors,
                "overall_success_rate": round(overall_success_rate, 2),
                "agents_by_type": agents_by_type,
                "agents_by_status": agents_by_status,
                "recent_activity": recent_activity_data
            }
            
            logger.debug("Generated agent statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting agent statistics: {str(e)}")
            raise

    def batch_update_status(self, agent_ids: List[int], status: str) -> int:
        """
        批量更新代理状态
        
        Args:
            agent_ids: 代理ID列表
            status: 目标状态
            
        Returns:
            更新成功的数量
        """
        try:
            updated_count = self.db.query(Agent).filter(
                and_(
                    Agent.id.in_(agent_ids),
                    Agent.is_deleted == 0
                )
            ).update(
                {
                    Agent.status: status,
                    Agent.updated_at: datetime.utcnow()
                },
                synchronize_session=False
            )
            
            self.db.commit()
            
            logger.info(f"Batch updated {updated_count} agents to status '{status}'")
            return updated_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error batch updating agent status: {str(e)}")
            raise

    def get_agents_with_configs(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        获取包含配置信息的代理列表
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            代理列表（包含配置信息）
        """
        try:
            agents = self.db.query(Agent).options(
                joinedload(Agent.agent_configs)
            ).filter(
                Agent.is_deleted == 0
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(agents)} agents with configurations")
            return agents
            
        except Exception as e:
            logger.error(f"Error getting agents with configs: {str(e)}")
            raise

    def get_most_active_agents(self, limit: int = 10) -> List[Agent]:
        """
        获取最活跃的代理
        
        Args:
            limit: 限制返回的记录数
            
        Returns:
            最活跃的代理列表
        """
        try:
            agents = self.db.query(Agent).filter(
                Agent.is_deleted == 0
            ).order_by(desc(Agent.run_count)).limit(limit).all()
            
            logger.debug(f"Retrieved {len(agents)} most active agents")
            return agents
            
        except Exception as e:
            logger.error(f"Error getting most active agents: {str(e)}")
            raise

    def get_agents_by_success_rate(self, min_rate: float = 0.0, max_rate: float = 1.0,
                                  skip: int = 0, limit: int = 100) -> List[Agent]:
        """
        根据成功率范围获取代理
        
        Args:
            min_rate: 最小成功率
            max_rate: 最大成功率
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            代理列表
        """
        try:
            # 使用原生SQL计算成功率
            agents = self.db.query(Agent).filter(
                and_(
                    Agent.run_count > 0,
                    Agent.is_deleted == 0,
                    (Agent.success_count * 1.0 / Agent.run_count) >= min_rate,
                    (Agent.success_count * 1.0 / Agent.run_count) <= max_rate
                )
            ).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(agents)} agents with success rate between {min_rate}-{max_rate}")
            return agents
            
        except Exception as e:
            logger.error(f"Error getting agents by success rate: {str(e)}")
            raise