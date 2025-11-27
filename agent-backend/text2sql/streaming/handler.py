"""
流式响应处理

处理LangGraph的流式输出
"""

import json
import asyncio
from typing import Any, AsyncIterator, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class StreamEventType(str, Enum):
    """流事件类型"""
    START = "start"
    MESSAGE = "message"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    AGENT_ACTION = "agent_action"
    AGENT_FINISH = "agent_finish"
    ERROR = "error"
    END = "end"


@dataclass
class StreamEvent:
    """流事件"""
    event_type: StreamEventType
    data: Dict[str, Any] = field(default_factory=dict)
    agent_name: Optional[str] = None
    timestamp: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event_type.value,
            "data": self.data,
            "agent": self.agent_name,
            "timestamp": self.timestamp
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class StreamHandler:
    """流式响应处理器
    
    处理LangGraph的流式输出，转换为标准事件格式
    """
    
    def __init__(
        self,
        on_message: Optional[Callable[[StreamEvent], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None
    ):
        """初始化流处理器
        
        Args:
            on_message: 消息回调函数
            on_error: 错误回调函数
        """
        self.on_message = on_message
        self.on_error = on_error
        self._buffer = []
        
    async def process_stream(
        self,
        stream: AsyncIterator,
        stream_mode: str = "messages"
    ) -> AsyncIterator[StreamEvent]:
        """处理流式输出
        
        Args:
            stream: LangGraph流
            stream_mode: 流模式 (messages, values, updates)
            
        Yields:
            StreamEvent事件
        """
        import time
        
        # 发送开始事件
        start_event = StreamEvent(
            event_type=StreamEventType.START,
            data={"stream_mode": stream_mode},
            timestamp=time.time()
        )
        yield start_event
        
        try:
            async for chunk in stream:
                event = self._parse_chunk(chunk, stream_mode)
                if event:
                    event.timestamp = time.time()
                    
                    if self.on_message:
                        self.on_message(event)
                    
                    yield event
                    
        except Exception as e:
            error_event = StreamEvent(
                event_type=StreamEventType.ERROR,
                data={"error": str(e)},
                timestamp=time.time()
            )
            
            if self.on_error:
                self.on_error(e)
            
            yield error_event
            
        finally:
            # 发送结束事件
            end_event = StreamEvent(
                event_type=StreamEventType.END,
                timestamp=time.time()
            )
            yield end_event
    
    def _parse_chunk(
        self, 
        chunk: Any, 
        stream_mode: str
    ) -> Optional[StreamEvent]:
        """解析流块
        
        Args:
            chunk: 流块数据
            stream_mode: 流模式
            
        Returns:
            解析后的事件
        """
        if stream_mode == "messages":
            return self._parse_message_chunk(chunk)
        elif stream_mode == "values":
            return self._parse_value_chunk(chunk)
        elif stream_mode == "updates":
            return self._parse_update_chunk(chunk)
        else:
            return StreamEvent(
                event_type=StreamEventType.MESSAGE,
                data={"content": str(chunk)}
            )
    
    def _parse_message_chunk(self, chunk: Any) -> Optional[StreamEvent]:
        """解析消息模式的块"""
        if hasattr(chunk, 'content'):
            return StreamEvent(
                event_type=StreamEventType.MESSAGE,
                data={"content": chunk.content}
            )
        elif isinstance(chunk, tuple) and len(chunk) == 2:
            message, metadata = chunk
            return StreamEvent(
                event_type=StreamEventType.MESSAGE,
                data={
                    "content": getattr(message, 'content', str(message)),
                    "metadata": metadata
                }
            )
        return None
    
    def _parse_value_chunk(self, chunk: Any) -> Optional[StreamEvent]:
        """解析值模式的块"""
        if isinstance(chunk, dict):
            return StreamEvent(
                event_type=StreamEventType.MESSAGE,
                data=chunk
            )
        return StreamEvent(
            event_type=StreamEventType.MESSAGE,
            data={"value": str(chunk)}
        )
    
    def _parse_update_chunk(self, chunk: Any) -> Optional[StreamEvent]:
        """解析更新模式的块"""
        if isinstance(chunk, dict):
            # 检查是否是工具调用
            if "tool_calls" in str(chunk):
                return StreamEvent(
                    event_type=StreamEventType.TOOL_CALL,
                    data=chunk
                )
            return StreamEvent(
                event_type=StreamEventType.AGENT_ACTION,
                data=chunk
            )
        return None


async def stream_to_list(stream: AsyncIterator) -> list:
    """将异步流转换为列表
    
    Args:
        stream: 异步迭代器
        
    Returns:
        事件列表
    """
    events = []
    async for event in stream:
        events.append(event)
    return events


async def collect_stream_content(stream: AsyncIterator) -> str:
    """收集流式内容
    
    Args:
        stream: 流式处理器输出
        
    Returns:
        合并的内容字符串
    """
    contents = []
    async for event in stream:
        if isinstance(event, StreamEvent):
            content = event.data.get("content", "")
            if content:
                contents.append(content)
    return "".join(contents)
