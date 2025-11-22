"""
ApiProjectController 单元测试
"""
from datetime import datetime

from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiProjectController:
    """API项目控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session, test_project):
        """测试分页查询"""
        response = client.post(
            "/ApiProject/queryByPage",
            json={"page": 1, "pageSize": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert "list" in data["data"]
        assert "total" in data["data"]
        assert data["data"]["total"] >= 1
    
    def test_query_by_id(self, client: TestClient, test_project):
        """测试根据ID查询"""
        response = client.get(
            f"/ApiProject/queryById?id={test_project.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == test_project.id
        assert data["data"]["project_name"] == test_project.project_name
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的ID"""
        response = client.get("/ApiProject/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]
    
    def test_query_all(self, client: TestClient, test_project):
        """测试查询所有项目"""
        response = client.get("/ApiProject/queryAll")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 1
    
    def test_insert(self, client: TestClient):
        """测试新增项目"""
        new_project = {
            "project_name": "新测试项目",
            "project_desc": "这是一个新的测试项目"
        }
        
        response = client.post("/ApiProject/insert", json=new_project)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
        assert data["data"]["id"] > 0
    
    def test_update(self, client: TestClient, test_project):
        """测试更新项目"""
        update_data = {
            "id": test_project.id,
            "project_name": "更新后的项目名",
            "project_desc": "更新后的描述"
        }
        
        response = client.put("/ApiProject/update", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_update_not_found(self, client: TestClient):
        """测试更新不存在的项目"""
        update_data = {
            "id": 99999,
            "project_name": "不存在的项目"
        }
        
        response = client.put("/ApiProject/update", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    def test_delete(self, client: TestClient, session: Session):
        """测试删除项目"""
        # 先创建一个项目
        from apitest.model.ApiProjectModel import ApiProject
        
        project = ApiProject(
            project_name="待删除项目",
            project_desc="用于测试删除",
            create_time=datetime.now()
        )
        session.add(project)
        session.commit()
        session.refresh(project)
        
        # 删除项目
        response = client.delete(f"/ApiProject/delete?id={project.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_delete_not_found(self, client: TestClient):
        """测试删除不存在的项目"""
        response = client.delete("/ApiProject/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
