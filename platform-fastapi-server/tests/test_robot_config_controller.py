"""
RobotConfigController 机器人配置模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestRobotConfigController:
    """机器人配置控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询机器人配置"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="测试机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        
        response = client.post("/RobotConfig/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="飞书机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        
        response = client.post("/RobotConfig/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "robot_type": "feishu"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询机器人配置"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="ID查询机器人",
            robot_type="dingtalk",
            webhook_url="https://oapi.dingtalk.com/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        response = client.get(f"/RobotConfig/queryById?id={robot.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["robot_name"] == "ID查询机器人"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的机器人配置"""
        response = client.get("/RobotConfig/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert "没有数据" in data.get("msg", "")
    
    def test_query_all(self, client: TestClient, session: Session):
        """测试查询所有启用的机器人"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="启用的机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/test",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        
        response = client.get("/RobotConfig/queryAll")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_robot(self, client: TestClient):
        """测试新增机器人配置"""
        response = client.post("/RobotConfig/insert", json={
            "robot_name": "新增测试机器人",
            "robot_type": "feishu",
            "webhook_url": "https://open.feishu.cn/new",
            "is_enabled": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
    
    def test_update_robot(self, client: TestClient, session: Session):
        """测试更新机器人配置"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="待更新机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/old",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        response = client.put("/RobotConfig/update", json={
            "id": robot.id,
            "robot_name": "更新后的机器人名",
            "webhook_url": "https://open.feishu.cn/updated"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_robot_not_found(self, client: TestClient):
        """测试更新不存在的机器人配置"""
        response = client.put("/RobotConfig/update", json={
            "id": 99999,
            "robot_name": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_robot(self, client: TestClient, session: Session):
        """测试删除机器人配置"""
        from msgmanage.model.RobotConfigModel import RobotConfig
        
        robot = RobotConfig(
            robot_name="待删除机器人",
            robot_type="feishu",
            webhook_url="https://open.feishu.cn/delete",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(robot)
        session.commit()
        session.refresh(robot)
        
        response = client.delete(f"/RobotConfig/delete?id={robot.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_robot_not_found(self, client: TestClient):
        """测试删除不存在的机器人配置"""
        response = client.delete("/RobotConfig/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
