"""
ApiDbBaseController 数据库配置模块完整单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiDbBaseController:
    """数据库配置控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session, test_project):
        """测试分页查询数据库配置"""
        from apitest.model.ApiDbBaseModel import ApiDbBase
        
        db_config = ApiDbBase(
            project_id=test_project.id,
            db_name="测试数据库",
            db_type="mysql",
            host="localhost",
            port=3306,
            username="root",
            password="test123",
            database="test_db",
            create_time=datetime.now()
        )
        session.add(db_config)
        session.commit()
        
        response = client.post("/ApiDbBase/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session, test_project):
        """测试根据ID查询数据库配置"""
        from apitest.model.ApiDbBaseModel import ApiDbBase
        
        db_config = ApiDbBase(
            project_id=test_project.id,
            db_name="ID查询数据库",
            db_type="mysql",
            host="localhost",
            port=3306,
            username="root",
            password="test123",
            database="test_db",
            create_time=datetime.now()
        )
        session.add(db_config)
        session.commit()
        session.refresh(db_config)
        
        response = client.get(f"/ApiDbBase/queryById?id={db_config.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的数据库配置"""
        response = client.get("/ApiDbBase/queryById?id=99999")
        
        assert response.status_code == 200
    
    def test_insert_db_config(self, client: TestClient, test_project):
        """测试新增数据库配置"""
        response = client.post("/ApiDbBase/insert", json={
            "project_id": test_project.id,
            "db_name": "新增测试数据库",
            "db_type": "mysql",
            "host": "localhost",
            "port": 3306,
            "username": "root",
            "password": "test123",
            "database": "new_test_db"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_db_config(self, client: TestClient, session: Session, test_project):
        """测试更新数据库配置"""
        from apitest.model.ApiDbBaseModel import ApiDbBase
        
        db_config = ApiDbBase(
            project_id=test_project.id,
            db_name="待更新数据库",
            db_type="mysql",
            host="localhost",
            port=3306,
            username="root",
            password="old_pass",
            database="test_db",
            create_time=datetime.now()
        )
        session.add(db_config)
        session.commit()
        session.refresh(db_config)
        
        response = client.put("/ApiDbBase/update", json={
            "id": db_config.id,
            "db_name": "更新后的数据库名",
            "password": "new_pass"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_db_config(self, client: TestClient, session: Session, test_project):
        """测试删除数据库配置"""
        from apitest.model.ApiDbBaseModel import ApiDbBase
        
        db_config = ApiDbBase(
            project_id=test_project.id,
            db_name="待删除数据库",
            db_type="mysql",
            host="localhost",
            port=3306,
            username="root",
            password="test123",
            database="delete_db",
            create_time=datetime.now()
        )
        session.add(db_config)
        session.commit()
        session.refresh(db_config)
        
        response = client.delete(f"/ApiDbBase/delete?id={db_config.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_project_id(self, client: TestClient, session: Session, test_project):
        """测试根据项目ID查询数据库配置"""
        from apitest.model.ApiDbBaseModel import ApiDbBase
        
        db_config = ApiDbBase(
            project_id=test_project.id,
            db_name="项目查询数据库",
            db_type="mysql",
            host="localhost",
            port=3306,
            username="root",
            password="test123",
            database="project_db",
            create_time=datetime.now()
        )
        session.add(db_config)
        session.commit()
        
        response = client.get(f"/ApiDbBase/queryByProjectId?project_id={test_project.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
