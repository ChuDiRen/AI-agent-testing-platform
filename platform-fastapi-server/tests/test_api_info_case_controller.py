"""
ApiInfoCaseController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from datetime import datetime


class TestApiInfoCaseController:
    """API用例控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, test_case):
        """测试分页查询用例"""
        response = client.post(
            "/ApiInfoCase/queryByPage",
            json={"page": 1, "pageSize": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert data["data"]["total"] >= 1
    
    def test_query_by_id(self, client: TestClient, test_case):
        """测试根据ID查询用例"""
        response = client.get(f"/ApiInfoCase/queryById?id={test_case.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == test_case.id
        assert data["data"]["case_name"] == test_case.case_name
    
    def test_insert(self, client: TestClient, test_project):
        """测试新增用例"""
        new_case = {
            "project_id": test_project.id,
            "case_name": "新测试用例",
            "case_desc": "用于测试的用例",
            "steps": []
        }
        
        response = client.post("/ApiInfoCase/insert", json=new_case)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
    
    def test_insert_with_steps(self, client: TestClient, test_project):
        """测试新增带步骤的用例"""
        new_case = {
            "project_id": test_project.id,
            "case_name": "带步骤的用例",
            "case_desc": "包含测试步骤",
            "steps": [
                {
                    "run_order": 1,
                    "step_desc": "步骤1",
                    "operation_type_id": 1,
                    "keyword_id": 1,
                    "step_data": {}
                }
            ]
        }
        
        response = client.post("/ApiInfoCase/insert", json=new_case)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update(self, client: TestClient, test_case):
        """测试更新用例"""
        update_data = {
            "id": test_case.id,
            "case_name": "更新后的用例名",
            "case_desc": "更新后的描述"
        }
        
        response = client.put("/ApiInfoCase/update", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete(self, client: TestClient, session: Session, test_project):
        """测试删除用例"""
        from apitest.model.ApiInfoCaseModel import ApiInfoCase
        
        case = ApiInfoCase(
            project_id=test_project.id,
            case_name="待删除用例",
            case_desc="测试删除",
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
