"""
API测试集合详情管理 接口测试
接口清单:
- GET /ApiCollectionDetail/queryByCollectionId - 根据集合ID查询关联用例
- POST /ApiCollectionDetail/insert - 新增集合详情
- PUT /ApiCollectionDetail/update - 更新集合详情
- DELETE /ApiCollectionDetail/delete - 删除集合详情
- POST /ApiCollectionDetail/batchAdd - 批量添加用例到集合
- POST /ApiCollectionDetail/batchUpdateOrder - 批量更新执行顺序
- GET /ApiCollectionDetail/getDdtTemplate - 获取用例数据驱动模板
"""
import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestApiCollectionDetailAPI:
    """API测试集合详情管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for detail_id in self.created_ids:
            try:
                self.client.delete("/ApiCollectionDetail/delete", params={"id": detail_id})
            except:
                pass
        self.client.close()
    
    def _create_test_detail(self, collection_info_id=1, case_info_id=1):
        """创建测试集合详情"""
        response = self.client.post("/ApiCollectionDetail/insert", json={
            "collection_info_id": collection_info_id,
            "case_info_id": case_info_id,
            "run_order": 1
        })
        if response.status_code == 200 and response.json().get("code") == 200:
            detail_id = response.json().get("data", {}).get("id")
            if detail_id:
                self.created_ids.append(detail_id)
            return detail_id
        return None
    
    # ==================== GET /ApiCollectionDetail/queryByCollectionId 按集合ID查询测试 ====================
    
    def test_query_by_collection_id_success(self):
        """按集合ID查询 - 正常请求"""
        response = self.client.get("/ApiCollectionDetail/queryByCollectionId", params={"collection_info_id": 1})
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_query_by_collection_id_empty(self):
        """按集合ID查询 - 空结果"""
        response = self.client.get("/ApiCollectionDetail/queryByCollectionId", params={"collection_info_id": 99999})
        data = self.client.assert_success(response)
        assert len(data.get("data", [])) == 0
    
    def test_query_by_collection_id_missing_param(self):
        """按集合ID查询 - 缺少参数"""
        response = self.client.get("/ApiCollectionDetail/queryByCollectionId")
        assert response.status_code == 422
    
    # ==================== POST /ApiCollectionDetail/insert 新增详情测试 ====================
    
    def test_insert_success(self):
        """新增详情 - 正常请求"""
        response = self.client.post("/ApiCollectionDetail/insert", json={
            "collection_info_id": 1,
            "case_info_id": 1,
            "run_order": 1
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_with_ddt_data(self):
        """新增详情 - 带数据驱动"""
        response = self.client.post("/ApiCollectionDetail/insert", json={
            "collection_info_id": 1,
            "case_info_id": 1,
            "run_order": 1,
            "ddt_data": [{"desc": "测试数据1", "username": "test"}]
        })
        data = self.client.assert_success(response)
        assert "id" in data.get("data", {})
        self.created_ids.append(data["data"]["id"])
    
    def test_insert_missing_required(self):
        """新增详情 - 缺少必填字段"""
        response = self.client.post("/ApiCollectionDetail/insert", json={
            "run_order": 1
        })
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== PUT /ApiCollectionDetail/update 更新详情测试 ====================
    
    def test_update_success(self):
        """更新详情 - 正常请求"""
        detail_id = self._create_test_detail()
        if detail_id:
            response = self.client.put("/ApiCollectionDetail/update", json={
                "id": detail_id,
                "run_order": 2
            })
            self.client.assert_success(response)
    
    def test_update_not_exist(self):
        """更新详情 - 数据不存在"""
        response = self.client.put("/ApiCollectionDetail/update", json={
            "id": 99999,
            "run_order": 1
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== DELETE /ApiCollectionDetail/delete 删除详情测试 ====================
    
    def test_delete_success(self):
        """删除详情 - 正常请求"""
        detail_id = self._create_test_detail()
        if detail_id:
            self.created_ids.remove(detail_id)
            response = self.client.delete("/ApiCollectionDetail/delete", params={"id": detail_id})
            self.client.assert_success(response)
    
    def test_delete_not_exist(self):
        """删除详情 - 数据不存在"""
        response = self.client.delete("/ApiCollectionDetail/delete", params={"id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    # ==================== POST /ApiCollectionDetail/batchUpdateOrder 批量更新顺序测试 ====================
    
    def test_batch_update_order_success(self):
        """批量更新顺序 - 正常请求"""
        detail_id = self._create_test_detail()
        if detail_id:
            response = self.client.post("/ApiCollectionDetail/batchUpdateOrder", json=[
                {"id": detail_id, "run_order": 3}
            ])
            self.client.assert_success(response)
    
    def test_batch_update_order_empty(self):
        """批量更新顺序 - 空列表"""
        response = self.client.post("/ApiCollectionDetail/batchUpdateOrder", json=[])
        self.client.assert_success(response)
    
    # ==================== GET /ApiCollectionDetail/getDdtTemplate 获取DDT模板测试 ====================
    
    def test_get_ddt_template_success(self):
        """获取DDT模板 - 正常请求"""
        response = self.client.get("/ApiCollectionDetail/getDdtTemplate", params={"case_info_id": 1})
        assert response.status_code == 200
    
    def test_get_ddt_template_not_exist(self):
        """获取DDT模板 - 用例不存在"""
        response = self.client.get("/ApiCollectionDetail/getDdtTemplate", params={"case_info_id": 99999})
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_get_ddt_template_missing_param(self):
        """获取DDT模板 - 缺少参数"""
        response = self.client.get("/ApiCollectionDetail/getDdtTemplate")
        assert response.status_code == 422
