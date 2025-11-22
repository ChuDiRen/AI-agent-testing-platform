"""
ApiGroupController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiGroupController:
    """API分组控制器测试类"""
    
    def test_query_by_page(self, client: TestClient):
        """测试分页查询"""
        response = client.post("/ApiGroup/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_insert(self, client: TestClient, test_project):
        """测试新增分组"""
        data = {"project_id": test_project.id, "group_name": "测试分组"}
        response = client.post("/ApiGroup/insert", json=data)
        assert response.status_code == 200
    
    def test_update(self, client: TestClient, session: Session, test_project):
        """测试更新"""
        from apitest.model.ApiInfoGroupModel import ApiInfoGroup
        group = ApiInfoGroup(project_id=test_project.id, group_name="test")
        session.add(group)
        session.commit()
        session.refresh(group)
        
        response = client.put("/ApiGroup/update", json={"id": group.id, "group_name": "updated"})
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, session: Session, test_project):
        """测试删除"""
        from apitest.model.ApiInfoGroupModel import ApiInfoGroup
        group = ApiInfoGroup(project_id=test_project.id, group_name="test")
        session.add(group)
        session.commit()
        session.refresh(group)
        
        response = client.delete(f"/ApiGroup/delete?id={group.id}")
        assert response.status_code == 200
