"""
ApiMetaController 单元测试
"""
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiMetaController:
    """API元数据控制器测试类"""
    
    def test_query_by_page(self, client: TestClient):
        """测试分页查询"""
        response = client.post("/ApiMeta/queryByPage", json={"page": 1, "pageSize": 10})
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session, test_project):
        """测试ID查询"""
        from apitest.model.ApiMetaModel import ApiMeta
        meta = ApiMeta(project_id=test_project.id, mate_name="test")
        session.add(meta)
        session.commit()
        session.refresh(meta)
        
        response = client.get(f"/ApiMeta/queryById?id={meta.id}")
        assert response.status_code == 200
    
    def test_update(self, client: TestClient, session: Session, test_project):
        """测试更新"""
        from apitest.model.ApiMetaModel import ApiMeta
        meta = ApiMeta(project_id=test_project.id, mate_name="test")
        session.add(meta)
        session.commit()
        session.refresh(meta)
        
        response = client.put("/ApiMeta/update", json={"id": meta.id, "mate_name": "updated"})
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, session: Session, test_project):
        """测试删除"""
        from apitest.model.ApiMetaModel import ApiMeta
        meta = ApiMeta(project_id=test_project.id, mate_name="test")
        session.add(meta)
        session.commit()
        session.refresh(meta)
        
        response = client.delete(f"/ApiMeta/delete?id={meta.id}")
        assert response.status_code == 200
