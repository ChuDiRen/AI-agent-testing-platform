"""消息过滤器 - 智能消息过滤算法"""
from typing import List

from langchain_core.messages import BaseMessage

from .config import FilterConfig
from .utils import MessageType, filter_messages_by_type


class MessageFilter:
    """消息过滤器 - 按类型反向保留最新 N 条"""

    @staticmethod
    def filter_messages(messages: List[BaseMessage], strategy: FilterConfig) -> List[BaseMessage]:
        """根据策略过滤消息 (使用字典驱动 + 列表推导式优化)"""
        if not messages:
            return []

        # 使用字典驱动的过滤策略
        filter_rules = [
            (MessageType.HUMAN, strategy.human),
            (MessageType.AI, strategy.ai),
            (MessageType.TOOL, strategy.tool),
            (MessageType.SYSTEM, strategy.system),
        ]

        # 收集所有过滤后的消息
        filtered = [
            msg
            for msg_type, count in filter_rules if count > 0
            for msg in filter_messages_by_type(messages, msg_type, count)
        ]

        # 按原始顺序排序 (使用 index 方法)
        return sorted(filtered, key=messages.index)

    @staticmethod
    def should_filter(messages: List[BaseMessage], strategy: FilterConfig) -> bool:
        """判断是否需要过滤 (使用 sum 优化)"""
        required_total = sum([strategy.human, strategy.ai, strategy.tool, strategy.system])
        return len(messages) > required_total

