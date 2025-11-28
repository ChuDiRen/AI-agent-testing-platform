"""中间件适配器"""
from typing import Dict, Any, Optional

from .config import FilterConfig
from .context_manager import ContextManagerFactory


class MessageFilterMiddleware:
    """消息过滤中间件"""
    def __init__(self, filter_config: FilterConfig, phase_name: str = ""):
        self.filter_config = filter_config
        self.phase_name = phase_name
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updates = ContextManagerFactory.filter_messages_before_call(
            state=state,
            strategy=self.filter_config,
            phase_name=self.phase_name
        )
        return updates or {}


class StateSyncMiddleware:
    """状态同步中间件"""
    def __init__(self, save_to_field: str, phase_name: str = ""):
        self.save_to_field = save_to_field
        self.phase_name = phase_name
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        updates = ContextManagerFactory.save_output_after_call(
            state=state,
            field_name=self.save_to_field,
            phase_name=self.phase_name
        )
        return updates or {}


class DynamicPromptMiddleware:
    """动态提示词注入中间件"""
    def __init__(self, context_fields: Dict[str, str], execution_guide: Optional[str] = None):
        self.context_fields = context_fields
        self.execution_guide = execution_guide
    
    def build_prompt(self, base_prompt: str, state: Dict[str, Any]) -> str:
        return ContextManagerFactory.build_context_prompt(
            base_prompt=base_prompt,
            context_fields=self.context_fields,
            state=state,
            execution_guide=self.execution_guide
        )


class HumanInTheLoopMiddleware:
    """人工审核中间件"""
    def __init__(self, interrupt_before: bool = False, interrupt_after: bool = False):
        self.interrupt_before = interrupt_before
        self.interrupt_after = interrupt_after
    
    def should_interrupt_before(self, state: Dict[str, Any]) -> bool:
        return self.interrupt_before
    
    def should_interrupt_after(self, state: Dict[str, Any]) -> bool:
        return self.interrupt_after
    
    def get_approval(self, state: Dict[str, Any], output: str) -> bool:
        print(f"\n{'='*80}")
        print(f"⏸️  人工审核点")
        print(f"{'='*80}")
        print(f"\n智能体输出:\n{output[:500]}...")  # 只显示前500字符
        print(f"\n是否通过审核? (y/n/edit): ", end="")
        
        choice = input().strip().lower()
        
        if choice == 'y':
            return True
        elif choice == 'edit':
            print("请输入修改后的内容 (输入END结束):")
            lines = []
            while True:
                line = input()
                if line == "END":
                    break
                lines.append(line)
            # 这里可以将修改后的内容保存到state
            return True
        else:
            return False

