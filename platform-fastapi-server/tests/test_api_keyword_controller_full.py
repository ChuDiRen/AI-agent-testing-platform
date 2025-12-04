"""
ApiKeyWordController 关键字管理模块完整单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiKeyWordController:
    """关键字控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询关键字"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        
        keyword = ApiKeyWord(
            keyword_name="测试关键字",
            keyword_code="test_keyword",
            keyword_type="http",
            create_time=datetime.now()
        )
        session.add(keyword)
        session.commit()
        
        response = client.post("/ApiKeyWord/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        
        keyword = ApiKeyWord(
            keyword_name="HTTP关键字",
            keyword_code="http_keyword",
            keyword_type="http",
            create_time=datetime.now()
        )
        session.add(keyword)
        session.commit()
        
        response = client.post("/ApiKeyWord/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "keyword_type": "http"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询关键字"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        
        keyword = ApiKeyWord(
            keyword_name="ID查询关键字",
            keyword_code="id_query_keyword",
            keyword_type="http",
            create_time=datetime.now()
        )
        session.add(keyword)
        session.commit()
        session.refresh(keyword)
        
        response = client.get(f"/ApiKeyWord/queryById?id={keyword.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的关键字"""
        response = client.get("/ApiKeyWord/queryById?id=99999")
        
        assert response.status_code == 200
    
    def test_insert_keyword(self, client: TestClient):
        """测试新增关键字"""
        response = client.post("/ApiKeyWord/insert", json={
            "keyword_name": "新增测试关键字",
            "keyword_code": "new_test_keyword",
            "keyword_type": "http",
            "description": "测试描述"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_keyword(self, client: TestClient, session: Session):
        """测试更新关键字"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        
        keyword = ApiKeyWord(
            keyword_name="待更新关键字",
            keyword_code="update_keyword",
            keyword_type="http",
            create_time=datetime.now()
        )
        session.add(keyword)
        session.commit()
        session.refresh(keyword)
        
        response = client.put("/ApiKeyWord/update", json={
            "id": keyword.id,
            "keyword_name": "更新后的关键字名"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_keyword(self, client: TestClient, session: Session):
        """测试删除关键字"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        
        keyword = ApiKeyWord(
            keyword_name="待删除关键字",
            keyword_code="delete_keyword",
            keyword_type="http",
            create_time=datetime.now()
        )
        session.add(keyword)
        session.commit()
        session.refresh(keyword)
        
        response = client.delete(f"/ApiKeyWord/delete?id={keyword.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_all(self, client: TestClient, session: Session):
        """测试查询所有关键字"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        
        keyword = ApiKeyWord(
            keyword_name="全部查询关键字",
            keyword_code="all_query_keyword",
            keyword_type="http",
            create_time=datetime.now()
        )
        session.add(keyword)
        session.commit()
        
        response = client.get("/ApiKeyWord/queryAll")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
