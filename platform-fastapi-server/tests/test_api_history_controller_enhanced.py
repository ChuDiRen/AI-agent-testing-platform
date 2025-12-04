"""
ApiHistoryController API测试历史管理模块增强单元测试
覆盖所有接口: queryByPage, queryById, execute, status, delete, queryByPlanId, queryByExecutionUuid
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, MagicMock


class TestApiHistoryController:
    """API测试历史控制器增强测试类"""

    def test_query_by_page_success(self, client: TestClient, session: Session, admin_headers):
        """测试分页查询API测试历史成功"""
        from apitest.model.ApiHistoryModel import ApiHistory

        # 创建测试历史记录
        history = ApiHistory(
            api_info_id=1,
            project_id=1,
            test_name="测试执行1",
            test_status="success",
            request_url="https://api.example.com/test1",
            request_method="GET",
            status_code=200,
            response_time=150,
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        session.add(history)
        session.commit()

        response = client.post("/ApiHistory/queryByPage",
            json={"page": 1, "pageSize": 10},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["list"]) >= 1

    def test_query_by_page_with_filters(self, client: TestClient, session: Session, admin_headers):
        """测试带过滤条件的分页查询"""
        from apitest.model.ApiHistoryModel import ApiHistory

        # 创建多个不同状态的历史记录
        histories = [
            ApiHistory(
                api_info_id=1,
                project_id=1,
                test_name="成功测试",
                test_status="success",
                request_url="https://api.example.com/success",
                request_method="GET",
                status_code=200,
                create_time=datetime.now()
            ),
            ApiHistory(
                api_info_id=2,
                project_id=2,
                test_name="失败测试",
                test_status="failed",
                request_url="https://api.example.com/failed",
                request_method="POST",
                status_code=500,
                create_time=datetime.now()
            )
        ]

        for history in histories:
            session.add(history)
        session.commit()

        # 按项目ID过滤
        response = client.post("/ApiHistory/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "project_id": 1
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        # 验证返回的都是项目ID为1的记录
        for item in data["data"]["list"]:
            assert item["project_id"] == 1

        # 按测试状态过滤
        response = client.post("/ApiHistory/queryByPage",
            json={
                "page": 1,
                "pageSize": 10,
                "test_status": "success"
            },
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        if len(data["data"]["list"]) > 0:
            for item in data["data"]["list"]:
                assert item["test_status"] == "success"

    def test_query_by_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据ID查询API测试历史成功"""
        from apitest.model.ApiHistoryModel import ApiHistory

        history = ApiHistory(
            api_info_id=1,
            project_id=1,
            test_name="单个查询测试",
            test_status="success",
            request_url="https://api.example.com/single",
            request_method="GET",
            status_code=200,
            response_time=200,
            create_time=datetime.now()
        )
        session.add(history)
        session.commit()

        response = client.get(f"/ApiHistory/queryById?id={history.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == history.id
        assert data["data"]["test_name"] == "单个查询测试"
        assert data["data"]["test_status"] == "success"

    def test_query_by_id_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的测试历史ID"""
        response = client.get("/ApiHistory/queryById?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]

    @patch('apitest.api.ApiHistoryController.subprocess.run')
    def test_execute_test_success(self, mock_subprocess, client: TestClient, session: Session, admin_headers):
        """测试执行API接口测试成功"""
        from apitest.model.ApiHistoryModel import ApiHistory
        from apitest.model.ApiInfoModel import ApiInfo

        # 先创建API接口信息
        api_info = ApiInfo(
            project_id=1,
            api_name="测试接口",
            request_method="GET",
            request_url="https://api.example.com/test",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()

        # 模拟subprocess执行成功
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "测试执行成功"
        mock_subprocess.return_value = mock_result

        execute_request = {
            "api_info_id": api_info.id,
            "test_name": "执行测试用例",
            "environment": "test"
        }

        response = client.post("/ApiHistory/execute",
            json=execute_request,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "test_id" in data["data"]
        assert data["data"]["status"] == "running"

    def test_execute_test_api_not_found(self, client: TestClient, admin_headers):
        """测试执行不存在的API接口测试"""
        execute_request = {
            "api_info_id": 99999,
            "test_name": "不存在的接口测试",
            "environment": "test"
        }

        response = client.post("/ApiHistory/execute",
            json=execute_request,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        # 应该创建测试记录但执行时会出错

    def test_get_test_status_success(self, client: TestClient, session: Session, admin_headers):
        """测试查询API测试状态成功"""
        from apitest.model.ApiHistoryModel import ApiHistory

        history = ApiHistory(
            api_info_id=1,
            project_id=1,
            test_name="状态查询测试",
            test_status="success",
            request_url="https://api.example.com/status",
            request_method="GET",
            status_code=200,
            response_time=180,
            create_time=datetime.now(),
            finish_time=datetime.now()
        )
        session.add(history)
        session.commit()

        response = client.get(f"/ApiHistory/status?test_id={history.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["test_id"] == history.id
        assert data["data"]["status"] == "success"
        assert data["data"]["response_time"] == 180
        assert data["data"]["status_code"] == 200

    def test_get_test_status_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的测试状态"""
        response = client.get("/ApiHistory/status?test_id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_get_test_status_running(self, client: TestClient, session: Session, admin_headers):
        """测试查询运行中的测试状态"""
        from apitest.model.ApiHistoryModel import ApiHistory

        history = ApiHistory(
            api_info_id=1,
            project_id=1,
            test_name="运行中测试",
            test_status="running",
            request_url="https://api.example.com/running",
            request_method="POST",
            create_time=datetime.now()
            # 不设置finish_time，表示还在运行
        )
        session.add(history)
        session.commit()

        response = client.get(f"/ApiHistory/status?test_id={history.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["status"] == "running"
        assert data["data"]["response_time"] is None

    def test_delete_history_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除API测试历史成功"""
        from apitest.model.ApiHistoryModel import ApiHistory

        history = ApiHistory(
            api_info_id=1,
            project_id=1,
            test_name="待删除测试",
            test_status="success",
            request_url="https://api.example.com/delete",
            request_method="DELETE",
            status_code=200,
            create_time=datetime.now()
        )
        session.add(history)
        session.commit()

        response = client.delete(f"/ApiHistory/delete?id={history.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_history_not_found(self, client: TestClient, admin_headers):
        """测试删除不存在的测试历史"""
        response = client.delete("/ApiHistory/delete?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_query_by_plan_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据测试计划ID查询历史记录成功"""
        from apitest.model.ApiHistoryModel import ApiHistory

        # 创建多个属于同一测试计划的历史记录
        histories = [
            ApiHistory(
                api_info_id=1,
                project_id=1,
                plan_id=100,
                test_name="计划测试1",
                test_status="success",
                request_url="https://api.example.com/plan1",
                request_method="GET",
                status_code=200,
                create_time=datetime.now(),
                finish_time=datetime.now()
            ),
            ApiHistory(
                api_info_id=2,
                project_id=1,
                plan_id=100,
                test_name="计划测试2",
                test_status="success",
                request_url="https://api.example.com/plan2",
                request_method="POST",
                status_code=201,
                create_time=datetime.now(),
                finish_time=datetime.now()
            ),
            ApiHistory(
                api_info_id=3,
                project_id=1,
                plan_id=200,  # 不同的计划ID
                test_name="其他计划测试",
                test_status="success",
                request_url="https://api.example.com/other",
                request_method="PUT",
                status_code=200,
                create_time=datetime.now(),
                finish_time=datetime.now()
            )
        ]

        for history in histories:
            session.add(history)
        session.commit()

        response = client.get("/ApiHistory/queryByPlanId?plan_id=100",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)
        # 验证返回的都是plan_id为100的记录
        for item in data["data"]:
            assert item["plan_id"] == 100

    def test_query_by_execution_uuid_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据批量执行UUID查询历史记录成功"""
        from apitest.model.ApiHistoryModel import ApiHistory

        execution_uuid = "test-uuid-12345"

        # 创建多个属于同一批次执行的历史记录
        histories = [
            ApiHistory(
                api_info_id=1,
                project_id=1,
                execution_uuid=execution_uuid,
                test_name="批量测试1",
                test_status="success",
                request_url="https://api.example.com/batch1",
                request_method="GET",
                status_code=200,
                create_time=datetime.now(),
                finish_time=datetime.now()
            ),
            ApiHistory(
                api_info_id=2,
                project_id=1,
                execution_uuid=execution_uuid,
                test_name="批量测试2",
                test_status="failed",
                request_url="https://api.example.com/batch2",
                request_method="POST",
                status_code=500,
                create_time=datetime.now(),
                finish_time=datetime.now()
            ),
            ApiHistory(
                api_info_id=3,
                project_id=1,
                execution_uuid="other-uuid",  # 不同的UUID
                test_name="其他批量测试",
                test_status="success",
                request_url="https://api.example.com/other",
                request_method="PUT",
                status_code=200,
                create_time=datetime.now(),
                finish_time=datetime.now()
            )
        ]

        for history in histories:
            session.add(history)
        session.commit()

        response = client.get(f"/ApiHistory/queryByExecutionUuid?execution_uuid={execution_uuid}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)
        # 验证返回的都是指定execution_uuid的记录
        for item in data["data"]:
            assert item["execution_uuid"] == execution_uuid

    def test_query_by_execution_uuid_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的执行UUID"""
        response = client.get("/ApiHistory/queryByExecutionUuid?execution_uuid=nonexistent-uuid",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert isinstance(data["data"], list)
        assert len(data["data"]) == 0

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.post("/ApiHistory/queryByPage",
            json={"page": 1, "pageSize": 10}
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]

    def test_unauthorized_execute(self, client: TestClient):
        """测试未授权执行测试"""
        execute_request = {
            "api_info_id": 1,
            "test_name": "未授权测试",
            "environment": "test"
        }

        response = client.post("/ApiHistory/execute",
            json=execute_request
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]


class TestApiHistoryIntegration:
    """API测试历史集成测试"""

    def test_full_test_execution_workflow(self, client: TestClient, session: Session, admin_headers):
        """测试完整的测试执行工作流程"""
        from apitest.model.ApiHistoryModel import ApiHistory
        from apitest.model.ApiInfoModel import ApiInfo

        # 1. 创建API接口信息
        api_info = ApiInfo(
            project_id=1,
            api_name="完整流程测试接口",
            request_method="GET",
            request_url="https://api.example.com/full-test",
            api_description="用于完整流程测试的接口",
            create_time=datetime.now()
        )
        session.add(api_info)
        session.commit()

        # 2. 执行测试（模拟）
        with patch('apitest.api.ApiHistoryController.subprocess.run') as mock_subprocess:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "测试执行成功"
            mock_subprocess.return_value = mock_result

            execute_request = {
                "api_info_id": api_info.id,
                "test_name": "完整流程测试",
                "environment": "test"
            }

            response = client.post("/ApiHistory/execute",
                json=execute_request,
                headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200
            test_id = data["data"]["test_id"]

            # 3. 查询测试状态
            response = client.get(f"/ApiHistory/status?test_id={test_id}",
                headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

            # 4. 查询测试历史详情
            response = client.get(f"/ApiHistory/queryById?id={test_id}",
                headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200

            # 5. 清理测试记录
            response = client.delete(f"/ApiHistory/delete?id={test_id}",
                headers=admin_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 200