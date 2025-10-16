from typing import List, Dict, Optional
from sqlmodel import select, Session
import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """对话上下文服务 - 管理对话上下文和消息历史"""
    
    @staticmethod
    def build_context(
        session: Session,
        conversation_id: int,
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        构建对话上下文
        
        Args:
            session: 数据库会话
            conversation_id: 对话会话ID
            max_messages: 最多包含的消息数
            
        Returns:
            消息列表 [{"role": "user/assistant", "content": "..."}, ...]
        """
        from sysmanage.model.AiMessage import AiMessage
        
        # 获取最近的N条消息（不包括当前正在生成的）
        messages_query = select(AiMessage).where(
            AiMessage.conversation_id == conversation_id
        ).order_by(AiMessage.create_time.desc()).limit(max_messages)
        
        messages = session.exec(messages_query).all()
        messages.reverse()  # 正序排列
        
        # 构建上下文
        context = []
        for msg in messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context
    
    @staticmethod
    def get_system_prompt(test_type: str = "API") -> str:
        """
        获取系统提示词
        
        Args:
            test_type: 测试类型（API/Web/App）
            
        Returns:
            系统提示词
        """
        prompts = {
            "API": """你是一位专业的API测试工程师。你的任务是根据用户的需求，生成高质量的API测试用例。
生成的测试用例必须是以下JSON格式：
{
  "case_name": "测试用例名称",
  "priority": "P0/P1/P2/P3",
  "precondition": "前置条件",
  "test_steps": ["步骤1", "步骤2"],
  "expected_result": "预期结果"
}
请确保生成的测试用例覆盖正常流程和异常情况。""",
            
            "Web": """你是一位专业的Web测试工程师。你的任务是根据用户的需求，生成高质量的Web UI测试用例。
生成的测试用例必须是以下JSON格式：
{
  "case_name": "测试用例名称",
  "priority": "P0/P1/P2/P3",
  "precondition": "前置条件",
  "test_steps": ["步骤1", "步骤2"],
  "expected_result": "预期结果"
}
请确保测试用例包括界面元素定位和用户交互。""",
            
            "App": """你是一位专业的移动应用测试工程师。你的任务是根据用户的需求，生成高质量的App测试用例。
生成的测试用例必须是以下JSON格式：
{
  "case_name": "测试用例名称",
  "priority": "P0/P1/P2/P3",
  "precondition": "前置条件",
  "test_steps": ["步骤1", "步骤2"],
  "expected_result": "预期结果"
}
请确保测试用例包括App特有的测试场景（如网络切换、后台运行等）。"""
        }
        
        return prompts.get(test_type, prompts["API"])
    
    @staticmethod
    def extract_test_cases_from_content(content: str) -> List[Dict]:
        """
        从AI响应内容中提取测试用例
        
        Args:
            content: AI生成的内容
            
        Returns:
            提取到的测试用例列表
        """
        import json
        import re
        
        test_cases = []
        
        # 查找JSON对象
        json_pattern = r'\{[^{}]*\}'
        matches = re.finditer(json_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                json_str = match.group()
                test_case = json.loads(json_str)
                # 验证必要字段
                if all(key in test_case for key in ["case_name", "priority", "test_steps", "expected_result"]):
                    test_cases.append(test_case)
            except json.JSONDecodeError:
                continue
        
        return test_cases
    
    @staticmethod
    def calculate_token_count(text: str) -> int:
        """
        简单的token计数（每4个字符约等于1个token）
        
        Args:
            text: 要计数的文本
            
        Returns:
            大约的token数
        """
        return len(text) // 4
    
    @staticmethod
    def should_summarize_context(
        session: Session,
        conversation_id: int,
        max_tokens: int = 4000
    ) -> bool:
        """
        判断是否需要总结对话上下文
        
        Args:
            session: 数据库会话
            conversation_id: 对话会话ID
            max_tokens: 最大token数
            
        Returns:
            是否需要总结
        """
        from sysmanage.model.AiMessage import AiMessage
        
        # 获取所有消息
        messages = session.exec(
            select(AiMessage).where(
                AiMessage.conversation_id == conversation_id
            )
        ).all()
        
        # 计算总token数
        total_tokens = sum(
            ConversationService.calculate_token_count(msg.content)
            for msg in messages
        )
        
        return total_tokens > max_tokens
