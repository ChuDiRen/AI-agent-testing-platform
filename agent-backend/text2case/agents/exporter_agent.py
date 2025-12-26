"""数据导出智能体 - 基于 ReAct 模式

使用 langgraph.prebuilt.create_react_agent 创建
配合工具函数实现测试用例导出
"""
from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel

from ..tools.testcase_tools import EXPORT_TOOLS


def create_exporter_agent(model: BaseChatModel, tools: List = None) -> Any:
    """创建数据导出智能体
    
    Args:
        model: LLM 模型
        tools: 工具列表，默认使用 EXPORT_TOOLS
        
    Returns:
        配置好的 ReAct 代理
    """
    if tools is None:
        tools = list(EXPORT_TOOLS)
    
    prompt = """你是一个数据导出专家，负责将测试用例导出为 XMind 和 Excel 格式。

## 可用工具
- export_to_xmind: 导出为 XMind 思维导图（JSON格式）
- export_to_excel: 导出为 Excel 表格（xlsx/csv格式）

## 工作流程
1. 从上下文中获取测试用例文本
2. 调用 export_to_xmind 工具导出思维导图
3. 调用 export_to_excel 工具导出 Excel 表格
4. 返回两个文件的路径

## 重要
- 必须同时导出 XMind 和 Excel 两种格式
- 导出完成后，返回文件路径供用户下载
- 如果导出失败，返回错误信息

## 输出格式
导出完成后，返回：
- XMind 文件路径: xxx
- Excel 文件路径: xxx
"""
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="exporter_expert",
        prompt=prompt
    )
    
    return agent


async def export_testcases(
    agent,
    testcases: str,
    formats: List[str] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """导出测试用例
    
    Args:
        agent: 导出代理
        testcases: 测试用例文本
        formats: 导出格式列表 ["xmind", "excel"]
        config: 运行配置
        
    Returns:
        导出结果
    """
    if formats is None:
        formats = ["xmind", "excel"]
    
    format_str = "、".join(formats)
    
    messages = [
        {
            "role": "user",
            "content": f"""请将以下测试用例导出为 {format_str} 格式：

{testcases}

请使用相应的导出工具完成导出。
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result
