"""
ApiKeyWordController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime


class TestApiKeyWordController:
    """API关键字控制器测试类"""
    
    def test_query_all(self, client: TestClient):
        """测试查询所有"""
        response = client.get("/ApiKeyWord/queryAll")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_insert(self, client: TestClient):
        """测试新增关键字"""
        data = {"name": "测试关键字", "keyword_fun_name": "test_func"}
        response = client.post("/ApiKeyWord/insert", json=data)
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_update(self, client: TestClient, session: Session):
        """测试更新"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        kw = ApiKeyWord(name="test", keyword_fun_name="func")
        session.add(kw)
        session.commit()
        session.refresh(kw)
        
        response = client.put("/ApiKeyWord/update", json={"id": kw.id, "name": "updated"})
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, session: Session):
        """测试删除"""
        from apitest.model.ApiKeyWordModel import ApiKeyWord
        kw = ApiKeyWord(name="test", keyword_fun_name="func")
        session.add(kw)
        session.commit()
        session.refresh(kw)
        
        response = client.delete(f"/ApiKeyWord/delete?id={kw.id}")
        assert response.status_code == 200
