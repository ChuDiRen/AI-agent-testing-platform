"""测试用例评审智能体 - 基于 ReAct 模式

使用 langgraph.prebuilt.create_react_agent 创建
配合工具函数实现测试用例评审
"""
from pathlib import Path
from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from ..tools.testcase_tools import validate_testcase_format


@tool
def calculate_quality_score(
    coverage_score: int,
    completeness_score: int,
    clarity_score: int,
    executability_score: int,
    design_score: int
) -> Dict[str, Any]:
    """计算测试用例质量总分
    
    根据五个维度的评分计算总分和评级。
    
    Args:
        coverage_score: 覆盖度得分 (0-30)
        completeness_score: 完整性得分 (0-25)
        clarity_score: 清晰度得分 (0-20)
        executability_score: 可执行性得分 (0-15)
        design_score: 设计合理性得分 (0-10)
        
    Returns:
        包含总分、评级、是否通过的字典
    """
    total = coverage_score + completeness_score + clarity_score + executability_score + design_score
    
    if total >= 85:
        grade = "优秀"
        passed = True
    elif total >= 70:
        grade = "良好"
        passed = True
    elif total >= 60:
        grade = "合格"
        passed = True
    else:
        grade = "不合格"
        passed = False
    
    return {
        "total_score": total,
        "grade": grade,
        "passed": passed,
        "dimensions": {
            "覆盖度": f"{coverage_score}/30",
            "完整性": f"{completeness_score}/25",
            "清晰度": f"{clarity_score}/20",
            "可执行性": f"{executability_score}/15",
            "设计合理性": f"{design_score}/10",
        }
    }


def _load_prompt() -> str:
    """加载评审提示词"""
    prompt_path = Path(__file__).parent.parent / "prompts" / "TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding='utf-8')
    
    # 默认提示词
    return """你是一个资深的测试用例审查专家，负责审查测试用例的质量。

## 评审维度
1. 覆盖度 (30分): 是否覆盖了所有功能点和场景
2. 完整性 (25分): 用例元素是否齐全
3. 清晰度 (20分): 描述是否清晰易懂
4. 可执行性 (15分): 步骤是否可以直接执行
5. 设计合理性 (10分): 优先级和粒度是否合理

## 工作流程
1. 使用 validate_testcase_format 工具检查格式
2. 逐个维度评分
3. 使用 calculate_quality_score 工具计算总分
4. 输出评审报告

## 评审标准
- ≥85分: 优秀，通过
- 70-84分: 良好，通过
- 60-69分: 合格，通过
- <60分: 不合格，需要修改
"""


def create_reviewer_agent(model: BaseChatModel, tools: List = None) -> Any:
    """创建测试用例评审智能体
    
    Args:
        model: LLM 模型
        tools: 工具列表
        
    Returns:
        配置好的 ReAct 代理
    """
    if tools is None:
        tools = [validate_testcase_format, calculate_quality_score]
    
    prompt = _load_prompt()
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="reviewer_expert",
        prompt=prompt
    )
    
    return agent


async def review_testcases(
    agent,
    requirement: str,
    analysis: str,
    testcases: str,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """评审测试用例
    
    Args:
        agent: 评审代理
        requirement: 原始需求
        analysis: 需求分析结果
        testcases: 测试用例文本
        config: 运行配置
        
    Returns:
        评审结果
    """
    messages = [
        {
            "role": "user",
            "content": f"""请评审以下测试用例：

## 原始需求
{requirement}

## 需求分析
{analysis}

## 测试用例
{testcases}

请按以下步骤操作：
1. 使用 validate_testcase_format 工具检查格式
2. 逐个维度评分（覆盖度、完整性、清晰度、可执行性、设计合理性）
3. 使用 calculate_quality_score 工具计算总分
4. 输出完整的评审报告
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result
