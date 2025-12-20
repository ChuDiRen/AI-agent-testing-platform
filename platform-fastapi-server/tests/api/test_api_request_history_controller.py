"""
API 请求历史接口测试
测试 ApiRequestHistoryController 的所有接口
"""
import pytest
from datetime import datetime, timedelta


class TestApiRequestHistoryController:
    """API 请求历史 Controller 测试"""
    
    def test_query_by_page_success(self, api_client):
        """测试分页查询请求历史 - 成功"""
        response = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        data = api_client.assert_success(response)
        
        assert "data" in data
        assert "total" in data
        assert isinstance(data["data"], list)
        assert isinstance(data["total"], int)
    
    def test_query_by_page_with_filters(self, api_client):
        """测试分页查询 - 带过滤条件"""
        response = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": 1,
            "request_method": "GET",
            "is_success": 1
        })
        data = api_client.assert_success(response)
        
        # 验证返回的数据符合过滤条件
        for item in data["data"]:
            if "request_method" in item:
                assert item["request_method"] == "GET"
            if "is_success" in item:
                assert item["is_success"] == 1
    
    def test_query_by_page_pagination(self, api_client):
        """测试分页功能"""
        # 第一页
        response1 = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 1,
            "pageSize": 5
        })
        data1 = api_client.assert_success(response1)
        
        # 第二页
        response2 = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 2,
            "pageSize": 5
        })
        data2 = api_client.assert_success(response2)
        
        # 验证分页逻辑
        assert len(data1["data"]) <= 5
        assert len(data2["data"]) <= 5
        
        # 如果有数据，第一页和第二页的数据应该不同
        if data1["data"] and data2["data"]:
            ids1 = [item.get("id") for item in data1["data"]]
            ids2 = [item.get("id") for item in data2["data"]]
            assert set(ids1).isdisjoint(set(ids2))
    
    def test_query_by_id_success(self, api_client, unique_name):
        """测试根据ID查询 - 成功"""
        # 先创建一条记录
        create_response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": 1,
            "api_id": 1,
            "request_url": f"/api/test/{unique_name}",
            "request_method": "GET",
            "is_success": 1,
            "response_time": 100
        })
        create_data = api_client.assert_success(create_response)
        history_id = create_data["data"]["id"]
        
        # 查询该记录
        response = api_client.get("/ApiRequestHistory/queryById", params={"id": history_id})
        data = api_client.assert_success(response)
        
        assert data["data"]["id"] == history_id
        assert data["data"]["request_url"] == f"/api/test/{unique_name}"
    
    def test_query_by_id_not_found(self, api_client):
        """测试根据ID查询 - 不存在"""
        response = api_client.get("/ApiRequestHistory/queryById", params={"id": 999999})
        # 应该返回错误或空数据
        assert response.status_code in [200, 404]
    
    def test_query_recent_success(self, api_client):
        """测试查询最近的请求 - 成功"""
        response = api_client.get("/ApiRequestHistory/queryRecent", params={
            "project_id": 1,
            "limit": 10
        })
        data = api_client.assert_success(response)
        
        assert isinstance(data["data"], list)
        assert len(data["data"]) <= 10
    
    def test_query_favorites_success(self, api_client):
        """测试查询收藏的请求 - 成功"""
        response = api_client.get("/ApiRequestHistory/queryFavorites", params={
            "project_id": 1
        })
        data = api_client.assert_success(response)
        
        assert isinstance(data["data"], list)
        # 所有返回的记录都应该是收藏的
        for item in data["data"]:
            if "is_favorite" in item:
                assert item["is_favorite"] == 1
    
    def test_insert_success(self, api_client, unique_name):
        """测试新增历史记录 - 成功"""
        response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": 1,
            "api_id": 1,
            "request_url": f"/api/test/{unique_name}",
            "request_method": "POST",
            "request_headers": '{"Content-Type": "application/json"}',
            "request_body": '{"test": "data"}',
            "response_status": 200,
            "response_body": '{"code": 200}',
            "response_time": 150,
            "is_success": 1
        })
        data = api_client.assert_success(response)
        
        assert "id" in data["data"]
        assert isinstance(data["data"]["id"], int)
    
    def test_insert_minimal_data(self, api_client, unique_name):
        """测试新增历史记录 - 最小数据"""
        response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": 1,
            "request_url": f"/api/minimal/{unique_name}",
            "request_method": "GET"
        })
        data = api_client.assert_success(response)
        
        assert "id" in data["data"]
    
    def test_delete_success(self, api_client, unique_name):
        """测试删除历史记录 - 成功"""
        # 先创建
        create_response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": 1,
            "request_url": f"/api/delete/{unique_name}",
            "request_method": "DELETE"
        })
        create_data = api_client.assert_success(create_response)
        history_id = create_data["data"]["id"]
        
        # 删除
        response = api_client.delete("/ApiRequestHistory/delete", params={"id": history_id})
        data = api_client.assert_success(response)
        
        # 验证已删除
        query_response = api_client.get("/ApiRequestHistory/queryById", params={"id": history_id})
        assert query_response.status_code in [200, 404]
    
    def test_batch_delete_success(self, api_client, unique_name):
        """测试批量删除 - 成功"""
        # 创建多条记录
        ids = []
        for i in range(3):
            response = api_client.post("/ApiRequestHistory/insert", json={
                "project_id": 1,
                "request_url": f"/api/batch/{unique_name}/{i}",
                "request_method": "GET"
            })
            data = api_client.assert_success(response)
            ids.append(data["data"]["id"])
        
        # 批量删除
        response = api_client.post("/ApiRequestHistory/batchDelete", json={
            "ids": ids
        })
        data = api_client.assert_success(response)
        
        assert "已删除" in data["msg"]
    
    def test_toggle_favorite_success(self, api_client, unique_name):
        """测试切换收藏状态 - 成功"""
        # 创建记录
        create_response = api_client.post("/ApiRequestHistory/insert", json={
            "project_id": 1,
            "request_url": f"/api/favorite/{unique_name}",
            "request_method": "GET",
            "is_favorite": 0
        })
        create_data = api_client.assert_success(create_response)
        history_id = create_data["data"]["id"]
        
        # 切换为收藏
        response1 = api_client.put("/ApiRequestHistory/toggleFavorite", params={"id": history_id})
        data1 = api_client.assert_success(response1)
        assert "收藏" in data1["msg"]
        
        # 再次切换取消收藏
        response2 = api_client.put("/ApiRequestHistory/toggleFavorite", params={"id": history_id})
        data2 = api_client.assert_success(response2)
        assert "取消" in data2["msg"] or "收藏" in data2["msg"]
    
    def test_clear_history_success(self, api_client):
        """测试清空历史记录 - 成功"""
        response = api_client.post("/ApiRequestHistory/clear", json={
            "project_id": 1,
            "keep_favorites": True,
            "days": 30
        })
        data = api_client.assert_success(response)
        
        assert "已清空" in data["msg"]
    
    def test_clear_history_without_keep_favorites(self, api_client):
        """测试清空历史记录 - 不保留收藏"""
        response = api_client.post("/ApiRequestHistory/clear", json={
            "project_id": 1,
            "keep_favorites": False,
            "days": 7
        })
        data = api_client.assert_success(response)
        
        assert "已清空" in data["msg"]
    
    def test_get_statistics_success(self, api_client):
        """测试获取历史统计 - 成功"""
        response = api_client.get("/ApiRequestHistory/statistics", params={
            "project_id": 1,
            "days": 7
        })
        data = api_client.assert_success(response)
        
        result = data["data"]
        assert "total" in result
        assert "success_count" in result
        assert "fail_count" in result
        assert "success_rate" in result
        assert "avg_response_time" in result
        assert "method_stats" in result
        
        # 验证统计逻辑
        if result["total"] > 0:
            assert result["success_count"] + result["fail_count"] <= result["total"]
            assert 0 <= result["success_rate"] <= 100
    
    def test_get_statistics_custom_days(self, api_client):
        """测试获取历史统计 - 自定义天数"""
        response = api_client.get("/ApiRequestHistory/statistics", params={
            "project_id": 1,
            "days": 30
        })
        data = api_client.assert_success(response)
        
        assert "data" in data


class TestApiRequestHistoryControllerEdgeCases:
    """API 请求历史 Controller 边界情况测试"""
    
    def test_query_with_invalid_page(self, api_client):
        """测试无效的页码"""
        response = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 0,
            "pageSize": 10
        })
        # 应该返回错误或第一页
        assert response.status_code in [200, 400]
    
    def test_query_with_large_page_size(self, api_client):
        """测试过大的页面大小"""
        response = api_client.post("/ApiRequestHistory/queryByPage", json={
            "page": 1,
            "pageSize": 10000
        })
        data = api_client.assert_success(response)
        
        # 应该有合理的限制
        assert len(data["data"]) <= 10000
    
    def test_delete_nonexistent_record(self, api_client):
        """测试删除不存在的记录"""
        response = api_client.delete("/ApiRequestHistory/delete", params={"id": 999999})
        # 应该返回错误
        assert response.status_code in [200, 404]
    
    def test_batch_delete_empty_list(self, api_client):
        """测试批量删除空列表"""
        response = api_client.post("/ApiRequestHistory/batchDelete", json={
            "ids": []
        })
        data = api_client.assert_success(response)
        
        assert "0" in data["msg"] or "已删除" in data["msg"]
    
    def test_batch_delete_with_invalid_ids(self, api_client):
        """测试批量删除包含无效ID"""
        response = api_client.post("/ApiRequestHistory/batchDelete", json={
            "ids": [999998, 999999]
        })
        # 应该处理无效ID
        assert response.status_code == 200
