"""
ApiMetaController 和 ApiOperationTypeController 元数据模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiMetaController:
    """API元数据控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询元数据"""
        from apitest.model.ApiMetaModel import ApiMeta
        
        meta = ApiMeta(
            meta_key="test_key",
            meta_value="test_value",
            meta_type="config",
            description="测试元数据",
            create_time=datetime.now()
        )
        session.add(meta)
        session.commit()
        
        response = client.post("/ApiMeta/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询元数据"""
        from apitest.model.ApiMetaModel import ApiMeta
        
        meta = ApiMeta(
            meta_key="id_query_key",
            meta_value="id_query_value",
            meta_type="config",
            create_time=datetime.now()
        )
        session.add(meta)
        session.commit()
        session.refresh(meta)
        
        response = client.get(f"/ApiMeta/queryById?id={meta.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_meta(self, client: TestClient):
        """测试新增元数据"""
        response = client.post("/ApiMeta/insert", json={
            "meta_key": "new_meta_key",
            "meta_value": "new_meta_value",
            "meta_type": "config",
            "description": "新增元数据"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_meta(self, client: TestClient, session: Session):
        """测试更新元数据"""
        from apitest.model.ApiMetaModel import ApiMeta
        
        meta = ApiMeta(
            meta_key="update_key",
            meta_value="old_value",
            meta_type="config",
            create_time=datetime.now()
        )
        session.add(meta)
        session.commit()
        session.refresh(meta)
        
        response = client.put("/ApiMeta/update", json={
            "id": meta.id,
            "meta_value": "new_value"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_meta(self, client: TestClient, session: Session):
        """测试删除元数据"""
        from apitest.model.ApiMetaModel import ApiMeta
        
        meta = ApiMeta(
            meta_key="delete_key",
            meta_value="delete_value",
            meta_type="config",
            create_time=datetime.now()
        )
        session.add(meta)
        session.commit()
        session.refresh(meta)
        
        response = client.delete(f"/ApiMeta/delete?id={meta.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_key(self, client: TestClient, session: Session):
        """测试根据Key查询元数据"""
        from apitest.model.ApiMetaModel import ApiMeta
        
        meta = ApiMeta(
            meta_key="unique_key",
            meta_value="unique_value",
            meta_type="config",
            create_time=datetime.now()
        )
        session.add(meta)
        session.commit()
        
        response = client.get("/ApiMeta/queryByKey?meta_key=unique_key")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestApiOperationTypeController:
    """操作类型控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询操作类型"""
        from apitest.model.ApiOperationTypeModel import OperationType
        
        op_type = OperationType(
            type_name="测试操作类型",
            type_code="test_op",
            description="测试描述",
            create_time=datetime.now()
        )
        session.add(op_type)
        session.commit()
        
        response = client.post("/ApiOperationType/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询操作类型"""
        from apitest.model.ApiOperationTypeModel import OperationType
        
        op_type = OperationType(
            type_name="ID查询操作类型",
            type_code="id_query_op",
            create_time=datetime.now()
        )
        session.add(op_type)
        session.commit()
        session.refresh(op_type)
        
        response = client.get(f"/ApiOperationType/queryById?id={op_type.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_operation_type(self, client: TestClient):
        """测试新增操作类型"""
        response = client.post("/ApiOperationType/insert", json={
            "type_name": "新增操作类型",
            "type_code": "new_op_type",
            "description": "新增描述"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_operation_type(self, client: TestClient, session: Session):
        """测试更新操作类型"""
        from apitest.model.ApiOperationTypeModel import OperationType
        
        op_type = OperationType(
            type_name="待更新操作类型",
            type_code="update_op",
            create_time=datetime.now()
        )
        session.add(op_type)
        session.commit()
        session.refresh(op_type)
        
        response = client.put("/ApiOperationType/update", json={
            "id": op_type.id,
            "type_name": "更新后的操作类型"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_operation_type(self, client: TestClient, session: Session):
        """测试删除操作类型"""
        from apitest.model.ApiOperationTypeModel import OperationType
        
        op_type = OperationType(
            type_name="待删除操作类型",
            type_code="delete_op",
            create_time=datetime.now()
        )
        session.add(op_type)
        session.commit()
        session.refresh(op_type)
        
        response = client.delete(f"/ApiOperationType/delete?id={op_type.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_all(self, client: TestClient, session: Session):
        """测试查询所有操作类型"""
        from apitest.model.ApiOperationTypeModel import OperationType
        
        op_type = OperationType(
            type_name="全部查询操作类型",
            type_code="all_query_op",
            create_time=datetime.now()
        )
        session.add(op_type)
        session.commit()
        
        response = client.get("/ApiOperationType/queryAll")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
