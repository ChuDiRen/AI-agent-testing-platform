"""
ApiCollectionDetailController 集合详情接口测试
测试服务地址: http://127.0.0.1:5000
"""
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiCollectionDetailController:
    """测试集合详情控制器测试类"""
    
    # ==================== 查询接口 ====================
    
    def test_query_by_collection_id(self, client: TestClient, test_collection):
        """测试根据集合ID查询"""
        response = client.get(f"/ApiCollectionDetail/queryByCollectionId?collection_info_id={test_collection.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_query_by_collection_id_with_data(self, client: TestClient, session: Session, test_collection, test_case):
        """测试根据集合ID查询 - 有数据"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        # 创建测试数据
        detail = ApiCollectionDetail(
            collection_info_id=test_collection.id,
            case_info_id=test_case.id,
            run_order=1,
            create_time=datetime.now()
        )
        session.add(detail)
        session.commit()
        
        response = client.get(f"/ApiCollectionDetail/queryByCollectionId?collection_info_id={test_collection.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 1
    
    def test_query_by_collection_id_empty(self, client: TestClient):
        """测试根据集合ID查询 - 空结果"""
        response = client.get("/ApiCollectionDetail/queryByCollectionId?collection_info_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_collection_id_order(self, client: TestClient, session: Session, test_collection, test_case):
        """测试查询结果按run_order排序"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        # 创建多条数据，顺序不同
        for order in [3, 1, 2]:
            detail = ApiCollectionDetail(
                collection_info_id=test_collection.id,
                case_info_id=test_case.id,
                run_order=order,
                create_time=datetime.now()
            )
            session.add(detail)
        session.commit()
        
        response = client.get(f"/ApiCollectionDetail/queryByCollectionId?collection_info_id={test_collection.id}")
        assert response.status_code == 200
        data = response.json()
        # 验证按顺序排列
        orders = [item["run_order"] for item in data["data"]["list"]]
        assert orders == sorted(orders)
    
    # ==================== 新增接口 ====================
    
    def test_insert(self, client: TestClient, test_collection, test_case):
        """测试新增集合详情"""
        data = {
            "collection_info_id": test_collection.id,
            "case_info_id": test_case.id,
            "run_order": 1
        }
        response = client.post("/ApiCollectionDetail/insert", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert "id" in result["data"]
    
    def test_insert_with_ddt_data(self, client: TestClient, test_collection, test_case):
        """测试新增集合详情 - 带DDT数据"""
        data = {
            "collection_info_id": test_collection.id,
            "case_info_id": test_case.id,
            "run_order": 1,
            "ddt_data": {"param1": "value1", "param2": "value2"}
        }
        response = client.post("/ApiCollectionDetail/insert", json=data)
        assert response.status_code == 200
    
    def test_insert_missing_collection_id(self, client: TestClient, test_case):
        """测试新增 - 缺少集合ID"""
        data = {
            "case_info_id": test_case.id,
            "run_order": 1
        }
        response = client.post("/ApiCollectionDetail/insert", json=data)
        assert response.status_code == 422
    
    # ==================== 更新接口 ====================
    
    def test_update(self, client: TestClient, session: Session, test_collection, test_case):
        """测试更新集合详情"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        detail = ApiCollectionDetail(
            collection_info_id=test_collection.id,
            case_info_id=test_case.id,
            run_order=1,
            create_time=datetime.now()
        )
        session.add(detail)
        session.commit()
        session.refresh(detail)
        
        response = client.put("/ApiCollectionDetail/update", json={
            "id": detail.id,
            "run_order": 5
        })
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_update_not_found(self, client: TestClient):
        """测试更新 - 记录不存在"""
        response = client.put("/ApiCollectionDetail/update", json={
            "id": 99999,
            "run_order": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    def test_update_ddt_data(self, client: TestClient, session: Session, test_collection, test_case):
        """测试更新DDT数据"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        detail = ApiCollectionDetail(
            collection_info_id=test_collection.id,
            case_info_id=test_case.id,
            run_order=1,
            create_time=datetime.now()
        )
        session.add(detail)
        session.commit()
        session.refresh(detail)
        
        response = client.put("/ApiCollectionDetail/update", json={
            "id": detail.id,
            "ddt_data": {"new_param": "new_value"}
        })
        assert response.status_code == 200
    
    # ==================== 删除接口 ====================
    
    def test_delete(self, client: TestClient, session: Session, test_collection, test_case):
        """测试删除"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        detail = ApiCollectionDetail(
            collection_info_id=test_collection.id,
            case_info_id=test_case.id,
            run_order=1,
            create_time=datetime.now()
        )
        session.add(detail)
        session.commit()
        session.refresh(detail)
        
        response = client.delete(f"/ApiCollectionDetail/delete?id={detail.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_delete_not_found(self, client: TestClient):
        """测试删除 - 记录不存在"""
        response = client.delete("/ApiCollectionDetail/delete?id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    # ==================== 批量添加接口 ====================
    
    def test_batch_add(self, client: TestClient, session: Session, test_collection, test_case):
        """测试批量添加用例到集合"""
        from apitest.model.ApiInfoCaseModel import ApiInfoCase
        
        # 创建多个测试用例
        case_ids = []
        for i in range(3):
            case = ApiInfoCase(
                project_id=test_case.project_id,
                case_name=f"批量测试用例{i}",
                create_time=datetime.now(),
                modify_time=datetime.now()
            )
            session.add(case)
            session.commit()
            session.refresh(case)
            case_ids.append(case.id)
        
        response = client.post(
            f"/ApiCollectionDetail/batchAdd?collection_info_id={test_collection.id}",
            json=case_ids
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "3" in data["msg"]
    
    def test_batch_add_empty_list(self, client: TestClient, test_collection):
        """测试批量添加 - 空列表"""
        response = client.post(
            f"/ApiCollectionDetail/batchAdd?collection_info_id={test_collection.id}",
            json=[]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "0" in data["msg"]
    
    def test_batch_add_auto_order(self, client: TestClient, session: Session, test_collection, test_case):
        """测试批量添加 - 自动顺序递增"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        # 先创建一条记录
        existing = ApiCollectionDetail(
            collection_info_id=test_collection.id,
            case_info_id=test_case.id,
            run_order=5,
            create_time=datetime.now()
        )
        session.add(existing)
        session.commit()
        
        # 批量添加新用例
        response = client.post(
            f"/ApiCollectionDetail/batchAdd?collection_info_id={test_collection.id}",
            json=[test_case.id]
        )
        assert response.status_code == 200
    
    # ==================== 批量更新顺序接口 ====================
    
    def test_batch_update_order(self, client: TestClient, session: Session, test_collection, test_case):
        """测试批量更新执行顺序"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        # 创建多条记录
        details = []
        for i in range(3):
            detail = ApiCollectionDetail(
                collection_info_id=test_collection.id,
                case_info_id=test_case.id,
                run_order=i + 1,
                create_time=datetime.now()
            )
            session.add(detail)
            session.commit()
            session.refresh(detail)
            details.append(detail)
        
        # 更新顺序
        update_data = [
            {"id": details[0].id, "run_order": 3},
            {"id": details[1].id, "run_order": 1},
            {"id": details[2].id, "run_order": 2}
        ]
        
        response = client.post("/ApiCollectionDetail/batchUpdateOrder", json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_batch_update_order_partial(self, client: TestClient, session: Session, test_collection, test_case):
        """测试批量更新顺序 - 部分更新"""
        from apitest.model.ApiCollectionDetailModel import ApiCollectionDetail
        
        detail = ApiCollectionDetail(
            collection_info_id=test_collection.id,
            case_info_id=test_case.id,
            run_order=1,
            create_time=datetime.now()
        )
        session.add(detail)
        session.commit()
        session.refresh(detail)
        
        # 只更新存在的记录
        update_data = [
            {"id": detail.id, "run_order": 10},
            {"id": 99999, "run_order": 20}  # 不存在的ID
        ]
        
        response = client.post("/ApiCollectionDetail/batchUpdateOrder", json=update_data)
        assert response.status_code == 200
    
    def test_batch_update_order_empty(self, client: TestClient):
        """测试批量更新顺序 - 空列表"""
        response = client.post("/ApiCollectionDetail/batchUpdateOrder", json=[])
        assert response.status_code == 200
        assert response.json()["code"] == 200
