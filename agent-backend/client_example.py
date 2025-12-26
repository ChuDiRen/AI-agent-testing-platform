from langgraph_sdk import get_client
import asyncio
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# 连接到运行在端口 2025 的 LangGraph API 服务器
client = get_client(url="http://localhost:2025")

# Agent 测试配置：(agent_name, question)
# Chinook 数据库包含以下表：
# - Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine
# - MediaType, Playlist, PlaylistTrack, Track
AGENT_TESTS = [
    ("sql_agent", "显示数据库中的表列表"),
    ("sql_agent_hitl", "查询每个客户的订单数量"),
    ("sql_agent_graph", "哪个音乐类型的曲目平均时长最长？"),
    ("api_agent", "获取宠物店 API 的信息"),
    ("text2sql_agent", "查询销售额最高的前5位艺术家"),
    ("text2case_agent", "根据登录功能生成测试用例"),
]


@dataclass
class AgentStep:
    """Agent 执行步骤"""
    agent_name: str
    action: str  # "handoff" | "response" | "tool_call"
    content: str = ""
    tokens: Dict[str, int] = field(default_factory=dict)


@dataclass
class TestResult:
    """测试结果"""
    question: str
    final_answer: str = ""
    steps: List[AgentStep] = field(default_factory=list)
    total_tokens: int = 0
    success: bool = True
    error: str = ""
    thread_id: str = ""


async def get_or_create_thread(thread_id: Optional[str] = None) -> str:
    """获取或创建持久化 thread
    
    Args:
        thread_id: 可选的 thread_id，如果提供则尝试使用现有 thread
        
    Returns:
        thread_id
    """
    if thread_id:
        # 尝试获取现有 thread
        try:
            thread = await client.threads.get(thread_id)
            return thread["thread_id"]
        except Exception:
            pass
    
    # 创建新 thread
    thread = await client.threads.create()
    return thread["thread_id"]


async def run_agent_test(
    agent_name: str, 
    question: str, 
    verbose: bool = False,
    thread_id: Optional[str] = None,
    use_persistent_thread: bool = True
) -> TestResult:
    """通用的 Agent 测试函数
    
    Args:
        agent_name: Agent 名称
        question: 测试问题
        verbose: 是否输出详细日志
        thread_id: 可选的 thread_id（用于会话持久化）
        use_persistent_thread: 是否使用持久化 thread
        
    Returns:
        测试结果
    """
    result = TestResult(question=question)
    
    print(f"\n{'='*70}")
    print(f"🧪 测试 {agent_name}")
    print(f"❓ 问题: {question}")
    print("-" * 70)
    
    # 获取或创建 thread
    if use_persistent_thread:
        result.thread_id = await get_or_create_thread(thread_id)
        print(f"📌 Thread ID: {result.thread_id}")
    else:
        result.thread_id = ""
    
    try:
        async for chunk in client.runs.stream(
            result.thread_id if use_persistent_thread else None,
            agent_name,
            input={
                "messages": [{
                    "role": "human",
                    "content": question,
                }],
            },
        ):
            if chunk.event == "values":
                messages = chunk.data.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    msg_type = last_msg.get("type", "")
                    agent = last_msg.get("name", "unknown")
                    content = last_msg.get("content", "")
                    usage = last_msg.get("usage_metadata", {})
                    
                    # 记录 token 使用
                    if usage:
                        tokens = usage.get("total_tokens", 0)
                        result.total_tokens += tokens
                    
                    # 记录步骤
                    if msg_type == "ai" and content:
                        step = AgentStep(
                            agent_name=agent,
                            action="response",
                            content=content[:200] + "..." if len(content) > 200 else content,
                            tokens=usage
                        )
                        result.steps.append(step)
                        
                        if verbose:
                            print(f"  📤 [{agent}] {content[:100]}...")
                    
                    # 记录 handoff
                    if msg_type == "tool" and "transfer" in last_msg.get("name", ""):
                        tool_name = last_msg.get("name", "")
                        if verbose:
                            print(f"  🔄 {tool_name}")
                    
                    # 捕获最终答案（supervisor 的最后一条消息）
                    if msg_type == "ai" and agent == "supervisor" and content and not last_msg.get("tool_calls"):
                        result.final_answer = content
            
            elif chunk.event == "metadata" and verbose:
                print(f"  📋 Run ID: {chunk.data.get('run_id', 'N/A')}")
        
        result.success = True
        
    except Exception as e:
        result.success = False
        result.error = str(e)
        import traceback
        traceback.print_exc()
    
    return result


def print_result(result: TestResult, agent_name: str):
    """打印测试结果"""
    print("\n" + "=" * 70)
    print("📊 测试结果摘要")
    print("=" * 70)
    
    # 状态
    status = "✅ 成功" if result.success else f"❌ 失败: {result.error}"
    print(f"状态: {status}")
    
    # Thread ID
    if result.thread_id:
        print(f"Thread ID: {result.thread_id}")
    
    # 执行流程
    print(f"\n📍 执行流程 ({len(result.steps)} 步):")
    flow = []
    for step in result.steps:
        name = step.agent_name or "unknown"
        if name not in flow or flow[-1] != name:
            flow.append(name)
    print(f"   {' → '.join(flow) if flow else '(无执行流程)'}")
    
    # Token 统计
    print(f"\n💰 Token 消耗: {result.total_tokens:,}")
    
    # 各 Agent Token 明细
    agent_tokens = {}
    for step in result.steps:
        if step.tokens:
            name = step.agent_name
            tokens = step.tokens.get("total_tokens", 0)
            agent_tokens[name] = agent_tokens.get(name, 0) + tokens
    
    if agent_tokens:
        print("   按 Agent 分布:")
        for name, tokens in sorted(agent_tokens.items(), key=lambda x: -x[1]):
            pct = tokens / result.total_tokens * 100 if result.total_tokens > 0 else 0
            bar = "█" * int(pct / 5)
            print(f"   - {name}: {tokens:,} ({pct:.1f}%) {bar}")
    
    # 最终答案
    print("\n" + "=" * 70)
    print("🎯 最终答案")
    print("=" * 70)
    print(result.final_answer if result.final_answer else "(无答案)")
    
    # 优化建议
    print("\n" + "=" * 70)
    print("💡 优化建议")
    print("=" * 70)
    
    suggestions = []
    
    # 检查 token 消耗
    if result.total_tokens > 500000:
        suggestions.append("⚠️ Token 消耗过高，建议优化 Schema 信息传递方式")
    
    # 检查各 Agent token 分布
    for name, tokens in agent_tokens.items():
        if tokens > 1000000:
            suggestions.append(f"⚠️ {name} 消耗 {tokens:,} tokens，可能存在 prompt 过长问题")
    
    # 检查步骤数
    if len(result.steps) > 10:
        suggestions.append(f"⚠️ 执行步骤过多 ({len(result.steps)} 步)，考虑简化流程")
    
    if not suggestions:
        suggestions.append("✅ 流程正常，无明显优化点")
    
    for s in suggestions:
        print(f"   {s}")
    
    print("\n" + "=" * 70)


async def test_all_agents():
    """依次测试所有 Agent"""
    for agent_name, question in AGENT_TESTS:
        result = await run_agent_test(agent_name, question, use_persistent_thread=True)
        print_result(result, agent_name)


async def test_conversation_memory(agent_name: str = "text2sql_agent"):
    """测试会话记忆功能
    
    连续发送多个问题到同一个 thread，验证记忆是否生效
    """
    print(f"\n{'='*70}")
    print(f"🧠 测试会话记忆 - {agent_name}")
    print("=" * 70)
    
    # 创建一个持久化 thread
    thread = await client.threads.create()
    thread_id = thread["thread_id"]
    print(f"📌 创建 Thread: {thread_id}")
    
    # 连续发送多个相关问题
    questions = [
        "查询所有艺术家的名称",
        "上一个查询返回了多少条记录？",  # 这个问题需要记忆才能回答
        "帮我筛选出名字以 A 开头的艺术家",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n--- 第 {i} 轮对话 ---")
        result = await run_agent_test(
            agent_name, 
            question, 
            verbose=True,
            thread_id=thread_id,
            use_persistent_thread=True
        )
        print(f"答案: {result.final_answer[:200] if result.final_answer else '(无)'}")
    
    print(f"\n✅ 会话记忆测试完成，Thread ID: {thread_id}")
    print("   可以使用此 Thread ID 继续对话")


async def main():
    """主函数"""
    print("🎯 LangGraph 客户端测试")
    print("📍 服务器地址: http://localhost:2025")
    print("📚 可用 Agents: sql_agent, sql_agent_hitl, sql_agent_graph, api_agent, text2sql_agent, text2case_agent")
    
    # 单独测试某个 Agent（使用 Chinook 数据库相关问题）
    # 可选问题：
    # - "查询销售额最高的前5位艺术家"
    # - "哪个音乐类型的曲目平均时长最长？"
    # - "查询每个客户的订单数量"
    # - "列出所有专辑及其艺术家名称"
    # - "查询2010年的总销售额"
    
    # 测试 text2sql（带持久化记忆）
    # result = await run_agent_test("text2sql_agent", "查询销售额最高的前5位艺术家", verbose=True)
    # print_result(result, "text2sql_agent")
    
    # 测试 text2case（带持久化记忆）
    # result = await run_agent_test("text2case_agent", "根据登录功能生成测试用例", verbose=True)
    # print_result(result, "text2case_agent")
    
    # 测试会话记忆
    await test_conversation_memory("text2sql_agent")
    
    # 测试所有 Agent
    # await test_all_agents()


if __name__ == "__main__":
    asyncio.run(main())
