"""测试用例编写智能体 - 基于 ReAct 模式

使用 langgraph.prebuilt.create_react_agent 创建
配合工具函数实现测试用例生成
"""
from pathlib import Path
from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel

from ..tools.testcase_tools import TESTCASE_TOOLS


def _load_prompt() -> str:
    """加载用例编写提示词"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_WRITER_SYSTEM_MESSAGE.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding='utf-8')
    
    # 默认提示词
    return """你是一个经验丰富的测试工程师，专门负责编写高质量的测试用例。

## 工作流程
1. 首先使用 select_test_methods 工具选择合适的测试方法
2. 根据推荐的测试方法设计测试用例
3. 使用 generate_test_data 工具生成测试数据
4. 使用 validate_testcase_format 工具验证用例格式

## 测试用例格式
```
### TC-[编号] [用例标题]

**优先级**：P0/P1/P2/P3
**前置条件**：
- 条件1
**测试步骤**：
1. 步骤1
2. 步骤2
**预期结果**：
1. 结果1
2. 结果2
**测试数据**：
- 参数1：值1
---
```

## 覆盖要求
- 正常流程（30%）
- 边界值（30%）
- 异常处理（30%）
- 其他场景（10%）
"""


def create_writer_agent(model: BaseChatModel, tools: List = None) -> Any:
    """创建测试用例编写智能体
    
    Args:
        model: LLM 模型
        tools: 工具列表，默认使用 TESTCASE_TOOLS
        
    Returns:
        配置好的 ReAct 代理
    """
    if tools is None:
        tools = list(TESTCASE_TOOLS)
    
    prompt = _load_prompt()
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="writer_expert",
        prompt=prompt
    )
    
    return agent


async def generate_testcases(
    agent,
    requirement: str,
    analysis: str,
    test_type: str = "API",
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成测试用例
    
    Args:
        agent: 编写代理
        requirement: 原始需求
        analysis: 需求分析结果
        test_type: 测试类型
        config: 运行配置
        
    Returns:
        生成结果
    """
    messages = [
        {
            "role": "user",
            "content": f"""请基于以下信息编写测试用例：

## 原始需求
{requirement}

## 需求分析
{analysis}

## 测试类型
{test_type}

请按以下步骤操作：
1. 使用 select_test_methods 工具选择合适的测试方法
2. 根据推荐的方法设计测试用例
3. 使用 validate_testcase_format 工具验证格式
4. 输出完整的测试用例
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result
