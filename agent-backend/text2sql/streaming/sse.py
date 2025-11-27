"""
SSE (Server-Sent Events) 模块

提供SSE格式的流式响应
"""

import json
import asyncio
from typing import Any, AsyncIterator, Dict, Optional

from text2sql.streaming.handler import StreamEvent, StreamEventType


class SSEMessage:
    """SSE消息"""
    
    def __init__(
        self,
        data: Any,
        event: Optional[str] = None,
        id: Optional[str] = None,
        retry: Optional[int] = None
    ):
        """初始化SSE消息
        
        Args:
            data: 消息数据
            event: 事件类型
            id: 消息ID
            retry: 重连延迟（毫秒）
        """
        self.data = data
        self.event = event
        self.id = id
        self.retry = retry
    
    def encode(self) -> str:
        """编码为SSE格式字符串"""
        lines = []
        
        if self.id is not None:
            lines.append(f"id: {self.id}")
        
        if self.event is not None:
            lines.append(f"event: {self.event}")
        
        if self.retry is not None:
            lines.append(f"retry: {self.retry}")
        
        # 数据行
        if isinstance(self.data, str):
            data_str = self.data
        else:
            data_str = json.dumps(self.data, ensure_ascii=False)
        
        # 处理多行数据
        for line in data_str.split('\n'):
            lines.append(f"data: {line}")
        
        lines.append("")  # 空行表示消息结束
        lines.append("")
        
        return "\n".join(lines)


class SSEResponse:
    """SSE响应生成器"""
    
    CONTENT_TYPE = "text/event-stream"
    
    def __init__(
        self,
        stream: AsyncIterator[StreamEvent],
        ping_interval: int = 30
    ):
        """初始化SSE响应
        
        Args:
            stream: 事件流
            ping_interval: ping间隔（秒），保持连接
        """
        self.stream = stream
        self.ping_interval = ping_interval
        self._closed = False
    
    async def __aiter__(self) -> AsyncIterator[str]:
        """异步迭代生成SSE消息"""
        message_id = 0
        
        try:
            async for event in self.stream:
                if self._closed:
                    break
                
                message_id += 1
                
                sse_msg = SSEMessage(
                    data=event.to_dict(),
                    event=event.event_type.value,
                    id=str(message_id)
                )
                
                yield sse_msg.encode()
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            # 发送错误事件
            error_msg = SSEMessage(
                data={"error": str(e)},
                event="error"
            )
            yield error_msg.encode()
    
    def close(self):
        """关闭响应"""
        self._closed = True


def create_sse_response(
    stream: AsyncIterator[StreamEvent]
) -> SSEResponse:
    """创建SSE响应
    
    Args:
        stream: 事件流
        
    Returns:
        SSEResponse实例
    """
    return SSEResponse(stream)


async def format_as_sse(
    stream: AsyncIterator,
    event_type: str = "message"
) -> AsyncIterator[str]:
    """将流格式化为SSE
    
    简化的SSE格式化器
    
    Args:
        stream: 数据流
        event_type: 事件类型
        
    Yields:
        SSE格式的字符串
    """
    async for data in stream:
        if isinstance(data, dict):
            data_str = json.dumps(data, ensure_ascii=False)
        else:
            data_str = str(data)
        
        yield f"event: {event_type}\ndata: {data_str}\n\n"
    
    # 发送结束事件
    yield "event: end\ndata: {}\n\n"


def sse_keepalive() -> str:
    """生成keepalive消息"""
    return ": keepalive\n\n"


def sse_comment(text: str) -> str:
    """生成SSE注释"""
    return f": {text}\n"
