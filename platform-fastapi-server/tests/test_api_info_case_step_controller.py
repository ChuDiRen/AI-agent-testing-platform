"""
ApiInfoCaseStepController 用例步骤接口测试
测试服务地址: http://127.0.0.1:5000
"""
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiInfoCaseStepController:
    """用例步骤控制器测试类"""
    
    # ==================== 查询接口 ====================
    
    def test_query_by_case_id(self, client: TestClient, test_case):
        """测试根据用例ID查询步骤"""
        response = client.get(f"/ApiInfoCaseStep/queryByCaseId?case_info_id={test_case.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_query_by_case_id_with_data(self, client: TestClient, session: Session, test_case):
        """测试根据用例ID查询 - 有数据"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="测试步骤",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        
        response = client.get(f"/ApiInfoCaseStep/queryByCaseId?case_info_id={test_case.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["list"]) >= 1
    
    def test_query_by_case_id_empty(self, client: TestClient):
        """测试根据用例ID查询 - 空结果"""
        response = client.get("/ApiInfoCaseStep/queryByCaseId?case_info_id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_case_id_order(self, client: TestClient, session: Session, test_case):
        """测试查询结果按run_order排序"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        # 创建多条数据，顺序不同
        for order in [3, 1, 2]:
            step = ApiInfoCaseStep(
                case_info_id=test_case.id,
                run_order=order,
                step_desc=f"步骤{order}",
                create_time=datetime.now()
            )
            session.add(step)
        session.commit()
        
        response = client.get(f"/ApiInfoCaseStep/queryByCaseId?case_info_id={test_case.id}")
        assert response.status_code == 200
        data = response.json()
        # 验证按顺序排列
        orders = [item["run_order"] for item in data["data"]["list"]]
        assert orders == sorted(orders)
    
    # ==================== 新增接口 ====================
    
    def test_insert(self, client: TestClient, test_case):
        """测试新增步骤"""
        data = {
            "case_info_id": test_case.id,
            "run_order": 1,
            "step_desc": "测试步骤"
        }
        response = client.post("/ApiInfoCaseStep/insert", json=data)
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert "id" in result["data"]
    
    def test_insert_with_step_data(self, client: TestClient, test_case):
        """测试新增步骤 - 带步骤数据"""
        data = {
            "case_info_id": test_case.id,
            "run_order": 1,
            "step_desc": "发送POST请求",
            "step_data": {
                "method": "POST",
                "url": "/api/test",
                "headers": {"Content-Type": "application/json"},
                "body": {"key": "value"}
            }
        }
        response = client.post("/ApiInfoCaseStep/insert", json=data)
        assert response.status_code == 200
    
    def test_insert_multiple_steps(self, client: TestClient, test_case):
        """测试新增多个步骤"""
        for i in range(1, 4):
            data = {
                "case_info_id": test_case.id,
                "run_order": i,
                "step_desc": f"步骤{i}"
            }
            response = client.post("/ApiInfoCaseStep/insert", json=data)
            assert response.status_code == 200
    
    def test_insert_missing_case_id(self, client: TestClient):
        """测试新增 - 缺少用例ID"""
        data = {
            "run_order": 1,
            "step_desc": "测试步骤"
        }
        response = client.post("/ApiInfoCaseStep/insert", json=data)
        assert response.status_code == 422
    
    def test_insert_empty_desc(self, client: TestClient, test_case):
        """测试新增 - 空步骤描述"""
        data = {
            "case_info_id": test_case.id,
            "run_order": 1,
            "step_desc": ""
        }
        response = client.post("/ApiInfoCaseStep/insert", json=data)
        # 空描述可能允许或拒绝，取决于业务逻辑
        assert response.status_code in [200, 422]
    
    # ==================== 更新接口 ====================
    
    def test_update(self, client: TestClient, session: Session, test_case):
        """测试更新步骤"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="原始步骤",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        session.refresh(step)
        
        response = client.put("/ApiInfoCaseStep/update", json={
            "id": step.id,
            "step_desc": "更新后的步骤"
        })
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_update_step_data(self, client: TestClient, session: Session, test_case):
        """测试更新步骤数据"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="测试步骤",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        session.refresh(step)
        
        response = client.put("/ApiInfoCaseStep/update", json={
            "id": step.id,
            "step_data": {"method": "GET", "url": "/api/updated"}
        })
        assert response.status_code == 200
    
    def test_update_run_order(self, client: TestClient, session: Session, test_case):
        """测试更新执行顺序"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="测试步骤",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        session.refresh(step)
        
        response = client.put("/ApiInfoCaseStep/update", json={
            "id": step.id,
            "run_order": 10
        })
        assert response.status_code == 200
    
    def test_update_not_found(self, client: TestClient):
        """测试更新 - 步骤不存在"""
        response = client.put("/ApiInfoCaseStep/update", json={
            "id": 99999,
            "step_desc": "不存在的步骤"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    # ==================== 删除接口 ====================
    
    def test_delete(self, client: TestClient, session: Session, test_case):
        """测试删除步骤"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="待删除步骤",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        session.refresh(step)
        
        response = client.delete(f"/ApiInfoCaseStep/delete?id={step.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_delete_not_found(self, client: TestClient):
        """测试删除 - 步骤不存在"""
        response = client.delete("/ApiInfoCaseStep/delete?id=99999")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 500
        assert "不存在" in data["msg"]
    
    def test_delete_verify_removed(self, client: TestClient, session: Session, test_case):
        """测试删除后验证已移除"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="验证删除",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        session.refresh(step)
        step_id = step.id
        
        # 删除
        response = client.delete(f"/ApiInfoCaseStep/delete?id={step_id}")
        assert response.status_code == 200
        
        # 再次删除应该失败
        response = client.delete(f"/ApiInfoCaseStep/delete?id={step_id}")
        assert response.status_code == 200
        assert response.json()["code"] == 500
    
    # ==================== 批量更新顺序接口 ====================
    
    def test_batch_update_order(self, client: TestClient, session: Session, test_case):
        """测试批量更新步骤顺序"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        # 创建多条记录
        steps = []
        for i in range(3):
            step = ApiInfoCaseStep(
                case_info_id=test_case.id,
                run_order=i + 1,
                step_desc=f"步骤{i + 1}",
                create_time=datetime.now()
            )
            session.add(step)
            session.commit()
            session.refresh(step)
            steps.append(step)
        
        # 更新顺序：3->1, 1->2, 2->3
        update_data = [
            {"id": steps[0].id, "run_order": 2},
            {"id": steps[1].id, "run_order": 3},
            {"id": steps[2].id, "run_order": 1}
        ]
        
        response = client.post("/ApiInfoCaseStep/batchUpdateOrder", json=update_data)
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_batch_update_order_single(self, client: TestClient, session: Session, test_case):
        """测试批量更新顺序 - 单条记录"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="单条更新",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        session.refresh(step)
        
        update_data = [{"id": step.id, "run_order": 5}]
        
        response = client.post("/ApiInfoCaseStep/batchUpdateOrder", json=update_data)
        assert response.status_code == 200
    
    def test_batch_update_order_empty(self, client: TestClient):
        """测试批量更新顺序 - 空列表"""
        response = client.post("/ApiInfoCaseStep/batchUpdateOrder", json=[])
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_batch_update_order_partial_invalid(self, client: TestClient, session: Session, test_case):
        """测试批量更新顺序 - 部分ID无效"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        
        step = ApiInfoCaseStep(
            case_info_id=test_case.id,
            run_order=1,
            step_desc="有效步骤",
            create_time=datetime.now()
        )
        session.add(step)
        session.commit()
        session.refresh(step)
        
        update_data = [
            {"id": step.id, "run_order": 10},
            {"id": 99999, "run_order": 20}
        ]
        
        response = client.post("/ApiInfoCaseStep/batchUpdateOrder", json=update_data)
        assert response.status_code == 200
    
    def test_batch_update_order_missing_fields(self, client: TestClient):
        """测试批量更新顺序 - 缺少字段"""
        update_data = [
            {"id": 1},  # 缺少run_order
            {"run_order": 2}  # 缺少id
        ]
        
        response = client.post("/ApiInfoCaseStep/batchUpdateOrder", json=update_data)
        # 缺少字段的记录会被跳过
        assert response.status_code == 200
