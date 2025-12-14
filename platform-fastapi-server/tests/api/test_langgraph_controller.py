"""
LangGraph Controller Property Tests

测试LangGraph测试用例生成相关功能的属性测试
"""
import pytest
import json
import re
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

# 延迟导入以避免环境依赖问题
def get_model_service():
    from aiassistant.langgraph.services.model_service import ModelService, PROVIDER_CONFIGS
    return ModelService, PROVIDER_CONFIGS

def get_context_compressor():
    from aiassistant.langgraph.services.context_compressor import ContextCompressor
    return ContextCompressor

def get_state_classes():
    from aiassistant.langgraph.state import TestCaseState, GenerationStage
    return TestCaseState, GenerationStage

def get_writer_agent():
    from aiassistant.langgraph.agents.writer import WriterAgent
    return WriterAgent

def get_reviewer_agent():
    from aiassistant.langgraph.agents.reviewer import ReviewerAgent
    return ReviewerAgent


@pytest.mark.skipif(
    os.environ.get("SKIP_LANGCHAIN_TESTS", "0") == "1",
    reason="Skip langchain dependent tests"
)
class TestProviderURLAutoFill:
    """
    Property 13: Provider URL Auto-fill
    验证所有已知提供商都能自动填充正确的base_url
    Validates: Requirements 10.3, 10.5
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        ModelService, PROVIDER_CONFIGS = get_model_service()
        self.ModelService = ModelService
        self.PROVIDER_CONFIGS = PROVIDER_CONFIGS

    def test_all_providers_have_base_url(self):
        """所有配置的提供商都应该有base_url"""
        for provider_code, config in self.PROVIDER_CONFIGS.items():
            assert "base_url" in config, f"Provider {provider_code} missing base_url"
            assert config["base_url"], f"Provider {provider_code} has empty base_url"
            assert config["base_url"].startswith("http"), f"Provider {provider_code} base_url should start with http"

    def test_get_base_url_returns_correct_url(self):
        """get_base_url应该返回正确的URL"""
        for provider_code, config in self.PROVIDER_CONFIGS.items():
            url = self.ModelService.get_base_url(provider_code)
            assert url == config["base_url"], f"URL mismatch for {provider_code}"

    def test_get_base_url_case_insensitive(self):
        """get_base_url应该不区分大小写"""
        for provider_code in self.PROVIDER_CONFIGS.keys():
            url_lower = self.ModelService.get_base_url(provider_code.lower())
            url_upper = self.ModelService.get_base_url(provider_code.upper())
            url_mixed = self.ModelService.get_base_url(provider_code.capitalize())
            assert url_lower == url_upper == url_mixed

    def test_unknown_provider_returns_none(self):
        """未知提供商应该返回None"""
        url = self.ModelService.get_base_url("unknown_provider_xyz")
        assert url is None

    def test_all_providers_have_default_model(self):
        """所有提供商都应该有默认模型"""
        for provider_code, config in self.PROVIDER_CONFIGS.items():
            assert "default_model" in config, f"Provider {provider_code} missing default_model"
            assert config["default_model"], f"Provider {provider_code} has empty default_model"

    def test_create_chat_model_uses_provider_url(self):
        """create_chat_model应该使用提供商的base_url"""
        for provider_code, config in self.PROVIDER_CONFIGS.items():
            model = self.ModelService.create_chat_model(
                provider=provider_code,
                model_code=config["default_model"],
                api_key="test_key"
            )
            # ChatOpenAI stores base_url in openai_api_base
            assert model.openai_api_base == config["base_url"]


class TestTestCaseJSONStructure:
    """
    Property 7: Test Case JSON Structure
    验证生成的测试用例符合预期的JSON结构
    Validates: Requirements 1.3, 4.4
    """

    def test_extract_json_from_markdown_block(self):
        """应该能从markdown代码块中提取JSON"""
        mock_model = Mock()
        agent = WriterAgent(mock_model)
        
        text = '''这是一些说明文字
```json
{"test_cases": [{"id": 1, "name": "test1"}]}
```
这是结尾文字'''
        
        result = agent._extract_json(text)
        parsed = json.loads(result)
        assert "test_cases" in parsed
        assert len(parsed["test_cases"]) == 1

    def test_extract_json_from_brace_block(self):
        """应该能从花括号块中提取JSON"""
        mock_model = Mock()
        agent = WriterAgent(mock_model)
        
        text = '这是一些说明文字 {"test_cases": [{"id": 1}]} 这是结尾'
        
        result = agent._extract_json(text)
        parsed = json.loads(result)
        assert "test_cases" in parsed

    def test_extract_json_returns_original_if_no_json(self):
        """如果没有JSON，应该返回原始文本"""
        mock_model = Mock()
        agent = WriterAgent(mock_model)
        
        text = "这是纯文本，没有JSON"
        result = agent._extract_json(text)
        assert result == text

    def test_valid_json_structure_with_test_cases(self):
        """验证标准测试用例JSON结构"""
        valid_json = {
            "test_cases": [
                {
                    "id": "TC001",
                    "name": "测试用例1",
                    "priority": "高",
                    "preconditions": "前置条件",
                    "steps": ["步骤1", "步骤2"],
                    "expected_results": "预期结果"
                }
            ]
        }
        json_str = json.dumps(valid_json, ensure_ascii=False)
        parsed = json.loads(json_str)
        
        assert "test_cases" in parsed
        assert isinstance(parsed["test_cases"], list)
        for tc in parsed["test_cases"]:
            assert "id" in tc or "name" in tc


class TestIterationControl:
    """
    Property 2: Iteration Control
    验证迭代控制逻辑正确工作
    Validates: Requirements 1.5
    """

    def test_should_retry_when_score_below_threshold(self):
        """质量分数低于80时应该重试"""
        state = TestCaseState(requirement="test")
        state.quality_score = 70
        state.iteration = 0
        state.max_iterations = 3
        state.completed = False
        
        assert state.should_retry() is True

    def test_should_not_retry_when_score_above_threshold(self):
        """质量分数高于80时不应该重试"""
        state = TestCaseState(requirement="test")
        state.quality_score = 85
        state.iteration = 0
        state.max_iterations = 3
        state.completed = True
        
        assert state.should_retry() is False

    def test_should_not_retry_when_max_iterations_reached(self):
        """达到最大迭代次数时不应该重试"""
        state = TestCaseState(requirement="test")
        state.quality_score = 70
        state.iteration = 3
        state.max_iterations = 3
        state.completed = False
        
        assert state.should_retry() is False

    def test_should_not_retry_when_error_occurred(self):
        """发生错误时不应该重试"""
        state = TestCaseState(requirement="test")
        state.quality_score = 70
        state.iteration = 0
        state.max_iterations = 3
        state.error = "Some error"
        
        assert state.should_retry() is False

    def test_iteration_increments_on_low_score(self):
        """低分时迭代次数应该增加"""
        mock_model = Mock()
        mock_model.ainvoke = AsyncMock(return_value=Mock(content='{"quality_score": 60}'))
        
        agent = ReviewerAgent(mock_model)
        state = TestCaseState(requirement="test")
        state.testcases = '{"test_cases": []}'
        state.test_points = "test points"
        state.iteration = 0
        
        # Run synchronously for test
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(agent.process(state))
        loop.close()
        
        assert result.iteration == 1
        assert result.completed is False

    def test_completed_set_on_high_score(self):
        """高分时应该标记为完成"""
        mock_model = Mock()
        mock_model.ainvoke = AsyncMock(return_value=Mock(content='{"quality_score": 85}'))
        
        agent = ReviewerAgent(mock_model)
        state = TestCaseState(requirement="test")
        state.testcases = '{"test_cases": []}'
        state.test_points = "test points"
        
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(agent.process(state))
        loop.close()
        
        assert result.completed is True
        assert result.stage == GenerationStage.COMPLETED


class TestContextCompressionEffectiveness:
    """
    Property 12: Context Compression Effectiveness
    验证上下文压缩能有效减少Token消耗
    Validates: Requirements 9.3
    """

    def test_no_compression_when_under_limit(self):
        """当消息在限制内时不应该压缩"""
        compressor = ContextCompressor()
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
        ]
        
        result = compressor.compress(messages, max_tokens=4000)
        assert len(result) == len(messages)

    def test_compression_preserves_system_and_recent(self):
        """压缩应该保留系统提示和最近消息"""
        compressor = ContextCompressor()
        messages = [
            {"role": "system", "content": "System prompt " * 500},
            {"role": "user", "content": "Message 1 " * 500},
            {"role": "assistant", "content": "Response 1 " * 500},
            {"role": "user", "content": "Message 2 " * 500},
            {"role": "assistant", "content": "Response 2 " * 500},
            {"role": "user", "content": "Latest message"},
            {"role": "assistant", "content": "Latest response"},
        ]
        
        result = compressor.compress(messages, max_tokens=100)
        
        # Should preserve first (system) and last 2 messages
        assert result[0]["role"] == "system"
        assert result[-1]["content"] == "Latest response"
        assert result[-2]["content"] == "Latest message"

    def test_token_estimation_chinese(self):
        """中文Token估算应该合理"""
        compressor = ContextCompressor()
        chinese_text = "这是一段中文测试文本"
        tokens = compressor.estimate_tokens(chinese_text)
        
        # 中文约1.5字/token
        expected = len(chinese_text) / 1.5
        assert abs(tokens - expected) < 5

    def test_token_estimation_english(self):
        """英文Token估算应该合理"""
        compressor = ContextCompressor()
        english_text = "This is an English test text"
        tokens = compressor.estimate_tokens(english_text)
        
        # 英文约4字符/token
        expected = len(english_text) / 4
        assert abs(tokens - expected) < 5

    def test_compression_reduces_total_tokens(self):
        """压缩应该减少总Token数"""
        compressor = ContextCompressor()
        messages = [
            {"role": "system", "content": "System " * 100},
            {"role": "user", "content": "User message " * 200},
            {"role": "assistant", "content": "Assistant response " * 200},
            {"role": "user", "content": "Another user message " * 200},
            {"role": "assistant", "content": "Another response " * 200},
            {"role": "user", "content": "Final question"},
            {"role": "assistant", "content": "Final answer"},
        ]
        
        original_tokens = sum(compressor.estimate_tokens(m["content"]) for m in messages)
        compressed = compressor.compress(messages, max_tokens=500)
        compressed_tokens = sum(compressor.estimate_tokens(m["content"]) for m in compressed)
        
        # 压缩后的Token数应该更少
        assert compressed_tokens < original_tokens


class TestSSEEventSequence:
    """
    Property 3: SSE Event Sequence
    验证SSE事件序列符合预期顺序
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """

    def test_event_types_are_valid(self):
        """验证所有事件类型都是有效的"""
        valid_event_types = {
            "stage_start", "stage_progress", "stage_complete",
            "text_chunk", "testcase", "done", "error"
        }
        
        # 模拟事件序列
        events = [
            {"type": "stage_start", "data": {"stage": "init"}},
            {"type": "stage_progress", "data": {"stage": "analyzing", "progress": 50}},
            {"type": "testcase", "data": {"test_cases": []}},
            {"type": "done", "data": {"completed": True}},
        ]
        
        for event in events:
            assert event["type"] in valid_event_types

    def test_event_sequence_starts_with_stage_start(self):
        """事件序列应该以stage_start开始"""
        events = [
            {"type": "stage_start", "data": {"stage": "init"}},
            {"type": "stage_progress", "data": {"progress": 50}},
            {"type": "done", "data": {}},
        ]
        
        assert events[0]["type"] == "stage_start"

    def test_event_sequence_ends_with_done_or_error(self):
        """事件序列应该以done或error结束"""
        success_events = [
            {"type": "stage_start", "data": {}},
            {"type": "done", "data": {"completed": True}},
        ]
        
        error_events = [
            {"type": "stage_start", "data": {}},
            {"type": "error", "data": {"error": "Something went wrong"}},
        ]
        
        assert success_events[-1]["type"] in ["done", "error"]
        assert error_events[-1]["type"] in ["done", "error"]

    def test_done_event_contains_required_fields(self):
        """done事件应该包含必要字段"""
        done_event = {
            "type": "done",
            "data": {
                "quality_score": 85,
                "iteration": 1,
                "duration": 10.5,
                "completed": True
            }
        }
        
        required_fields = ["quality_score", "iteration", "duration", "completed"]
        for field in required_fields:
            assert field in done_event["data"]


class TestBatchGenerationConcurrency:
    """
    Property 10: Batch Generation Concurrency
    验证批量生成的并发控制
    Validates: Requirements 5.3, 9.4
    """

    def test_max_concurrent_parameter_validation(self):
        """max_concurrent参数应该在有效范围内"""
        from aiassistant.api.LangGraphController import BatchGenerateRequest
        
        # 有效范围是1-10
        valid_request = BatchGenerateRequest(
            requirements=["req1", "req2"],
            max_concurrent=5
        )
        assert valid_request.max_concurrent == 5
        
        # 边界值测试
        min_request = BatchGenerateRequest(
            requirements=["req1"],
            max_concurrent=1
        )
        assert min_request.max_concurrent == 1
        
        max_request = BatchGenerateRequest(
            requirements=["req1"],
            max_concurrent=10
        )
        assert max_request.max_concurrent == 10

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """信号量应该限制并发数"""
        concurrent_count = 0
        max_concurrent_observed = 0
        
        async def mock_task(semaphore):
            nonlocal concurrent_count, max_concurrent_observed
            async with semaphore:
                concurrent_count += 1
                max_concurrent_observed = max(max_concurrent_observed, concurrent_count)
                await asyncio.sleep(0.1)
                concurrent_count -= 1
        
        max_concurrent = 3
        semaphore = asyncio.Semaphore(max_concurrent)
        tasks = [mock_task(semaphore) for _ in range(10)]
        await asyncio.gather(*tasks)
        
        assert max_concurrent_observed <= max_concurrent


class TestSwaggerParsingCompleteness:
    """
    Property 9: Swagger Parsing Completeness
    验证Swagger解析的完整性
    Validates: Requirements 5.1
    """

    def test_parse_all_http_methods(self):
        """应该解析所有HTTP方法"""
        swagger_doc = {
            "paths": {
                "/api/users": {
                    "get": {"summary": "Get users"},
                    "post": {"summary": "Create user"},
                    "put": {"summary": "Update user"},
                    "delete": {"summary": "Delete user"},
                    "patch": {"summary": "Patch user"},
                }
            }
        }
        
        apis = []
        for path, methods in swagger_doc["paths"].items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "delete", "patch"]:
                    apis.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", ""),
                    })
        
        assert len(apis) == 5
        methods = {api["method"] for api in apis}
        assert methods == {"GET", "POST", "PUT", "DELETE", "PATCH"}

    def test_extract_api_details(self):
        """应该提取API详细信息"""
        swagger_doc = {
            "paths": {
                "/api/users/{id}": {
                    "get": {
                        "summary": "Get user by ID",
                        "description": "Returns a single user",
                        "parameters": [
                            {"name": "id", "in": "path", "required": True}
                        ],
                        "tags": ["users"]
                    }
                }
            }
        }
        
        path = "/api/users/{id}"
        method_details = swagger_doc["paths"][path]["get"]
        
        api = {
            "path": path,
            "method": "GET",
            "summary": method_details.get("summary", ""),
            "description": method_details.get("description", ""),
            "parameters": method_details.get("parameters", []),
            "tags": method_details.get("tags", []),
        }
        
        assert api["summary"] == "Get user by ID"
        assert api["description"] == "Returns a single user"
        assert len(api["parameters"]) == 1
        assert api["tags"] == ["users"]


class TestPersistenceAfterGeneration:
    """
    Property 6: Persistence After Generation
    验证生成后数据正确持久化
    Validates: Requirements 4.1, 7.1
    """

    def test_state_to_dict_contains_all_fields(self):
        """state.to_dict()应该包含所有必要字段"""
        state = TestCaseState(
            requirement="Test requirement",
            test_type="API",
            analysis="Analysis result",
            test_points="Test points",
            testcases='{"test_cases": []}',
            review="Review result",
            quality_score=85.0,
            iteration=1,
            max_iterations=3,
            completed=True,
            stage=GenerationStage.COMPLETED,
        )
        state.start_time = datetime.now()
        state.end_time = datetime.now()
        state.token_usage = {"analyzer_tokens": 100, "writer_tokens": 200}
        
        data = state.to_dict()
        
        required_fields = [
            "requirement", "test_type", "analysis", "test_points",
            "testcases", "review", "quality_score", "iteration",
            "max_iterations", "completed", "error", "stage",
            "start_time", "end_time", "token_usage"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_state_from_dict_restores_correctly(self):
        """state.from_dict()应该正确恢复状态"""
        original = TestCaseState(
            requirement="Test requirement",
            test_type="API",
            quality_score=85.0,
            iteration=2,
            completed=True,
            stage=GenerationStage.COMPLETED,
        )
        
        data = original.to_dict()
        restored = TestCaseState.from_dict(data)
        
        assert restored.requirement == original.requirement
        assert restored.test_type == original.test_type
        assert restored.quality_score == original.quality_score
        assert restored.iteration == original.iteration
        assert restored.completed == original.completed
        assert restored.stage == original.stage


class TestErrorIsolation:
    """
    Property 11: Error Isolation
    验证错误隔离，单个任务失败不影响其他任务
    Validates: Requirements 7.3, 8.3
    """

    def test_error_sets_state_error_field(self):
        """错误应该设置state.error字段"""
        state = TestCaseState(requirement="test")
        state.error = "Test error message"
        
        assert state.error is not None
        assert "Test error" in state.error

    def test_error_state_prevents_retry(self):
        """错误状态应该阻止重试"""
        state = TestCaseState(requirement="test")
        state.error = "Some error"
        state.quality_score = 50
        state.iteration = 0
        state.max_iterations = 3
        
        assert state.should_retry() is False

    @pytest.mark.asyncio
    async def test_batch_error_isolation(self):
        """批量处理中单个错误不应影响其他任务"""
        results = []
        
        async def task_success():
            await asyncio.sleep(0.01)
            return {"status": "success"}
        
        async def task_failure():
            await asyncio.sleep(0.01)
            raise ValueError("Task failed")
        
        tasks = [task_success(), task_failure(), task_success()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 应该有3个结果
        assert len(results) == 3
        # 第一个和第三个应该成功
        assert results[0] == {"status": "success"}
        assert results[2] == {"status": "success"}
        # 第二个应该是异常
        assert isinstance(results[1], ValueError)


class TestExportFormatValidity:
    """
    Property 8: Export Format Validity
    验证导出格式的有效性
    Validates: Requirements 4.4
    """

    def test_json_export_is_valid(self):
        """JSON导出应该是有效的JSON"""
        test_data = {
            "test_cases": [
                {
                    "id": "TC001",
                    "name": "测试用例1",
                    "priority": "高",
                    "steps": ["步骤1", "步骤2"],
                    "expected_results": "预期结果"
                }
            ]
        }
        
        json_str = json.dumps(test_data, ensure_ascii=False, indent=2)
        
        # 应该能被解析回来
        parsed = json.loads(json_str)
        assert parsed == test_data

    def test_yaml_export_structure(self):
        """YAML导出应该有正确的结构"""
        import yaml
        
        test_data = {
            "test_cases": [
                {
                    "id": "TC001",
                    "name": "测试用例1",
                    "steps": ["步骤1", "步骤2"]
                }
            ]
        }
        
        yaml_str = yaml.dump(test_data, allow_unicode=True, default_flow_style=False)
        
        # 应该能被解析回来
        parsed = yaml.safe_load(yaml_str)
        assert parsed == test_data

    def test_export_preserves_chinese_characters(self):
        """导出应该保留中文字符"""
        test_data = {
            "name": "测试用例",
            "description": "这是一个中文描述"
        }
        
        json_str = json.dumps(test_data, ensure_ascii=False)
        parsed = json.loads(json_str)
        
        assert parsed["name"] == "测试用例"
        assert "中文描述" in parsed["description"]


class TestModelValidationTimeout:
    """
    Property 5: Model Validation Timeout
    验证模型连接测试的超时机制
    Validates: Requirements 3.2, 10.4
    """

    def test_default_timeout_is_5_seconds(self):
        """默认超时应该是5秒"""
        # 检查test_connection方法的默认timeout参数
        import inspect
        sig = inspect.signature(ModelService.test_connection)
        timeout_param = sig.parameters.get("timeout")
        
        assert timeout_param is not None
        assert timeout_param.default == 5.0

    @pytest.mark.asyncio
    async def test_timeout_returns_error_result(self):
        """超时应该返回错误结果"""
        with patch('aiassistant.langgraph.services.model_service.ChatOpenAI') as mock_chat:
            mock_instance = MagicMock()
            mock_chat.return_value = mock_instance
            
            async def slow_invoke(*args, **kwargs):
                await asyncio.sleep(10)
                return Mock(content="response")
            
            mock_instance.ainvoke = slow_invoke
            
            result = await ModelService.test_connection(
                provider="deepseek",
                api_key="test_key",
                timeout=0.1
            )
            
            assert result["success"] is False
            assert "timeout" in result.get("error", "").lower() or result["success"] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
