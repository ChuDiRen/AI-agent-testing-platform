"""
用户管理 API 接口测试
接口清单:
- POST /user/queryByPage - 分页查询用户
- GET /user/queryById - 根据ID查询用户
- POST /user/insert - 新增用户
- PUT /user/update - 更新用户
- DELETE /user/delete - 删除用户
- POST /user/assignRoles - 为用户分配角色
- GET /user/roles/{user_id} - 获取用户的角色
- PUT /user/updateStatus - 更新用户状态
"""
from datetime import datetime

import pytest


class TestUserAPI:
    """用户管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        # 清理测试数据
        for user_id in self.created_ids:
            try:
                self.client.delete("/user/delete", params={"id": user_id})
            except:
                pass
    
    def _create_test_user(self):
        """创建测试用户"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/user/insert", json={
            "username": f"test_user_{unique}",
            "password": "test123456",
            "email": f"test_{unique}@test.com",
            "mobile": "13800138000",
            "status": "1"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            user_id = response.json().get("data", {}).get("id")
            if user_id:
                self.created_ids.append(user_id)
            return user_id
        return None
    
    # ==================== POST /user/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/user/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带用户名筛选"""
        response = self.client.post("/user/queryByPage", json={
            "page": 1, "pageSize": 10,
            "username": "admin"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/user/queryByPage", json={
            "page": 1, "pageSize": 10,
            "username": "不存在的用户_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_invalid_page(self):
        """分页查询 - 无效页码"""
        response = self.client.post("/user/queryByPage", json={
            "page": -1, "pageSize": 10
        })
        # 应返回错误或空结果
        assert response.status_code == 200
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/user/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /user/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        user_id = self._create_test_user()
        if user_id:
            response = self.client.get("/user/queryById", params={"id": user_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == user_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/user/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    def test_query_by_id_invalid_id(self):
        """ID查询 - 无效ID"""
        response = self.client.get("/user/queryById", params={"id": "abc"})
        assert response.status_code == 422
    
    def test_query_by_id_unauthorized(self):
        """ID查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/user/queryById", params={"id": 1})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== POST /user/insert 新增用户测试 ====================
    
    def test_insert_success(self):
        """新增用户 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/user/insert", json={
            "username": f"test_user_{unique}",
            "password": "test123456",
            "email": f"test_{unique}@test.com",
            "mobile": "13800138000",
            "status": "1"
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增用户 - 缺少必填字段"""
        response = self.client.post("/user/insert", json={
            "email": "test@test.com"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    def test_insert_empty_username(self):
        """新增用户 - 空用户名"""
        response = self.client.post("/user/insert", json={
            "username": "",
            "password": "test123456"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    def test_insert_unauthorized(self):
        """新增用户 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/user/insert", json={
            "username": "test_unauth",
            "password": "test123456"
        })
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== PUT /user/update 更新用户测试 ====================
    
    def test_update_success(self):
        """更新用户 - 正常请求"""
        user_id = self._create_test_user()
        if user_id:
            response = self.client.put("/user/update", json={
                "id": user_id,
                "email": "updated@test.com"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新用户 - 数据不存在"""
        response = self.client.put("/user/update", json={
            "id": 99999,
            "email": "test@test.com"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_update_partial_fields(self):
        """更新用户 - 部分字段"""
        user_id = self._create_test_user()
        if user_id:
            response = self.client.put("/user/update", json={
                "id": user_id,
                "mobile": "13900139000"
            })
            self.client.assert_success(response)
    
    def test_update_unauthorized(self):
        """更新用户 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.put("/user/update", json={
            "id": 1,
            "email": "unauth@test.com"
        })
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== DELETE /user/delete 删除用户测试 ====================
    
    def test_delete_success(self):
        """删除用户 - 正常请求"""
        user_id = self._create_test_user()
        if user_id:
            self.created_ids.remove(user_id)  # 从清理列表移除
            response = self.client.delete("/user/delete", params={"id": user_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除用户 - 数据不存在"""
        response = self.client.delete("/user/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_delete_unauthorized(self):
        """删除用户 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.delete("/user/delete", params={"id": 1})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== POST /user/assignRoles 分配角色测试 ====================
    
    def test_assign_roles_success(self):
        """分配角色 - 正常请求"""
        user_id = self._create_test_user()
        if user_id:
            response = self.client.post("/user/assignRoles", json={
                "id": user_id,
                "role_ids": [1]
            })
            self.client.assert_success(response)
    
    def test_assign_roles_user_not_exist(self):
        """分配角色 - 用户不存在"""
        response = self.client.post("/user/assignRoles", json={
            "id": 99999,
            "role_ids": [1]
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_assign_roles_unauthorized(self):
        """分配角色 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/user/assignRoles", json={
            "id": 1,
            "role_ids": [1]
        })
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /user/roles/{user_id} 获取用户角色测试 ====================
    
    def test_get_roles_success(self):
        """获取用户角色 - 正常请求"""
        user_id = self._create_test_user()
        if user_id:
            response = self.client.get(f"/user/roles/{user_id}")
            self.client.assert_success(response)
    
    def test_get_roles_unauthorized(self):
        """获取用户角色 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/user/roles/1")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== PUT /user/updateStatus 更新状态测试 ====================
    
    def test_update_status_success(self):
        """更新状态 - 正常请求"""
        user_id = self._create_test_user()
        if user_id:
            response = self.client.put("/user/updateStatus", json={
                "id": user_id,
                "status": "0"
            })
            self.client.assert_success(response)
    
    def test_update_status_not_exist(self):
        """更新状态 - 用户不存在"""
        response = self.client.put("/user/updateStatus", json={
            "id": 99999,
            "status": "0"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_update_status_unauthorized(self):
        """更新状态 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.put("/user/updateStatus", json={
            "id": 1,
            "status": "0"
        })
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== 参数化测试 ====================
    
    @pytest.mark.parametrize("page,page_size,expected", [
        (1, 10, True),
        (1, 50, True),
        (1, 100, True),
    ])
    def test_pagination_params(self, page, page_size, expected):
        """分页参数校验"""
        response = self.client.post("/user/queryByPage", json={
            "page": page, "pageSize": page_size
        })
        if expected:
            assert response.status_code == 200
