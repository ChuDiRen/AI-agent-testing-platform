"""简单的服务器连接测试"""
import asyncio
from langgraph_sdk import get_client

async def test():
    client = get_client(url="http://localhost:2025")
    
    print("1. 测试服务器连接...")
    try:
        assistants = await client.assistants.search()
        print(f"   ✅ 连接成功，发现 {len(assistants)} 个 assistants")
        for a in assistants:
            print(f"      - {a['graph_id']}")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return
    
    print("\n2. 测试创建 thread...")
    try:
        thread = await client.threads.create()
        print(f"   ✅ Thread 创建成功: {thread['thread_id']}")
    except Exception as e:
        print(f"   ❌ Thread 创建失败: {e}")
        return
    
    print("\n3. 测试简单的 Agent 调用...")
    try:
        # 使用最简单的 agent
        async for chunk in client.runs.stream(
            thread["thread_id"],
            "react_agent_func",  # 使用简单的 react agent
            input={"messages": [{"role": "human", "content": "计算 1+1"}]},
        ):
            print(f"   收到 chunk: {chunk.event}")
            if chunk.event == "values":
                msgs = chunk.data.get("messages", [])
                if msgs:
                    last = msgs[-1]
                    if last.get("content"):
                        print(f"   内容: {last['content'][:100]}...")
        print("   ✅ Agent 调用成功")
    except Exception as e:
        print(f"   ❌ Agent 调用失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
