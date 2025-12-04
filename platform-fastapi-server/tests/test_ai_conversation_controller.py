"""
AiConversationController AI对话模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestAiConversationController:
    """AI对话控制器测试类"""
    
    def test_create_conversation(self, client: TestClient, session: Session):
        """测试创建对话会话"""
        from aiassistant.model.AiModel import AiModel
        
        model = AiModel(
            model_name="对话测试模型",
            model_code="conversation_model",
            provider="openai",
            api_key="test_key",
            is_enabled=True,
            create_time=datetime.now()
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        
        response = client.post("/AiConversation/create", json={
            "model_id": model.id,
            "session_title": "测试对话",
            "test_type": "API"
        })
        
        assert response.status_code == 200
    
    def test_create_conversation_model_not_found(self, client: TestClient):
        """测试创建对话时模型不存在"""
        response = client.post("/AiConversation/create", json={
            "model_id": 99999,
            "session_title": "测试对话",
            "test_type": "API"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_list_conversations(self, client: TestClient, session: Session):
        """测试获取对话列表"""
        from aiassistant.model.AiConversation import AiConversation
        
        conversation = AiConversation(
            user_id=1,
            session_title="列表测试对话",
            model_id=1,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()
        
        response = client.get("/AiConversation/list?page=1&page_size=10")
        
        assert response.status_code == 200
    
    def test_get_messages(self, client: TestClient, session: Session):
        """测试获取对话消息"""
        from aiassistant.model.AiConversation import AiConversation
        from aiassistant.model.AiMessage import AiMessage
        
        conversation = AiConversation(
            user_id=1,
            session_title="消息测试对话",
            model_id=1,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        message = AiMessage(
            conversation_id=conversation.id,
            role="user",
            content="测试消息",
            message_type="text",
            create_time=datetime.now()
        )
        session.add(message)
        session.commit()
        
        response = client.get(f"/AiConversation/{conversation.id}/messages")
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
    
    def test_delete_conversation(self, client: TestClient, session: Session):
        """测试删除对话"""
        from aiassistant.model.AiConversation import AiConversation
        
        conversation = AiConversation(
            user_id=1,
            session_title="待删除对话",
            model_id=1,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        response = client.delete(f"/AiConversation/{conversation.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_conversation_not_found(self, client: TestClient):
        """测试删除不存在的对话"""
        response = client.delete("/AiConversation/99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_update_title(self, client: TestClient, session: Session):
        """测试更新对话标题"""
        from aiassistant.model.AiConversation import AiConversation
        
        conversation = AiConversation(
            user_id=1,
            session_title="原始标题",
            model_id=1,
            test_type="API",
            status="active",
            create_time=datetime.now()
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        
        response = client.put(f"/AiConversation/{conversation.id}/title?title=新标题")
        
        assert response.status_code == 200
    
    def test_update_title_not_found(self, client: TestClient):
        """测试更新不存在对话的标题"""
        response = client.put("/AiConversation/99999/title?title=新标题")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
