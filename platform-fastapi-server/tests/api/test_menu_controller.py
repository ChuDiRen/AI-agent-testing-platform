"""
菜单管理 API 接口测试
接口清单:
- GET /menu/tree - 获取菜单树
- GET /menu/queryById - 根据ID查询菜单
- POST /menu/insert - 新增菜单
- PUT /menu/update - 更新菜单
- DELETE /menu/delete - 删除菜单
- GET /menu/user/{user_id} - 获取用户菜单权限
"""
from datetime import datetime

import pytest
from ..conftest import APIClient, API_BASE_URL


class TestMenuAPI:
    """菜单管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for menu_id in self.created_ids:
            try:
                self.client.delete("/menu/delete", params={"id": menu_id})
            except:
                pass
    
    def _create_test_menu(self, parent_id=0):
        """创建测试菜单"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/menu/insert", json={
            "menu_name": f"测试菜单_{unique}",
            "parent_id": parent_id,
            "order_num": 99,
            "path": f"/test_{unique}",
            "menu_type": "M",
            "visible": "0",
            "status": "0"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            menu_id = response.json().get("data", {}).get("id")
            if menu_id:
                self.created_ids.append(menu_id)
            return menu_id
        return None
    
    # ==================== GET /menu/tree 获取菜单树测试 ====================
    
    def test_get_tree_success(self):
        """获取菜单树 - 正常请求"""
        response = self.client.get("/menu/tree")
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_get_tree_unauthorized(self):
        """获取菜单树 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/menu/tree")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /menu/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        menu_id = self._create_test_menu()
        if menu_id:
            response = self.client.get("/menu/queryById", params={"id": menu_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == menu_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/menu/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == -1 or data["data"] is None
    
    # ==================== POST /menu/insert 新增菜单测试 ====================
    
    def test_insert_success(self):
        """新增菜单 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/menu/insert", json={
            "menu_name": f"测试菜单_{unique}",
            "parent_id": 0,
            "order_num": 99,
            "path": f"/test_{unique}",
            "menu_type": "M",
            "visible": "0",
            "status": "0"
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增菜单 - 缺少必填字段"""
        response = self.client.post("/menu/insert", json={
            "order_num": 99
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /menu/update 更新菜单测试 ====================
    
    def test_update_success(self):
        """更新菜单 - 正常请求"""
        menu_id = self._create_test_menu()
        if menu_id:
            response = self.client.put("/menu/update", json={
                "id": menu_id,
                "menu_name": "更新后的菜单名"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新菜单 - 数据不存在"""
        response = self.client.put("/menu/update", json={
            "id": 99999,
            "menu_name": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /menu/delete 删除菜单测试 ====================
    
    def test_delete_success(self):
        """删除菜单 - 正常请求"""
        menu_id = self._create_test_menu()
        if menu_id:
            self.created_ids.remove(menu_id)
            response = self.client.delete("/menu/delete", params={"id": menu_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除菜单 - 数据不存在"""
        response = self.client.delete("/menu/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_delete_with_children(self):
        """删除菜单 - 存在子菜单"""
        parent_id = self._create_test_menu()
        if parent_id:
            child_id = self._create_test_menu(parent_id=parent_id)
            if child_id:
                response = self.client.delete("/menu/delete", params={"id": parent_id})
                assert response.json()["code"] == -1 or "子菜单" in response.json().get("msg", "")
    
    # ==================== GET /menu/user/{user_id} 获取用户菜单测试 ====================
    
    def test_get_user_menus_success(self):
        """获取用户菜单 - 正常请求"""
        response = self.client.get("/menu/user/1")
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_get_user_menus_unauthorized(self):
        """获取用户菜单 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/menu/user/1")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
