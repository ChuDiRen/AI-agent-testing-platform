"""
API测试计划管理 - API测试用例
测试 ApiCollectionInfoController 的所有接口
"""
import pytest


class TestApiCollectionInfoQueryByPage:
    """分页查询测试计划"""
    
    def test_query_by_page_success(self, api_client):
        """成功分页查询"""
        response = api_client.post("/ApiCollectionInfo/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = api_client.assert_success(response)
        assert "list" in data.get("data", {}) or isinstance(data.get("data"), list)
    
    def test_query_by_page_with_project_id(self, api_client):
        """按项目ID过滤查询"""
        response = api_client.post("/ApiCollectionInfo/queryByPage", json={
            "page": 1, "pageSize": 10, "project_id": 1
        })
        api_client.assert_success(response)
    
    def test_query_by_page_with_plan_name(self, api_client):
        """按计划名称模糊查询"""
        response = api_client.post("/ApiCollectionInfo/queryByPage", json={
            "page": 1, "pageSize": 10, "plan_name": "测试"
        })
        api_client.assert_success(response)
    
    def test_query_by_page_unauthorized(self, api_client_no_auth):
        """未授权访问"""
        response = api_client_no_auth.post("/ApiCollectionInfo/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        assert response.status_code in [401, 403]


class TestApiCollectionInfoQueryById:
    """根据ID查询测试计划"""
    
    def test_query_by_id_success(self, api_client):
        """成功查询"""
        response = api_client.get("/ApiCollectionInfo/queryById", params={"id": 1})
        assert response.status_code == 200
    
    def test_query_by_id_not_exist(self, api_client):
        """查询不存在的ID"""
        response = api_client.get("/ApiCollectionInfo/queryById", params={"id": 999999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self, api_client):
        """缺少必填参数"""
        response = api_client.get("/ApiCollectionInfo/queryById")
        assert response.status_code == 422
    
    def test_query_by_id_invalid_param(self, api_client):
        """无效参数类型"""
        response = api_client.get("/ApiCollectionInfo/queryById", params={"id": "abc"})
        assert response.status_code == 422


class TestApiCollectionInfoInsert:
    """新增测试计划"""
    
    def test_insert_success(self, api_client, unique_name):
        """成功新增"""
        response = api_client.post("/ApiCollectionInfo/insert", json={
            "project_id": 1,
            "plan_name": f"测试计划_{unique_name}",
            "plan_desc": "自动化测试创建"
        })
        data = api_client.assert_success(response)
        assert "新增成功" in data.get("msg", "")
    
    def test_insert_missing_required(self, api_client):
        """缺少必填字段"""
        response = api_client.post("/ApiCollectionInfo/insert", json={
            "plan_desc": "缺少plan_name"
        })
        assert response.status_code == 422
    
    def test_insert_unauthorized(self, api_client_no_auth):
        """未授权新增"""
        response = api_client_no_auth.post("/ApiCollectionInfo/insert", json={
            "project_id": 1, "plan_name": "test"
        })
        assert response.status_code in [401, 403]


class TestApiCollectionInfoUpdate:
    """更新测试计划"""
    
    def test_update_success(self, api_client):
        """成功更新"""
        response = api_client.put("/ApiCollectionInfo/update", json={
            "id": 1,
            "plan_name": "更新后的计划名称"
        })
        assert response.status_code == 200
    
    def test_update_not_exist(self, api_client):
        """更新不存在的记录"""
        response = api_client.put("/ApiCollectionInfo/update", json={
            "id": 999999,
            "plan_name": "不存在"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") != 200 or "不存在" in data.get("msg", "")
    
    def test_update_missing_id(self, api_client):
        """缺少ID"""
        response = api_client.put("/ApiCollectionInfo/update", json={
            "plan_name": "缺少ID"
        })
        assert response.status_code == 422


class TestApiCollectionInfoDelete:
    """删除测试计划"""
    
    def test_delete_not_exist(self, api_client):
        """删除不存在的记录"""
        response = api_client.delete("/ApiCollectionInfo/delete", params={"id": 999999})
        assert response.status_code == 200
    
    def test_delete_missing_param(self, api_client):
        """缺少必填参数"""
        response = api_client.delete("/ApiCollectionInfo/delete")
        assert response.status_code == 422
    
    def test_delete_unauthorized(self, api_client_no_auth):
        """未授权删除"""
        response = api_client_no_auth.delete("/ApiCollectionInfo/delete", params={"id": 1})
        assert response.status_code in [401, 403]


class TestApiCollectionInfoAddCase:
    """添加用例到测试计划"""
    
    def test_add_case_success(self, api_client):
        """成功添加用例"""
        response = api_client.post("/ApiCollectionInfo/addCase", json={
            "plan_id": 1,
            "case_info_id": 1,
            "run_order": 1
        })
        assert response.status_code == 200
    
    def test_add_case_duplicate(self, api_client):
        """重复添加用例"""
        # 先添加一次
        api_client.post("/ApiCollectionInfo/addCase", json={
            "plan_id": 1, "case_info_id": 1, "run_order": 1
        })
        # 再次添加
        response = api_client.post("/ApiCollectionInfo/addCase", json={
            "plan_id": 1, "case_info_id": 1, "run_order": 2
        })
        assert response.status_code == 200


class TestApiCollectionInfoBatchAddCases:
    """批量添加用例"""
    
    def test_batch_add_cases_success(self, api_client):
        """成功批量添加"""
        response = api_client.post("/ApiCollectionInfo/batchAddCases", json={
            "plan_id": 1,
            "case_ids": [1, 2, 3]
        })
        assert response.status_code == 200
    
    def test_batch_add_cases_empty(self, api_client):
        """空用例列表"""
        response = api_client.post("/ApiCollectionInfo/batchAddCases", json={
            "plan_id": 1,
            "case_ids": []
        })
        assert response.status_code == 200


class TestApiCollectionInfoRemoveCase:
    """从测试计划移除用例"""
    
    def test_remove_case_not_exist(self, api_client):
        """移除不存在的关联"""
        response = api_client.delete("/ApiCollectionInfo/removeCase", params={"plan_case_id": 999999})
        assert response.status_code == 200
    
    def test_remove_case_missing_param(self, api_client):
        """缺少参数"""
        response = api_client.delete("/ApiCollectionInfo/removeCase")
        assert response.status_code == 422


class TestApiCollectionInfoUpdateDdtData:
    """更新数据驱动信息"""
    
    def test_update_ddt_data_success(self, api_client):
        """成功更新DDT数据"""
        response = api_client.post("/ApiCollectionInfo/updateDdtData", json={
            "plan_case_id": 1,
            "ddt_data": [{"desc": "测试数据1", "username": "test"}]
        })
        assert response.status_code == 200
    
    def test_update_ddt_data_not_exist(self, api_client):
        """更新不存在的关联"""
        response = api_client.post("/ApiCollectionInfo/updateDdtData", json={
            "plan_case_id": 999999,
            "ddt_data": []
        })
        assert response.status_code == 200
