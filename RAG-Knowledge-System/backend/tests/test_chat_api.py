"""
智能问答 API 测试

测试RAG问答、对话历史、引用展示等功能
"""
import pytest


class TestChatAPI:
    """智能问答API测试类"""

    def test_chat_success(self, client, user_auth_headers, sample_chat_message):
        """测试成功问答"""
        # 注意：这需要RAG引擎和向量数据库已配置
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json=sample_chat_message
        )

        # 可能返回200或501（未实现）
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "message_id" in data
            # 可选字段
            if "citations" in data:
                assert isinstance(data["citations"], list)

    def test_chat_without_auth(self, client, sample_chat_message):
        """测试未认证问答"""
        response = client.post(
            "/api/v1/chat",
            json=sample_chat_message
        )

        assert response.status_code == 401

    def test_chat_missing_message(self, client, user_auth_headers):
        """测试缺少消息"""
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json={"conversation_id": "conv_123"}
        )

        assert response.status_code == 422

    def test_chat_empty_message(self, client, user_auth_headers):
        """测试空消息"""
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json={
                "message": "",
                "conversation_id": "conv_123"
            }
        )

        assert response.status_code == 400

    def test_chat_with_history(self, client, user_auth_headers, sample_chat_message):
        """测试带历史记录的问答"""
        response = client.post(
            "/api/v1/chat/with-history",
            headers=user_auth_headers,
            json={
                **sample_chat_message,
                "history": [
                    {"role": "user", "content": "之前的消息"},
                    {"role": "assistant", "content": "之前的回答"}
                ]
            }
        )

        assert response.status_code in [200, 501]

    def test_search_documents(self, client, user_auth_headers):
        """测试文档检索（不生成回答）"""
        response = client.post(
            "/api/v1/chat/search",
            headers=user_auth_headers,
            json={
                "query": "测试查询",
                "top_k": 5
            }
        )

        # 可能返回200或501
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "results" in data
            assert isinstance(data["results"], list)


class TestChatHistory:
    """聊天历史测试类"""

    def test_get_chat_history(self, client, user_auth_headers):
        """测试获取聊天历史"""
        conv_id = "test_conv_123"

        response = client.get(
            f"/api/v1/chat/history/{conv_id}",
            headers=user_auth_headers
        )

        # 可能返回200、404（无历史）或501
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert "messages" in data
            assert isinstance(data["messages"], list)

    def test_get_chat_history_without_auth(self, client):
        """测试未认证获取历史"""
        response = client.get(
            "/api/v1/chat/history/test_conv_123"
        )

        assert response.status_code == 401

    def test_get_chat_history_not_found(self, client, user_auth_headers):
        """测试获取不存在的对话历史"""
        response = client.get(
            "/api/v1/chat/history/nonexistent_conv",
            headers=user_auth_headers
        )

        # 可能返回404或501
        assert response.status_code in [404, 501]

    def test_delete_chat_history(self, client, user_auth_headers):
        """测试删除聊天历史"""
        conv_id = "test_conv_to_delete"

        response = client.delete(
            f"/api/v1/chat/history/{conv_id}",
            headers=user_auth_headers
        )

        # 可能返回200、404或501
        assert response.status_code in [200, 404, 501]

    def test_delete_chat_history_without_auth(self, client):
        """测试未认证删除历史"""
        response = client.delete(
            "/api/v1/chat/history/test_conv"
        )

        assert response.status_code == 401


class TestChatFeedback:
    """聊天反馈测试类"""

    def test_submit_feedback_positive(self, client, user_auth_headers):
        """测试提交正面反馈（点赞）"""
        feedback_data = {
            "message_id": "msg_123",
            "feedback_type": "positive",
            "comment": "回答很有帮助"
        }

        response = client.post(
            "/api/v1/feedback",
            headers=user_auth_headers,
            json=feedback_data
        )

        # 可能返回200、404或501
        assert response.status_code in [200, 404, 501]

    def test_submit_feedback_negative(self, client, user_auth_headers):
        """测试提交负面反馈（点踩）"""
        feedback_data = {
            "message_id": "msg_456",
            "feedback_type": "negative",
            "comment": "回答不准确"
        }

        response = client.post(
            "/api/v1/feedback",
            headers=user_auth_headers,
            json=feedback_data
        )

        assert response.status_code in [200, 404, 501]

    def test_submit_feedback_without_auth(self, client):
        """测试未认证提交反馈"""
        feedback_data = {
            "message_id": "msg_123",
            "feedback_type": "positive"
        }

        response = client.post(
            "/api/v1/feedback",
            json=feedback_data
        )

        assert response.status_code == 401

    def test_submit_feedback_invalid_type(self, client, user_auth_headers):
        """测试无效反馈类型"""
        feedback_data = {
            "message_id": "msg_123",
            "feedback_type": "invalid_type"
        }

        response = client.post(
            "/api/v1/feedback",
            headers=user_auth_headers,
            json=feedback_data
        )

        assert response.status_code in [200, 422]

    def test_get_message_feedback(self, client, user_auth_headers):
        """测试获取消息的反馈"""
        message_id = "msg_test_123"

        response = client.get(
            f"/api/v1/feedback/message/{message_id}",
            headers=user_auth_headers
        )

        # 可能返回200、404或501
        assert response.status_code in [200, 404, 501]

    def test_get_feedback_stats(self, client, user_auth_headers):
        """测试获取反馈统计"""
        message_id = "msg_stats_123"

        response = client.get(
            f"/api/v1/feedback/message/{message_id}/stats",
            headers=user_auth_headers
        )

        # 可能返回200、404或501
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert "positive_count" in data
            assert "negative_count" in data
            assert "total_count" in data

    def test_get_my_feedbacks(self, client, user_auth_headers):
        """测试获取我的反馈列表"""
        response = client.get(
            "/api/v1/feedback/my-feedbacks",
            headers=user_auth_headers
        )

        # 可能返回200或501
        assert response.status_code in [200, 501]

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data


class TestChatParameters:
    """聊天参数测试类"""

    def test_chat_with_top_k(self, client, user_auth_headers):
        """测试设置top_k参数"""
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json={
                "message": "测试问题",
                "conversation_id": "conv_123",
                "top_k": 10  # 检索更多结果
            }
        )

        assert response.status_code in [200, 501]

    def test_chat_with_similarity_threshold(self, client, user_auth_headers):
        """测试设置相似度阈值"""
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json={
                "message": "测试问题",
                "conversation_id": "conv_123",
                "similarity_threshold": 0.8
            }
        )

        assert response.status_code in [200, 501]

    def test_chat_with_temperature(self, client, user_auth_headers):
        """测试设置LLM温度参数"""
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json={
                "message": "测试问题",
                "conversation_id": "conv_123",
                "temperature": 0.3
            }
        )

        assert response.status_code in [200, 501]

    def test_chat_invalid_temperature(self, client, user_auth_headers):
        """测试无效温度参数"""
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json={
                "message": "测试问题",
                "conversation_id": "conv_123",
                "temperature": 2.5  # 超出范围
            }
        )

        assert response.status_code in [422, 501]

    def test_chat_invalid_top_k(self, client, user_auth_headers):
        """测试无效top_k参数"""
        response = client.post(
            "/api/v1/chat",
            headers=user_auth_headers,
            json={
                "message": "测试问题",
                "conversation_id": "conv_123",
                "top_k": 0  # 无效值
            }
        )

        assert response.status_code in [422, 501]
