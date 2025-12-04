"""
集成测试
测试多个模块之间的交互
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestUserRoleIntegration:
    """用户角色集成测试"""
    
    def test_user_role_workflow(self, client: TestClient, session: Session):
        """测试用户角色完整工作流"""
        from sysmanage.model.user import User
        from sysmanage.model.role import Role
        
        # 1. 创建用户
        user = User(
            username="integration_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # 2. 创建角色
        role = Role(
            role_name="integration_role",
            remark="集成测试角色",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        session.refresh(role)
        
        # 3. 为用户分配角色
        response = client.post("/user/assignRoles", json={
            "id": user.id,
            "role_ids": [role.id]
        })
        assert response.status_code == 200
        assert response.json()["code"] == 200
        
        # 4. 验证用户角色
        response = client.get(f"/user/roles/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert role.id in data["data"]


class TestApiTestWorkflow:
    """API测试工作流集成测试"""
    
    def test_api_test_workflow(self, client: TestClient, session: Session):
        """测试API测试完整工作流"""
        from apitest.model.ApiProjectModel import ApiProject
        from apitest.model.ApiInfoModel import ApiInfo
        from apitest.model.ApiInfoCaseModel import ApiInfoCase
        
        # 1. 创建项目
        project = ApiProject(
            project_name="集成测试项目",
            project_desc="用于集成测试",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        
        # 2. 创建API接口
        api_info = ApiInfo(
            project_id=project.id,
            api_name="集成测试接口",
            request_method="POST",
            request_url="https://api.test.com/integration",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()
        session.refresh(api_info)
        
        # 3. 创建测试用例
        test_case = ApiInfoCase(
            project_id=project.id,
            case_name="集成测试用例",
            case_desc="测试描述",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(test_case)
        session.commit()
        session.refresh(test_case)
        
        # 4. 验证项目下的接口
        response = client.post("/ApiInfo/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project.id
        })
        assert response.status_code == 200
        
        # 5. 验证项目下的用例
        response = client.post("/ApiInfoCase/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": project.id
        })
        assert response.status_code == 200


class TestPluginExecutorIntegration:
    """插件执行器集成测试"""
    
    def test_plugin_executor_workflow(self, client: TestClient, session: Session):
        """测试插件执行器工作流"""
        from plugin.model.PluginModel import Plugin
        
        # 1. 注册插件
        plugin = Plugin(
            plugin_name="集成测试执行器",
            plugin_code="integration_executor",
            plugin_type="executor",
            version="1.0.0",
            is_enabled=1,
            command="python",
            create_time=datetime.now()
        )
        session.add(plugin)
        session.commit()
        session.refresh(plugin)
        
        # 2. 查询插件
        response = client.get(f"/Plugin/queryById?id={plugin.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
        
        # 3. 健康检查
        response = client.post(f"/Plugin/healthCheck?id={plugin.id}")
        assert response.status_code == 200
        
        # 4. 获取执行器列表
        response = client.get("/Task/executors")
        assert response.status_code == 200


class TestAiAssistantIntegration:
    """AI助手集成测试"""
    
    def test_ai_assistant_workflow(self, client: TestClient, session: Session):
        """测试AI助手工作流"""
        from aiassistant.model.AiModel import AiModel
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        # 1. 创建AI模型
        model = AiModel(
            model_name="集成测试模型",
            model_code="integration_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        
        # 2. 创建提示词模板
        template = PromptTemplate(
            name="集成测试模板",
            test_type="API",
            template_type="system",
            content="请生成{count}个测试用例",
            is_active=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        # 3. 查询启用的模型
        response = client.get("/AiModel/queryEnabled")
        assert response.status_code == 200
        
        # 4. 查询模板
        response = client.get("/PromptTemplate/queryByType?testType=API")
        assert response.status_code == 200


class TestRobotMessageIntegration:
    """机器人消息集成测试"""
    
    def test_robot_message_workflow(self, client: TestClient, session: Session):
        """测试机器人消息工作流"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
        
        # 1. 创建机器人配置
        robot = RobotConfig(
            robot_name="集成测试机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/integration",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        # 2. 创建消息模板
        template = RobotMsgConfig(
            robot_id=robot.id,
            template_name="集成测试模板",
            msg_type="text",
            template_content="测试结果：{{result}}",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        # 3. 查询机器人的模板
        response = client.get(f"/RobotMsgConfig/queryByRobotId?robot_id={robot.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
