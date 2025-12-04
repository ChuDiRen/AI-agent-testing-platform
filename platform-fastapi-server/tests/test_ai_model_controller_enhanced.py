"""
AiModelController AI模型管理模块增强单元测试
覆盖所有接口: queryByPage, queryById, queryEnabled, insert, update, delete, toggleStatus, testConnection
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, MagicMock


class TestAiModelController:
    """AI模型控制器增强测试类"""

    def test_query_by_page_success(self, client: TestClient, session: Session, admin_headers):
        """测试分页查询AI模型成功"""
        from aiassistant.model.AiModel import AiModel

        # 创建测试模型
        model = AiModel(
            model_name="GPT-4",
            model_code="gpt-4",
            api_key="test-api-key",
            api_url="https://api.openai.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        response = client.post("/AiModel/queryByPage",
            json={"page": 1, "pageSize": 10},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        assert "total" in data["data"]
        assert len(data["data"]["list"]) >= 1

    def test_query_by_id_success(self, client: TestClient, session: Session, admin_headers):
        """测试根据ID查询AI模型成功"""
        from aiassistant.model.AiModel import AiModel

        model = AiModel(
            model_name="Claude-3",
            model_code="claude-3",
            api_key="test-api-key",
            api_url="https://api.anthropic.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        response = client.get(f"/AiModel/queryById?id={model.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["id"] == model.id
        assert data["data"]["model_name"] == "Claude-3"

    def test_query_by_id_not_found(self, client: TestClient, admin_headers):
        """测试查询不存在的AI模型ID"""
        response = client.get("/AiModel/queryById?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "没有数据" in data["msg"]

    def test_query_enabled_success(self, client: TestClient, session: Session):
        """测试查询所有已启用的模型成功"""
        from aiassistant.model.AiModel import AiModel

        # 创建多个模型，部分启用部分禁用
        models = [
            AiModel(
                model_name="Enabled Model 1",
                model_code="enabled1",
                api_key="key1",
                api_url="https://api1.com",
                is_enabled=True,
                create_time=datetime.now()
            ),
            AiModel(
                model_name="Enabled Model 2",
                model_code="enabled2",
                api_key="key2",
                api_url="https://api2.com",
                is_enabled=True,
                create_time=datetime.now()
            ),
            AiModel(
                model_name="Disabled Model",
                model_code="disabled1",
                api_key="key3",
                api_url="https://api3.com",
                is_enabled=False,
                create_time=datetime.now()
            )
        ]

        for model in models:
            session.add(model)
        session.commit()

        response = client.get("/AiModel/queryEnabled")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "list" in data["data"]
        # 应该只返回启用的模型
        for model in data["data"]["list"]:
            assert model["is_enabled"] is True

    def test_insert_model_success(self, client: TestClient, admin_headers):
        """测试新增AI模型成功"""
        model_data = {
            "model_name": "New AI Model",
            "model_code": "new-ai-model",
            "api_key": "new-api-key",
            "api_url": "https://api.new-ai.com",
            "is_enabled": True,
            "model_type": "chat",
            "max_tokens": 4096,
            "temperature": 0.7,
            "remark": "新创建的AI模型"
        }

        response = client.post("/AiModel/insert",
            json=model_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
        assert data["data"]["model_name"] == "New AI Model"

    def test_update_model_success(self, client: TestClient, session: Session, admin_headers):
        """测试更新AI模型成功"""
        from aiassistant.model.AiModel import AiModel

        # 先创建模型
        model = AiModel(
            model_name="Old Model",
            model_code="old-model",
            api_key="old-key",
            api_url="https://api.old.com",
            is_enabled=False,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        # 更新模型
        update_data = {
            "id": model.id,
            "model_name": "Updated Model",
            "api_url": "https://api.updated.com",
            "is_enabled": True,
            "max_tokens": 8192,
            "temperature": 0.5
        }

        response = client.put("/AiModel/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_update_model_not_found(self, client: TestClient, admin_headers):
        """测试更新不存在的AI模型"""
        update_data = {
            "id": 99999,
            "model_name": "Nonexistent Model",
            "api_url": "https://api.nonexistent.com"
        }

        response = client.put("/AiModel/update",
            json=update_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_delete_model_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除AI模型成功"""
        from aiassistant.model.AiModel import AiModel

        model = AiModel(
            model_name="Delete Model",
            model_code="delete-model",
            api_key="delete-key",
            api_url="https://api.delete.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        response = client.delete(f"/AiModel/delete?id={model.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_model_not_found(self, client: TestClient, admin_headers):
        """测试删除不存在的AI模型"""
        response = client.delete("/AiModel/delete?id=99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_toggle_status_enable(self, client: TestClient, session: Session, admin_headers):
        """测试启用模型状态切换成功"""
        from aiassistant.model.AiModel import AiModel

        # 创建禁用的模型
        model = AiModel(
            model_name="Disabled Model",
            model_code="disabled-model",
            api_key="test-key",
            api_url="https://api.test.com",
            is_enabled=False,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        toggle_data = {
            "id": model.id,
            "is_enabled": True
        }

        response = client.post("/AiModel/toggleStatus",
            json=toggle_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_toggle_status_disable(self, client: TestClient, session: Session, admin_headers):
        """测试禁用模型状态切换成功"""
        from aiassistant.model.AiModel import AiModel

        # 创建启用的模型
        model = AiModel(
            model_name="Enabled Model",
            model_code="enabled-model",
            api_key="test-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        toggle_data = {
            "id": model.id,
            "is_enabled": False
        }

        response = client.post("/AiModel/toggleStatus",
            json=toggle_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_toggle_status_not_found(self, client: TestClient, admin_headers):
        """测试切换不存在模型的状态"""
        toggle_data = {
            "id": 99999,
            "is_enabled": True
        }

        response = client.post("/AiModel/toggleStatus",
            json=toggle_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    @patch('requests.post')
    def test_connection_success(self, mock_post, client: TestClient, session: Session, admin_headers):
        """测试模型API连接成功"""
        from aiassistant.model.AiModel import AiModel

        # 创建测试模型
        model = AiModel(
            model_name="Test Model",
            model_code="test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        # 模拟成功的API响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        connection_data = {
            "id": model.id
        }

        response = client.post("/AiModel/testConnection",
            json=connection_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    @patch('requests.post')
    def test_connection_failure(self, mock_post, client: TestClient, session: Session, admin_headers):
        """测试模型API连接失败"""
        from aiassistant.model.AiModel import AiModel

        model = AiModel(
            model_name="Failed Model",
            model_code="failed-model",
            api_key="test-api-key",
            api_url="https://api.failed.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()

        # 模拟失败的API响应
        mock_post.side_effect = Exception("Connection failed")

        connection_data = {
            "id": model.id
        }

        response = client.post("/AiModel/testConnection",
            json=connection_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "失败" in data["msg"]

    def test_connection_model_not_found(self, client: TestClient, admin_headers):
        """测试连接不存在的模型"""
        connection_data = {
            "id": 99999
        }

        response = client.post("/AiModel/testConnection",
            json=connection_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.post("/AiModel/queryByPage",
            json={"page": 1, "pageSize": 10}
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]

    def test_unauthorized_status_toggle(self, client: TestClient):
        """测试未授权的状态切换"""
        toggle_data = {
            "id": 1,
            "is_enabled": True
        }

        response = client.post("/AiModel/toggleStatus",
            json=toggle_data
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]

    def test_unauthorized_connection_test(self, client: TestClient):
        """测试未授权的连接测试"""
        connection_data = {
            "id": 1
        }

        response = client.post("/AiModel/testConnection",
            json=connection_data
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]


class TestAiModelControllerIntegration:
    """AI模型管理集成测试"""

    def test_full_model_lifecycle(self, client: TestClient, session: Session, admin_headers):
        """测试完整的模型生命周期"""
        from aiassistant.model.AiModel import AiModel

        # 1. 创建模型
        model_data = {
            "model_name": "Lifecycle Model",
            "model_code": "lifecycle-model",
            "api_key": "lifecycle-key",
            "api_url": "https://api.lifecycle.com",
            "is_enabled": False,
            "max_tokens": 2048,
            "temperature": 0.6
        }

        response = client.post("/AiModel/insert",
            json=model_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        model_id = response.json()["data"]["id"]

        # 2. 查询模型详情
        response = client.get(f"/AiModel/queryById?id={model_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["data"]["model_name"] == "Lifecycle Model"

        # 3. 测试连接（模拟）
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_post.return_value = mock_response

            response = client.post("/AiModel/testConnection",
                json={"id": model_id},
                headers=admin_headers
            )
            assert response.status_code == 200

        # 4. 启用模型
        response = client.post("/AiModel/toggleStatus",
            json={"id": model_id, "is_enabled": True},
            headers=admin_headers
        )
        assert response.status_code == 200

        # 5. 验证模型在启用列表中
        response = client.get("/AiModel/queryEnabled")
        assert response.status_code == 200
        enabled_models = response.json()["data"]["list"]
        assert any(model["id"] == model_id for model in enabled_models)

        # 6. 更新模型
        update_data = {
            "id": model_id,
            "model_name": "Updated Lifecycle Model",
            "max_tokens": 4096
        }
        response = client.put("/AiModel/update",
            json=update_data,
            headers=admin_headers
        )
        assert response.status_code == 200

        # 7. 禁用模型
        response = client.post("/AiModel/toggleStatus",
            json={"id": model_id, "is_enabled": False},
            headers=admin_headers
        )
        assert response.status_code == 200

        # 8. 删除模型
        response = client.delete(f"/AiModel/delete?id={model_id}",
            headers=admin_headers
        )
        assert response.status_code == 200

        # 9. 验证模型已删除
        response = client.get(f"/AiModel/queryById?id={model_id}",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert "没有数据" in response.json()["msg"]

    def test_multiple_models_status_management(self, client: TestClient, session: Session, admin_headers):
        """测试多个模型的状态管理"""
        from aiassistant.model.AiModel import AiModel

        # 创建多个模型
        models = []
        for i in range(5):
            model = AiModel(
                model_name=f"Model {i+1}",
                model_code=f"model-{i+1}",
                api_key=f"key-{i+1}",
                api_url=f"https://api{i+1}.com",
                is_enabled=False,  # 初始都禁用
                create_time=datetime.now()
            )
            session.add(model)
            models.append(model)
        session.commit()

        # 启用部分模型
        for i in range(0, 3):  # 启用前3个
            response = client.post("/AiModel/toggleStatus",
                json={"id": models[i].id, "is_enabled": True},
                headers=admin_headers
            )
            assert response.status_code == 200

        # 验证启用模型数量
        response = client.get("/AiModel/queryEnabled")
        assert response.status_code == 200
        enabled_models = response.json()["data"]["list"]
        assert len(enabled_models) == 3

        # 禁用部分模型
        for i in range(1, 3):  # 禁用第2、3个
            response = client.post("/AiModel/toggleStatus",
                json={"id": models[i].id, "is_enabled": False},
                headers=admin_headers
            )
            assert response.status_code == 200

        # 验证最终启用模型数量
        response = client.get("/AiModel/queryEnabled")
        assert response.status_code == 200
        enabled_models = response.json()["data"]["list"]
        assert len(enabled_models) == 1
        assert enabled_models[0]["model_name"] == "Model 1"

    def test_model_connection_batch_test(self, client: TestClient, session: Session, admin_headers):
        """测试批量模型连接测试"""
        from aiassistant.model.AiModel import AiModel

        # 创建多个模型
        models = []
        for i in range(3):
            model = AiModel(
                model_name=f"Test Model {i+1}",
                model_code=f"test-model-{i+1}",
                api_key=f"test-key-{i+1}",
                api_url=f"https://test-api{i+1}.com",
                is_enabled=True,
                create_time=datetime.now()
            )
            session.add(model)
            models.append(model)
        session.commit()

        # 批量测试连接
        with patch('requests.post') as mock_post:
            # 模拟前两个成功，第三个失败
            def side_effect(*args, **kwargs):
                response = MagicMock()
                if "test-api3.com" in args[0]:
                    response.status_code = 500
                    response.json.return_value = {"error": "Internal error"}
                    raise Exception("Connection failed")
                else:
                    response.status_code = 200
                    response.json.return_value = {"status": "ok"}
                return response

            mock_post.side_effect = side_effect

            # 测试每个模型
            results = []
            for model in models:
                response = client.post("/AiModel/testConnection",
                    json={"id": model.id},
                    headers=admin_headers
                )
                results.append(response.status_code == 200)

            # 应该有2个成功，1个失败
            assert sum(results) == 2