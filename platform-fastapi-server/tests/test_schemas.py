"""
Schema验证单元测试
测试所有Pydantic Schema的验证功能
"""
import pytest
from pydantic import ValidationError


class TestUserSchemas:
    """用户Schema测试"""
    
    def test_user_query_valid(self):
        """测试有效的用户查询"""
        from sysmanage.schemas.user_schema import UserQuery
        
        query = UserQuery(page=1, pageSize=10, username="test")
        assert query.page == 1
        assert query.pageSize == 10
        assert query.username == "test"
    
    def test_user_query_default(self):
        """测试用户查询默认值"""
        from sysmanage.schemas.user_schema import UserQuery
        
        query = UserQuery()
        assert query.page == 1
        assert query.pageSize == 10
    
    def test_user_create_valid(self):
        """测试有效的用户创建"""
        from sysmanage.schemas.user_schema import UserCreate
        
        user = UserCreate(
            username="newuser",
            password="password123",
            dept_id=1,
            email="test@example.com"
        )
        assert user.username == "newuser"
    
    def test_user_update_valid(self):
        """测试有效的用户更新"""
        from sysmanage.schemas.user_schema import UserUpdate
        
        user = UserUpdate(id=1, email="updated@example.com")
        assert user.id == 1
        assert user.email == "updated@example.com"


class TestRoleSchemas:
    """角色Schema测试"""
    
    def test_role_query_valid(self):
        """测试有效的角色查询"""
        from sysmanage.schemas.role_schema import RoleQuery
        
        query = RoleQuery(page=1, pageSize=10, role_name="admin")
        assert query.role_name == "admin"
    
    def test_role_create_valid(self):
        """测试有效的角色创建"""
        from sysmanage.schemas.role_schema import RoleCreate
        
        role = RoleCreate(role_name="新角色", remark="测试角色")
        assert role.role_name == "新角色"


class TestMenuSchemas:
    """菜单Schema测试"""
    
    def test_menu_create_valid(self):
        """测试有效的菜单创建"""
        from sysmanage.schemas.menu_schema import MenuCreate
        
        menu = MenuCreate(
            menu_name="测试菜单",
            parent_id=0,
            menu_type="C",
            path="/test"
        )
        assert menu.menu_name == "测试菜单"
    
    def test_menu_update_valid(self):
        """测试有效的菜单更新"""
        from sysmanage.schemas.menu_schema import MenuUpdate
        
        menu = MenuUpdate(id=1, menu_name="更新菜单")
        assert menu.id == 1


class TestDeptSchemas:
    """部门Schema测试"""
    
    def test_dept_create_valid(self):
        """测试有效的部门创建"""
        from sysmanage.schemas.dept_schema import DeptCreate
        
        dept = DeptCreate(dept_name="测试部门", parent_id=0, order_num=1)
        assert dept.dept_name == "测试部门"
    
    def test_dept_update_valid(self):
        """测试有效的部门更新"""
        from sysmanage.schemas.dept_schema import DeptUpdate
        
        dept = DeptUpdate(id=1, dept_name="更新部门")
        assert dept.id == 1


class TestApiProjectSchemas:
    """API项目Schema测试"""
    
    def test_project_query_valid(self):
        """测试有效的项目查询"""
        from apitest.schemas.api_project_schema import ApiProjectQuery
        
        query = ApiProjectQuery(page=1, pageSize=10)
        assert query.page == 1
    
    def test_project_create_valid(self):
        """测试有效的项目创建"""
        from apitest.schemas.api_project_schema import ApiProjectCreate
        
        project = ApiProjectCreate(
            project_name="测试项目",
            project_desc="项目描述"
        )
        assert project.project_name == "测试项目"


class TestApiInfoSchemas:
    """API接口Schema测试"""
    
    def test_api_info_query_valid(self):
        """测试有效的接口查询"""
        from apitest.schemas.api_info_schema import ApiInfoQuery
        
        query = ApiInfoQuery(page=1, pageSize=10, project_id=1)
        assert query.project_id == 1
    
    def test_api_info_create_valid(self):
        """测试有效的接口创建"""
        from apitest.schemas.api_info_schema import ApiInfoCreate
        
        api = ApiInfoCreate(
            project_id=1,
            api_name="测试接口",
            request_method="POST",
            request_url="https://api.test.com"
        )
        assert api.api_name == "测试接口"


class TestPluginSchemas:
    """插件Schema测试"""
    
    def test_plugin_query_valid(self):
        """测试有效的插件查询"""
        from plugin.schemas.plugin_schema import PluginQuery
        
        query = PluginQuery(pageNum=1, pageSize=10, plugin_name="test")
        assert query.plugin_name == "test"
    
    def test_plugin_query_default(self):
        """测试插件查询默认值"""
        from plugin.schemas.plugin_schema import PluginQuery
        
        query = PluginQuery()
        assert query.pageNum == 1
        assert query.pageSize == 10


class TestAiModelSchemas:
    """AI模型Schema测试"""
    
    def test_ai_model_query_valid(self):
        """测试有效的AI模型查询"""
        from aiassistant.schemas.ai_model_schema import AiModelQuery
        
        query = AiModelQuery(page=1, pageSize=10, provider="openai")
        assert query.provider == "openai"
    
    def test_ai_model_create_valid(self):
        """测试有效的AI模型创建"""
        from aiassistant.schemas.ai_model_schema import AiModelCreate
        
        model = AiModelCreate(
            model_name="测试模型",
            model_code="test_model",
            provider="openai",
            api_key="sk-test"
        )
        assert model.model_name == "测试模型"


class TestPromptTemplateSchemas:
    """提示词模板Schema测试"""
    
    def test_template_query_valid(self):
        """测试有效的模板查询"""
        from aiassistant.schemas.prompt_template_schema import PromptTemplateQuery
        
        query = PromptTemplateQuery(page=1, pageSize=10, test_type="API")
        assert query.test_type == "API"
    
    def test_template_create_valid(self):
        """测试有效的模板创建"""
        from aiassistant.schemas.prompt_template_schema import PromptTemplateCreate
        
        template = PromptTemplateCreate(
            name="测试模板",
            test_type="API",
            template_type="system",
            content="测试内容"
        )
        assert template.name == "测试模板"


class TestTestCaseSchemas:
    """测试用例Schema测试"""
    
    def test_case_query_valid(self):
        """测试有效的用例查询"""
        from aiassistant.schemas.test_case_schema import TestCaseQuery
        
        query = TestCaseQuery(page=1, pageSize=10, test_type="API", priority="P0")
        assert query.test_type == "API"
        assert query.priority == "P0"
    
    def test_case_create_valid(self):
        """测试有效的用例创建"""
        from aiassistant.schemas.test_case_schema import TestCaseCreate
        
        case = TestCaseCreate(
            case_name="测试用例",
            test_type="API",
            priority="P0",
            test_steps="[\"步骤1\"]",
            expected_result="预期结果"
        )
        assert case.case_name == "测试用例"


class TestRobotConfigSchemas:
    """机器人配置Schema测试"""
    
    def test_robot_query_valid(self):
        """测试有效的机器人查询"""
        from msgmanage.schemas.robot_config_schema import RobotConfigQuery
        
        query = RobotConfigQuery(page=1, pageSize=10, robot_type="feishu")
        assert query.robot_type == "feishu"
    
    def test_robot_create_valid(self):
        """测试有效的机器人创建"""
        from msgmanage.schemas.robot_config_schema import RobotConfigCreate
        
        robot = RobotConfigCreate(
            robot_name="测试机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test"
        )
        assert robot.robot_name == "测试机器人"


class TestGenTableSchemas:
    """代码生成表配置Schema测试"""
    
    def test_gen_table_query_valid(self):
        """测试有效的表配置查询"""
        from generator.schemas.gen_table_schema import GenTableQuery
        
        query = GenTableQuery(page=1, pageSize=10, table_name="user")
        assert query.table_name == "user"
    
    def test_gen_table_update_valid(self):
        """测试有效的表配置更新"""
        from generator.schemas.gen_table_schema import GenTableUpdate
        
        table = GenTableUpdate(id=1, table_comment="更新注释")
        assert table.id == 1
