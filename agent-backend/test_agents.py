from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2025")

async def run_test(agent_name, question):
    """运行单个智能体测试"""
    print(f"\n🧪 测试 {agent_name}")
    print(f"❓ 问题: {question}")
    print("-" * 50)
    
    try:
        result = client.runs.stream(
            None,
            agent_name,
            input={"messages": [{"role": "human", "content": question}]},
        )
        
        final_answer = ""
        async for chunk in result:
            if chunk.event == "values":
                messages = chunk.data.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    if last_msg.get("type") == "ai" and last_msg.get("content"):
                        content = last_msg.get("content", "")
                        agent = last_msg.get("name", "unknown")
                        print(f"📤 [{agent}]: {content[:200]}...")
                        
                        if agent == "supervisor" or not final_answer:
                            final_answer = content
        
        print(f"\n✅ 测试完成")
        print(f"🎯 最终答案: {final_answer}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

# 直接运行的测试函数
async def test_sql():
    await run_test("sql_agent_hitl", "查询每个客户的订单数量")

async def test_sql_graph():
    await run_test("sql_agent_graph", "哪个音乐类型的曲目平均时长最长？")

async def test_api():
    await run_test("api_agent", "获取宠物店 API 的信息")

async def test_text2sql():
    await run_test("text2sql_agent", "查询销售额最高的前5位艺术家")

async def test_text2case():
    await run_test("text2case_agent", "根据登录功能生成测试用例")

async def test_rag():
    await run_test("rag_agent", "什么是机器学习？")

async def test_react():
    await run_test("react_agent_func", "计算 2 + 2 的结果")

async def test_supervisor():
    await run_test("supervisor_agent", "帮我查询数据库中有多少个客户")

async def test_sql_skills():
    await run_test("sql_agent_skills", "查询每个客户的订单数量")

# 想测试哪个智能体，就直接取消注释对应的函数
async def main():
    # 取消注释下面任意一行来测试对应的智能体
    await test_sql_skills()  # 测试 SQL Skills 智能体
    # await test_sql_graph()
    # await test_api()
    # await test_text2sql()
    # await test_text2case()
    await test_sql()  # 测试 SQL 智能体
    # await test_react()
    # await test_supervisor()

if __name__ == "__main__":
    asyncio.run(main())
