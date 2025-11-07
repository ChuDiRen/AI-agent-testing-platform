"""中间件适配器 - 将 middlewareV1 函数式API封装为 LangGraph 中间件类"""
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from .config import FilterConfig
from .context_manager import ContextManagerFactory


class MessageFilterMiddleware:
    """消息过滤中间件 - 在调用模型前过滤消息历史"""
    
    def __init__(self, filter_config: FilterConfig, phase_name: str = ""):
        """初始化消息过滤中间件
        
        Args:
            filter_config: 过滤策略配置
            phase_name: 阶段名称
        """
        self.filter_config = filter_config
        self.phase_name = phase_name
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行消息过滤
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        updates = ContextManagerFactory.filter_messages_before_call(
            state=state,
            strategy=self.filter_config,
            phase_name=self.phase_name
        )
        return updates or {}


class StateSyncMiddleware:
    """状态同步中间件 - 在模型调用后保存AI输出到状态"""
    
    def __init__(self, save_to_field: str, phase_name: str = ""):
        """初始化状态同步中间件
        
        Args:
            save_to_field: 保存到哪个状态字段
            phase_name: 阶段名称
        """
        self.save_to_field = save_to_field
        self.phase_name = phase_name
    
    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """执行状态同步
        
        Args:
            state: 当前状态
            
        Returns:
            更新后的状态
        """
        updates = ContextManagerFactory.save_output_after_call(
            state=state,
            field_name=self.save_to_field,
            phase_name=self.phase_name
        )
        return updates or {}


class DynamicPromptMiddleware:
    """动态提示词注入中间件 - 自动注入上下文到系统提示词"""
    
    def __init__(self, context_fields: Dict[str, str], execution_guide: Optional[str] = None):
        """初始化动态提示词中间件
        
        Args:
            context_fields: 要注入的上下文字段映射 {state_field: title}
            execution_guide: 执行指南文本
        """
        self.context_fields = context_fields
        self.execution_guide = execution_guide
    
    def build_prompt(self, base_prompt: str, state: Dict[str, Any]) -> str:
        """构建包含上下文的提示词
        
        Args:
            base_prompt: 基础提示词
            state: 当前状态
            
        Returns:
            增强后的提示词
        """
        return ContextManagerFactory.build_context_prompt(
            base_prompt=base_prompt,
            context_fields=self.context_fields,
            state=state,
            execution_guide=self.execution_guide
        )


class HumanInTheLoopMiddleware:
    """人工审核中间件 - 在关键步骤暂停等待人工确认"""
    
    def __init__(self, interrupt_before: bool = False, interrupt_after: bool = False):
        """初始化人工审核中间件
        
        Args:
            interrupt_before: 是否在执行前暂停
            interrupt_after: 是否在执行后暂停
        """
        self.interrupt_before = interrupt_before
        self.interrupt_after = interrupt_after
    
    def should_interrupt_before(self, state: Dict[str, Any]) -> bool:
        """判断是否在执行前暂停
        
        Args:
            state: 当前状态
            
        Returns:
            是否暂停
        """
        return self.interrupt_before
    
    def should_interrupt_after(self, state: Dict[str, Any]) -> bool:
        """判断是否在执行后暂停
        
        Args:
            state: 当前状态
            
        Returns:
            是否暂停
        """
        return self.interrupt_after
    
    def get_approval(self, state: Dict[str, Any], output: str) -> bool:
        """获取人工审核结果
        
        Args:
            state: 当前状态
            output: 智能体输出
            
        Returns:
            是否通过审核
        """
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

