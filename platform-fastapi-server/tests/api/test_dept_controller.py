"""
部门管理 API 接口测试
接口清单:
- GET /dept/tree - 获取部门树
- GET /dept/queryById - 根据ID查询部门
- POST /dept/insert - 新增部门
- PUT /dept/update - 更新部门
- DELETE /dept/delete - 删除部门
"""
from datetime import datetime

import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestDeptAPI:
    """部门管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for dept_id in self.created_ids:
            try:
                self.client.delete("/dept/delete", params={"id": dept_id})
            except:
                pass
        self.client.close()
    
    def _create_test_dept(self, parent_id=0):
        """创建测试部门"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/dept/insert", json={
            "dept_name": f"测试部门_{unique}",
            "parent_id": parent_id,
            "order_num": 99
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            dept_id = response.json().get("data", {}).get("id")
            if dept_id:
                self.created_ids.append(dept_id)
            return dept_id
        return None
    
    # ==================== GET /dept/tree 获取部门树测试 ====================
    
    def test_get_tree_success(self):
        """获取部门树 - 正常请求"""
        response = self.client.get("/dept/tree")
        data = self.client.assert_success(response)
        assert "treeData" in data
    
    def test_get_tree_unauthorized(self):
        """获取部门树 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/dept/tree")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /dept/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        dept_id = self._create_test_dept()
        if dept_id:
            response = self.client.get("/dept/queryById", params={"id": dept_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == dept_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/dept/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == -1 or data["data"] is None
    
    # ==================== POST /dept/insert 新增部门测试 ====================
    
    def test_insert_success(self):
        """新增部门 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/dept/insert", json={
            "dept_name": f"测试部门_{unique}",
            "parent_id": 0,
            "order_num": 99
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增部门 - 缺少必填字段"""
        response = self.client.post("/dept/insert", json={
            "order_num": 99
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /dept/update 更新部门测试 ====================
    
    def test_update_success(self):
        """更新部门 - 正常请求"""
        dept_id = self._create_test_dept()
        if dept_id:
            response = self.client.put("/dept/update", json={
                "id": dept_id,
                "dept_name": "更新后的部门名"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新部门 - 数据不存在"""
        response = self.client.put("/dept/update", json={
            "id": 99999,
            "dept_name": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /dept/delete 删除部门测试 ====================
    
    def test_delete_success(self):
        """删除部门 - 正常请求"""
        dept_id = self._create_test_dept()
        if dept_id:
            self.created_ids.remove(dept_id)
            response = self.client.delete("/dept/delete", params={"id": dept_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除部门 - 数据不存在"""
        response = self.client.delete("/dept/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_delete_with_children(self):
        """删除部门 - 存在子部门"""
        parent_id = self._create_test_dept()
        if parent_id:
            child_id = self._create_test_dept(parent_id=parent_id)
            if child_id:
                response = self.client.delete("/dept/delete", params={"id": parent_id})
                assert response.json()["code"] == -1 or "子部门" in response.json().get("msg", "")
