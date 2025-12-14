"""
API测试报告查看器 接口测试
接口清单:
- GET /ApiReportViewer/view - 查看测试报告
- GET /ApiReportViewer/download - 下载测试报告
- GET /ApiReportViewer/list - 列出所有测试报告
"""
import pytest
from tests.conftest import APIClient, API_BASE_URL


class TestApiReportViewerAPI:
    """API测试报告查看器接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        yield
        self.client.close()
    
    # ==================== GET /ApiReportViewer/view 查看报告测试 ====================
    
    def test_view_report_by_history_id(self):
        """查看报告 - 通过history_id"""
        response = self.client.get("/ApiReportViewer/view", params={"history_id": 1})
        # 报告可能存在或不存在，检查返回状态
        assert response.status_code in [200, 400, 404]
    
    def test_view_report_by_execution_uuid(self):
        """查看报告 - 通过execution_uuid"""
        response = self.client.get("/ApiReportViewer/view", params={"execution_uuid": "test-uuid-123"})
        assert response.status_code in [200, 400, 404]
    
    def test_view_report_missing_params(self):
        """查看报告 - 缺少参数"""
        response = self.client.get("/ApiReportViewer/view")
        assert response.status_code == 400
    
    def test_view_report_not_exist(self):
        """查看报告 - 报告不存在"""
        response = self.client.get("/ApiReportViewer/view", params={"history_id": 99999})
        assert response.status_code in [200, 404]
    
    # ==================== GET /ApiReportViewer/download 下载报告测试 ====================
    
    def test_download_report_by_history_id(self):
        """下载报告 - 通过history_id"""
        response = self.client.get("/ApiReportViewer/download", params={"history_id": 1})
        # 报告可能存在或不存在
        assert response.status_code in [200, 400, 404]
    
    def test_download_report_by_execution_uuid(self):
        """下载报告 - 通过execution_uuid"""
        response = self.client.get("/ApiReportViewer/download", params={"execution_uuid": "test-uuid-123"})
        assert response.status_code in [200, 400, 404]
    
    def test_download_report_missing_params(self):
        """下载报告 - 缺少参数"""
        response = self.client.get("/ApiReportViewer/download")
        assert response.status_code == 400
    
    def test_download_report_not_exist(self):
        """下载报告 - 报告不存在"""
        response = self.client.get("/ApiReportViewer/download", params={"history_id": 99999})
        assert response.status_code in [200, 404]
    
    # ==================== GET /ApiReportViewer/list 列出报告测试 ====================
    
    def test_list_reports_success(self):
        """列出报告 - 正常请求"""
        response = self.client.get("/ApiReportViewer/list")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 200
        assert "data" in data
    
    def test_list_reports_structure(self):
        """列出报告 - 返回结构验证"""
        response = self.client.get("/ApiReportViewer/list")
        assert response.status_code == 200
        data = response.json()
        if data.get("code") == 200 and data.get("data"):
            report_data = data["data"]
            assert "list" in report_data or "total" in report_data
