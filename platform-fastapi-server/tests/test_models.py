"""
数据模型单元测试
测试所有SQLModel模型的基本功能
"""
import pytest
from datetime import datetime
from sqlmodel import Session


class TestUserModel:
    """用户模型测试"""
    
    def test_create_user(self, session: Session):
        """测试创建用户"""
        from sysmanage.model.user import User
        
        user = User(
            username="model_test_user",
            password="test123",
            dept_id=1,
            email="test@example.com",
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.id is not None
        assert user.username == "model_test_user"
    
    def test_user_default_values(self, session: Session):
        """测试用户默认值"""
        from sysmanage.model.user import User
        
        user = User(
            username="default_test_user",
            password="test123"
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        assert user.status == "1"
        assert user.ssex == "2"


class TestRoleModel:
    """角色模型测试"""
    
    def test_create_role(self, session: Session):
        """测试创建角色"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="model_test_role",
            remark="测试角色",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        session.refresh(role)
        
        assert role.id is not None
        assert role.role_name == "model_test_role"


class TestMenuModel:
    """菜单模型测试"""
    
    def test_create_menu(self, session: Session):
        """测试创建菜单"""
        from sysmanage.model.menu import Menu
        
        menu = Menu(
            menu_name="model_test_menu",
            parent_id=0,
            menu_type="C",
            path="/test",
            create_time=datetime.now()
        )
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        assert menu.id is not None
        assert menu.menu_name == "model_test_menu"
    
    def test_menu_default_values(self, session: Session):
        """测试菜单默认值"""
        from sysmanage.model.menu import Menu
        
        menu = Menu(
            menu_name="default_menu",
            parent_id=0
        )
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        assert menu.menu_type == "C"
        assert menu.visible == "0"
        assert menu.status == "0"


class TestDeptModel:
    """部门模型测试"""
    
    def test_create_dept(self, session: Session):
        """测试创建部门"""
        from sysmanage.model.dept import Dept
        
        dept = Dept(
            dept_name="model_test_dept",
            parent_id=0,
            order_num=1,
            create_time=datetime.now()
        )
        session.add(dept)
        session.commit()
        session.refresh(dept)
        
        assert dept.id is not None
        assert dept.dept_name == "model_test_dept"


class TestApiProjectModel:
    """API项目模型测试"""
    
    def test_create_project(self, session: Session):
        """测试创建项目"""
        from apitest.model.ApiProjectModel import ApiProject
        
        project = ApiProject(
            project_name="model_test_project",
            project_desc="测试项目描述",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        
        assert project.id is not None
        assert project.project_name == "model_test_project"


class TestApiInfoModel:
    """API接口模型测试"""
    
    def test_create_api_info(self, session: Session, test_project):
        """测试创建API接口"""
        from apitest.model.ApiInfoModel import ApiInfo
        
        api_info = ApiInfo(
            project_id=test_project.id,
            api_name="model_test_api",
            request_method="POST",
            request_url="https://api.test.com/test",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()
        session.refresh(api_info)
        
        assert api_info.id is not None
        assert api_info.api_name == "model_test_api"


class TestPluginModel:
    """插件模型测试"""
    
    def test_create_plugin(self, session: Session):
        """测试创建插件"""
        from plugin.model.PluginModel import Plugin
        
        plugin = Plugin(
            plugin_name="model_test_plugin",
            plugin_code="model_test_code",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        assert plugin.id is not None
        assert plugin.plugin_name == "model_test_plugin"


class TestAiModelModel:
    """AI模型模型测试"""
    
    def test_create_ai_model(self, session: Session):
        """测试创建AI模型"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="model_test_ai",
            model_code="model_test_ai_code",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        
        assert model.id is not None
        assert model.model_name == "model_test_ai"


class TestPromptTemplateModel:
    """提示词模板模型测试"""
    
    def test_create_template(self, session: Session):
        """测试创建提示词模板"""
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = PromptTemplate(
            name="model_test_template",
            test_type="API",
            template_type="system",
            content="测试内容",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        assert template.id is not None
        assert template.name == "model_test_template"


class TestRobotConfigModel:
    """机器人配置模型测试"""
    
    def test_create_robot_config(self, session: Session):
        """测试创建机器人配置"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="model_test_robot",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        assert robot.id is not None
        assert robot.robot_name == "model_test_robot"


class TestGenTableModel:
    """代码生成表配置模型测试"""
    
    def test_create_gen_table(self, session: Session):
        """测试创建表配置"""
        from generator.model.GenTable import GenTable
        
        table = GenTable(
            table_name="t_model_test",
            table_comment="模型测试表",
            class_name="ModelTest",
            module_name="test",
            business_name="model_test",
            function_name="模型测试",
            create_time=datetime.now()
        )
        session.add(table)
        session.commit()
        session.refresh(table)
        
        assert table.id is not None
        assert table.table_name == "t_model_test"
