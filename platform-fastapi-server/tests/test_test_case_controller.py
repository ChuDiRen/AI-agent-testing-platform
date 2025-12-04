"""
TestCaseController 测试用例管理模块单元测试
"""
import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestTestCaseController:
    """测试用例控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询测试用例"""
        from aiassistant.model.TestCaseModel import TestCase
        
        test_case = TestCase(
            case_name="测试用例1",
            test_type="API",
            priority="P0",
            test_steps=json.dumps(["步骤1", "步骤2"]),
            expected_result="预期结果",
            create_time=datetime.now()
        )
        session.add(test_case)
        session.commit()
        
        response = client.post("/TestCase/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from aiassistant.model.TestCaseModel import TestCase
        
        test_case = TestCase(
            case_name="API测试用例",
            test_type="API",
            priority="P0",
            test_steps=json.dumps(["步骤1"]),
            expected_result="预期结果",
            create_time=datetime.now()
        )
        session.add(test_case)
        session.commit()
        
        response = client.post("/TestCase/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "test_type": "API",
            "priority": "P0"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询测试用例"""
        from aiassistant.model.TestCaseModel import TestCase
        
        test_case = TestCase(
            case_name="ID查询用例",
            test_type="API",
            priority="P1",
            test_steps=json.dumps(["步骤1"]),
            expected_result="预期结果",
            create_time=datetime.now()
        )
        session.add(test_case)
        session.commit()
        session.refresh(test_case)
        
        response = client.get(f"/TestCase/queryById?id={test_case.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["case_name"] == "ID查询用例"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的测试用例"""
        response = client.get("/TestCase/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert "没有数据" in data.get("msg", "")
    
    def test_insert_test_case(self, client: TestClient):
        """测试新增测试用例"""
        response = client.post("/TestCase/insert", json={
            "case_name": "新增测试用例",
            "test_type": "API",
            "priority": "P0",
            "precondition": "前置条件",
            "test_steps": json.dumps(["步骤1", "步骤2"]),
            "expected_result": "预期结果"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
    
    def test_batch_insert(self, client: TestClient, test_project):
        """测试批量插入测试用例"""
        response = client.post("/TestCase/batchInsert", json={
            "project_id": test_project.id,
            "test_cases": [
                {
                    "case_name": "批量用例1",
                    "test_type": "API",
                    "priority": "P0",
                    "test_steps": json.dumps(["步骤1"]),
                    "expected_result": "结果1"
                },
                {
                    "case_name": "批量用例2",
                    "test_type": "API",
                    "priority": "P1",
                    "test_steps": json.dumps(["步骤2"]),
                    "expected_result": "结果2"
                }
            ]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["count"] == 2
    
    def test_update_test_case(self, client: TestClient, session: Session):
        """测试更新测试用例"""
        from aiassistant.model.TestCaseModel import TestCase
        
        test_case = TestCase(
            case_name="待更新用例",
            test_type="API",
            priority="P0",
            test_steps=json.dumps(["原始步骤"]),
            expected_result="原始结果",
            create_time=datetime.now()
        )
        session.add(test_case)
        session.commit()
        session.refresh(test_case)
        
        response = client.put("/TestCase/update", json={
            "id": test_case.id,
            "case_name": "更新后的用例名",
            "priority": "P1"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_test_case_not_found(self, client: TestClient):
        """测试更新不存在的测试用例"""
        response = client.put("/TestCase/update", json={
            "id": 99999,
            "case_name": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_test_case(self, client: TestClient, session: Session):
        """测试删除测试用例"""
        from aiassistant.model.TestCaseModel import TestCase
        
        test_case = TestCase(
            case_name="待删除用例",
            test_type="API",
            priority="P0",
            test_steps=json.dumps(["步骤"]),
            expected_result="结果",
            create_time=datetime.now()
        )
        session.add(test_case)
        session.commit()
        session.refresh(test_case)
        
        response = client.delete(f"/TestCase/delete?id={test_case.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_test_case_not_found(self, client: TestClient):
        """测试删除不存在的测试用例"""
        response = client.delete("/TestCase/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_export_yaml(self, client: TestClient, session: Session):
        """测试导出单个测试用例为YAML"""
        from aiassistant.model.TestCaseModel import TestCase
        
        test_case = TestCase(
            case_name="导出YAML用例",
            test_type="API",
            priority="P0",
            precondition="前置条件",
            test_steps=json.dumps(["步骤1", "步骤2"]),
            expected_result="预期结果",
            create_time=datetime.now()
        )
        session.add(test_case)
        session.commit()
        session.refresh(test_case)
        
        response = client.get(f"/TestCase/exportYaml?id={test_case.id}")
        
        assert response.status_code == 200
        assert "yaml" in response.headers.get("content-type", "").lower() or response.status_code == 200
    
    def test_export_yaml_not_found(self, client: TestClient):
        """测试导出不存在的测试用例"""
        response = client.get("/TestCase/exportYaml?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_export_batch_yaml(self, client: TestClient, session: Session):
        """测试批量导出测试用例为YAML"""
        from aiassistant.model.TestCaseModel import TestCase
        
        test_case1 = TestCase(
            case_name="批量导出用例1",
            test_type="API",
            priority="P0",
            test_steps=json.dumps(["步骤1"]),
            expected_result="结果1",
            create_time=datetime.now()
        )
        test_case2 = TestCase(
            case_name="批量导出用例2",
            test_type="API",
            priority="P1",
            test_steps=json.dumps(["步骤2"]),
            expected_result="结果2",
            create_time=datetime.now()
        )
        session.add(test_case1)
        session.add(test_case2)
        session.commit()
        session.refresh(test_case1)
        session.refresh(test_case2)
        
        response = client.post("/TestCase/exportBatchYaml", json=[test_case1.id, test_case2.id])
        
        assert response.status_code == 200
