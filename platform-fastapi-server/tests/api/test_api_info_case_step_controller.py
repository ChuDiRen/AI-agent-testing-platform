"""
API用例步骤管理 接口测试
接口清单:
- GET /ApiInfoCaseStep/queryByCaseId - 根据用例ID查询步骤
- POST /ApiInfoCaseStep/insert - 新增用例步骤
- PUT /ApiInfoCaseStep/update - 更新用例步骤
- DELETE /ApiInfoCaseStep/delete - 删除用例步骤
- POST /ApiInfoCaseStep/batchUpdateOrder - 批量更新步骤顺序
"""
from datetime import datetime

import pytest


class TestApiInfoCaseStepAPI:
    """API用例步骤管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        """使用全局 api_client fixture"""
        self.client = api_client
        self.created_ids = []
        yield
        for step_id in self.created_ids:
            try:
                self.client.delete("/ApiInfoCaseStep/delete", params={"id": step_id})
            except:
                pass
    
    def _create_test_step(self, case_info_id=1):
        """创建测试步骤"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiInfoCaseStep/insert", json={
            "case_info_id": case_info_id,
            "run_order": 1,
            "step_desc": f"测试步骤_{unique}",
            "operation_type_id": 1,
            "keyword_id": 1,
            "step_data": {"url": "http://test.com", "method": "GET"}
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            step_id = response.json().get("data", {}).get("id")
            if step_id:
                self.created_ids.append(step_id)
            return step_id
        return None
    
    # ==================== GET /ApiInfoCaseStep/queryByCaseId 按用例ID查询测试 ====================
    
    def test_query_by_case_id_success(self):
        """按用例ID查询 - 正常请求"""
        response = self.client.get("/ApiInfoCaseStep/queryByCaseId", params={"case_info_id": 1})
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_query_by_case_id_empty(self):
        """按用例ID查询 - 空结果"""
        response = self.client.get("/ApiInfoCaseStep/queryByCaseId", params={"case_info_id": 99999})
        data = self.client.assert_success(response)
        assert len(data.get("data", [])) == 0
    
    def test_query_by_case_id_missing_param(self):
        """按用例ID查询 - 缺少参数"""
        response = self.client.get("/ApiInfoCaseStep/queryByCaseId")
        assert response.status_code == 422
    
    # ==================== POST /ApiInfoCaseStep/insert 新增步骤测试 ====================
    
    def test_insert_success(self):
        """新增步骤 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/ApiInfoCaseStep/insert", json={
            "case_info_id": 1,
            "run_order": 1,
            "step_desc": f"测试步骤_{unique}",
            "operation_type_id": 1,
            "keyword_id": 1,
            "step_data": {"url": "http://test.com"}
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增步骤 - 缺少必填字段"""
        response = self.client.post("/ApiInfoCaseStep/insert", json={
            "step_desc": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /ApiInfoCaseStep/update 更新步骤测试 ====================
    
    def test_update_success(self):
        """更新步骤 - 正常请求"""
        step_id = self._create_test_step()
        if step_id:
            response = self.client.put("/ApiInfoCaseStep/update", json={
                "id": step_id,
                "step_desc": "更新后的描述"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新步骤 - 数据不存在"""
        response = self.client.put("/ApiInfoCaseStep/update", json={
            "id": 99999,
            "step_desc": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiInfoCaseStep/delete 删除步骤测试 ====================
    
    def test_delete_success(self):
        """删除步骤 - 正常请求"""
        step_id = self._create_test_step()
        if step_id:
            self.created_ids.remove(step_id)
            response = self.client.delete("/ApiInfoCaseStep/delete", params={"id": step_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除步骤 - 数据不存在"""
        response = self.client.delete("/ApiInfoCaseStep/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== POST /ApiInfoCaseStep/batchUpdateOrder 批量更新顺序测试 ====================
    
    def test_batch_update_order_success(self):
        """批量更新顺序 - 正常请求"""
        step_id = self._create_test_step()
        if step_id:
            response = self.client.post("/ApiInfoCaseStep/batchUpdateOrder", json=[
                {"id": step_id, "run_order": 2}
            ])
            self.client.assert_success(response)
    
    def test_batch_update_order_empty(self):
        """批量更新顺序 - 空列表"""
        response = self.client.post("/ApiInfoCaseStep/batchUpdateOrder", json=[])
        self.client.assert_success(response)
