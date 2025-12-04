"""
RobotMsgConfigController 机器人消息模板模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestRobotMsgConfigController:
    """机器人消息模板控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询消息模板"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
        
        robot = RobotConfig(
            robot_name="模板测试机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        template = RobotMsgConfig(
            robot_id=robot.id,
            template_name="测试模板",
            msg_type="text",
            template_content="测试内容",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        
        response = client.post("/RobotMsgConfig/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询消息模板"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
        
        robot = RobotConfig(
            robot_name="ID查询机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        template = RobotMsgConfig(
            robot_id=robot.id,
            template_name="ID查询模板",
            msg_type="text",
            template_content="测试内容",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        response = client.get(f"/RobotMsgConfig/queryById?id={template.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["template_name"] == "ID查询模板"
    
    def test_query_by_robot_id(self, client: TestClient, session: Session):
        """测试根据机器人ID查询模板"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
        
        robot = RobotConfig(
            robot_name="关联查询机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        template = RobotMsgConfig(
            robot_id=robot.id,
            template_name="关联模板",
            msg_type="text",
            template_content="测试内容",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        
        response = client.get(f"/RobotMsgConfig/queryByRobotId?robot_id={robot.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_template(self, client: TestClient, session: Session):
        """测试新增消息模板"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="新增模板机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        response = client.post("/RobotMsgConfig/insert", json={
            "robot_id": robot.id,
            "template_name": "新增测试模板",
            "msg_type": "text",
            "template_content": "这是测试内容 {{name}}",
            "is_enabled": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
    
    def test_update_template(self, client: TestClient, session: Session):
        """测试更新消息模板"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
        
        robot = RobotConfig(
            robot_name="更新模板机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        template = RobotMsgConfig(
            robot_id=robot.id,
            template_name="待更新模板",
            msg_type="text",
            template_content="原始内容",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        response = client.put("/RobotMsgConfig/update", json={
            "id": template.id,
            "template_name": "更新后的模板名",
            "template_content": "更新后的内容"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_template(self, client: TestClient, session: Session):
        """测试删除消息模板"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        from msgmanage.model.RobotMsgConfigModel import RobotMsgConfig
        
        robot = RobotConfig(
            robot_name="删除模板机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        template = RobotMsgConfig(
            robot_id=robot.id,
            template_name="待删除模板",
            msg_type="text",
            template_content="测试内容",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(template)
        session.commit()
        session.refresh(template)
        
        response = client.delete(f"/RobotMsgConfig/delete?id={template.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestReplaceVariables:
    """变量替换测试"""
    
    def test_replace_variables(self):
        """测试替换模板变量"""
        from msgmanage.api.RobotMsgConfigController import replace_variables
        
        template = "你好，{{name}}！测试结果：{{result}}"
        variables = {"name": "张三", "result": "通过"}
        
        result = replace_variables(template, variables)
        assert result == "你好，张三！测试结果：通过"
    
    def test_replace_variables_empty(self):
        """测试空变量替换"""
        from msgmanage.api.RobotMsgConfigController import replace_variables
        
        template = "固定内容"
        result = replace_variables(template, {})
        assert result == "固定内容"
    
    def test_replace_variables_none(self):
        """测试None变量替换"""
        from msgmanage.api.RobotMsgConfigController import replace_variables
        
        template = "固定内容"
        result = replace_variables(template, None)
        assert result == "固定内容"
