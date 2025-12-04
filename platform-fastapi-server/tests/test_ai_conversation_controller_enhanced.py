"""
AiConversationController AI对话模块单元测试
覆盖所有接口: create, list, get_messages, chat, delete, update_title
"""
import pytest
import json
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session
from unittest.mock import patch, AsyncGenerator


class TestAiConversationController:
    """AI对话控制器测试类"""

    def test_create_conversation_success(self, client: TestClient, session: Session, admin_headers):
        """测试创建AI对话会话成功"""
        from aiassistant.model.AiModel import AiModel

        # 先创建启用的AI模型
        ai_model = AiModel(
            model_name="测试模型",
            model_code="test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        conversation_data = {
            "model_id": ai_model.id,
            "session_title": "测试对话会话",
            "test_type": "API",
            "project_id": 1
        }

        response = client.post("/AiConversation/create",
            json=conversation_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
        assert data["data"]["session_title"] == "测试对话会话"
        assert data["data"]["model_id"] == ai_model.id

    def test_create_conversation_model_disabled(self, client: TestClient, session: Session, admin_headers):
        """测试创建对话会话时模型被禁用"""
        from aiassistant.model.AiModel import AiModel

        # 创建禁用的AI模型
        disabled_model = AiModel(
            model_name="禁用模型",
            model_code="disabled-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=False,
            create_time=datetime.now()
        )
        session.add(disabled_model)
        session.commit()

        conversation_data = {
            "model_id": disabled_model.id,
            "session_title": "测试对话会话",
            "test_type": "API"
        }

        response = client.post("/AiConversation/create",
            json=conversation_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在或已禁用" in data["msg"]

    def test_create_conversation_model_not_exist(self, client: TestClient, admin_headers):
        """测试创建对话会话时模型不存在"""
        conversation_data = {
            "model_id": 99999,
            "session_title": "测试对话会话",
            "test_type": "API"
        }

        response = client.post("/AiConversation/create",
            json=conversation_data,
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在或已禁用" in data["msg"]

    def test_list_conversations_success(self, client: TestClient, session: Session, admin_headers):
        """测试获取对话列表成功"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiModel import AiModel

        # 先创建AI模型和对话
        ai_model = AiModel(
            model_name="列表测试模型",
            model_code="list-test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        conversations = [
            AiConversation(
                user_id=1,
                session_title="对话1",
                model_id=ai_model.id,
                test_type="API",
                status="active",
                create_time=datetime.now(),
                update_time=datetime.now()
            ),
            AiConversation(
                user_id=1,
                session_title="对话2",
                model_id=ai_model.id,
                test_type="UI",
                status="active",
                create_time=datetime.now(),
                update_time=datetime.now()
            )
        ]

        for conv in conversations:
            session.add(conv)
        session.commit()

        response = client.get("/AiConversation/list?page=1&page_size=10",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "total" in data["data"]
        assert "items" in data["data"]
        assert len(data["data"]["items"]) >= 2

    def test_list_conversations_with_pagination(self, client: TestClient, session: Session, admin_headers):
        """测试分页获取对话列表"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiModel import AiModel

        ai_model = AiModel(
            model_name="分页测试模型",
            model_code="pagination-test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        # 创建多个对话
        for i in range(5):
            conv = AiConversation(
                user_id=1,
                session_title=f"分页测试对话{i+1}",
                model_id=ai_model.id,
                test_type="API",
                status="active",
                create_time=datetime.now(),
                update_time=datetime.now()
            )
            session.add(conv)
        session.commit()

        # 测试第一页
        response = client.get("/AiConversation/list?page=1&page_size=2",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert len(data["data"]["items"]) <= 2
        assert data["data"]["total"] >= 5

    def test_get_messages_success(self, client: TestClient, session: Session, admin_headers):
        """测试获取对话消息成功"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiMessage import AiMessage
        from aiassistant.model.AiModel import AiModel

        # 创建AI模型和对话
        ai_model = AiModel(
            model_name="消息测试模型",
            model_code="message-test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        conversation = AiConversation(
            user_id=1,
            session_title="消息测试对话",
            model_id=ai_model.id,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()

        # 创建消息
        messages = [
            AiMessage(
                conversation_id=conversation.id,
                role="user",
                content="你好",
                message_type="text",
                create_time=datetime.now()
            ),
            AiMessage(
                conversation_id=conversation.id,
                role="assistant",
                content="你好！有什么可以帮助你的吗？",
                message_type="text",
                create_time=datetime.now()
            )
        ]

        for msg in messages:
            session.add(msg)
        session.commit()

        response = client.get(f"/AiConversation/{conversation.id}/messages",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) >= 2
        assert data["data"][0]["role"] == "user"
        assert data["data"][1]["role"] == "assistant"

    def test_get_messages_conversation_not_exist(self, client: TestClient, admin_headers):
        """测试获取不存在对话的消息"""
        response = client.get("/AiConversation/99999/messages",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) == 0

    @patch('core.AiStreamService.AiStreamService.call_ai_stream')
    async def test_chat_stream_success(self, mock_ai_stream, client: TestClient, session: Session, admin_headers):
        """测试流式对话成功"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiModel import AiModel

        # 创建AI模型和对话
        ai_model = AiModel(
            model_name="对话测试模型",
            model_code="chat-test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        conversation = AiConversation(
            user_id=1,
            session_title="流式对话测试",
            model_id=ai_model.id,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()

        # 模拟AI流式响应
        async def mock_stream_response(model_code, api_key, api_url, messages, temperature, max_tokens):
            yield "你好！"
            yield "我是AI助手"
            yield "有什么可以帮助你的吗？"

        mock_ai_stream.return_value = mock_stream_response("test-model", "test-key", "test-url", [], 0.7, 1000)

        chat_request = {
            "conversation_id": conversation.id,
            "model_id": ai_model.id,
            "user_message": "你好，请介绍一下自己",
            "include_context": False,
            "max_tokens": 1000
        }

        response = client.post("/AiConversation/chat",
            json=chat_request,
            headers=admin_headers,
            headers={"Accept": "text/event-stream"}
        )

        # 流式响应应该返回200状态码
        assert response.status_code == 200

    def test_chat_stream_conversation_not_exist(self, client: TestClient, admin_headers):
        """测试流式对话时对话不存在"""
        chat_request = {
            "conversation_id": 99999,
            "model_id": 1,
            "user_message": "测试消息",
            "include_context": False,
            "max_tokens": 1000
        }

        response = client.post("/AiConversation/chat",
            json=chat_request,
            headers=admin_headers
        )

        # 应该返回流式响应，但包含错误信息
        assert response.status_code == 200

    def test_delete_conversation_success(self, client: TestClient, session: Session, admin_headers):
        """测试删除对话成功"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiModel import AiModel

        # 创建AI模型和对话
        ai_model = AiModel(
            model_name="删除测试模型",
            model_code="delete-test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        conversation = AiConversation(
            user_id=1,
            session_title="待删除对话",
            model_id=ai_model.id,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()

        response = client.delete(f"/AiConversation/{conversation.id}",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]

    def test_delete_conversation_not_exist(self, client: TestClient, admin_headers):
        """测试删除不存在的对话"""
        response = client.delete("/AiConversation/99999",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_update_title_success(self, client: TestClient, session: Session, admin_headers):
        """测试更新对话标题成功"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiModel import AiModel

        # 创建AI模型和对话
        ai_model = AiModel(
            model_name="更新标题测试模型",
            model_code="update-title-test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        conversation = AiConversation(
            user_id=1,
            session_title="原标题",
            model_id=ai_model.id,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()

        response = client.put(f"/AiConversation/{conversation.id}/title?title=新标题",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["session_title"] == "新标题"

    def test_update_title_not_exist(self, client: TestClient, admin_headers):
        """测试更新不存在对话的标题"""
        response = client.put("/AiConversation/99999/title?title=新标题",
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]

    def test_update_title_too_long(self, client: TestClient, session: Session, admin_headers):
        """测试更新标题时标题过长"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiModel import AiModel

        ai_model = AiModel(
            model_name="标题长度测试模型",
            model_code="title-length-test-model",
            api_key="test-api-key",
            api_url="https://api.test.com",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(ai_model)
        session.commit()

        conversation = AiConversation(
            user_id=1,
            session_title="原标题",
            model_id=ai_model.id,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()

        # 创建超过200字符的标题
        long_title = "x" * 201

        response = client.put(f"/AiConversation/{conversation.id}/title?title={long_title}",
            headers=admin_headers
        )

        # 应该返回验证错误
        assert response.status_code == 422

    def test_unauthorized_access(self, client: TestClient):
        """测试未授权访问"""
        response = client.post("/AiConversation/create",
            json={"model_id": 1, "session_title": "测试"}
        )

        # 应该返回401未授权或被重定向
        assert response.status_code in [401, 403, 302]