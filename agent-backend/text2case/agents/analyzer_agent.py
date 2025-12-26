"""需求分析智能体 - 基于 ReAct 模式

使用 langgraph.prebuilt.create_react_agent 创建
配合工具函数实现需求分析
"""
from pathlib import Path
from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from ..tools.requirement_tools import REQUIREMENT_TOOLS


def _load_prompt() -> str:
    """加载需求分析提示词"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_READER_SYSTEM_MESSAGE.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding='utf-8')
    
    # 默认提示词
    return """你是一个专业的需求分析专家，负责分析测试需求。

## 职责
1. 理解需求的业务背景和目标
2. 识别功能点和业务规则
3. 提取测试要点和关注点
4. 识别潜在的风险和边界条件

## 输出格式
请按以下结构输出分析结果：

### 1. 需求概述
简要描述需求的核心功能

### 2. 功能点列表
- 功能点1
- 功能点2
- ...

### 3. 业务规则
- 规则1
- 规则2
- ...

### 4. 测试要点
- 要点1
- 要点2
- ...

### 5. 风险识别
- 风险1
- 风险2
- ...

请使用工具辅助分析，确保分析全面准确。
"""


def create_analyzer_agent(model: BaseChatModel, tools: List = None) -> Any:
    """创建需求分析智能体
    
    Args:
        model: LLM 模型
        tools: 工具列表，默认使用 REQUIREMENT_TOOLS
        
    Returns:
        配置好的 ReAct 代理
    """
    if tools is None:
        tools = list(REQUIREMENT_TOOLS)
    
    prompt = _load_prompt()
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="analyzer_expert",
        prompt=prompt
    )
    
    return agent


async def analyze_requirement(
    agent,
    requirement: str,
    test_type: str = "API",
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """分析需求
    
    Args:
        agent: 分析代理
        requirement: 需求描述
        test_type: 测试类型 (API/Web/App)
        config: 运行配置
        
    Returns:
        分析结果
    """
    messages = [
        {
            "role": "user",
            "content": f"""请分析以下{test_type}测试需求：

{requirement}

请使用工具辅助分析，输出完整的需求分析结果。
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result
