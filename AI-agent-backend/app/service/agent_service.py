# Copyright (c) 2025 左岚. All rights reserved.
"""
AI代理Service
处理AI代理相关的业务逻辑
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from app.entity.agent import Agent, AgentStatus, AgentType
from app.repository.agent_repository import AgentRepository
from app.repository.agent_config_repository import AgentConfigRepository
from app.dto.agent_dto import (
    AgentCreateRequest, AgentUpdateRequest, AgentSearchRequest,
    AgentResponse, AgentListResponse, AgentStatisticsResponse,
    AgentBatchOperationRequest, AgentBatchOperationResponse
)
from app.core.logger import get_logger
from app.utils.exceptions import BusinessException
from app.core.logger import get_logger
from app.utils.exceptions import BusinessException

logger = get_logger(__name__)


class AgentService:
    """AI代理Service类"""

    def __init__(self, db: Session):
        self.db = db
        self.agent_repo = AgentRepository(db)
        self.config_repo = AgentConfigRepository(db)

    def create_agent(self, request: AgentCreateRequest, created_by_id: int) -> AgentResponse:
        """
        创建AI代理
        
        Args:
            request: 创建代理请求
            created_by_id: 创建者ID
            
        Returns:
            代理响应
        """
        try:
            # 检查名称是否已存在
            existing_agent = self.agent_repo.find_by_name(request.name)
            if existing_agent:
                raise BusinessException(f"代理名称 '{request.name}' 已存在")
            
            # 创建代理实体
            agent = Agent(
                name=request.name,
                type=request.type.value,
                description=request.description,
                created_by_id=created_by_id,
                config=request.config,
                version=request.version
            )
            
            # 保存到数据库
            created_agent = self.agent_repo.create(agent)
            
            logger.info(f"Created agent '{created_agent.name}' with id {created_agent.id}")
            return self._convert_to_response(created_agent)
            
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}")
            raise

    def get_agent_by_id(self, agent_id: int) -> Optional[AgentResponse]:
        """
        根据ID获取代理
        
        Args:
            agent_id: 代理ID
            
        Returns:
            代理响应或None
        """
        try:
            agent = self.agent_repo.get_by_id(agent_id)
            if not agent:
                return None
            
            return self._convert_to_response(agent)
            
        except Exception as e:
            logger.error(f"Error getting agent by id {agent_id}: {str(e)}")
            raise

    def update_agent(self, agent_id: int, request: AgentUpdateRequest) -> Optional[AgentResponse]:
        """
        更新代理信息
        
        Args:
            agent_id: 代理ID
            request: 更新请求
            
        Returns:
            更新后的代理响应或None
        """
        try:
            agent = self.agent_repo.get_by_id(agent_id)
            if not agent:
                raise BusinessException(f"代理 {agent_id} 不存在")
            
            # 检查名称是否冲突
            if request.name and request.name != agent.name:
                existing_agent = self.agent_repo.find_by_name(request.name)
                if existing_agent:
                    raise BusinessException(f"代理名称 '{request.name}' 已存在")
            
            # 准备更新数据
            update_data = {}
            if request.name is not None:
                update_data['name'] = request.name
            if request.type is not None:
                update_data['type'] = request.type.value
            if request.description is not None:
                update_data['description'] = request.description
            if request.config is not None:
                update_data['config'] = request.config
            if request.version is not None:
                update_data['version'] = request.version
            
            # 更新代理
            updated_agent = self.agent_repo.update(agent_id, update_data)
            if not updated_agent:
                raise BusinessException(f"更新代理 {agent_id} 失败")
            
            logger.info(f"Updated agent {agent_id}")
            return self._convert_to_response(updated_agent)
            
        except Exception as e:
            logger.error(f"Error updating agent {agent_id}: {str(e)}")
            raise

    def delete_agent(self, agent_id: int) -> bool:
        """
        删除代理
        
        Args:
            agent_id: 代理ID
            
        Returns:
            是否删除成功
        """
        try:
            agent = self.agent_repo.get_by_id(agent_id)
            if not agent:
                raise BusinessException(f"代理 {agent_id} 不存在")
            
            # 检查代理状态
            if agent.is_running():
                raise BusinessException(f"不能删除正在运行的代理")
            
            # 软删除代理
            success = self.agent_repo.delete(agent_id, soft_delete=True)
            
            if success:
                logger.info(f"Deleted agent {agent_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting agent {agent_id}: {str(e)}")
            raise

    def search_agents(self, request: AgentSearchRequest) -> AgentListResponse:
        """
        搜索代理
        
        Args:
            request: 搜索请求
            
        Returns:
            代理列表响应
        """
        try:
            agents, total = self.agent_repo.search(
                keyword=request.keyword,
                agent_type=request.type.value if request.type else None,
                status=request.status.value if request.status else None,
                created_by_id=request.created_by_id,
                start_date=request.start_date,
                end_date=request.end_date,
                skip=request.skip,
                limit=request.limit
            )
            
            # 转换为响应对象
            agent_responses = [self._convert_to_response(agent) for agent in agents]
            
            return AgentListResponse(
                agents=agent_responses,
                total=total,
                page=request.page,
                page_size=request.page_size,
                total_pages=(total + request.page_size - 1) // request.page_size
            )
            
        except Exception as e:
            logger.error(f"Error searching agents: {str(e)}")
            raise

    def get_agent_statistics(self) -> AgentStatisticsResponse:
        """
        获取代理统计信息
        
        Returns:
            代理统计响应
        """
        try:
            statistics = self.agent_repo.get_statistics()
            
            return AgentStatisticsResponse(**statistics)
            
        except Exception as e:
            logger.error(f"Error getting agent statistics: {str(e)}")
            raise

    def start_agent(self, agent_id: int) -> AgentResponse:
        """
        启动代理
        
        Args:
            agent_id: 代理ID
            
        Returns:
            代理响应
        """
        try:
            agent = self.agent_repo.get_by_id(agent_id)
            if not agent:
                raise BusinessException(f"代理 {agent_id} 不存在")
            
            if not agent.is_active():
                raise BusinessException(f"代理 {agent_id} 未激活，无法启动")
            
            if agent.is_running():
                raise BusinessException(f"代理 {agent_id} 已在运行中")
            
            # 启动代理
            agent.start()
            self.agent_repo.update(agent_id, {
                'status': agent.status,
                'last_run_time': agent.last_run_time
            })
            
            logger.info(f"Started agent {agent_id}")
            return self._convert_to_response(agent)
            
        except Exception as e:
            logger.error(f"Error starting agent {agent_id}: {str(e)}")
            raise

    def stop_agent(self, agent_id: int) -> AgentResponse:
        """
        停止代理
        
        Args:
            agent_id: 代理ID
            
        Returns:
            代理响应
        """
        try:
            agent = self.agent_repo.get_by_id(agent_id)
            if not agent:
                raise BusinessException(f"代理 {agent_id} 不存在")
            
            if not agent.is_running():
                raise BusinessException(f"代理 {agent_id} 未在运行")
            
            # 停止代理
            agent.stop()
            self.agent_repo.update(agent_id, {'status': agent.status})
            
            logger.info(f"Stopped agent {agent_id}")
            return self._convert_to_response(agent)
            
        except Exception as e:
            logger.error(f"Error stopping agent {agent_id}: {str(e)}")
            raise

    def batch_operation(self, request: AgentBatchOperationRequest) -> AgentBatchOperationResponse:
        """
        批量操作代理
        
        Args:
            request: 批量操作请求
            
        Returns:
            批量操作响应
        """
        try:
            total = len(request.agent_ids)
            success_count = 0
            failed_ids = []
            errors = []
            
            for agent_id in request.agent_ids:
                try:
                    if request.operation == 'activate':
                        self._activate_agent(agent_id)
                    elif request.operation == 'deactivate':
                        self._deactivate_agent(agent_id)
                    elif request.operation == 'start':
                        self.start_agent(agent_id)
                    elif request.operation == 'stop':
                        self.stop_agent(agent_id)
                    elif request.operation == 'delete':
                        self.delete_agent(agent_id)
                    
                    success_count += 1
                    
                except Exception as e:
                    failed_ids.append(agent_id)
                    errors.append(f"代理 {agent_id}: {str(e)}")
            
            failed_count = total - success_count
            success_rate = (success_count / total * 100) if total > 0 else 0.0
            
            logger.info(f"Batch operation '{request.operation}' completed: {success_count}/{total} successful")
            
            return AgentBatchOperationResponse(
                total=total,
                success_count=success_count,
                failed_count=failed_count,
                failed_ids=failed_ids,
                errors=errors,
                success_rate=round(success_rate, 2)
            )
            
        except Exception as e:
            logger.error(f"Error in batch operation: {str(e)}")
            raise

    def _activate_agent(self, agent_id: int):
        """激活代理"""
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise BusinessException(f"代理 {agent_id} 不存在")
        
        agent.activate()
        self.agent_repo.update(agent_id, {'status': agent.status})

    def _deactivate_agent(self, agent_id: int):
        """停用代理"""
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            raise BusinessException(f"代理 {agent_id} 不存在")
        
        if agent.is_running():
            raise BusinessException(f"不能停用正在运行的代理")
        
        agent.deactivate()
        self.agent_repo.update(agent_id, {'status': agent.status})

    def _convert_to_response(self, agent: Agent) -> AgentResponse:
        """转换为响应对象"""
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            type=agent.type,
            description=agent.description,
            status=agent.status,
            config=agent.config,
            version=agent.version,
            created_by_id=agent.created_by_id,
            created_at=agent.created_at,
            updated_at=agent.updated_at,
            last_run_time=agent.last_run_time,
            run_count=agent.run_count,
            success_count=agent.success_count,
            error_count=agent.error_count,
            success_rate=agent.get_success_rate(),
            error_rate=agent.get_error_rate()
        )