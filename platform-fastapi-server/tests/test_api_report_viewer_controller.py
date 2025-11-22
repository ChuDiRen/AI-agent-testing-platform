"""
ApiReportViewerController 单元测试
"""
from fastapi.testclient import TestClient


class TestApiReportViewerController:
    """API报告查看器控制器测试类"""
    
    def test_view_report_no_params(self, client: TestClient):
        """测试查看报告 - 无参数"""
        response = client.get("/ApiReportViewer/view")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 400
        assert "参数" in data["msg"]
    
    def test_view_report_not_found(self, client: TestClient):
        """测试查看报告 - 报告不存在"""
        response = client.get("/ApiReportViewer/view?history_id=99999")
        
        assert response.status_code == 404
    
    def test_list_reports(self, client: TestClient):
        """测试列出所有报告"""
        response = client.get("/ApiReportViewer/list")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
    
    def test_download_report_no_params(self, client: TestClient):
        """测试下载报告 - 无参数"""
        response = client.get("/ApiReportViewer/download")
        
        assert response.status_code == 400
    
    def test_download_report_not_found(self, client: TestClient):
        """测试下载报告 - 报告不存在"""
        response = client.get("/ApiReportViewer/download?history_id=99999")
        
        assert response.status_code == 404
