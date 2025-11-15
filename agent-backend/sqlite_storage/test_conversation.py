# 测试函数（可选）
from langchain_core.messages import HumanMessage

from conversation_agent import graph


def test_conversation():
    """测试对话功能"""
    # 直接使用导入的编译好的graph对象
    test_graph = graph

    # 配置
    config = {
        "configurable": {
            "thread_id": "test_thread_1"
        }
    }

    # 第一轮对话
    print("=== 第一轮对话 ===")
    result1 = test_graph.invoke(
        {"messages": [HumanMessage(content="你好，我叫小明")]},
        config=config
    )
    print(f"用户: 你好，我叫小明")
    print(f"助手: {result1['messages'][-1].content}")
    print(f"对话次数: {result1['conversation_count']}")

    # 第二轮对话
    print("\n=== 第二轮对话 ===")
    result2 = test_graph.invoke(
        {"messages": [HumanMessage(content="你还记得我的名字吗？")]},
        config=config
    )
    print(f"用户: 你还记得我的名字吗？")
    print(f"助手: {result2['messages'][-1].content}")
    print(f"对话次数: {result2['conversation_count']}")

    # 第三轮对话
    print("\n=== 第三轮对话 ===")
    result3 = test_graph.invoke(
        {"messages": [HumanMessage(content="我们之前聊了几次？")]},
        config=config
    )
    print(f"用户: 我们之前聊了几次？")
    print(f"助手: {result3['messages'][-1].content}")
    print(f"对话次数: {result3['conversation_count']}")


if __name__ == "__main__":
    test_conversation()
