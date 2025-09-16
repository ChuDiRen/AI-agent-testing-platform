# Copyright (c) 2025 左岚. All rights reserved.
"""
AI测试用例生成功能单元测试
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from app.service.multi_agent_service import MultiAgentTestCaseGenerator, GenerationStatus
from app.service.test_case_service import TestCaseService
from app.entity.test_case import TestCase, TestCaseStatus
from app.dto.test_case_dto import TestCaseCreateRequest


class TestMultiAgentTestCaseGenerator:
    """多智能体测试用例生成器单元测试"""

    @pytest.fixture
    def generator(self):
        return MultiAgentTestCaseGenerator()

    @pytest.fixture
    def sample_requirements(self):
        return """
        用户登录功能需求：
        1. 用户可以通过用户名和密码登录系统
        2. 登录成功后跳转到主页面
        3. 登录失败显示错误信息
        """

    @pytest.mark.asyncio
    async def test_generate_test_cases_success(self, generator, sample_requirements):
        """测试成功生成测试用例"""
        result = await generator.generate_test_cases(sample_requirements)
        
        assert result["generation_id"] is not None
        assert result["status"] == GenerationStatus.COMPLETED.value
        assert result["total_generated"] > 0
        assert len(result["generated_cases"]) > 0

    @pytest.mark.asyncio
    async def test_initialize_agents(self, generator):
        """测试初始化智能体"""
        await generator._initialize_agents()
        
        assert len(generator.agents) == 4

    def test_validate_test_case_valid(self, generator):
        """测试验证有效的测试用例"""
        valid_case = {
            "用例名称": "登录功能测试",
            "步骤描述": "1. 打开登录页面\n2. 输入用户名和密码",
            "预期结果": "登录成功"
        }
        
        result = generator._validate_test_case(valid_case)
        assert result is True

    def test_deduplicate_test_cases(self, generator):
        """测试去重测试用例"""
        duplicate_cases = [
            {"用例名称": "登录测试", "步骤描述": "测试步骤1"},
            {"用例名称": "登录测试", "步骤描述": "测试步骤2"},
            {"用例名称": "退出测试", "步骤描述": "测试步骤3"}
        ]
        
        result = generator._deduplicate_test_cases(duplicate_cases)
        assert len(result) == 2


class TestTestCaseService:
    """测试用例Service单元测试"""

    @pytest.fixture
    def mock_db(self):
        return Mock()

    @pytest.fixture
    def test_case_service(self, mock_db):
        service = TestCaseService(mock_db)
        service.test_case_repo = Mock()
        return service

    @pytest.fixture
    def sample_test_case(self):
        test_case = TestCase(name="Sample Test Case", created_by_id=1)
        test_case.id = 1
        return test_case

    def test_create_test_case_success(self, test_case_service, sample_test_case):
        """测试成功创建测试用例"""
        request = TestCaseCreateRequest(name="Sample Test Case")
        test_case_service.test_case_repo.create.return_value = sample_test_case
        
        result = test_case_service.create_test_case(request, created_by_id=1)
        
        assert result.name == "Sample Test Case"
        test_case_service.test_case_repo.create.assert_called_once()

    def test_execute_test_case_success(self, test_case_service, sample_test_case):
        """测试成功执行测试用例"""
        sample_test_case.status = TestCaseStatus.PENDING.value
        test_case_service.test_case_repo.get_by_id.return_value = sample_test_case
        test_case_service.test_case_repo.update.return_value = sample_test_case
        
        result = test_case_service.execute_test_case(1, executor_id=1)
        
        assert result is not None
        test_case_service.test_case_repo.update.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])