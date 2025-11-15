"""工具函数 - 消息处理、类型判断等"""
from enum import Enum
from typing import List, Optional, Dict, Type

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage


class MessageType(Enum):
    """消息类型枚举"""
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"
    TOOL = "tool"


# 类型映射表
_TYPE_MAP: Dict[MessageType, Type[BaseMessage]] = {
    MessageType.HUMAN: HumanMessage,
    MessageType.AI: AIMessage,
    MessageType.SYSTEM: SystemMessage,
    MessageType.TOOL: ToolMessage,
}


def is_message_type(msg: BaseMessage, msg_type: MessageType) -> bool:
    """判断消息类型"""
    return isinstance(msg, _TYPE_MAP[msg_type])


def has_content(msg: BaseMessage) -> bool:
    """检查消息是否有内容"""
    return (hasattr(msg, 'content') and
            (msg.content.strip() if isinstance(msg.content, str) else bool(msg.content)))


def filter_messages_by_type(
    messages: List[BaseMessage],
    msg_type: MessageType,
    count: int,
    require_content: bool = True
) -> List[BaseMessage]:
    """按类型过滤消息,保留最新的 N 条 (使用列表推导式和切片优化)"""
    if count <= 0:
        return []

    # 使用生成器表达式 + 列表推导式优化
    filtered = [
        msg for msg in reversed(messages)
        if is_message_type(msg, msg_type) and (not require_content or has_content(msg))
    ][:count]

    return list(reversed(filtered))  # 恢复原始顺序


def extract_latest_ai_message(messages: List[BaseMessage]) -> Optional[str]:
    """提取最新的 AI 消息内容 (使用 next + 生成器优化)"""
    return next(
        (msg.content for msg in reversed(messages)
         if isinstance(msg, AIMessage) and has_content(msg)),
        None
    )


def extract_latest_tool_message(messages: List[BaseMessage], tool_name: Optional[str] = None) -> Optional[str]:
    """提取最新的工具消息内容 (使用 next + 生成器优化)"""
    return next(
        (msg.content for msg in reversed(messages)
         if isinstance(msg, ToolMessage) and
         (not tool_name or getattr(msg, 'name', None) == tool_name) and
         has_content(msg)),
        None
    )


def get_message_stats(messages: List[BaseMessage]) -> Dict[str, int]:
    """获取消息统计信息 (使用字典推导式 + sum 优化)"""
    type_counts = {
        'human': sum(1 for m in messages if isinstance(m, HumanMessage)),
        'ai': sum(1 for m in messages if isinstance(m, AIMessage)),
        'system': sum(1 for m in messages if isinstance(m, SystemMessage)),
        'tool': sum(1 for m in messages if isinstance(m, ToolMessage)),
    }
    return {'total': len(messages), **type_counts}

