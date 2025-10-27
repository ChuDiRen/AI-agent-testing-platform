# 步骤1: 定义工具和模型

from langchain.tools import tool
from langchain.chat_models import init_chat_model
import os

# 初始化模型（使用ModelScope配置）
model = init_chat_model(
    "anthropic:ZhipuAI/GLM-4.5",  # 使用智谱AI GLM-4.5模型
    temperature=0,
    api_key=os.getenv("ANTHROPIC_AUTH_TOKEN", "ms-a08f6d40-522a-4b8d-9310-666777f1a5b8"),
    base_url=os.getenv("ANTHROPIC_BASE_URL", "https://api-inference.modelscope.cn")
)


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

# 注意: 以下测试代码已注释，避免在模块加载时执行
# langgraph 服务只需要 graph 对象，不需要在启动时调用模型
# 如需测试，请在独立脚本中导入 graph 并调用

# from IPython.display import Image, display
# # 显示智能体图
# display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
#
# # 调用智能体
# from langchain.messages import HumanMessage
# messages = [HumanMessage(content="计算 3 加 4 的结果。")]
# messages = graph.invoke({"messages": messages})
# for m in messages["messages"]:
#     m.pretty_print()