import logging
import re
from typing import Dict, Optional

from sqlmodel import select, Session

logger = logging.getLogger(__name__)


class PromptService:
    """提示词渲染服务 - 处理模板变量替换"""
    
    @staticmethod
    def render_prompt(
        template_content: str,
        variables: Dict[str, any]
    ) -> str:
        """
        渲染提示词模板，替换变量
        
        Args:
            template_content: 模板内容（支持{variable}形式）
            variables: 变量字典
            
        Returns:
            渲染后的内容
        """
        result = template_content
        
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    @staticmethod
    def extract_variables_from_template(template_content: str) -> list:
        """
        从模板中提取所有变量
        
        Args:
            template_content: 模板内容
            
        Returns:
            变量列表
        """
        # 查找所有{variable}格式的变量
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, template_content)
        return list(set(variables))  # 去重
    
    @staticmethod
    def get_prompt_template(
        session: Session,
        template_id: int
    ) -> Optional[str]:
        """
        获取提示词模板
        
        Args:
            session: 数据库会话
            template_id: 模板ID
            
        Returns:
            模板内容或None
        """
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        template = session.get(PromptTemplate, template_id)
        if template and template.is_active:
            return template.content
        return None
    
    @staticmethod
    def get_prompt_by_type(
        session: Session,
        test_type: str,
        template_type: str = "system"
    ) -> Optional[str]:
        """
        按类型获取提示词模板
        
        Args:
            session: 数据库会话
            test_type: 测试类型（API/Web/App）
            template_type: 模板类型（system/user）
            
        Returns:
            模板内容或None
        """
        from aiassistant.model.PromptTemplate import PromptTemplate
        
        query = select(PromptTemplate).where(
            (PromptTemplate.test_type == test_type) &
            (PromptTemplate.template_type == template_type) &
            (PromptTemplate.is_active == True)
        ).order_by(PromptTemplate.create_time.desc()).limit(1)
        
        result = session.exec(query).first()
        return result.content if result else None
    
    @staticmethod
    def build_system_message(
        test_type: str = "API",
        case_count: int = 10
    ) -> Dict[str, str]:
        """
        构建系统消息
        
        Args:
            test_type: 测试类型
            case_count: 用例数量
            
        Returns:
            系统消息字典
        """
        system_prompts = {
            "API": f"""你是一位专业的API测试工程师。你的任务是根据用户的需求生成{case_count}个高质量的API测试用例。
            
请以JSON数组格式返回测试用例，每个用例包含以下字段：
- case_name: 用例名称
- priority: 优先级（P0/P1/P2/P3）
- precondition: 前置条件
- test_steps: 测试步骤（数组格式）
- expected_result: 预期结果

确保测试用例覆盖正常流程和边界情况。""",
            
            "Web": f"""你是一位专业的Web UI测试工程师。你的任务是根据用户的需求生成{case_count}个高质量的Web测试用例。

请以JSON数组格式返回测试用例，每个用例包含以下字段：
- case_name: 用例名称
- priority: 优先级（P0/P1/P2/P3）
- precondition: 前置条件
- test_steps: 测试步骤（数组格式）
- expected_result: 预期结果

确保包括界面元素定位和用户交互。""",
            
            "App": f"""你是一位专业的移动应用测试工程师。你的任务是根据用户的需求生成{case_count}个高质量的App测试用例。

请以JSON数组格式返回测试用例，每个用例包含以下字段：
- case_name: 用例名称
- priority: 优先级（P0/P1/P2/P3）
- precondition: 前置条件
- test_steps: 测试步骤（数组格式）
- expected_result: 预期结果

确保包括App特有的测试场景。"""
        }
        
        content = system_prompts.get(test_type, system_prompts["API"])
        return {"role": "system", "content": content}
