"""
ApiInfoCaseController 测试用例管理模块完整单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiInfoCaseController:
    """API测试用例控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, test_case):
        """测试分页查询测试用例"""
        response = client.post("/ApiInfoCase/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_project_filter(self, client: TestClient, test_case, test_project):
        """测试按项目过滤查询"""
        response = client.post("/ApiInfoCase/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "project_id": test_project.id
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, test_case):
        """测试根据ID查询测试用例"""
        response = client.get(f"/ApiInfoCase/queryById?id={test_case.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的测试用例"""
        response = client.get("/ApiInfoCase/queryById?id=99999")
        
        assert response.status_code == 200
    
    def test_insert_case(self, client: TestClient, test_project):
        """测试新增测试用例"""
        response = client.post("/ApiInfoCase/insert", json={
            "project_id": test_project.id,
            "case_name": "新增测试用例",
            "case_desc": "测试描述"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_case(self, client: TestClient, test_case):
        """测试更新测试用例"""
        response = client.put("/ApiInfoCase/update", json={
            "id": test_case.id,
            "case_name": "更新后的用例名",
            "case_desc": "更新后的描述"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_case(self, client: TestClient, session: Session, test_project):
        """测试删除测试用例"""
        from apitest.model.ApiInfoCaseModel import ApiInfoCase
        
        case = ApiInfoCase(
            project_id=test_project.id,
            case_name="待删除用例",
            case_desc="删除测试",
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(case)
        session.commit()
        session.refresh(case)
        
        response = client.delete(f"/ApiInfoCase/delete?id={case.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200


class TestApiInfoCaseStepController:
    """API测试用例步骤控制器测试类"""
    
    def test_query_by_case_id(self, client: TestClient, test_case):
        """测试根据用例ID查询步骤"""
        response = client.get(f"/ApiInfoCaseStep/queryByCaseId?case_id={test_case.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_step(self, client: TestClient, test_case, test_api_info):
        """测试新增测试步骤"""
        response = client.post("/ApiInfoCaseStep/insert", json={
            "case_id": test_case.id,
            "api_id": test_api_info.id,
            "step_name": "测试步骤",
            "step_order": 1
        })
        
        assert response.status_code == 200
    
    def test_batch_insert_steps(self, client: TestClient, test_case, test_api_info):
        """测试批量新增测试步骤"""
        response = client.post("/ApiInfoCaseStep/batchInsert", json={
            "case_id": test_case.id,
            "steps": [
                {"api_id": test_api_info.id, "step_name": "步骤1", "step_order": 1},
                {"api_id": test_api_info.id, "step_name": "步骤2", "step_order": 2}
            ]
        })
        
        assert response.status_code == 200
