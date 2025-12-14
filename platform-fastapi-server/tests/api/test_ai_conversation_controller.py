"""
AI对话管理 API 接口测试
接口清单:
- POST /AiConversation/create - 创建AI对话会话
- GET /AiConversation/list - 获取用户对话列表
- GET /AiConversation/{conversation_id}/messages - 获取对话的所有消息
- POST /AiConversation/chat - AI流式对话接口(SSE)
- DELETE /AiConversation/{conversation_id} - 删除对话会话
- PUT /AiConversation/{conversation_id}/title - 更新对话标题
"""
import pytest
from datetime import datetime
from tests.conftest import APIClient, API_BASE_URL


class TestAiConversationAPI:
    """AI对话管理接口测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient(base_url=API_BASE_URL)
        self.client.login()
        self.created_ids = []
        yield
        for conv_id in self.created_ids:
            try:
                self.client.delete(f"/AiConversation/{conv_id}")
            except:
                pass
        self.client.close()
    
    def _get_enabled_model_id(self):
        """获取一个已启用的AI模型ID"""
        response = self.client.get("/AiModel/queryEnabled")
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data and len(data) > 0:
                return data[0].get("id")
        return None
    
    def _create_test_conversation(self, model_id=None):
        """创建测试对话"""
        if not model_id:
            model_id = self._get_enabled_model_id()
        if not model_id:
            return None
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        response = self.client.post("/AiConversation/create", json={
            "model_id": model_id,
            "session_title": f"测试对话_{unique}",
            "test_type": "API"
        })
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "id" in data:
                conv_id = data.get("id")
                if conv_id:
                    self.created_ids.append(conv_id)
                return conv_id
        return None
    
    # ==================== POST /AiConversation/create 创建对话测试 ====================
    
    def test_create_conversation_success(self):
        """创建对话 - 正常请求"""
        model_id = self._get_enabled_model_id()
        if model_id:
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            response = self.client.post("/AiConversation/create", json={
                "model_id": model_id,
                "session_title": f"测试对话_{unique}",
                "test_type": "API"
            })
            assert response.status_code == 200
            data = response.json()
            if isinstance(data, dict) and "id" in data:
                self.created_ids.append(data["id"])
                assert data["id"] > 0
    
    def test_create_conversation_invalid_model(self):
        """创建对话 - 无效模型ID"""
        response = self.client.post("/AiConversation/create", json={
            "model_id": 99999,
            "session_title": "测试对话",
            "test_type": "API"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == -1 or "不存在" in data.get("msg", "") or "禁用" in data.get("msg", "")
    
    def test_create_conversation_missing_model_id(self):
        """创建对话 - 缺少模型ID"""
        response = self.client.post("/AiConversation/create", json={
            "session_title": "测试对话"
        })
        assert response.status_code == 422
    
    def test_create_conversation_unauthorized(self):
        """创建对话 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.post("/AiConversation/create", json={
            "model_id": 1,
            "session_title": "测试"
        })
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /AiConversation/list 获取对话列表测试 ====================
    
    def test_list_conversations_success(self):
        """获取对话列表 - 正常请求"""
        response = self.client.get("/AiConversation/list")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data or "items" in data
    
    def test_list_conversations_with_pagination(self):
        """获取对话列表 - 带分页参数"""
        response = self.client.get("/AiConversation/list", params={
            "page": 1,
            "page_size": 10
        })
        assert response.status_code == 200
        data = response.json()
        assert "total" in data or "items" in data
    
    def test_list_conversations_page_2(self):
        """获取对话列表 - 第二页"""
        response = self.client.get("/AiConversation/list", params={
            "page": 2,
            "page_size": 5
        })
        assert response.status_code == 200
    
    def test_list_conversations_unauthorized(self):
        """获取对话列表 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.get("/AiConversation/list")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== GET /AiConversation/{id}/messages 获取消息测试 ====================
    
    def test_get_messages_success(self):
        """获取对话消息 - 正常请求"""
        conv_id = self._create_test_conversation()
        if conv_id:
            response = self.client.get(f"/AiConversation/{conv_id}/messages")
            assert response.status_code == 200
            data = response.json()
            assert "data" in data
    
    def test_get_messages_not_exist(self):
        """获取对话消息 - 对话不存在"""
        response = self.client.get("/AiConversation/99999/messages")
        assert response.status_code == 200
        data = response.json()
        # 不存在的对话应返回空列表或错误
        assert "data" in data or data.get("code") == -1
    
    def test_get_messages_invalid_id(self):
        """获取对话消息 - 无效ID"""
        response = self.client.get("/AiConversation/abc/messages")
        assert response.status_code == 422
    
    # ==================== DELETE /AiConversation/{id} 删除对话测试 ====================
    
    def test_delete_conversation_success(self):
        """删除对话 - 正常请求"""
        conv_id = self._create_test_conversation()
        if conv_id:
            self.created_ids.remove(conv_id)
            response = self.client.delete(f"/AiConversation/{conv_id}")
            assert response.status_code == 200
            data = response.json()
            assert data.get("code") == 200 or "成功" in data.get("msg", "")
    
    def test_delete_conversation_not_exist(self):
        """删除对话 - 对话不存在"""
        response = self.client.delete("/AiConversation/99999")
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == -1 or "不存在" in data.get("msg", "")
    
    def test_delete_conversation_invalid_id(self):
        """删除对话 - 无效ID"""
        response = self.client.delete("/AiConversation/abc")
        assert response.status_code == 422
    
    def test_delete_conversation_unauthorized(self):
        """删除对话 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.delete("/AiConversation/1")
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== PUT /AiConversation/{id}/title 更新标题测试 ====================
    
    def test_update_title_success(self):
        """更新对话标题 - 正常请求"""
        conv_id = self._create_test_conversation()
        if conv_id:
            response = self.client.put(f"/AiConversation/{conv_id}/title", params={
                "title": "更新后的标题"
            })
            assert response.status_code == 200
            data = response.json()
            if "session_title" in data:
                assert data["session_title"] == "更新后的标题"
    
    def test_update_title_not_exist(self):
        """更新对话标题 - 对话不存在"""
        response = self.client.put("/AiConversation/99999/title", params={
            "title": "测试标题"
        })
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == -1 or "不存在" in data.get("msg", "")
    
    def test_update_title_missing_param(self):
        """更新对话标题 - 缺少标题参数"""
        conv_id = self._create_test_conversation()
        if conv_id:
            response = self.client.put(f"/AiConversation/{conv_id}/title")
            assert response.status_code == 422
    
    def test_update_title_empty(self):
        """更新对话标题 - 空标题"""
        conv_id = self._create_test_conversation()
        if conv_id:
            response = self.client.put(f"/AiConversation/{conv_id}/title", params={
                "title": ""
            })
            # 空标题可能被拒绝或接受
            assert response.status_code in [200, 422]
    
    def test_update_title_too_long(self):
        """更新对话标题 - 标题过长"""
        conv_id = self._create_test_conversation()
        if conv_id:
            long_title = "a" * 300  # 超过200字符限制
            response = self.client.put(f"/AiConversation/{conv_id}/title", params={
                "title": long_title
            })
            assert response.status_code == 422
    
    def test_update_title_unauthorized(self):
        """更新对话标题 - 未授权"""
        client = APIClient(base_url=API_BASE_URL)
        response = client.put("/AiConversation/1/title", params={"title": "test"})
        assert response.status_code in [401, 403] or response.json().get("code") != 200
        client.close()
    
    # ==================== POST /AiConversation/chat 流式对话测试 ====================
    # 注意：SSE流式接口测试需要特殊处理，这里只测试基本请求
    
    def test_chat_missing_conversation_id(self):
        """流式对话 - 缺少对话ID"""
        response = self.client.post("/AiConversation/chat", json={
            "user_message": "测试消息"
        })
        assert response.status_code == 422
    
    def test_chat_missing_message(self):
        """流式对话 - 缺少消息内容"""
        conv_id = self._create_test_conversation()
        if conv_id:
            response = self.client.post("/AiConversation/chat", json={
                "conversation_id": conv_id
            })
            assert response.status_code == 422
    
    def test_chat_invalid_conversation(self):
        """流式对话 - 无效对话ID"""
        model_id = self._get_enabled_model_id()
        if model_id:
            response = self.client.post("/AiConversation/chat", json={
                "conversation_id": 99999,
                "model_id": model_id,
                "user_message": "测试消息"
            })
            # SSE接口可能返回200但内容包含错误
            assert response.status_code in [200, 400, 404]
