# 步骤1: 定义工具和模型

import os

from langchain.chat_models import init_chat_model
from langchain.tools import tool

os.environ["DEEPSEEK_API_KEY"] = "sk-f79fae69b11a4fce88e04805bd6314b7"
model = init_chat_model("deepseek:deepseek-chat")

# 步骤2: 定义工具函数
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

# 步骤3: 定义状态（Functional API）

from langchain_core.messages import AnyMessage, SystemMessage, BaseMessage, ToolCall
from typing_extensions import TypedDict, Annotated
import operator


class MessagesState(TypedDict):
    """智能体状态 - 包含消息列表"""
    messages: Annotated[list[AnyMessage], operator.add]


# 步骤4: 导入 Functional API 装饰器

from langgraph.func import entrypoint, task
from langgraph.graph import add_messages


# 步骤5: 定义模型任务节点（使用 @task）

@task
def call_llm(messages: list[BaseMessage]) -> BaseMessage:
    """LLM决定是否调用工具"""
    return model_with_tools.invoke(
        [
            SystemMessage(
                content="你是一个智能助手，负责对一组输入执行算术运算。"
            )
        ]
        + messages
    )


# 步骤6: 定义工具任务节点（使用 @task）

@task
def call_tool(tool_call: ToolCall):
    """执行工具调用"""
    tool = tools_by_name[tool_call["name"]]
    return tool.invoke(tool_call)


# 步骤7: 定义智能体入口（使用 @entrypoint 和 Functional API）

@entrypoint(state_schema=MessagesState)
def agent(state: MessagesState) -> MessagesState:
    """
    主智能体函数 - 使用 Functional API 实现
    
    此函数使用 @entrypoint 装饰器定义智能体的入口点，
    通过 state_schema 参数明确指定状态结构，确保与前端兼容
    """
    # 从状态中提取消息列表
    messages = state.get("messages", [])
    
    # 验证消息是否为列表
    if not isinstance(messages, list):
        raise ValueError(f"期望消息为列表，但得到 {type(messages)}")
    
    # 调用 LLM（异步任务）
    model_response = call_llm(messages).result()

    # 循环处理工具调用
    while True:
        if not model_response.tool_calls:
            break

        # 并行执行所有工具调用
        tool_result_futures = [
            call_tool(tool_call) for tool_call in model_response.tool_calls
        ]
        tool_results = [fut.result() for fut in tool_result_futures]
        
        # 更新消息列表
        messages = add_messages(messages, [model_response, *tool_results])
        
        # 再次调用 LLM
        model_response = call_llm(messages).result()

    # 将最终响应添加到消息列表
    final_messages = add_messages(messages, model_response)
    
    # 返回完整状态（关键：必须返回包含 messages 的字典）
    return {"messages": final_messages}


# 调用示例
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    
    # 测试智能体
    messages = [HumanMessage(content="计算 3 加 4")]
    result = agent.invoke({"messages": messages})
    
    print("=" * 50)
    print("测试结果:")
    print("=" * 50)
    for m in result["messages"]:
        m.pretty_print()
