"""
ApiInfoCaseStepController 单元测试
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestApiInfoCaseStepController:
    """用例步骤控制器测试类"""
    
    def test_query_by_case_id(self, client: TestClient, test_case):
        """测试根据用例ID查询步骤"""
        response = client.get(f"/ApiInfoCaseStep/queryByCaseId?case_info_id={test_case.id}")
        assert response.status_code == 200
        assert response.json()["code"] == 200
    
    def test_insert(self, client: TestClient, test_case):
        """测试新增步骤"""
        data = {
            "case_info_id": test_case.id,
            "run_order": 1,
            "step_desc": "测试步骤"
        }
        response = client.post("/ApiInfoCaseStep/insert", json=data)
        assert response.status_code == 200
    
    def test_update(self, client: TestClient, session: Session, test_case):
        """测试更新步骤"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        step = ApiInfoCaseStep(case_info_id=test_case.id, run_order=1, step_desc="test")
        session.add(step)
        session.commit()
        session.refresh(step)
        
        response = client.put("/ApiInfoCaseStep/update", json={"id": step.id, "step_desc": "updated"})
        assert response.status_code == 200
    
    def test_delete(self, client: TestClient, session: Session, test_case):
        """测试删除步骤"""
        from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
        step = ApiInfoCaseStep(case_info_id=test_case.id, run_order=1, step_desc="test")
        session.add(step)
        session.commit()
        session.refresh(step)
        
        response = client.delete(f"/ApiInfoCaseStep/delete?id={step.id}")
        assert response.status_code == 200
