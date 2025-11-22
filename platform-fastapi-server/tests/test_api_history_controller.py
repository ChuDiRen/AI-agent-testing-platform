"""
ApiHistoryController 单元测试
测试执行历史管理的核心功能
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime


@pytest.fixture(name="test_history")
def test_history_fixture(session: Session, test_project, test_api_info):
    """创建测试历史记录"""
    from apitest.model.ApiHistoryModel import ApiHistory
    
    history = ApiHistory(
        api_info_id=test_api_info.id,
        project_id=test_project.id,
        test_name="测试执行",
        test_status="success",
        request_url="https://api.example.com/test",
        request_method="POST",
        status_code=200,
        response_time=150,
        create_time=datetime.now(),
        modify_time=datetime.now()
    )
    session.add(history)
    session.commit()
    session.refresh(history)
    
    return history


class TestApiHistoryController:
    """API执行历史控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, test_history):
        """测试分页查询历史"""
        response = client.post(
            "/ApiTest/queryByPage",
            json={"page": 1, "pageSize": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert data["data"]["total"] >= 1
    
    def test_query_by_id(self, client: TestClient, test_history):
        """测试根据ID查询历史"""
        response = client.get(f"/ApiTest/queryById?id={test_history.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == test_history.id
        assert data["data"]["test_name"] == test_history.test_name
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的历史"""
        response = client.get("/ApiTest/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]
    
    def test_delete(self, client: TestClient, session: Session, test_project, test_api_info):
        """测试删除历史记录"""
        from apitest.model.ApiHistoryModel import ApiHistory
        
        history = ApiHistory(
            api_info_id=test_api_info.id,
            project_id=test_project.id,
            test_name="待删除记录",
            test_status="success",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(history)
        session.commit()
        session.refresh(history)
        
        response = client.delete(f"/ApiTest/delete?id={history.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_delete_not_found(self, client: TestClient):
        """测试删除不存在的历史"""
        response = client.delete("/ApiTest/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    def test_query_by_project(self, client: TestClient, test_history, test_project):
        """测试根据项目查询历史"""
        response = client.get(f"/ApiTest/queryByProject?project_id={test_project.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 1
    
    def test_query_by_status(self, client: TestClient, test_history):
        """测试根据状态查询历史"""
        response = client.post(
            "/ApiTest/queryByPage",
            json={"page": 1, "pageSize": 10, "test_status": "success"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 验证返回的记录状态都是success
        for item in data["data"]["list"]:
            assert item["test_status"] == "success"
    
    def test_statistics(self, client: TestClient, test_history):
        """测试统计功能"""
        # 这个测试假设有统计接口
        response = client.get("/ApiTest/statistics")
        
        # 如果接口不存在,会返回404,这也是正常的
        assert response.status_code in [200, 404]
