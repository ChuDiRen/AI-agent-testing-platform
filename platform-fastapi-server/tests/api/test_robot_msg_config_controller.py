"""
机器人消息模板管理 接口测试
接口清单:
- POST /RobotMsgConfig/queryByPage - 分页查询消息模板
- GET /RobotMsgConfig/queryById - 根据ID查询消息模板
- GET /RobotMsgConfig/queryByRobotId - 根据机器人ID查询消息模板
- POST /RobotMsgConfig/insert - 新增消息模板
- PUT /RobotMsgConfig/update - 更新消息模板
- DELETE /RobotMsgConfig/delete - 删除消息模板
- POST /RobotMsgConfig/send - 发送消息
"""
from datetime import datetime

import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestRobotMsgConfigAPI:
    """机器人消息模板管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for template_id in self.created_ids:
            try:
                self.client.delete("/RobotMsgConfig/delete", params={"id": template_id})
            except:
                pass
        self.client.close()
    
    def _create_test_template(self, robot_id=1):
        """创建测试消息模板"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/RobotMsgConfig/insert", json={
            "robot_id": robot_id,
            "template_name": f"测试模板_{unique}",
            "msg_type": "text",
            "template_content": "这是测试消息内容 {{name}}",
            "is_enabled": True
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            template_id = response.json().get("data", {}).get("id")
            if template_id:
                self.created_ids.append(template_id)
            return template_id
        return None
    
    # ==================== POST /RobotMsgConfig/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/RobotMsgConfig/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_robot_filter(self):
        """分页查询 - 带机器人ID筛选"""
        response = self.client.post("/RobotMsgConfig/queryByPage", json={
            "page": 1, "pageSize": 10,
            "robot_id": 1
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_type_filter(self):
        """分页查询 - 带消息类型筛选"""
        response = self.client.post("/RobotMsgConfig/queryByPage", json={
            "page": 1, "pageSize": 10,
            "msg_type": "text"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_name_filter(self):
        """分页查询 - 带模板名筛选"""
        response = self.client.post("/RobotMsgConfig/queryByPage", json={
            "page": 1, "pageSize": 10,
            "template_name": "测试"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/RobotMsgConfig/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /RobotMsgConfig/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        template_id = self._create_test_template()
        if template_id:
            response = self.client.get("/RobotMsgConfig/queryById", params={"id": template_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == template_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/RobotMsgConfig/queryById", params={"id": 99999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self):
        """ID查询 - 缺少参数"""
        response = self.client.get("/RobotMsgConfig/queryById")
        assert response.status_code == 422
    
    # ==================== GET /RobotMsgConfig/queryByRobotId 按机器人ID查询测试 ====================
    
    def test_query_by_robot_id_success(self):
        """按机器人ID查询 - 正常请求"""
        response = self.client.get("/RobotMsgConfig/queryByRobotId", params={"robot_id": 1})
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_query_by_robot_id_empty(self):
        """按机器人ID查询 - 空结果"""
        response = self.client.get("/RobotMsgConfig/queryByRobotId", params={"robot_id": 99999})
        data = self.client.assert_success(response)
        assert len(data.get("data", [])) == 0
    
    def test_query_by_robot_id_missing_param(self):
        """按机器人ID查询 - 缺少参数"""
        response = self.client.get("/RobotMsgConfig/queryByRobotId")
        assert response.status_code == 422
    
    # ==================== POST /RobotMsgConfig/insert 新增模板测试 ====================
    
    def test_insert_success(self):
        """新增模板 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/RobotMsgConfig/insert", json={
            "robot_id": 1,
            "template_name": f"测试模板_{unique}",
            "msg_type": "text",
            "template_content": "测试消息内容",
            "is_enabled": True
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_markdown_type(self):
        """新增模板 - Markdown类型"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/RobotMsgConfig/insert", json={
            "robot_id": 1,
            "template_name": f"Markdown模板_{unique}",
            "msg_type": "markdown",
            "template_content": "## 标题\n- 内容1\n- 内容2",
            "is_enabled": True
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增模板 - 缺少必填字段"""
        response = self.client.post("/RobotMsgConfig/insert", json={
            "template_name": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /RobotMsgConfig/update 更新模板测试 ====================
    
    def test_update_success(self):
        """更新模板 - 正常请求"""
        template_id = self._create_test_template()
        if template_id:
            response = self.client.put("/RobotMsgConfig/update", json={
                "id": template_id,
                "template_name": "更新后的模板名"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新模板 - 数据不存在"""
        response = self.client.put("/RobotMsgConfig/update", json={
            "id": 99999,
            "template_name": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /RobotMsgConfig/delete 删除模板测试 ====================
    
    def test_delete_success(self):
        """删除模板 - 正常请求"""
        template_id = self._create_test_template()
        if template_id:
            self.created_ids.remove(template_id)
            response = self.client.delete("/RobotMsgConfig/delete", params={"id": template_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除模板 - 数据不存在"""
        response = self.client.delete("/RobotMsgConfig/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== POST /RobotMsgConfig/send 发送消息测试 ====================
    
    def test_send_template_not_exist(self):
        """发送消息 - 模板不存在"""
        response = self.client.post("/RobotMsgConfig/send", json={
            "template_id": 99999,
            "variables": {"name": "测试"}
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_send_missing_template_id(self):
        """发送消息 - 缺少模板ID"""
        response = self.client.post("/RobotMsgConfig/send", json={
            "variables": {"name": "测试"}
        })
        assert response.status_code == 422
