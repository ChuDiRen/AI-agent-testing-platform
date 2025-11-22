"""
ApiDbBaseController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime


class TestApiDbBaseController:
    """API数据库配置控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, test_project):
        """测试分页查询"""
        response = client.post("/ApiDbBase/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_insert(self, client: TestClient, test_project):
        """测试新增数据库配置"""
        data = {
            "project_id": test_project.id,
            "name": "测试数据库",
            "db_type": "mysql",
            "db_info": "{}"
        }
        response = client.post("/ApiDbBase/insert", json=data)
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_update(self, client: TestClient, session: Session, test_project):
        """测试更新"""
        from apitest.model.ApiDbBaseModel import ApiDbBase
        db = ApiDbBase(project_id=test_project.id, name="test", db_type="mysql", db_info="{}")
        session.add(db)
        session.commit()
        session.refresh(db)
        
        response = client.put("/ApiDbBase/update", json={"id": db.id, "name": "updated"})
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, session: Session, test_project):
        """测试删除"""
        from apitest.model.ApiDbBaseModel import ApiDbBase
        db = ApiDbBase(project_id=test_project.id, name="test", db_type="mysql", db_info="{}")
        session.add(db)
        session.commit()
        session.refresh(db)
        
        response = client.delete(f"/ApiDbBase/delete?id={db.id}")
        assert response.status_code == 200
