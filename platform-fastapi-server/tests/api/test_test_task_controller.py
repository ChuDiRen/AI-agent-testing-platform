"""
测试任务管理 接口测试
接口清单:
- POST /TestTask/queryByPage - 分页查询测试任务
- GET /TestTask/queryById - 根据ID查询测试任务
- POST /TestTask/insert - 新增测试任务
- PUT /TestTask/update - 更新测试任务
- DELETE /TestTask/delete - 删除测试任务
- POST /TestTask/execute - 执行测试任务
- PUT /TestTask/updateStatus - 更新任务状态
- POST /TestTask/queryExecutions - 查询任务执行记录
- GET /TestTask/getExecutionDetail - 获取执行记录详情
"""
import pytest
from datetime import datetime
from tests.conftest import APIClient, API_BASE_URL


class TestTestTaskAPI:
    """测试任务管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for task_id in self.created_ids:
            try:
                self.client.delete("/TestTask/delete", params={"id": task_id})
            except:
                pass
        self.client.close()
    
    def _create_test_task(self):
        """创建测试任务"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/TestTask/insert", json={
            "project_id": 1,
            "task_name": f"测试任务_{unique}",
            "task_desc": "自动化测试创建",
            "task_type": "manual",
            "plan_id": 1
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            # 查询刚创建的任务
            query_resp = self.client.post("/TestTask/queryByPage", json={
                "page": 1, "pageSize": 1,
                "task_name": f"测试任务_{unique}"
            })
            if query_resp.status_code == 200:
                data = query_resp.json().get("data", [])
                if data:
                    task_id = data[0].get("id")
                    if task_id:
                        self.created_ids.append(task_id)
                    return task_id
        return None
    
    # ==================== POST /TestTask/queryByPage 分页查询测试 ====================
    
    def test_query_by_page_success(self):
        """分页查询 - 正常请求"""
        response = self.client.post("/TestTask/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_by_page_with_project_filter(self):
        """分页查询 - 带项目ID筛选"""
        response = self.client.post("/TestTask/queryByPage", json={
            "page": 1, "pageSize": 10,
            "project_id": 1
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_name_filter(self):
        """分页查询 - 带任务名筛选"""
        response = self.client.post("/TestTask/queryByPage", json={
            "page": 1, "pageSize": 10,
            "task_name": "测试"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_type_filter(self):
        """分页查询 - 带任务类型筛选"""
        response = self.client.post("/TestTask/queryByPage", json={
            "page": 1, "pageSize": 10,
            "task_type": "manual"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_with_status_filter(self):
        """分页查询 - 带状态筛选"""
        response = self.client.post("/TestTask/queryByPage", json={
            "page": 1, "pageSize": 10,
            "task_status": "pending"
        })
        self.client.assert_success(response)
    
    def test_query_by_page_unauthorized(self):
        """分页查询 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/TestTask/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /TestTask/queryById ID查询测试 ====================
    
    def test_query_by_id_success(self):
        """ID查询 - 正常请求"""
        task_id = self._create_test_task()
        if task_id:
            response = self.client.get("/TestTask/queryById", params={"id": task_id})
            data = self.client.assert_success(response)
            assert data["data"]["id"] == task_id
    
    def test_query_by_id_not_exist(self):
        """ID查询 - 数据不存在"""
        response = self.client.get("/TestTask/queryById", params={"id": 99999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self):
        """ID查询 - 缺少参数"""
        response = self.client.get("/TestTask/queryById")
        assert response.status_code == 422
    
    # ==================== POST /TestTask/insert 新增任务测试 ====================
    
    def test_insert_success(self):
        """新增任务 - 正常请求"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/TestTask/insert", json={
            "project_id": 1,
            "task_name": f"测试任务_{unique}",
            "task_desc": "自动化测试创建",
            "task_type": "manual",
            "plan_id": 1
        })
        self.client.assert_success(response)
    
    def test_insert_with_case_ids(self):
        """新增任务 - 带用例ID列表"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/TestTask/insert", json={
            "project_id": 1,
            "task_name": f"测试任务_{unique}",
            "task_type": "manual",
            "case_ids": [1, 2, 3]
        })
        self.client.assert_success(response)
    
    def test_insert_missing_required(self):
        """新增任务 - 缺少必填字段"""
        response = self.client.post("/TestTask/insert", json={
            "task_desc": "测试"
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /TestTask/update 更新任务测试 ====================
    
    def test_update_success(self):
        """更新任务 - 正常请求"""
        task_id = self._create_test_task()
        if task_id:
            response = self.client.put("/TestTask/update", json={
                "id": task_id,
                "task_desc": "更新后的描述"
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新任务 - 数据不存在"""
        response = self.client.put("/TestTask/update", json={
            "id": 99999,
            "task_desc": "测试"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /TestTask/delete 删除任务测试 ====================
    
    def test_delete_success(self):
        """删除任务 - 正常请求"""
        task_id = self._create_test_task()
        if task_id:
            self.created_ids.remove(task_id)
            response = self.client.delete("/TestTask/delete", params={"id": task_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除任务 - 数据不存在"""
        response = self.client.delete("/TestTask/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== PUT /TestTask/updateStatus 更新状态测试 ====================
    
    def test_update_status_success(self):
        """更新状态 - 正常请求"""
        task_id = self._create_test_task()
        if task_id:
            response = self.client.put("/TestTask/updateStatus", params={
                "id": task_id,
                "status": "disabled"
            })
            self.client.assert_success(response)
    
    def test_update_status_invalid(self):
        """更新状态 - 无效状态值"""
        task_id = self._create_test_task()
        if task_id:
            response = self.client.put("/TestTask/updateStatus", params={
                "id": task_id,
                "status": "invalid_status"
            })
            assert response.json()["code"] == -1 or "无效" in response.json().get("msg", "")
    
    def test_update_status_not_exist(self):
        """更新状态 - 任务不存在"""
        response = self.client.put("/TestTask/updateStatus", params={
            "id": 99999,
            "status": "pending"
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== POST /TestTask/queryExecutions 查询执行记录测试 ====================
    
    def test_query_executions_success(self):
        """查询执行记录 - 正常请求"""
        response = self.client.post("/TestTask/queryExecutions", json={
            "page": 1, "pageSize": 10
        })
        data = self.client.assert_success(response)
        assert "data" in data
        assert "total" in data
    
    def test_query_executions_with_task_filter(self):
        """查询执行记录 - 带任务ID筛选"""
        response = self.client.post("/TestTask/queryExecutions", json={
            "page": 1, "pageSize": 10,
            "task_id": 1
        })
        self.client.assert_success(response)
    
    # ==================== GET /TestTask/getExecutionDetail 获取执行详情测试 ====================
    
    def test_get_execution_detail_not_exist(self):
        """获取执行详情 - 数据不存在"""
        response = self.client.get("/TestTask/getExecutionDetail", params={"id": 99999})
        assert response.status_code == 200
