"""
操作类型管理 - API测试用例
测试 ApiOperationTypeController 的所有接口
"""
import pytest


class TestOperationTypeQueryAll:
    """查询所有操作类型"""
    
    def test_query_all_success(self, api_client):
        """成功查询所有"""
        response = api_client.get("/OperationType/queryAll")
        data = api_client.assert_success(response)
        assert "list" in data.get("data", {}) or isinstance(data.get("data"), list)


class TestOperationTypeQueryByPage:
    """分页查询操作类型"""
    
    def test_query_by_page_success(self, api_client):
        """成功分页查询"""
        response = api_client.post("/OperationType/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = api_client.assert_success(response)
        assert "list" in data.get("data", {}) or isinstance(data.get("data"), list)
    
    def test_query_by_page_with_name(self, api_client):
        """按名称模糊查询"""
        response = api_client.post("/OperationType/queryByPage", json={
            "page": 1, "pageSize": 10, "operation_type_name": "HTTP"
        })
        api_client.assert_success(response)
    
    def test_query_by_page_unauthorized(self, api_client_no_auth):
        """未授权访问"""
        response = api_client_no_auth.post("/OperationType/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        assert response.status_code in [401, 403]


class TestOperationTypeQueryById:
    """根据ID查询操作类型"""
    
    def test_query_by_id_success(self, api_client):
        """成功查询"""
        response = api_client.get("/OperationType/queryById", params={"id": 1})
        assert response.status_code == 200
    
    def test_query_by_id_not_exist(self, api_client):
        """查询不存在的ID"""
        response = api_client.get("/OperationType/queryById", params={"id": 999999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self, api_client):
        """缺少必填参数"""
        response = api_client.get("/OperationType/queryById")
        assert response.status_code == 422
    
    def test_query_by_id_invalid_param(self, api_client):
        """无效参数类型"""
        response = api_client.get("/OperationType/queryById", params={"id": "abc"})
        assert response.status_code == 422


class TestOperationTypeInsert:
    """新增操作类型"""
    
    def test_insert_success(self, api_client, unique_name):
        """成功新增"""
        response = api_client.post("/OperationType/insert", json={
            "operation_type_name": f"操作类型_{unique_name}",
            "operation_type_code": f"CODE_{unique_name}",
            "description": "自动化测试创建"
        })
        data = api_client.assert_success(response)
        assert "添加成功" in data.get("msg", "")
    
    def test_insert_missing_required(self, api_client):
        """缺少必填字段"""
        response = api_client.post("/OperationType/insert", json={
            "description": "缺少名称"
        })
        assert response.status_code == 422
    
    def test_insert_unauthorized(self, api_client_no_auth):
        """未授权新增"""
        response = api_client_no_auth.post("/OperationType/insert", json={
            "operation_type_name": "test"
        })
        assert response.status_code in [401, 403]


class TestOperationTypeUpdate:
    """更新操作类型"""
    
    def test_update_success(self, api_client):
        """成功更新"""
        response = api_client.put("/OperationType/update", json={
            "id": 1,
            "operation_type_name": "更新后的名称"
        })
        assert response.status_code == 200
    
    def test_update_not_exist(self, api_client):
        """更新不存在的记录"""
        response = api_client.put("/OperationType/update", json={
            "id": 999999,
            "operation_type_name": "不存在"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") != 200 or "不存在" in data.get("msg", "")
    
    def test_update_missing_id(self, api_client):
        """缺少ID"""
        response = api_client.put("/OperationType/update", json={
            "operation_type_name": "缺少ID"
        })
        assert response.status_code == 422


class TestOperationTypeDelete:
    """删除操作类型"""
    
    def test_delete_not_exist(self, api_client):
        """删除不存在的记录"""
        response = api_client.delete("/OperationType/delete", params={"id": 999999})
        assert response.status_code == 200
    
    def test_delete_missing_param(self, api_client):
        """缺少必填参数"""
        response = api_client.delete("/OperationType/delete")
        assert response.status_code == 422
    
    def test_delete_unauthorized(self, api_client_no_auth):
        """未授权删除"""
        response = api_client_no_auth.delete("/OperationType/delete", params={"id": 1})
        assert response.status_code in [401, 403]
