"""
ApiOperationTypeController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiOperationTypeController:
    """操作类型控制器测试类"""
    
    def test_query_all(self, client: TestClient):
        """测试查询所有"""
        response = client.get("/OperationType/queryAll")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_insert(self, client: TestClient):
        """测试新增"""
        data = {"operation_type_name": "测试类型", "ex_fun_name": "test_func"}
        response = client.post("/OperationType/insert", json=data)
        assert response.status_code == 200
    
    def test_update(self, client: TestClient, session: Session):
        """测试更新"""
        from apitest.model.ApiOperationTypeModel import OperationType
        op = OperationType(operation_type_name="test", ex_fun_name="func")
        session.add(op)
        session.commit()
        session.refresh(op)
        
        response = client.put("/OperationType/update", json={"id": op.id, "operation_type_name": "updated"})
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, session: Session):
        """测试删除"""
        from apitest.model.ApiOperationTypeModel import OperationType
        op = OperationType(operation_type_name="test", ex_fun_name="func")
        session.add(op)
        session.commit()
        session.refresh(op)
        
        response = client.delete(f"/OperationType/delete?id={op.id}")
        assert response.status_code == 200
