"""
角色管理 API 接口测试
接口清单:
- POST /role/queryByPage - 分页查询角色
- GET /role/queryById - 根据ID查询角色
- POST /role/insert - 新增角色
- PUT /role/update - 更新角色
- DELETE /role/delete - 删除角色
- POST /role/assignMenus - 为角色分配菜单权限
- GET /role/menus/{role_id} - 获取角色的菜单权限
"""
from datetime import datetime

import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestRoleAPI:
    """角色管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for role_id in self.created_ids:
            try:
                self.client.delete("/role/delete", params={"id": role_id})
            except:
                pass
        self.client.close()
    
    def _create_test_role(self):
        """创建测试角色"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/role/insert", json={
            "role_name": f"测试角色_{unique}",
            "role_key": f"test_role_{unique}",
            "remark": "测试角色"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            role_id = response.json().get("data", {}).get("id")
            if role_id:
                self.created_ids.append(role_id)
            return role_id
        return None
    
    # ==================== POST /role/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/role/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带角色名筛选"""
        response = self.client.post("/role/queryByPage", json={
            "page": 1, "pageSize": 10,
            "role_name": "管理员"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/role/queryByPage", json={
            "page": 1, "pageSize": 10,
            "role_name": "不存在的角色_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/role/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /role/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        role_id = self._create_test_role()
        if role_id:
            response = self.client.get("/role/queryById", params={"id": role_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == role_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/role/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == -1 or data["data"] is None
    
    # ==================== POST /role/insert 新增角色测试 ====================
    
    def test_insert_success(self):
        """新增角色 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/role/insert", json={
            "role_name": f"测试角色_{unique}",
            "role_key": f"test_role_{unique}",
            "remark": "测试角色"
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_duplicate(self):
        """新增角色 - 重复角色名"""
        role_id = self._create_test_role()
        if role_id:
            # 获取刚创建的角色名
            response = self.client.get("/role/queryById", params={"id": role_id})
            role_name = response.json()["data"]["role_name"]
            # 尝试创建同名角色
            response = self.client.post("/role/insert", json={
                "role_name": role_name,
                "role_key": "duplicate_key"
            })
            assert response.json()["code"] != 200 or "已存在" in response.json().get("msg", "")
    
    def test_insert_missing_required(self):
        """新增角色 - 缺少必填字段"""
        response = self.client.post("/role/insert", json={
            "remark": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /role/update 更新角色测试 ====================
    
    def test_update_success(self):
        """更新角色 - 正常请求"""
        role_id = self._create_test_role()
        if role_id:
            response = self.client.put("/role/update", json={
                "id": role_id,
                "remark": "更新后的备注"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新角色 - 数据不存在"""
        response = self.client.put("/role/update", json={
            "id": 99999,
            "remark": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /role/delete 删除角色测试 ====================
    
    def test_delete_success(self):
        """删除角色 - 正常请求"""
        role_id = self._create_test_role()
        if role_id:
            self.created_ids.remove(role_id)
            response = self.client.delete("/role/delete", params={"id": role_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除角色 - 数据不存在"""
        response = self.client.delete("/role/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== POST /role/assignMenus 分配菜单测试 ====================
    
    def test_assign_menus_success(self):
        """分配菜单 - 正常请求"""
        role_id = self._create_test_role()
        if role_id:
            response = self.client.post("/role/assignMenus", json={
                "id": role_id,
                "menu_ids": [1, 2]
            })
            self.client.assert_success(response)
    
    def test_assign_menus_role_not_exist(self):
        """分配菜单 - 角色不存在"""
        response = self.client.post("/role/assignMenus", json={
            "id": 99999,
            "menu_ids": [1]
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== GET /role/menus/{role_id} 获取角色菜单测试 ====================
    
    def test_get_menus_success(self):
        """获取角色菜单 - 正常请求"""
        role_id = self._create_test_role()
        if role_id:
            response = self.client.get(f"/role/menus/{role_id}")
            self.client.assert_success(response)
