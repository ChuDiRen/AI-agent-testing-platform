"""
使用SQLite存储的示例Agent

这个示例展示了如何创建一个使用SQLite进行状态持久化的对话agent。
"""

import os
from typing import Annotated

from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

# 配置模型
os.environ["DEEPSEEK_API_KEY"] = "sk-f79fae69b11a4fce88e04805bd6314b7"
model = init_chat_model("deepseek:deepseek-chat")


# 定义状态
class ConversationState(TypedDict):
    """对话状态"""
    messages: Annotated[list[AnyMessage], add_messages]
    conversation_count: int


# 定义节点
def chatbot_node(state: ConversationState, *, store) -> dict:
    """
    聊天机器人节点
    
    处理用户消息并生成回复，并使用store存储用户信息
    
    Args:
        state: 对话状态
        store: Store实例，用于存储长期记忆
    """
    # 从最后一条消息中提取用户信息（简单示例：检测用户自我介绍）
    last_message = state["messages"][-1]
    user_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    # 简单的用户信息提取（实际应用中可以使用更复杂的NLP）
    if "我叫" in user_content or "我是" in user_content:
        # 提取用户名（简单示例）
        import re
        name_match = re.search(r'我叫(\w+)', user_content)
        if name_match:
            user_name = name_match.group(1)
            # 存储到store中
            namespace = ("user_info", "test_thread_1")  # 使用thread_id作为命名空间的一部分
            store.put(
                namespace=namespace,
                key="name",
                value={"name": user_name, "introduced_at": str(state.get("conversation_count", 0))}
            )
    
    # 尝试从store中获取用户信息
    namespace = ("user_info", "test_thread_1")
    user_info = store.get(namespace=namespace, key="name")
    
    # 构建系统提示
    system_content = "你是一个友好的助手。你会记住之前的对话内容，并能够进行连贯的多轮对话。"
    if user_info:
        system_content += f"\n用户信息：用户名是 {user_info.value['name']}"
    
    system_message = SystemMessage(content=system_content)
    
    # 调用模型
    messages = [system_message] + state["messages"]
    response = model.invoke(messages)
    
    # 更新对话计数
    conversation_count = state.get("conversation_count", 0) + 1
    
    return {
        "messages": [response],
        "conversation_count": conversation_count
    }


# 构建图
def create_conversation_graph(checkpointer=None, store=None):
    """创建对话图
    
    Args:
        checkpointer: 可选的checkpointer实例，用于持久化对话状态
        store: 可选的store实例，用于长期记忆存储
    """
    
    # 创建状态图
    workflow = StateGraph(ConversationState)
    
    # 添加节点
    workflow.add_node("chatbot", chatbot_node)
    
    # 添加边
    workflow.add_edge(START, "chatbot")
    workflow.add_edge("chatbot", END)
    
    # 编译图
    # 如果提供了checkpointer和store，则使用它们；否则通过langgraph.json配置注入
    graph = workflow.compile(checkpointer=checkpointer, store=store)
    
    return graph


# 导出图供langgraph使用 (LangGraph API 自动处理持久化)
graph = create_conversation_graph()


