"""状态同步器 - 状态管理和更新"""
from typing import Dict, Any, List, Optional

from langchain_core.messages import BaseMessage

from .utils import extract_latest_ai_message, extract_latest_tool_message


class StateSynchronizer:
    """状态同步器 - 自动提取 AI 输出并保存到 state 字段"""

    @staticmethod
    def save_ai_output_to_state(state: Dict[str, Any], field_name: str, messages: List[BaseMessage]) -> Optional[str]:
        """从消息历史中提取最新的 AI 输出"""
        return extract_latest_ai_message(messages)

    @staticmethod
    def save_tool_output_to_state(state: Dict[str, Any], field_name: str, messages: List[BaseMessage],
                                   tool_name: Optional[str] = None) -> Optional[str]:
        """从消息历史中提取最新的工具输出"""
        return extract_latest_tool_message(messages, tool_name)


class StateUpdateBuilder:
    """状态更新构建器 - 用于构建 state 更新字典 (支持链式调用)"""

    def __init__(self):
        self.updates: Dict[str, Any] = {}

    def add_field(self, field_name: str, value: Any) -> 'StateUpdateBuilder':
        """添加字段更新 (支持链式调用)"""
        if value is not None:
            self.updates[field_name] = value
        return self

    def add_fields(self, fields: Dict[str, Any]) -> 'StateUpdateBuilder':
        """批量添加字段更新 (使用字典推导式优化)"""
        self.updates.update({k: v for k, v in fields.items() if v is not None})
        return self

    def add_if_not_exists(self, state: Dict[str, Any], field_name: str, value: Any) -> 'StateUpdateBuilder':
        """只在字段不存在或为空时添加"""
        if not state.get(field_name):
            self.add_field(field_name, value)
        return self

    def build(self) -> Optional[Dict[str, Any]]:
        """构建最终的更新字典"""
        return self.updates or None

    def __len__(self) -> int:
        """返回更新字段数量"""
        return len(self.updates)

    def __bool__(self) -> bool:
        """判断是否有更新"""
        return bool(self.updates)


class StateInitializer:
    """状态初始化器 - 初始化状态字段"""

    @staticmethod
    def init_phase_field(state: Dict[str, Any], phase_name: str) -> Optional[str]:
        """初始化阶段字段 (使用三元表达式优化)"""
        return phase_name if state.get('current_phase') != phase_name else None

    @staticmethod
    def init_iteration_counter(state: Dict[str, Any]) -> int:
        """初始化迭代计数器"""
        return state.get('iteration', 0) + 1

    @staticmethod
    def init_timestamp_field(state: Dict[str, Any], field_name: str) -> Optional[str]:
        """初始化时间戳字段 (使用 walrus 运算符优化)"""
        from datetime import datetime
        return datetime.now().isoformat() if not state.get(field_name) else None

