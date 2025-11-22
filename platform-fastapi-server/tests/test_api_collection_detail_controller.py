"""
ApiCollectionDetailController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiCollectionDetailController:
    """测试集合详情控制器测试类"""
    
    def test_query_by_collection_id(self, client: TestClient, test_collection):
        """测试根据集合ID查询"""
        response = client.get(f"/ApiCollectionDetail/queryByCollectionId?collection_info_id={test_collection.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_batch_insert(self, client: TestClient, test_collection, test_case):
        """测试批量插入"""
        data = {
            "collection_info_id": test_collection.id,
            "details": [{"case_info_id": test_case.id, "run_order": 1}]
        }
        response = client.post("/ApiCollectionDetail/batchInsert", json=data)
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, session: Session, test_collection, test_case):
        """测试删除"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        detail = ApiCollectionDetail(collection_info_id=test_collection.id, case_info_id=test_case.id, run_order=1)
        session.add(detail)
        session.commit()
        session.refresh(detail)
        
        response = client.delete(f"/ApiCollectionDetail/delete?id={detail.id}")
        assert response.status_code == 200
