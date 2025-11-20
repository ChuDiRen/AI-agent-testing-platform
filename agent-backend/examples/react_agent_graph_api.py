# 步骤1: 定义工具和模型

import os
import sys

# 添加父目录到路径，以便导入自定义工具
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_chat_model  # 使用自定义的init_chat_model（支持硅基流动）
from langchain.tools import tool

os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
model = init_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
# 定义工具函数
@tool
def multiply(a: int, b: int) -> int:
    """计算两个整数的乘积

    参数:
        a: 第一个整数
        b: 第二个整数
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """计算两个整数的和

    参数:
        a: 第一个整数
        b: 第二个整数
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """计算两个整数的商

    参数:
        a: 被除数
        b: 除数
    """
    return a / b


# 将工具绑定到LLM
tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)

# 步骤2: 定义状态

from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator


class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]  # 消息列表
    llm_calls: int  # LLM调用次数

# 步骤3: 定义模型节点
from langchain.messages import SystemMessage


def llm_call(state: dict):
    """LLM决定是否调用工具"""

    return {
        "messages": [
            model_with_tools.invoke(
                [
                    SystemMessage(
                        content="你是一个智能助手，负责对一组输入执行算术运算。"
                    )
                ]
                + state["messages"]
            )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


# 步骤4: 定义工具节点

from langchain.messages import ToolMessage


def tool_node(state: dict):
    """执行工具调用"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}

# 步骤5: 定义终止判断逻辑

from typing import Literal
from langgraph.graph import StateGraph, START, END


# 条件边函数：根据LLM是否进行了工具调用来决定路由到工具节点还是结束
def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """根据LLM是否进行了工具调用来决定是否继续循环或停止"""

    messages = state["messages"]
    last_message = messages[-1]

    # 如果LLM进行了工具调用，则执行操作
    if last_message.tool_calls:
        return "tool_node"

    # 否则，停止（回复用户）
    return END

# 步骤6: 构建智能体

# 构建工作流
agent_builder = StateGraph(MessagesState)

# 添加节点
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)

# 添加边连接节点
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

# 编译智能体
graph = agent_builder.compile()
