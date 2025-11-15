"""上下文管理器工厂 - 创建标准化的中间件钩子"""
from typing import Dict, Any, Optional, Callable

from .config import FilterConfig
from .message_filter import MessageFilter
from .state_sync import StateSynchronizer, StateUpdateBuilder, StateInitializer

CustomLogicFunc = Callable[[Dict[str, Any], Any], Optional[Dict[str, Any]]]  # 自定义逻辑函数类型


class ContextManagerFactory:
    """中间件工厂类 - 统一创建标准化的钩子函数"""

    @staticmethod
    def filter_messages_before_call(state: Dict[str, Any], strategy: FilterConfig,
                                    phase_name: str = "") -> Dict[str, Any]:
        """在调用模型前过滤消息 (使用链式调用优化)"""
        messages = state.get('messages', [])
        if not messages:
            return {}

        filtered_messages = MessageFilter.filter_messages(messages, strategy)

        # 使用链式调用构建更新
        builder = StateUpdateBuilder()
        if len(filtered_messages) != len(messages):
            builder.add_field('messages', filtered_messages)

        if phase_name and (new_phase := StateInitializer.init_phase_field(state, phase_name)):
            builder.add_field('current_phase', new_phase)

        return builder.build() or {}

    @staticmethod
    def save_output_after_call(state: Dict[str, Any], field_name: str, phase_name: str = "",
                               custom_logic: Optional[CustomLogicFunc] = None) -> Dict[str, Any]:
        """在模型调用后保存输出 (使用链式调用 + 异常处理优化)"""
        messages = state.get('messages', [])
        builder = StateUpdateBuilder()

        # 保存 AI 输出 (使用 walrus 运算符)
        if field_name and (content := StateSynchronizer.save_ai_output_to_state(state, field_name, messages)):
            builder.add_field(field_name, content)

        # 执行自定义逻辑 (静默失败)
        if custom_logic:
            try:
                if custom_updates := custom_logic(state, None):
                    builder.add_fields(custom_updates)
            except Exception:
                pass  # 静默失败

        # 标记阶段完成
        if phase_name:
            builder.add_field(f'{phase_name}_completed', True)

        return builder.build() or {}

    @staticmethod
    def build_context_prompt(base_prompt: str, context_fields: Dict[str, str],
                            state: Dict[str, Any], execution_guide: Optional[str] = None) -> str:
        """构建包含上下文的提示词 (使用列表推导式 + join 优化)"""
        # 使用列表推导式收集上下文块
        context_blocks = [
            f"\n\n# {title}\n```\n{state[field]}\n```\n"
            for field, title in context_fields.items()
            if state.get(field)
        ]

        # 拼接所有部分
        parts = [base_prompt, *context_blocks]
        if execution_guide:
            parts.append(f"\n{execution_guide}")

        return ''.join(parts)

