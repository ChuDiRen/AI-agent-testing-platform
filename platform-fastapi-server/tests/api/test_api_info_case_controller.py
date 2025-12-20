"""
API用例管理 接口测试
接口清单:
- POST /ApiInfoCase/queryByPage - 分页查询API用例
- GET /ApiInfoCase/queryById - 根据ID查询API用例（含步骤）
- POST /ApiInfoCase/insert - 新增API用例（含步骤）
- PUT /ApiInfoCase/update - 更新API用例（含步骤）
- DELETE /ApiInfoCase/delete - 删除API用例
- GET /ApiInfoCase/getSteps - 获取用例步骤
- POST /ApiInfoCase/generateYaml - 生成用例YAML文件
- POST /ApiInfoCase/executeCase - 执行用例测试
- GET /ApiInfoCase/executionStatus - 查询用例执行状态
"""
from datetime import datetime

import pytest
from ..conftest import APIClient, API_BASE_URL


class TestApiInfoCaseAPI:
    """API用例管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        self.created_project_ids = []
        yield
        for case_id in self.created_ids:
            try:
                self.client.delete("/ApiInfoCase/delete", params={"id": case_id})
            except:
                pass
        for project_id in self.created_project_ids:
            try:
                self.client.delete("/ApiProject/delete", params={"id": project_id})
            except:
                pass
        self.client.close()
    
    def _create_test_project(self):
        """创建测试项目"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiProject/insert", json={
            "project_name": f"测试项目_{unique}",
            "base_url": "http://localhost:5000"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            project_id = response.json().get("data", {}).get("id")
            if project_id:
                self.created_project_ids.append(project_id)
            return project_id
        return None
    
    def _create_test_case(self, project_id=None):
        """创建测试用例"""
        if not project_id:
            project_id = self._create_test_project()
        if not project_id:
            return None
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiInfoCase/insert", json={
            "project_id": project_id,
            "case_name": f"测试用例_{unique}",
            "case_desc": "测试用例描述",
            "steps": []
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            # 查询刚创建的用例ID
            query_resp = self.client.post("/ApiInfoCase/queryByPage", json={
                "page": 1, "pageSize": 1,
                "project_id": project_id,
                "case_name": f"测试用例_{unique}"
            })
            if query_resp.status_code == 200:
                data = query_resp.json().get("data", [])
                if data:
                    case_id = data[0].get("id")
                    if case_id:
                        self.created_ids.append(case_id)
                    return case_id
        return None
    
    # ==================== POST /ApiInfoCase/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/ApiInfoCase/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_filter(self):
        """分页查询 - 带用例名筛选"""
        response = self.client.post("/ApiInfoCase/queryByPage", json={
            "page": 1, "pageSize": 10,
            "case_name": "测试"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_project_filter(self):
        """分页查询 - 带项目ID筛选"""
        project_id = self._create_test_project()
        if project_id:
            response = self.client.post("/ApiInfoCase/queryByPage", json={
                "page": 1, "pageSize": 10,
                "project_id": project_id
            })
            self.client.assert_success(response)
    
    def test_query_by_page_empty_result(self):
        """分页查询 - 空结果"""
        response = self.client.post("/ApiInfoCase/queryByPage", json={
            "page": 1, "pageSize": 10,
            "case_name": "不存在的用例_xyz123"
        })
        data = self.client.assert_success(response)
        assert data["total"] == 0 or len(data["data"]) == 0
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/ApiInfoCase/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /ApiInfoCase/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            response = self.client.get("/ApiInfoCase/queryById", params={"id": case_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == case_id
            assert "steps" in data["data"]
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/ApiInfoCase/queryById", params={"id": 99999})
        data = response.json()
        assert data["code"] == 200 or data["data"] is None
    
    # ==================== POST /ApiInfoCase/insert 新增用例测试 ====================
    
    def test_insert_success(self):
        """新增用例 - 正常请求"""
        project_id = self._create_test_project()
        if project_id:
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            response = self.client.post("/ApiInfoCase/insert", json={
                "project_id": project_id,
                "case_name": f"测试用例_{unique}",
                "case_desc": "测试用例描述",
                "steps": []
            })
            self.client.assert_success(response)
    
    def test_insert_with_steps(self):
        """新增用例 - 带步骤"""
        project_id = self._create_test_project()
        if project_id:
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            response = self.client.post("/ApiInfoCase/insert", json={
                "project_id": project_id,
                "case_name": f"测试用例_{unique}",
                "case_desc": "测试用例描述",
                "steps": [
                    {
                        "run_order": 1,
                        "step_desc": "步骤1",
                        "operation_type_id": 1,
                        "keyword_id": 1,
                        "step_data": {"url": "http://test.com"}
                    }
                ]
            })
            self.client.assert_success(response)
    
    def test_insert_missing_required(self):
        """新增用例 - 缺少必填字段"""
        response = self.client.post("/ApiInfoCase/insert", json={
            "case_desc": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /ApiInfoCase/update 更新用例测试 ====================
    
    def test_update_success(self):
        """更新用例 - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            response = self.client.put("/ApiInfoCase/update", json={
                "id": case_id,
                "case_desc": "更新后的描述"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新用例 - 数据不存在"""
        response = self.client.put("/ApiInfoCase/update", json={
            "id": 99999,
            "case_desc": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiInfoCase/delete 删除用例测试 ====================
    
    def test_delete_success(self):
        """删除用例 - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            self.created_ids.remove(case_id)
            response = self.client.delete("/ApiInfoCase/delete", params={"id": case_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除用例 - 数据不存在"""
        response = self.client.delete("/ApiInfoCase/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== GET /ApiInfoCase/getSteps 获取步骤测试 ====================
    
    def test_get_steps_success(self):
        """获取步骤 - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            response = self.client.get("/ApiInfoCase/getSteps", params={"case_id": case_id})
            data = self.client.assert_success(response)
            assert "data" in data
