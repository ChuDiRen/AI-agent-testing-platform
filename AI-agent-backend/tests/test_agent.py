# Copyright (c) 2025 左岚. All rights reserved.
"""
AI代理管理功能单元测试
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from sqlalchemy.orm import Session

from app.entity.agent import Agent, AgentStatus, AgentType
from app.service.agent_service import AgentService
from app.repository.agent_repository import AgentRepository
from app.dto.agent_dto import AgentCreateRequest, AgentUpdateRequest, AgentSearchRequest
from app.utils.exceptions import BusinessException


class TestAgentService:
    """AI代理Service单元测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_agent_repo(self):
        """模拟代理Repository"""
        return Mock(spec=AgentRepository)

    @pytest.fixture
    def agent_service(self, mock_db, mock_agent_repo):
        """创建代理Service实例"""
        service = AgentService(mock_db)
        service.agent_repo = mock_agent_repo
        return service

    @pytest.fixture
    def sample_agent(self):
        """创建示例代理实体"""
        agent = Agent(
            name="Test Agent",
            type=AgentType.CHAT.value,
            description="Test Description",
            created_by_id=1
        )
        agent.id = 1
        agent.created_at = datetime.now()
        agent.updated_at = datetime.now()
        return agent

    def test_create_agent_success(self, agent_service, mock_agent_repo, sample_agent):
        """测试成功创建代理"""
        # 准备
        request = AgentCreateRequest(
            name="Test Agent",
            type=AgentType.CHAT,
            description="Test Description"
        )
        
        mock_agent_repo.find_by_name.return_value = None  # 名称不存在
        mock_agent_repo.create.return_value = sample_agent
        
        # 执行
        result = agent_service.create_agent(request, created_by_id=1)
        
        # 验证
        assert result.name == "Test Agent"
        assert result.type == AgentType.CHAT.value
        assert result.description == "Test Description"
        mock_agent_repo.find_by_name.assert_called_once_with("Test Agent")
        mock_agent_repo.create.assert_called_once()

    def test_create_agent_duplicate_name(self, agent_service, mock_agent_repo, sample_agent):
        """测试创建重复名称的代理"""
        # 准备
        request = AgentCreateRequest(
            name="Test Agent",
            type=AgentType.CHAT
        )
        
        mock_agent_repo.find_by_name.return_value = sample_agent  # 名称已存在
        
        # 执行并验证异常
        with pytest.raises(BusinessException) as exc_info:
            agent_service.create_agent(request, created_by_id=1)
        
        assert "已存在" in str(exc_info.value)
        mock_agent_repo.create.assert_not_called()

    def test_get_agent_by_id_success(self, agent_service, mock_agent_repo, sample_agent):
        """测试成功获取代理"""
        # 准备
        mock_agent_repo.get_by_id.return_value = sample_agent
        
        # 执行
        result = agent_service.get_agent_by_id(1)
        
        # 验证
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Agent"
        mock_agent_repo.get_by_id.assert_called_once_with(1)

    def test_get_agent_by_id_not_found(self, agent_service, mock_agent_repo):
        """测试获取不存在的代理"""
        # 准备
        mock_agent_repo.get_by_id.return_value = None
        
        # 执行
        result = agent_service.get_agent_by_id(999)
        
        # 验证
        assert result is None
        mock_agent_repo.get_by_id.assert_called_once_with(999)

    def test_update_agent_success(self, agent_service, mock_agent_repo, sample_agent):
        """测试成功更新代理"""
        # 准备
        request = AgentUpdateRequest(
            name="Updated Agent",
            description="Updated Description"
        )
        
        updated_agent = Agent(
            name="Updated Agent",
            type=AgentType.CHAT.value,
            description="Updated Description",
            created_by_id=1
        )
        updated_agent.id = 1
        
        mock_agent_repo.get_by_id.return_value = sample_agent
        mock_agent_repo.find_by_name.return_value = None  # 新名称不冲突
        mock_agent_repo.update.return_value = updated_agent
        
        # 执行
        result = agent_service.update_agent(1, request)
        
        # 验证
        assert result is not None
        assert result.name == "Updated Agent"
        assert result.description == "Updated Description"
        mock_agent_repo.update.assert_called_once()

    def test_update_agent_name_conflict(self, agent_service, mock_agent_repo, sample_agent):
        """测试更新代理名称冲突"""
        # 准备
        request = AgentUpdateRequest(name="Existing Agent")
        
        existing_agent = Agent(name="Existing Agent", type=AgentType.CHAT.value, created_by_id=2)
        existing_agent.id = 2
        
        mock_agent_repo.get_by_id.return_value = sample_agent
        mock_agent_repo.find_by_name.return_value = existing_agent  # 名称冲突
        
        # 执行并验证异常
        with pytest.raises(BusinessException) as exc_info:
            agent_service.update_agent(1, request)
        
        assert "已存在" in str(exc_info.value)
        mock_agent_repo.update.assert_not_called()

    def test_delete_agent_success(self, agent_service, mock_agent_repo, sample_agent):
        """测试成功删除代理"""
        # 准备
        sample_agent.status = AgentStatus.STOPPED.value
        mock_agent_repo.get_by_id.return_value = sample_agent
        mock_agent_repo.delete.return_value = True
        
        # 执行
        result = agent_service.delete_agent(1)
        
        # 验证
        assert result is True
        mock_agent_repo.delete.assert_called_once_with(1, soft_delete=True)

    def test_delete_running_agent(self, agent_service, mock_agent_repo, sample_agent):
        """测试删除正在运行的代理"""
        # 准备
        sample_agent.status = AgentStatus.RUNNING.value
        mock_agent_repo.get_by_id.return_value = sample_agent
        
        # 执行并验证异常
        with pytest.raises(BusinessException) as exc_info:
            agent_service.delete_agent(1)
        
        assert "正在运行" in str(exc_info.value)
        mock_agent_repo.delete.assert_not_called()

    def test_start_agent_success(self, agent_service, mock_agent_repo, sample_agent):
        """测试成功启动代理"""
        # 准备
        sample_agent.status = AgentStatus.ACTIVE.value
        mock_agent_repo.get_by_id.return_value = sample_agent
        mock_agent_repo.update.return_value = sample_agent
        
        # 执行
        result = agent_service.start_agent(1)
        
        # 验证
        assert result is not None
        mock_agent_repo.update.assert_called_once()

    def test_start_inactive_agent(self, agent_service, mock_agent_repo, sample_agent):
        """测试启动未激活的代理"""
        # 准备
        sample_agent.status = AgentStatus.INACTIVE.value
        mock_agent_repo.get_by_id.return_value = sample_agent
        
        # 执行并验证异常
        with pytest.raises(BusinessException) as exc_info:
            agent_service.start_agent(1)
        
        assert "未激活" in str(exc_info.value)
        mock_agent_repo.update.assert_not_called()

    def test_search_agents_success(self, agent_service, mock_agent_repo, sample_agent):
        """测试成功搜索代理"""
        # 准备
        request = AgentSearchRequest(page=1, page_size=20, keyword="test")
        
        mock_agent_repo.search.return_value = ([sample_agent], 1)
        
        # 执行
        result = agent_service.search_agents(request)
        
        # 验证
        assert result.total == 1
        assert len(result.agents) == 1
        assert result.agents[0].name == "Test Agent"
        mock_agent_repo.search.assert_called_once()

    def test_get_agent_statistics(self, agent_service, mock_agent_repo):
        """测试获取代理统计信息"""
        # 准备
        mock_statistics = {
            "total_agents": 10,
            "active_agents": 8,
            "running_agents": 3,
            "error_agents": 1,
            "total_runs": 100,
            "total_success": 90,
            "total_errors": 10,
            "overall_success_rate": 90.0,
            "agents_by_type": {"chat": 5, "task": 3, "analysis": 2},
            "agents_by_status": {"active": 8, "inactive": 2},
            "recent_activity": []
        }
        
        mock_agent_repo.get_statistics.return_value = mock_statistics
        
        # 执行
        result = agent_service.get_agent_statistics()
        
        # 验证
        assert result.total_agents == 10
        assert result.active_agents == 8
        assert result.overall_success_rate == 90.0
        mock_agent_repo.get_statistics.assert_called_once()


class TestAgentRepository:
    """AI代理Repository单元测试"""

    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock(spec=Session)

    @pytest.fixture
    def agent_repo(self, mock_db):
        """创建代理Repository实例"""
        return AgentRepository(mock_db)

    @pytest.fixture
    def sample_agent(self):
        """创建示例代理实体"""
        agent = Agent(
            name="Test Agent",
            type=AgentType.CHAT.value,
            description="Test Description",
            created_by_id=1
        )
        agent.id = 1
        return agent

    def test_find_by_name_success(self, agent_repo, mock_db, sample_agent):
        """测试根据名称查找代理成功"""
        # 准备
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = sample_agent
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # 执行
        result = agent_repo.find_by_name("Test Agent")
        
        # 验证
        assert result is not None
        assert result.name == "Test Agent"
        mock_db.query.assert_called_once_with(Agent)

    def test_find_by_name_not_found(self, agent_repo, mock_db):
        """测试根据名称查找代理失败"""
        # 准备
        mock_query = Mock()
        mock_filter = Mock()
        mock_filter.first.return_value = None
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # 执行
        result = agent_repo.find_by_name("Nonexistent Agent")
        
        # 验证
        assert result is None
        mock_db.query.assert_called_once_with(Agent)

    def test_find_by_type_success(self, agent_repo, mock_db, sample_agent):
        """测试根据类型查找代理成功"""
        # 准备
        mock_query = Mock()
        mock_filter = Mock()
        mock_offset = Mock()
        mock_limit = Mock()
        mock_limit.all.return_value = [sample_agent]
        mock_offset.limit.return_value = mock_limit
        mock_filter.offset.return_value = mock_offset
        mock_query.filter.return_value = mock_filter
        mock_db.query.return_value = mock_query
        
        # 执行
        result = agent_repo.find_by_type(AgentType.CHAT.value)
        
        # 验证
        assert len(result) == 1
        assert result[0].type == AgentType.CHAT.value
        mock_db.query.assert_called_once_with(Agent)


if __name__ == "__main__":
    pytest.main([__file__])