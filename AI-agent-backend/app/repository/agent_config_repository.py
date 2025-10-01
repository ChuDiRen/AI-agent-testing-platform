"""
AI代理配置Repository
处理AI代理配置相关的数据访问操作
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.entity.agent_config import AgentConfig, ConfigType
from app.repository.base import BaseRepository
from app.core.logger import get_logger

logger = get_logger(__name__)


class AgentConfigRepository(BaseRepository[AgentConfig]):
    """AI代理配置Repository类"""

    def __init__(self, db: Session):
        super().__init__(db, AgentConfig)

    def find_by_agent_id(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[AgentConfig]:
        """
        根据代理ID查找配置
        
        Args:
            agent_id: 代理ID
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            配置列表
        """
        try:
            configs = self.db.query(AgentConfig).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.is_deleted == 0
                )
            ).order_by(AgentConfig.display_order, AgentConfig.config_key).offset(skip).limit(limit).all()
            
            logger.debug(f"Found {len(configs)} configs for agent {agent_id}")
            return configs
            
        except Exception as e:
            logger.error(f"Error finding configs for agent {agent_id}: {str(e)}")
            raise

    def find_by_config_key(self, agent_id: int, config_key: str) -> Optional[AgentConfig]:
        """
        根据代理ID和配置键查找配置
        
        Args:
            agent_id: 代理ID
            config_key: 配置键
            
        Returns:
            配置对象或None
        """
        try:
            config = self.db.query(AgentConfig).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.config_key == config_key,
                    AgentConfig.is_deleted == 0
                )
            ).first()
            
            logger.debug(f"Found config '{config_key}' for agent {agent_id}: {config is not None}")
            return config
            
        except Exception as e:
            logger.error(f"Error finding config '{config_key}' for agent {agent_id}: {str(e)}")
            raise

    def find_by_type(self, agent_id: int, config_type: str) -> List[AgentConfig]:
        """
        根据配置类型查找配置
        
        Args:
            agent_id: 代理ID
            config_type: 配置类型
            
        Returns:
            配置列表
        """
        try:
            configs = self.db.query(AgentConfig).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.config_type == config_type,
                    AgentConfig.is_deleted == 0
                )
            ).order_by(AgentConfig.display_order, AgentConfig.config_key).all()
            
            logger.debug(f"Found {len(configs)} configs of type '{config_type}' for agent {agent_id}")
            return configs
            
        except Exception as e:
            logger.error(f"Error finding configs by type '{config_type}' for agent {agent_id}: {str(e)}")
            raise

    def find_required_configs(self, agent_id: int) -> List[AgentConfig]:
        """
        查找必填配置
        
        Args:
            agent_id: 代理ID
            
        Returns:
            必填配置列表
        """
        try:
            configs = self.db.query(AgentConfig).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.is_required == 1,
                    AgentConfig.is_deleted == 0
                )
            ).order_by(AgentConfig.display_order, AgentConfig.config_key).all()
            
            logger.debug(f"Found {len(configs)} required configs for agent {agent_id}")
            return configs
            
        except Exception as e:
            logger.error(f"Error finding required configs for agent {agent_id}: {str(e)}")
            raise

    def find_enabled_configs(self, agent_id: int) -> List[AgentConfig]:
        """
        查找已启用的配置
        
        Args:
            agent_id: 代理ID
            
        Returns:
            已启用配置列表
        """
        try:
            configs = self.db.query(AgentConfig).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.is_enabled == 1,
                    AgentConfig.is_deleted == 0
                )
            ).order_by(AgentConfig.display_order, AgentConfig.config_key).all()
            
            logger.debug(f"Found {len(configs)} enabled configs for agent {agent_id}")
            return configs
            
        except Exception as e:
            logger.error(f"Error finding enabled configs for agent {agent_id}: {str(e)}")
            raise

    def search_configs(self, agent_id: int, keyword: str = None, config_type: str = None,
                      is_required: bool = None, is_enabled: bool = None,
                      skip: int = 0, limit: int = 100) -> tuple[List[AgentConfig], int]:
        """
        搜索配置
        
        Args:
            agent_id: 代理ID
            keyword: 搜索关键词
            config_type: 配置类型筛选
            is_required: 是否必填筛选
            is_enabled: 是否启用筛选
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            (配置列表, 总数量)
        """
        try:
            query = self.db.query(AgentConfig).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.is_deleted == 0
                )
            )
            
            # 关键词搜索
            if keyword:
                keyword_filter = or_(
                    AgentConfig.config_key.ilike(f'%{keyword}%'),
                    AgentConfig.description.ilike(f'%{keyword}%')
                )
                query = query.filter(keyword_filter)
            
            # 类型筛选
            if config_type:
                query = query.filter(AgentConfig.config_type == config_type)
            
            # 必填筛选
            if is_required is not None:
                query = query.filter(AgentConfig.is_required == (1 if is_required else 0))
            
            # 启用筛选
            if is_enabled is not None:
                query = query.filter(AgentConfig.is_enabled == (1 if is_enabled else 0))
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            configs = query.order_by(AgentConfig.display_order, AgentConfig.config_key).offset(skip).limit(limit).all()
            
            logger.debug(f"Search found {len(configs)} configs for agent {agent_id} (total: {total})")
            return configs, total
            
        except Exception as e:
            logger.error(f"Error searching configs for agent {agent_id}: {str(e)}")
            raise

    def get_config_statistics(self, agent_id: int) -> Dict[str, Any]:
        """
        获取配置统计信息
        
        Args:
            agent_id: 代理ID
            
        Returns:
            统计信息字典
        """
        try:
            # 基本统计
            total_configs = self.db.query(func.count(AgentConfig.id)).filter(
                and_(AgentConfig.agent_id == agent_id, AgentConfig.is_deleted == 0)
            ).scalar()
            
            required_configs = self.db.query(func.count(AgentConfig.id)).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.is_required == 1,
                    AgentConfig.is_deleted == 0
                )
            ).scalar()
            
            enabled_configs = self.db.query(func.count(AgentConfig.id)).filter(
                and_(
                    AgentConfig.agent_id == agent_id,
                    AgentConfig.is_enabled == 1,
                    AgentConfig.is_deleted == 0
                )
            ).scalar()
            
            # 按类型统计
            configs_by_type = {}
            for config_type in ConfigType:
                count = self.db.query(func.count(AgentConfig.id)).filter(
                    and_(
                        AgentConfig.agent_id == agent_id,
                        AgentConfig.config_type == config_type.value,
                        AgentConfig.is_deleted == 0
                    )
                ).scalar()
                configs_by_type[config_type.value] = count
            
            # 配置完整性检查
            required_configs_list = self.find_required_configs(agent_id)
            missing_configs = [
                config.config_key for config in required_configs_list
                if not config.config_value
            ]
            
            statistics = {
                "total_configs": total_configs,
                "required_configs": required_configs,
                "enabled_configs": enabled_configs,
                "configs_by_type": configs_by_type,
                "missing_required_configs": missing_configs,
                "config_completeness": round(
                    ((required_configs - len(missing_configs)) / required_configs * 100) if required_configs > 0 else 100.0,
                    2
                )
            }
            
            logger.debug(f"Generated config statistics for agent {agent_id}")
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting config statistics for agent {agent_id}: {str(e)}")
            raise

    def batch_update_configs(self, agent_id: int, config_updates: Dict[str, Any]) -> int:
        """
        批量更新配置
        
        Args:
            agent_id: 代理ID
            config_updates: 配置更新数据 {config_key: config_value, ...}
            
        Returns:
            更新成功的数量
        """
        try:
            updated_count = 0
            
            for config_key, config_value in config_updates.items():
                result = self.db.query(AgentConfig).filter(
                    and_(
                        AgentConfig.agent_id == agent_id,
                        AgentConfig.config_key == config_key,
                        AgentConfig.is_deleted == 0
                    )
                ).update(
                    {
                        AgentConfig.config_value: str(config_value),
                        AgentConfig.updated_at: datetime.utcnow()
                    },
                    synchronize_session=False
                )
                updated_count += result
            
            self.db.commit()
            
            logger.info(f"Batch updated {updated_count} configs for agent {agent_id}")
            return updated_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error batch updating configs for agent {agent_id}: {str(e)}")
            raise

    def duplicate_configs(self, source_agent_id: int, target_agent_id: int) -> int:
        """
        复制配置到另一个代理
        
        Args:
            source_agent_id: 源代理ID
            target_agent_id: 目标代理ID
            
        Returns:
            复制的配置数量
        """
        try:
            source_configs = self.find_by_agent_id(source_agent_id)
            new_configs = []
            
            for config in source_configs:
                new_config = AgentConfig(
                    agent_id=target_agent_id,
                    config_key=config.config_key,
                    config_value=config.config_value,
                    config_type=config.config_type,
                    description=config.description,
                    is_required=config.is_required_config(),
                    is_enabled=config.is_enabled_config(),
                    default_value=config.default_value,
                    validation_rules=config.validation_rules,
                    display_order=config.display_order
                )
                new_configs.append(new_config)
            
            created_configs = self.batch_create(new_configs)
            
            logger.info(f"Duplicated {len(created_configs)} configs from agent {source_agent_id} to {target_agent_id}")
            return len(created_configs)
            
        except Exception as e:
            logger.error(f"Error duplicating configs from agent {source_agent_id} to {target_agent_id}: {str(e)}")
            raise

    def get_config_values_dict(self, agent_id: int) -> Dict[str, Any]:
        """
        获取代理的配置值字典
        
        Args:
            agent_id: 代理ID
            
        Returns:
            配置值字典 {config_key: typed_value, ...}
        """
        try:
            configs = self.find_enabled_configs(agent_id)
            config_dict = {}
            
            for config in configs:
                config_dict[config.config_key] = config.get_typed_value()
            
            logger.debug(f"Retrieved config values dict for agent {agent_id}")
            return config_dict
            
        except Exception as e:
            logger.error(f"Error getting config values dict for agent {agent_id}: {str(e)}")
            raise
