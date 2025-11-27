"""
消息裁剪器

防止上下文爆炸，保留关键消息
"""

from typing import Any, Callable, List, Optional, Union
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage


class MessageTrimmer:
    """消息裁剪器
    
    根据配置裁剪消息列表，防止上下文超过模型限制
    """
    
    def __init__(
        self,
        max_tokens: int = 8000,
        max_messages: int = 20,
        strategy: str = "last",  # "last", "first", "smart"
        include_system: bool = True,
        token_counter: Optional[Callable[[str], int]] = None
    ):
        """初始化裁剪器
        
        Args:
            max_tokens: 最大token数
            max_messages: 最大消息数
            strategy: 裁剪策略
                - "last": 保留最后N条消息
                - "first": 保留最前N条消息
                - "smart": 智能裁剪，保留系统消息+第一条+最后N条
            include_system: 是否始终保留系统消息
            token_counter: token计数函数，默认使用字符长度估算
        """
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.strategy = strategy
        self.include_system = include_system
        self.token_counter = token_counter or self._default_token_counter
        
    @staticmethod
    def _default_token_counter(text: str) -> int:
        """默认token计数器（估算）
        
        中文约1.5字符/token，英文约4字符/token
        使用保守估计：2字符/token
        """
        return len(text) // 2
    
    def _get_message_content(self, message: BaseMessage) -> str:
        """获取消息内容"""
        if isinstance(message.content, str):
            return message.content
        elif isinstance(message.content, list):
            return " ".join(
                str(item.get("text", item)) 
                for item in message.content 
                if isinstance(item, dict)
            )
        return str(message.content)
    
    def _count_tokens(self, messages: List[BaseMessage]) -> int:
        """计算消息列表的总token数"""
        total = 0
        for msg in messages:
            content = self._get_message_content(msg)
            total += self.token_counter(content)
        return total
    
    def _extract_system_messages(
        self, 
        messages: List[BaseMessage]
    ) -> tuple[List[BaseMessage], List[BaseMessage]]:
        """分离系统消息和其他消息"""
        system_msgs = []
        other_msgs = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_msgs.append(msg)
            else:
                other_msgs.append(msg)
        return system_msgs, other_msgs
    
    def trim(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """裁剪消息列表
        
        Args:
            messages: 原始消息列表
            
        Returns:
            裁剪后的消息列表
        """
        if not messages:
            return messages
            
        # 分离系统消息
        if self.include_system:
            system_msgs, other_msgs = self._extract_system_messages(messages)
        else:
            system_msgs = []
            other_msgs = messages
            
        # 根据策略裁剪
        if self.strategy == "last":
            trimmed = self._trim_last(other_msgs)
        elif self.strategy == "first":
            trimmed = self._trim_first(other_msgs)
        elif self.strategy == "smart":
            trimmed = self._trim_smart(other_msgs)
        else:
            trimmed = other_msgs
            
        # 合并系统消息
        result = system_msgs + trimmed
        
        # 检查token限制
        while self._count_tokens(result) > self.max_tokens and len(trimmed) > 1:
            if self.strategy == "last":
                trimmed = trimmed[1:]
            else:
                trimmed = trimmed[:-1]
            result = system_msgs + trimmed
            
        return result
    
    def _trim_last(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """保留最后N条消息"""
        if len(messages) <= self.max_messages:
            return messages
        return messages[-self.max_messages:]
    
    def _trim_first(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """保留最前N条消息"""
        if len(messages) <= self.max_messages:
            return messages
        return messages[:self.max_messages]
    
    def _trim_smart(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """智能裁剪
        
        保留：
        - 第一条用户消息（提供上下文）
        - 最后N-1条消息（保持对话连贯）
        """
        if len(messages) <= self.max_messages:
            return messages
            
        # 找到第一条用户消息
        first_user_idx = 0
        for i, msg in enumerate(messages):
            if isinstance(msg, HumanMessage):
                first_user_idx = i
                break
                
        # 保留第一条用户消息和最后N-1条
        first_msg = [messages[first_user_idx]] if first_user_idx < len(messages) else []
        last_msgs = messages[-(self.max_messages - 1):]
        
        # 避免重复
        if first_msg and first_msg[0] in last_msgs:
            return last_msgs
            
        return first_msg + last_msgs


def trim_messages(
    messages: List[BaseMessage],
    max_tokens: int = 8000,
    max_messages: int = 20,
    strategy: str = "last",
    include_system: bool = True
) -> List[BaseMessage]:
    """裁剪消息列表的便捷函数
    
    Args:
        messages: 消息列表
        max_tokens: 最大token数
        max_messages: 最大消息数
        strategy: 裁剪策略
        include_system: 是否保留系统消息
        
    Returns:
        裁剪后的消息列表
    """
    trimmer = MessageTrimmer(
        max_tokens=max_tokens,
        max_messages=max_messages,
        strategy=strategy,
        include_system=include_system
    )
    return trimmer.trim(messages)
