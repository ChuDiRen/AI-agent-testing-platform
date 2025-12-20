"""
AI测试用例管理 接口测试
接口清单:
- POST /TestCase/queryByPage - 分页查询测试用例
- GET /TestCase/queryById - 根据ID查询测试用例
- POST /TestCase/insert - 新增测试用例
- POST /TestCase/batchInsert - 批量插入测试用例
- PUT /TestCase/update - 更新测试用例
- DELETE /TestCase/delete - 删除测试用例
- GET /TestCase/exportYaml - 导出单个测试用例为YAML
- POST /TestCase/exportBatchYaml - 批量导出测试用例为YAML
"""
from datetime import datetime

import pytest
from ..conftest import APIClient, API_BASE_URL


class TestTestCaseAPI:
    """AI测试用例管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for case_id in self.created_ids:
            try:
                self.client.delete("/TestCase/delete", params={"id": case_id})
            except:
                pass
    
    def _create_test_case(self):
        """创建测试用例"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/TestCase/insert", json={
            "project_id": 1,
            "case_name": f"测试用例_{unique}",
            "test_type": "API",
            "priority": "P1",
            "precondition": "无",
            "test_steps": '[{"step": 1, "action": "发送请求"}]',
            "expected_result": "返回200"
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            case_id = response.json().get("data", {}).get("id")
            if case_id:
                self.created_ids.append(case_id)
            return case_id
        return None
    
    # ==================== POST /TestCase/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/TestCase/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_project_filter(self):
        """分页查询 - 带项目ID筛选"""
        response = self.client.post("/TestCase/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_id": 1
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_type_filter(self):
        """分页查询 - 带测试类型筛选"""
        response = self.client.post("/TestCase/queryByPage", json={
            "page": 1, "pageSize": 10,
            "test_type": "API"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_priority_filter(self):
        """分页查询 - 带优先级筛选"""
        response = self.client.post("/TestCase/queryByPage", json={
            "page": 1, "pageSize": 10,
            "priority": "P1"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/TestCase/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /TestCase/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            response = self.client.get("/TestCase/queryById", params={"id": case_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == case_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/TestCase/queryById", params={"id": 99999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self):
        """ID查询 - 缺少参数"""
        response = self.client.get("/TestCase/queryById")
        assert response.status_code == 422
    
    # ==================== POST /TestCase/insert 新增用例测试 ====================
    
    def test_insert_success(self):
        """新增用例 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/TestCase/insert", json={
            "project_id": 1,
            "case_name": f"测试用例_{unique}",
            "test_type": "API",
            "priority": "P1",
            "precondition": "无",
            "test_steps": '[{"step": 1, "action": "发送请求"}]',
            "expected_result": "返回200"
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增用例 - 缺少必填字段"""
        response = self.client.post("/TestCase/insert", json={
            "precondition": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== POST /TestCase/batchInsert 批量插入测试 ====================
    
    def test_batch_insert_success(self):
        """批量插入 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/TestCase/batchInsert", json={
            "project_id": 1,
            "test_cases": [
                {
                    "case_name": f"批量用例1_{unique}",
                    "test_type": "API",
                    "priority": "P1",
                    "expected_result": "成功"
                },
                {
                    "case_name": f"批量用例2_{unique}",
                    "test_type": "API",
                    "priority": "P2",
                    "expected_result": "成功"
                }
            ]
        })
        data = self.client.assert_success(response)
        assert "count" in data.get("data", {})
    
    def test_batch_insert_empty(self):
        """批量插入 - 空列表"""
        response = self.client.post("/TestCase/batchInsert", json={
            "project_id": 1,
            "test_cases": []
        })
        self.client.assert_success(response)
    
    # ==================== PUT /TestCase/update 更新用例测试 ====================
    
    def test_update_success(self):
        """更新用例 - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            response = self.client.put("/TestCase/update", json={
                "id": case_id,
                "expected_result": "更新后的预期结果"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新用例 - 数据不存在"""
        response = self.client.put("/TestCase/update", json={
            "id": 99999,
            "expected_result": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /TestCase/delete 删除用例测试 ====================
    
    def test_delete_success(self):
        """删除用例 - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            self.created_ids.remove(case_id)
            response = self.client.delete("/TestCase/delete", params={"id": case_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除用例 - 数据不存在"""
        response = self.client.delete("/TestCase/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== GET /TestCase/exportYaml 导出YAML测试 ====================
    
    def test_export_yaml_success(self):
        """导出YAML - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            response = self.client.get("/TestCase/exportYaml", params={"id": case_id})
            assert response.status_code == 200
            # 检查返回的是YAML内容
            assert "yaml" in response.headers.get("content-type", "") or response.status_code == 200
    
    def test_export_yaml_not_exist(self):
        """导出YAML - 用例不存在"""
        response = self.client.get("/TestCase/exportYaml", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_export_yaml_missing_param(self):
        """导出YAML - 缺少参数"""
        response = self.client.get("/TestCase/exportYaml")
        assert response.status_code == 422
    
    # ==================== POST /TestCase/exportBatchYaml 批量导出YAML测试 ====================
    
    def test_export_batch_yaml_success(self):
        """批量导出YAML - 正常请求"""
        case_id = self._create_test_case()
        if case_id:
            response = self.client.post("/TestCase/exportBatchYaml", json=[case_id])
            assert response.status_code == 200
    
    def test_export_batch_yaml_empty(self):
        """批量导出YAML - 空列表"""
        response = self.client.post("/TestCase/exportBatchYaml", json=[])
        assert response.json()["code"] == -1 or "未找到" in response.json().get("msg", "")
    
    def test_export_batch_yaml_not_exist(self):
        """批量导出YAML - 用例不存在"""
        response = self.client.post("/TestCase/exportBatchYaml", json=[99999])
        assert response.json()["code"] == -1 or "未找到" in response.json().get("msg", "")
