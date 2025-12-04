"""
ApiCollectionController 接口集合管理模块完整单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiCollectionInfoController:
    """接口集合信息控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session, test_project):
        """测试分页查询接口集合"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            collection_name="测试集合",
            collection_desc="集合描述",
            create_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        
        response = client.post("/ApiCollectionInfo/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session, test_project):
        """测试根据ID查询接口集合"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            collection_name="ID查询集合",
            create_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        response = client.get(f"/ApiCollectionInfo/queryById?id={collection.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_collection(self, client: TestClient, test_project):
        """测试新增接口集合"""
        response = client.post("/ApiCollectionInfo/insert", json={
            "project_id": test_project.id,
            "collection_name": "新增测试集合",
            "collection_desc": "测试描述"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_collection(self, client: TestClient, session: Session, test_project):
        """测试更新接口集合"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            collection_name="待更新集合",
            create_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        response = client.put("/ApiCollectionInfo/update", json={
            "id": collection.id,
            "collection_name": "更新后的集合名"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_collection(self, client: TestClient, session: Session, test_project):
        """测试删除接口集合"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            collection_name="待删除集合",
            create_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        response = client.delete(f"/ApiCollectionInfo/delete?id={collection.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestApiCollectionDetailController:
    """接口集合详情控制器测试类"""
    
    def test_query_by_collection_id(self, client: TestClient, session: Session, test_project):
        """测试根据集合ID查询详情"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            collection_name="详情查询集合",
            create_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        response = client.get(f"/ApiCollectionDetail/queryByCollectionId?collection_id={collection.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_detail(self, client: TestClient, session: Session, test_project, test_api_info):
        """测试新增集合详情"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            collection_name="新增详情集合",
            create_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        response = client.post("/ApiCollectionDetail/insert", json={
            "collection_id": collection.id,
            "api_id": test_api_info.id,
            "sort_order": 1
        })
        
        assert response.status_code == 200
    
    def test_batch_insert_details(self, client: TestClient, session: Session, test_project, test_api_info):
        """测试批量新增集合详情"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            collection_name="批量新增集合",
            create_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        response = client.post("/ApiCollectionDetail/batchInsert", json={
            "collection_id": collection.id,
            "api_ids": [test_api_info.id]
        })
        
        assert response.status_code == 200
