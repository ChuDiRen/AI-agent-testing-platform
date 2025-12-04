"""
ApiHistoryController 历史记录模块完整单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiHistoryController:
    """API历史记录控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session, test_api_info):
        """测试分页查询历史记录"""
        from apitest.model.ApiHistoryModel import ApiHistory
        
        history = ApiHistory(
            api_id=test_api_info.id,
            request_url="https://api.test.com/test",
            request_method="POST",
            request_headers="{}",
            request_body="{}",
            response_status=200,
            response_body='{"code": 200}',
            response_time=100,
            create_time=datetime.now()
        )
        session.add(history)
        session.commit()
        
        response = client.post("/ApiHistory/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_api_id(self, client: TestClient, session: Session, test_api_info):
        """测试根据API ID查询历史记录"""
        from apitest.model.ApiHistoryModel import ApiHistory
        
        history = ApiHistory(
            api_id=test_api_info.id,
            request_url="https://api.test.com/test",
            request_method="GET",
            response_status=200,
            response_time=50,
            create_time=datetime.now()
        )
        session.add(history)
        session.commit()
        
        response = client.get(f"/ApiHistory/queryByApiId?api_id={test_api_info.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session, test_api_info):
        """测试根据ID查询历史记录"""
        from apitest.model.ApiHistoryModel import ApiHistory
        
        history = ApiHistory(
            api_id=test_api_info.id,
            request_url="https://api.test.com/test",
            request_method="POST",
            response_status=200,
            response_time=80,
            create_time=datetime.now()
        )
        session.add(history)
        session.commit()
        session.refresh(history)
        
        response = client.get(f"/ApiHistory/queryById?id={history.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的历史记录"""
        response = client.get("/ApiHistory/queryById?id=99999")
        
        assert response.status_code == 200
    
    def test_insert_history(self, client: TestClient, test_api_info):
        """测试新增历史记录"""
        response = client.post("/ApiHistory/insert", json={
            "api_id": test_api_info.id,
            "request_url": "https://api.test.com/new",
            "request_method": "POST",
            "request_headers": "{}",
            "request_body": '{"test": "data"}',
            "response_status": 200,
            "response_body": '{"code": 200}',
            "response_time": 120
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_history(self, client: TestClient, session: Session, test_api_info):
        """测试删除历史记录"""
        from apitest.model.ApiHistoryModel import ApiHistory
        
        history = ApiHistory(
            api_id=test_api_info.id,
            request_url="https://api.test.com/delete",
            request_method="DELETE",
            response_status=200,
            response_time=60,
            create_time=datetime.now()
        )
        session.add(history)
        session.commit()
        session.refresh(history)
        
        response = client.delete(f"/ApiHistory/delete?id={history.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_by_api_id(self, client: TestClient, session: Session, test_api_info):
        """测试根据API ID删除历史记录"""
        from apitest.model.ApiHistoryModel import ApiHistory
        
        # 创建多条历史记录
        for i in range(3):
            history = ApiHistory(
                api_id=test_api_info.id,
                request_url=f"https://api.test.com/batch{i}",
                request_method="GET",
                response_status=200,
                response_time=50 + i * 10,
                create_time=datetime.now()
            )
            session.add(history)
        session.commit()
        
        response = client.delete(f"/ApiHistory/deleteByApiId?api_id={test_api_info.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_latest(self, client: TestClient, session: Session, test_api_info):
        """测试查询最新历史记录"""
        from apitest.model.ApiHistoryModel import ApiHistory
        
        history = ApiHistory(
            api_id=test_api_info.id,
            request_url="https://api.test.com/latest",
            request_method="GET",
            response_status=200,
            response_time=30,
            create_time=datetime.now()
        )
        session.add(history)
        session.commit()
        
        response = client.get(f"/ApiHistory/queryLatest?api_id={test_api_info.id}&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
