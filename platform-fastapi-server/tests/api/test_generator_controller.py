"""
代码生成器 接口测试
接口清单:
- POST /Generator/preview - 预览生成代码
- POST /Generator/download - 下载生成代码
- POST /Generator/batchDownload - 批量下载代码
- GET /Generator/history - 获取代码生成历史
"""
import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestGeneratorAPI:
    """代码生成器接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        yield
        self.client.close()
    
    # ==================== POST /Generator/preview 预览代码测试 ====================
    
    def test_preview_success(self):
        """预览代码 - 正常请求"""
        response = self.client.post("/Generator/preview", json={
            "table_id": 1
        })
        # 表配置可能存在或不存在
        assert response.status_code == 200
    
    def test_preview_table_not_exist(self):
        """预览代码 - 表配置不存在"""
        response = self.client.post("/Generator/preview", json={
            "table_id": 99999
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_preview_missing_param(self):
        """预览代码 - 缺少参数"""
        response = self.client.post("/Generator/preview", json={})
        assert response.status_code == 422 or response.json()["code"] != 200
    
    def test_preview_unauthorized(self):
        """预览代码 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/Generator/preview", json={"table_id": 1})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== POST /Generator/download 下载代码测试 ====================
    
    def test_download_table_not_exist(self):
        """下载代码 - 表配置不存在"""
        response = self.client.post("/Generator/download", json={
            "table_id": 99999
        })
        assert response.json()["code"] == -1 or "不存在" in response.json().get("msg", "")
    
    def test_download_missing_param(self):
        """下载代码 - 缺少参数"""
        response = self.client.post("/Generator/download", json={})
        assert response.status_code == 422 or response.json()["code"] != 200
    
    # ==================== POST /Generator/batchDownload 批量下载测试 ====================
    
    def test_batch_download_empty(self):
        """批量下载 - 空列表"""
        response = self.client.post("/Generator/batchDownload", json={
            "table_ids": []
        })
        # 空列表可能返回空ZIP或错误
        assert response.status_code == 200
    
    def test_batch_download_not_exist(self):
        """批量下载 - 表配置不存在"""
        response = self.client.post("/Generator/batchDownload", json={
            "table_ids": [99999]
        })
        # 不存在的表会被跳过
        assert response.status_code == 200
    
    # ==================== GET /Generator/history 获取历史测试 ====================
    
    def test_get_history_success(self):
        """获取历史 - 正常请求"""
        response = self.client.get("/Generator/history")
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_get_history_with_table_filter(self):
        """获取历史 - 带表ID筛选"""
        response = self.client.get("/Generator/history", params={"table_id": 1})
        data = self.client.assert_success(response)
        assert "data" in data
    
    def test_get_history_unauthorized(self):
        """获取历史 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/Generator/history")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
