"""测试点设计智能体 - 使用 ReAct 模式 + 工具

基于 langgraph 官方 create_react_agent 构建
"""
from pathlib import Path
from typing import List

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent

from ..tools.requirement_tools import parse_requirement, extract_test_points


def get_designer_tools() -> List[BaseTool]:
    """获取测试点设计工具"""
    return [
        parse_requirement,
        extract_test_points,
    ]


def create_test_point_designer_agent(model: BaseChatModel):
    """创建测试点设计智能体 - ReAct 模式
    
    Args:
        model: LLM 模型
        
    Returns:
        ReAct Agent
    """
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_TEST_POINT_DESIGNER_SYSTEM_MESSAGE.txt"
    system_prompt = prompt_path.read_text(encoding='utf-8')
    
    tools = get_designer_tools()
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=system_prompt,
        name="test_point_designer",
    )
    
    return agent
