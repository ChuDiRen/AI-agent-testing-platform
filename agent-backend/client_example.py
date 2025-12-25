from langgraph_sdk import get_client
import asyncio

# 连接到运行在端口 2025 的 LangGraph API 服务器
client = get_client(url="http://localhost:2025")

async def main():
    """测试 SQL Agent 的基本功能"""
    
    # 测试问题：哪个音乐类型的曲目平均时长最长？
    question = "哪个音乐类型的曲目平均时长最长？"
    
    print(f"🚀 开始测试 SQL Agent...")
    print(f"❓ 问题: {question}")
    print("-" * 50)
    
    try:
        # 使用 sql_agent（从 langgraph.json 中定义）
        async for chunk in client.runs.stream(
            None,  # Threadless run
            "sql_agent",  # Agent 名称（从 langgraph.json 中定义）
            input={
                "messages": [{
                    "role": "human",
                    "content": question,
                }],
            },
        ):
            print(f"📥 接收事件类型: {chunk.event}")
            print(f"📊 数据: {chunk.data}")
            print("\n" + "="*50 + "\n")
            
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

async def test_multiple_agents():
    """测试多个不同的 agent"""
    
    agents_to_test = [
        ("sql_agent", "显示数据库中的表列表"),
        ("api_agent", "获取宠物店 API 的信息"),
        ("text2sql_agent", "帮我写一个查询用户订单的 SQL"),
    ]
    
    for agent_name, question in agents_to_test:
        print(f"\n🧪 测试 {agent_name}: {question}")
        print("-" * 50)
        
        try:
            async for chunk in client.runs.stream(
                None,
                agent_name,
                input={
                    "messages": [{
                        "role": "human",
                        "content": question,
                    }],
                },
            ):
                if chunk.event == "messages":
                    print(f"📝 消息: {chunk.data}")
                elif chunk.event == "tool_calls":
                    print(f"🔧 工具调用: {chunk.data}")
                else:
                    print(f"📥 事件: {chunk.event} - {chunk.data}")
                    
        except Exception as e:
            print(f"❌ {agent_name} 测试失败: {e}")

if __name__ == "__main__":
    print("🎯 LangGraph 客户端测试")
    print("📍 服务器地址: http://localhost:2025")
    print("📚 可用 Agents: sql_agent, sql_agent_hitl, sql_agent_graph, api_agent, text2sql_agent, text2testcase_agent")
    print("="*70)
    
    # 运行基本测试
    asyncio.run(main())
    
    # 运行多 agent 测试（可选）
    # asyncio.run(test_multiple_agents())
