"""
提示词模板管理 - API测试用例
测试 PromptTemplateController 的所有接口
"""
import pytest


class TestPromptTemplateQueryByPage:
    """分页查询提示词模板"""
    
    def test_query_by_page_success(self, api_client):
        """成功分页查询"""
        response = api_client.post("/PromptTemplate/queryByPage", json={
            "page": 1, "pageSize": 10
        })
        data = api_client.assert_success(response)
        assert "list" in data.get("data", {}) or isinstance(data.get("data"), list)
    
    def test_query_by_page_with_test_type(self, api_client):
        """按测试类型过滤"""
        response = api_client.post("/PromptTemplate/queryByPage", json={
            "page": 1, "pageSize": 10, "test_type": "API"
        })
        api_client.assert_success(response)
    
    def test_query_by_page_with_template_type(self, api_client):
        """按模板类型过滤"""
        response = api_client.post("/PromptTemplate/queryByPage", json={
            "page": 1, "pageSize": 10, "template_type": "system"
        })
        api_client.assert_success(response)
    
    def test_query_by_page_with_is_active(self, api_client):
        """按激活状态过滤"""
        response = api_client.post("/PromptTemplate/queryByPage", json={
            "page": 1, "pageSize": 10, "is_active": True
        })
        api_client.assert_success(response)


class TestPromptTemplateQueryById:
    """根据ID查询提示词模板"""
    
    def test_query_by_id_success(self, api_client):
        """成功查询"""
        response = api_client.get("/PromptTemplate/queryById", params={"id": 1})
        assert response.status_code == 200
    
    def test_query_by_id_not_exist(self, api_client):
        """查询不存在的ID"""
        response = api_client.get("/PromptTemplate/queryById", params={"id": 999999})
        assert response.status_code == 200
    
    def test_query_by_id_missing_param(self, api_client):
        """缺少必填参数"""
        response = api_client.get("/PromptTemplate/queryById")
        assert response.status_code == 422


class TestPromptTemplateQueryByType:
    """按测试类型获取激活的模板"""
    
    def test_query_by_type_success(self, api_client):
        """成功查询"""
        response = api_client.get("/PromptTemplate/queryByType", params={"testType": "API"})
        data = api_client.assert_success(response)
        assert "list" in data.get("data", {}) or isinstance(data.get("data"), list)
    
    def test_query_by_type_missing_param(self, api_client):
        """缺少必填参数"""
        response = api_client.get("/PromptTemplate/queryByType")
        assert response.status_code == 422


class TestPromptTemplateQueryAll:
    """查询所有提示词模板"""
    
    def test_query_all_success(self, api_client):
        """成功查询所有"""
        response = api_client.get("/PromptTemplate/queryAll")
        data = api_client.assert_success(response)
        assert "list" in data.get("data", {}) or isinstance(data.get("data"), list)


class TestPromptTemplateInsert:
    """新增提示词模板"""
    
    def test_insert_success(self, api_client, unique_name):
        """成功新增"""
        response = api_client.post("/PromptTemplate/insert", json={
            "name": f"模板_{unique_name}",
            "test_type": "API",
            "template_type": "system",
            "content": "这是一个测试模板内容",
            "is_active": True
        })
        data = api_client.assert_success(response)
        assert "添加成功" in data.get("msg", "")
    
    def test_insert_missing_required(self, api_client):
        """缺少必填字段"""
        response = api_client.post("/PromptTemplate/insert", json={
            "content": "缺少name"
        })
        assert response.status_code == 422


class TestPromptTemplateUpdate:
    """更新提示词模板"""
    
    def test_update_success(self, api_client):
        """成功更新"""
        response = api_client.put("/PromptTemplate/update", json={
            "id": 1,
            "name": "更新后的模板名称"
        })
        assert response.status_code == 200
    
    def test_update_not_exist(self, api_client):
        """更新不存在的记录"""
        response = api_client.put("/PromptTemplate/update", json={
            "id": 999999,
            "name": "不存在"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") != 200 or "不存在" in data.get("msg", "")
    
    def test_update_missing_id(self, api_client):
        """缺少ID"""
        response = api_client.put("/PromptTemplate/update", json={
            "name": "缺少ID"
        })
        assert response.status_code == 422


class TestPromptTemplateDelete:
    """删除提示词模板"""
    
    def test_delete_not_exist(self, api_client):
        """删除不存在的记录"""
        response = api_client.delete("/PromptTemplate/delete", params={"id": 999999})
        assert response.status_code == 200
    
    def test_delete_missing_param(self, api_client):
        """缺少必填参数"""
        response = api_client.delete("/PromptTemplate/delete")
        assert response.status_code == 422


class TestPromptTemplateToggleActive:
    """切换模板激活状态"""
    
    def test_toggle_active_success(self, api_client):
        """成功切换状态"""
        response = api_client.post("/PromptTemplate/toggleActive", params={"id": 1})
        assert response.status_code == 200
    
    def test_toggle_active_not_exist(self, api_client):
        """切换不存在的记录"""
        response = api_client.post("/PromptTemplate/toggleActive", params={"id": 999999})
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") != 200 or "不存在" in data.get("msg", "")
    
    def test_toggle_active_missing_param(self, api_client):
        """缺少参数"""
        response = api_client.post("/PromptTemplate/toggleActive")
        assert response.status_code == 422


class TestPromptTemplateQueryByTestType:
    """按测试类型查询模板"""
    
    def test_query_by_test_type_success(self, api_client):
        """成功查询"""
        response = api_client.get("/PromptTemplate/queryByTestType", params={"test_type": "API"})
        data = api_client.assert_success(response)
        assert "list" in data.get("data", {}) or isinstance(data.get("data"), list)
    
    def test_query_by_test_type_missing_param(self, api_client):
        """缺少参数"""
        response = api_client.get("/PromptTemplate/queryByTestType")
        assert response.status_code == 422
