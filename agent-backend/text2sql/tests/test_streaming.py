"""
流式查询测试
"""

import pytest
import asyncio

from ..streaming.handler import StreamHandler, StreamEvent, StreamEventType
from ..streaming.sse import SSEMessage, SSEResponse


class TestStreamHandler:
    """流处理器测试"""
    
    @pytest.mark.asyncio
    async def test_process_stream_events(self):
        """测试流事件处理"""
        # 模拟流数据
        async def mock_stream():
            yield {"content": "Hello"}
            yield {"content": " World"}
        
        handler = StreamHandler()
        events = []
        
        async for event in handler.process_stream(mock_stream(), "values"):
            events.append(event)
        
        # 应该有: START, 2个MESSAGE, END
        assert len(events) >= 3
        assert events[0].event_type == StreamEventType.START
        assert events[-1].event_type == StreamEventType.END
    
    @pytest.mark.asyncio
    async def test_stream_error_handling(self):
        """测试流错误处理"""
        async def error_stream():
            yield {"content": "OK"}
            raise ValueError("Test error")
        
        handler = StreamHandler()
        events = []
        
        async for event in handler.process_stream(error_stream(), "values"):
            events.append(event)
        
        # 应该有错误事件
        error_events = [e for e in events if e.event_type == StreamEventType.ERROR]
        assert len(error_events) == 1
        assert "Test error" in error_events[0].data.get("error", "")


class TestStreamEvent:
    """流事件测试"""
    
    def test_event_to_dict(self):
        """测试事件序列化"""
        event = StreamEvent(
            event_type=StreamEventType.MESSAGE,
            data={"content": "test"},
            agent_name="test_agent",
            timestamp=1234567890.0
        )
        
        result = event.to_dict()
        
        assert result["event"] == "message"
        assert result["data"]["content"] == "test"
        assert result["agent"] == "test_agent"
        assert result["timestamp"] == 1234567890.0
    
    def test_event_to_json(self):
        """测试事件JSON序列化"""
        event = StreamEvent(
            event_type=StreamEventType.MESSAGE,
            data={"content": "测试中文"}
        )
        
        json_str = event.to_json()
        
        assert "测试中文" in json_str
        assert "message" in json_str


class TestSSEMessage:
    """SSE消息测试"""
    
    def test_simple_message(self):
        """测试简单消息编码"""
        msg = SSEMessage(data="Hello World")
        encoded = msg.encode()
        
        assert "data: Hello World" in encoded
        assert encoded.endswith("\n\n")
    
    def test_message_with_event(self):
        """测试带事件类型的消息"""
        msg = SSEMessage(data={"test": 1}, event="update")
        encoded = msg.encode()
        
        assert "event: update" in encoded
        assert "data:" in encoded
    
    def test_message_with_id(self):
        """测试带ID的消息"""
        msg = SSEMessage(data="test", id="123")
        encoded = msg.encode()
        
        assert "id: 123" in encoded
    
    def test_multiline_data(self):
        """测试多行数据"""
        msg = SSEMessage(data="line1\nline2\nline3")
        encoded = msg.encode()
        
        assert "data: line1" in encoded
        assert "data: line2" in encoded
        assert "data: line3" in encoded


class TestSSEResponse:
    """SSE响应测试"""
    
    @pytest.mark.asyncio
    async def test_sse_response_iteration(self):
        """测试SSE响应迭代"""
        async def mock_events():
            yield StreamEvent(StreamEventType.START, {})
            yield StreamEvent(StreamEventType.MESSAGE, {"content": "test"})
            yield StreamEvent(StreamEventType.END, {})
        
        response = SSEResponse(mock_events())
        messages = []
        
        async for msg in response:
            messages.append(msg)
        
        assert len(messages) == 3
        for msg in messages:
            assert "event:" in msg
            assert "data:" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
