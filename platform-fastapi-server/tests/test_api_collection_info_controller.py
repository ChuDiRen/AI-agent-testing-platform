"""
ApiCollectionInfoController 单元测试
测试集合管理的核心功能
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime


@pytest.fixture(name="test_collection")
def test_collection_fixture(session: Session, test_project):
    """创建测试集合"""
    from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
    
    collection = ApiCollectionInfo(
        project_id=test_project.id,
        plan_name="测试集合",
        plan_desc="用于单元测试的集合",
        create_time=datetime.now(),
        modify_time=datetime.now()
    )
    session.add(collection)
    session.commit()
    session.refresh(collection)
    
    return collection


class TestApiCollectionInfoController:
    """API测试集合控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, test_collection):
        """测试分页查询集合"""
        response = client.post(
            "/ApiCollectionInfo/queryByPage",
            json={"page": 1, "pageSize": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert data["data"]["total"] >= 1
    
    def test_query_by_id(self, client: TestClient, test_collection):
        """测试根据ID查询集合"""
        response = client.get(
            f"/ApiCollectionInfo/queryById?id={test_collection.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == test_collection.id
        assert data["data"]["plan_name"] == test_collection.plan_name
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的集合"""
        response = client.get("/ApiCollectionInfo/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]
    
    def test_insert(self, client: TestClient, test_project):
        """测试新增集合"""
        new_collection = {
            "project_id": test_project.id,
            "plan_name": "新测试集合",
            "plan_desc": "这是一个新的测试集合"
        }
        
        response = client.post("/ApiCollectionInfo/insert", json=new_collection)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
        assert data["data"]["id"] > 0
    
    def test_update(self, client: TestClient, test_collection):
        """测试更新集合"""
        update_data = {
            "id": test_collection.id,
            "plan_name": "更新后的集合名",
            "plan_desc": "更新后的描述"
        }
        
        response = client.put("/ApiCollectionInfo/update", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_update_not_found(self, client: TestClient):
        """测试更新不存在的集合"""
        update_data = {
            "id": 99999,
            "plan_name": "不存在的集合"
        }
        
        response = client.put("/ApiCollectionInfo/update", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    def test_delete(self, client: TestClient, session: Session, test_project):
        """测试删除集合"""
        from apitest.model.ApiCollectionInfoModel import ApiCollectionInfo
        
        collection = ApiCollectionInfo(
            project_id=test_project.id,
            plan_name="待删除集合",
            plan_desc="用于测试删除",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(collection)
        session.commit()
        session.refresh(collection)
        
        response = client.delete(f"/ApiCollectionInfo/delete?id={collection.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_delete_not_found(self, client: TestClient):
        """测试删除不存在的集合"""
        response = client.delete("/ApiCollectionInfo/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    def test_add_case_to_collection(self, client: TestClient, test_collection, test_case):
        """测试添加用例到集合"""
        add_data = {
            "plan_id": test_collection.id,
            "case_info_id": test_case.id,
            "run_order": 1
        }
        
        response = client.post("/ApiCollectionInfo/addCase", json=add_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_batch_add_cases(self, client: TestClient, test_collection, test_case):
        """测试批量添加用例"""
        batch_data = {
            "plan_id": test_collection.id,
            "case_ids": [test_case.id]
        }
        
        response = client.post("/ApiCollectionInfo/batchAddCases", json=batch_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
