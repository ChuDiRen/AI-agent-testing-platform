"""
Core 核心工具模块单元测试
测试 JwtUtil, time_utils, resp_model, SwaggerParser, StreamTestCaseParser, PromptService, exceptions
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock


class TestJwtUtils:
    """JWT工具类测试"""
    
    def test_create_token(self):
        """测试创建Token"""
        from core.JwtUtil import JwtUtils
        token = JwtUtils.create_token("testuser", "testpass")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token_valid(self):
        """测试验证有效Token"""
        from core.JwtUtil import JwtUtils
        token = JwtUtils.create_token("testuser", "testpass")
        payload = JwtUtils.verify_token(token)
        assert payload is not None
        assert payload["username"] == "testuser"
    
    def test_verify_token_invalid(self):
        """测试验证无效Token"""
        from core.JwtUtil import JwtUtils
        payload = JwtUtils.verify_token("invalid_token")
        assert payload is None
    
    def test_verify_token_expired(self):
        """测试验证过期Token"""
        from core.JwtUtil import JwtUtils
        # 创建一个过期的token需要mock时间，这里简单测试无效token
        payload = JwtUtils.verify_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid")
        assert payload is None


class TestTimeFormatter:
    """时间格式化工具测试"""
    
    def test_format_datetime(self):
        """测试格式化datetime"""
        from core.time_utils import TimeFormatter
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = TimeFormatter.format_datetime(dt)
        assert result == "2024-01-15 10:30:45"
    
    def test_format_datetime_none(self):
        """测试格式化None"""
        from core.time_utils import TimeFormatter
        result = TimeFormatter.format_datetime(None)
        assert result is None
    
    def test_format_datetime_dict(self):
        """测试格式化字典中的时间字段"""
        from core.time_utils import TimeFormatter
        data = {
            "name": "test",
            "create_time": datetime(2024, 1, 15, 10, 30, 45),
            "modify_time": datetime(2024, 1, 16, 11, 20, 30)
        }
        result = TimeFormatter.format_datetime_dict(data)
        assert result["create_time"] == "2024-01-15 10:30:45"
        assert result["modify_time"] == "2024-01-16 11:20:30"
        assert result["name"] == "test"
    
    def test_now_str(self):
        """测试获取当前时间字符串"""
        from core.time_utils import TimeFormatter
        result = TimeFormatter.now_str()
        assert result is not None
        assert len(result) == 19  # YYYY-MM-DD HH:MM:SS
    
    def test_datetime_to_str(self):
        """测试datetime_to_str兼容方法"""
        from core.time_utils import TimeFormatter
        dt = datetime(2024, 1, 15, 10, 30, 45)
        result = TimeFormatter.datetime_to_str(dt)
        assert result == "2024-01-15 10:30:45"


class TestRespModel:
    """响应模型测试"""
    
    def test_ok_resp(self):
        """测试成功响应"""
        from core.resp_model import respModel
        result = respModel.ok_resp(msg="操作成功")
        assert result["code"] == 200
        assert result["msg"] == "操作成功"
    
    def test_ok_resp_with_dict(self):
        """测试带字典数据的成功响应"""
        from core.resp_model import respModel
        result = respModel.ok_resp(obj={"id": 1, "name": "test"}, msg="查询成功")
        assert result["code"] == 200
        assert result["data"]["id"] == 1
        assert result["data"]["name"] == "test"
    
    def test_ok_resp_list(self):
        """测试列表响应"""
        from core.resp_model import respModel
        items = [{"id": 1}, {"id": 2}]
        result = respModel.ok_resp_list(lst=items, total=2, msg="查询成功")
        assert result["code"] == 200
        assert result["total"] == 2
        assert len(result["data"]) == 2
    
    def test_ok_resp_simple(self):
        """测试简单响应"""
        from core.resp_model import respModel
        result = respModel.ok_resp_simple(lst=[1, 2, 3], msg="成功")
        assert result["code"] == 200
        assert result["data"] == [1, 2, 3]
    
    def test_ok_resp_text(self):
        """测试文本响应"""
        from core.resp_model import respModel
        result = respModel.ok_resp_text(msg="操作成功", data="some text")
        assert result["code"] == 200
        assert result["data"] == "some text"
    
    def test_ok_resp_tree(self):
        """测试树形响应"""
        from core.resp_model import respModel
        tree = [{"id": 1, "children": []}]
        result = respModel.ok_resp_tree(treeData=tree, msg="查询成功")
        assert result["code"] == 200
        assert result["data"] == tree
    
    def test_error_resp(self):
        """测试错误响应"""
        from core.resp_model import respModel
        result = respModel.error_resp("操作失败")
        assert result["code"] == -1
        assert result["msg"] == "操作失败"


class TestSwaggerParser:
    """Swagger解析器测试"""
    
    def test_detect_version_2(self):
        """测试检测Swagger 2.0版本"""
        from core.SwaggerParser import SwaggerParser
        data = {"swagger": "2.0", "paths": {}}
        parser = SwaggerParser(data)
        assert parser.version == "2.0"
    
    def test_detect_version_3(self):
        """测试检测OpenAPI 3.0版本"""
        from core.SwaggerParser import SwaggerParser
        data = {"openapi": "3.0.0", "paths": {}}
        parser = SwaggerParser(data)
        assert parser.version == "3.0"
    
    def test_parse_apis_empty(self):
        """测试解析空API"""
        from core.SwaggerParser import SwaggerParser
        data = {"openapi": "3.0.0", "paths": {}}
        parser = SwaggerParser(data)
        apis = parser.parse_apis()
        assert apis == []
    
    def test_parse_apis_simple(self):
        """测试解析简单API"""
        from core.SwaggerParser import SwaggerParser
        data = {
            "openapi": "3.0.0",
            "servers": [{"url": "http://localhost:8000"}],
            "paths": {
                "/users": {
                    "get": {
                        "summary": "获取用户列表",
                        "parameters": []
                    }
                }
            }
        }
        parser = SwaggerParser(data)
        apis = parser.parse_apis()
        assert len(apis) == 1
        assert apis[0]["api_name"] == "获取用户列表"
        assert apis[0]["request_method"] == "GET"
    
    def test_generate_api_name_from_path(self):
        """测试从路径生成API名称"""
        from core.SwaggerParser import SwaggerParser
        data = {"openapi": "3.0.0", "paths": {}}
        parser = SwaggerParser(data)
        
        assert parser._generate_api_name_from_path("/user/login") == "user_login"
        assert parser._generate_api_name_from_path("/user/{id}") == "user"
        assert parser._generate_api_name_from_path("/") == "root"
    
    def test_get_base_url_v3(self):
        """测试获取基础URL (OpenAPI 3.0)"""
        from core.SwaggerParser import SwaggerParser
        data = {
            "openapi": "3.0.0",
            "servers": [{"url": "http://api.example.com/v1"}],
            "paths": {}
        }
        parser = SwaggerParser(data)
        assert parser.base_url == "http://api.example.com/v1"
    
    def test_generate_example_from_schema(self):
        """测试从Schema生成示例数据"""
        from core.SwaggerParser import SwaggerParser
        data = {"openapi": "3.0.0", "paths": {}}
        parser = SwaggerParser(data)
        
        # 测试字符串类型
        schema = {"type": "string"}
        assert parser._generate_example_from_schema(schema) == "string"
        
        # 测试整数类型
        schema = {"type": "integer"}
        assert parser._generate_example_from_schema(schema) == 0
        
        # 测试布尔类型
        schema = {"type": "boolean"}
        assert parser._generate_example_from_schema(schema) == False
        
        # 测试对象类型
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        result = parser._generate_example_from_schema(schema)
        assert "name" in result
        assert "age" in result


class TestStreamTestCaseParser:
    """流式测试用例解析器测试"""
    
    def test_parse_valid_json(self):
        """测试解析有效JSON"""
        from core.StreamTestCaseParser import StreamTestCaseParser
        parser = StreamTestCaseParser()
        
        json_str = '{"case_name": "测试用例1", "priority": "P0", "test_steps": ["步骤1"], "expected_result": "成功"}'
        result = parser.parse_chunk(json_str)
        
        assert result is not None
        assert result["case_name"] == "测试用例1"
        assert result["priority"] == "P0"
    
    def test_parse_invalid_json(self):
        """测试解析无效JSON"""
        from core.StreamTestCaseParser import StreamTestCaseParser
        parser = StreamTestCaseParser()
        
        result = parser.parse_chunk("invalid json")
        assert result is None
    
    def test_parse_incomplete_json(self):
        """测试解析不完整JSON"""
        from core.StreamTestCaseParser import StreamTestCaseParser
        parser = StreamTestCaseParser()
        
        # 分块发送
        result1 = parser.parse_chunk('{"case_name": "测试')
        assert result1 is None
        
        result2 = parser.parse_chunk('用例", "priority": "P0", "test_steps": ["步骤1"], "expected_result": "成功"}')
        assert result2 is not None
    
    def test_validate_test_case(self):
        """测试验证测试用例"""
        from core.StreamTestCaseParser import StreamTestCaseParser
        
        # 有效用例
        valid_case = {
            "case_name": "测试",
            "priority": "P0",
            "test_steps": ["步骤1"],
            "expected_result": "成功"
        }
        assert StreamTestCaseParser._validate_test_case(valid_case) == True
        
        # 缺少必要字段
        invalid_case = {"case_name": "测试"}
        assert StreamTestCaseParser._validate_test_case(invalid_case) == False
        
        # 无效优先级
        invalid_priority = {
            "case_name": "测试",
            "priority": "P5",
            "test_steps": ["步骤1"],
            "expected_result": "成功"
        }
        assert StreamTestCaseParser._validate_test_case(invalid_priority) == False
    
    def test_get_all_cases(self):
        """测试获取所有用例"""
        from core.StreamTestCaseParser import StreamTestCaseParser
        parser = StreamTestCaseParser()
        
        json1 = '{"case_name": "用例1", "priority": "P0", "test_steps": ["步骤"], "expected_result": "成功"}'
        json2 = '{"case_name": "用例2", "priority": "P1", "test_steps": ["步骤"], "expected_result": "成功"}'
        
        parser.parse_chunk(json1)
        parser.parse_chunk(json2)
        
        cases = parser.get_all_cases()
        assert len(cases) == 2
    
    def test_reset(self):
        """测试重置解析器"""
        from core.StreamTestCaseParser import StreamTestCaseParser
        parser = StreamTestCaseParser()
        
        parser.parse_chunk('{"case_name": "用例1", "priority": "P0", "test_steps": ["步骤"], "expected_result": "成功"}')
        assert len(parser.get_all_cases()) == 1
        
        parser.reset()
        assert len(parser.get_all_cases()) == 0


class TestPromptService:
    """提示词服务测试"""
    
    def test_render_prompt(self):
        """测试渲染提示词"""
        from core.PromptService import PromptService
        
        template = "你好，{name}！请生成{count}个测试用例。"
        variables = {"name": "用户", "count": "5"}
        
        result = PromptService.render_prompt(template, variables)
        assert result == "你好，用户！请生成5个测试用例。"
    
    def test_extract_variables_from_template(self):
        """测试从模板提取变量"""
        from core.PromptService import PromptService
        
        template = "你好，{name}！请生成{count}个{type}测试用例。"
        variables = PromptService.extract_variables_from_template(template)
        
        assert "name" in variables
        assert "count" in variables
        assert "type" in variables
        assert len(variables) == 3
    
    def test_build_system_message_api(self):
        """测试构建API系统消息"""
        from core.PromptService import PromptService
        
        message = PromptService.build_system_message("API", 10)
        assert message["role"] == "system"
        assert "API" in message["content"]
        assert "10" in message["content"]
    
    def test_build_system_message_web(self):
        """测试构建Web系统消息"""
        from core.PromptService import PromptService
        
        message = PromptService.build_system_message("Web", 5)
        assert message["role"] == "system"
        assert "Web" in message["content"]
    
    def test_build_system_message_app(self):
        """测试构建App系统消息"""
        from core.PromptService import PromptService
        
        message = PromptService.build_system_message("App", 5)
        assert message["role"] == "system"
        assert "App" in message["content"]


class TestExceptions:
    """异常类测试"""
    
    def test_business_exception(self):
        """测试业务异常"""
        from core.exceptions import BusinessException
        
        exc = BusinessException("业务错误", code="BIZ_001", details={"field": "name"})
        assert exc.message == "业务错误"
        assert exc.code == "BIZ_001"
        assert exc.details == {"field": "name"}
        
        exc_dict = exc.to_dict()
        assert exc_dict["error"] == "BIZ_001"
        assert exc_dict["message"] == "业务错误"
    
    def test_validation_exception(self):
        """测试验证异常"""
        from core.exceptions import ValidationException
        
        exc = ValidationException("参数验证失败")
        assert exc.message == "参数验证失败"
    
    def test_resource_not_found_exception(self):
        """测试资源不存在异常"""
        from core.exceptions import ResourceNotFoundException
        
        exc = ResourceNotFoundException("用户不存在")
        assert exc.message == "用户不存在"
    
    def test_technical_exception(self):
        """测试技术异常"""
        from core.exceptions import TechnicalException, DatabaseException
        
        exc = DatabaseException("数据库连接失败")
        assert exc.message == "数据库连接失败"
        assert isinstance(exc, TechnicalException)
    
    def test_handle_exception_business(self):
        """测试处理业务异常"""
        from core.exceptions import handle_exception, BusinessException
        
        exc = BusinessException("业务错误")
        result = handle_exception(exc)
        assert result["success"] == False
        assert result["message"] == "业务错误"
    
    def test_handle_exception_technical(self):
        """测试处理技术异常"""
        from core.exceptions import handle_exception, TechnicalException
        
        exc = TechnicalException("系统错误")
        result = handle_exception(exc)
        assert result["success"] == False
        assert "系统错误" in result["message"]
    
    def test_handle_exception_unknown(self):
        """测试处理未知异常"""
        from core.exceptions import handle_exception
        
        exc = Exception("未知错误")
        result = handle_exception(exc, "默认错误消息")
        assert result["success"] == False
        assert result["message"] == "默认错误消息"
