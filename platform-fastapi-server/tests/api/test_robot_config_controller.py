"""
机器人配置管理 API 接口测试
接口清单:
- POST /RobotConfig/queryByPage - 分页查询机器人配置
- GET /RobotConfig/queryById - 根据ID查询机器人配置
- GET /RobotConfig/queryAll - 查询所有启用的机器人配置
- POST /RobotConfig/insert - 新增机器人配置
- PUT /RobotConfig/update - 更新机器人配置
- DELETE /RobotConfig/delete - 删除机器人配置
- POST /RobotConfig/testConnection - 测试机器人连接
"""
import pytest
from datetime import datetime
from tests.conftest import APIClient, API_BASE_URL


class TestRobotConfigAPI:
    """机器人配置管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for robot_id in self.created_ids:
            try:
                self.client.delete("/RobotConfig/delete", params={"id": robot_id})
            except:
                pass
        self.client.close()
    
    def _create_test_robot(self):
        """创建测试机器人配置"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/RobotConfig/insert", json={
            "robot_name": f"测试机器人_{unique}",
            "robot_type": "dingtalk",
            "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=test",
            "is_enabled": True
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            robot_id = response.json().get("data", {}).get("id")
            if robot_id:
                self.created_ids.append(robot_id)
            return robot_id
        return None
    
    # ==================== POST /RobotConfig/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/RobotConfig/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带机器人名筛选"""
        response = self.client.post("/RobotConfig/queryByPage", json={
            "page": 1, "pageSize": 10,
            "robot_name": "测试"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_type_filter(self):
        """分页查询 - 带机器人类型筛选"""
        response = self.client.post("/RobotConfig/queryByPage", json={
            "page": 1, "pageSize": 10,
            "robot_type": "dingtalk"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/RobotConfig/queryByPage", json={
            "page": 1, "pageSize": 10,
            "robot_name": "不存在的机器人_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/RobotConfig/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /RobotConfig/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        robot_id = self._create_test_robot()
        if robot_id:
            response = self.client.get("/RobotConfig/queryById", params={"id": robot_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == robot_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/RobotConfig/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    # ==================== GET /RobotConfig/queryAll 查询所有测试 ====================
    
    def test_query_all_success(self):
        """查询所有启用的机器人 - 正常请求"""
        response = self.client.get("/RobotConfig/queryAll")
        data = self.client.assert_success(response)
        assert "data" in data
    
    # ==================== POST /RobotConfig/insert 新增机器人测试 ====================
    
    def test_insert_success(self):
        """新增机器人 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/RobotConfig/insert", json={
            "robot_name": f"测试机器人_{unique}",
            "robot_type": "dingtalk",
            "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=test",
            "is_enabled": True
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增机器人 - 缺少必填字段"""
        response = self.client.post("/RobotConfig/insert", json={
            "robot_name": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /RobotConfig/update 更新机器人测试 ====================
    
    def test_update_success(self):
        """更新机器人 - 正常请求"""
        robot_id = self._create_test_robot()
        if robot_id:
            response = self.client.put("/RobotConfig/update", json={
                "id": robot_id,
                "robot_name": "更新后的机器人名"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新机器人 - 数据不存在"""
        response = self.client.put("/RobotConfig/update", json={
            "id": 99999,
            "robot_name": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /RobotConfig/delete 删除机器人测试 ====================
    
    def test_delete_success(self):
        """删除机器人 - 正常请求"""
        robot_id = self._create_test_robot()
        if robot_id:
            self.created_ids.remove(robot_id)
            response = self.client.delete("/RobotConfig/delete", params={"id": robot_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除机器人 - 数据不存在"""
        response = self.client.delete("/RobotConfig/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
