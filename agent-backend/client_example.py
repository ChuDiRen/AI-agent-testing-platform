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
    ("sql_agent_hitl", "查询每个客户的订单数量"),  # SQL Agent with Human-in-the-Loop
    ("sql_agent_graph", "哪个音乐类型的曲目平均时长最长？"),  # SQL Agent Graph
    ("api_agent", "获取宠物店 API 的信息"),  # API Agent
    ("text2sql_agent", "查询销售额最高的前5位艺术家"),  # Text-to-SQL Agent
    ("text2case_agent", "根据登录功能生成测试用例"),  # Text-to-Case Agent
    ("rag_agent", "什么是机器学习？"),  # RAG Agent
    ("react_agent_func", "计算 2 + 2 的结果"),  # ReAct Agent (Functional API)
    ("supervisor_agent", "帮我查询数据库中有多少个客户"),  # Supervisor Agent
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
    """测试结果（独立测试版本）"""
    question: str
    final_answer: str = ""
    steps: List[AgentStep] = field(default_factory=list)
    total_tokens: int = 0
    success: bool = True
    error: str = ""





async def run_agent_test(
    agent_name: str, 
    question: str, 
    verbose: bool = False
) -> TestResult:
    """独立的 Agent 测试函数（无线程依赖）
    
    Args:
        agent_name: Agent 名称
        question: 测试问题
        verbose: 是否输出详细日志
        
    Returns:
        测试结果
    """
    result = TestResult(question=question)
    
    print(f"\n{'='*70}")
    print(f"🧪 测试 {agent_name}")
    print(f"❓ 问题: {question}")
    print("-" * 70)
    
    try:
        # 使用 threadless 运行模式，每个测试完全独立
        async for chunk in client.runs.stream(
            None,  # Threadless run
            agent_name,
            input={
                "messages": [{
                    "role": "human",
                    "content": question,
                }],
            },
        ):
            if verbose:
                print(f"Receiving new event of type: {chunk.event}...")
                print(chunk.data)
                print("\n")
            
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
    """打印测试结果（独立测试版本）"""
    print("\n" + "=" * 70)
    print("📊 测试结果摘要")
    print("=" * 70)
    
    # 状态
    status = "✅ 成功" if result.success else f"❌ 失败: {result.error}"
    print(f"状态: {status}")
    
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


async def test_single_agent(agent_name: str, question: str = None, verbose: bool = True):
    """单独测试某个特定的 Agent
    
    Args:
        agent_name: Agent 名称
        question: 测试问题（如果为 None，则使用默认问题）
        verbose: 是否输出详细日志
        
    Returns:
        TestResult: 测试结果
    """
    # 如果没有提供问题，从 AGENT_TESTS 中找到对应的问题
    if question is None:
        for name, default_question in AGENT_TESTS:
            if name == agent_name:
                question = default_question
                break
        else:
            question = "测试智能体功能"  # 默认问题
    
    print(f"\n{'='*70}")
    print(f"🎯 单独测试 Agent: {agent_name}")
    print(f"❓ 问题: {question}")
    print("=" * 70)
    
    # 运行测试
    result = await run_agent_test(agent_name, question, verbose=verbose)
    
    # 打印结果
    print_result(result, agent_name)
    
    return result


# 每个智能体的独立测试方法
def create_agent_test_function(agent_name: str, default_question: str):
    """为特定智能体创建测试函数"""
    async def test_function(custom_question: str = None, verbose: bool = True):
        """测试 {agent_name} 智能体
        
        Args:
            custom_question: 自定义问题（如果为 None，使用默认问题）
            verbose: 是否输出详细日志
            
        Returns:
            TestResult: 测试结果
        """
        question = custom_question if custom_question is not None else default_question
        print(f"\n{'='*70}")
        print(f"🎯 测试 {agent_name} 智能体")
        print(f"❓ 问题: {question}")
        print("=" * 70)
        
        result = await run_agent_test(agent_name, question, verbose=verbose)
        print_result(result, agent_name)
        return result
    
    # 设置函数名称和文档字符串
    test_function.__name__ = f"test_{agent_name}"
    test_function.__doc__ = f"""测试 {agent_name} 智能体
    
    Args:
        custom_question: 自定义问题（如果为 None，使用默认问题 '{default_question}'）
        verbose: 是否输出详细日志
        
    Returns:
        TestResult: 测试结果
    """
    return test_function

# 为每个智能体创建独立的测试函数
test_sql_agent_hitl = create_agent_test_function("sql_agent_hitl", "查询每个客户的订单数量")
test_sql_agent_graph = create_agent_test_function("sql_agent_graph", "哪个音乐类型的曲目平均时长最长？")
test_api_agent = create_agent_test_function("api_agent", "获取宠物店 API 的信息")
test_text2sql_agent = create_agent_test_function("text2sql_agent", "查询销售额最高的前5位艺术家")
test_text2case_agent = create_agent_test_function("text2case_agent", "根据登录功能生成测试用例")
test_rag_agent = create_agent_test_function("rag_agent", "什么是机器学习？")
test_react_agent_func = create_agent_test_function("react_agent_func", "计算 2 + 2 的结果")
test_supervisor_agent = create_agent_test_function("supervisor_agent", "帮我查询数据库中有多少个客户")

# 智能体测试映射表
AGENT_TEST_FUNCTIONS = {
    "sql_agent_hitl": test_sql_agent_hitl,
    "sql_agent_graph": test_sql_agent_graph,
    "api_agent": test_api_agent,
    "text2sql_agent": test_text2sql_agent,
    "text2case_agent": test_text2case_agent,
    "rag_agent": test_rag_agent,
    "react_agent_func": test_react_agent_func,
    "supervisor_agent": test_supervisor_agent,
}


async def test_conversation_memory(agent_name: str = "text2sql_agent"):
    """测试会话记忆功能（已废弃 - 需要持久化线程）
    
    注意：此函数需要持久化线程支持，与新版本的独立测试模式不兼容。
    如需测试会话记忆，请使用支持线程的旧版本代码。
    """
    print(f"\n{'='*70}")
    print(f"⚠️ 会话记忆测试已废弃")
    print("=" * 70)
    print("此功能需要持久化线程支持，当前版本使用独立测试模式。")
    print("如需测试会话记忆功能，请使用支持线程的旧版本代码。")


async def demo_single_agent_testing():
    """演示如何单独测试特定智能体"""
    print(f"\n{'='*70}")
    print("🎯 单独智能体测试演示")
    print("=" * 70)
    
    # 示例1：测试 ReAct Agent 的数学计算能力
    print("\n📍 示例1：测试 ReAct Agent 的数学计算能力")
    await test_single_agent("react_agent_func", "计算 2 + 2 的结果")
    
    # 示例2：测试 Text-to-SQL Agent 的数据库查询能力
    print(f"\n{'='*70}")
    print("📍 示例2：测试 Text-to-SQL Agent 的数据库查询能力")
    await test_single_agent("text2sql_agent", "查询销售额最高的前3位艺术家")
    
    # 示例3：测试 RAG Agent 的知识问答能力
    print(f"\n{'='*70}")
    print("📍 示例3：测试 RAG Agent 的知识问答能力")
    await test_single_agent("rag_agent", "什么是机器学习？")
    
    # 示例4：使用自定义问题测试任意智能体
    print(f"\n{'='*70}")
    print("📍 示例4：使用自定义问题测试任意智能体")
    await test_single_agent("supervisor_agent", "帮我查询数据库中有多少个客户", verbose=True)


async def test_all_agents():
    """场景化测试所有智能体"""
    print("🎯 场景化测试所有智能体")
    print("=" * 70)
    
    # 按场景顺序测试所有智能体
    await test_sql_agent_hitl()
    await test_sql_agent_graph()
    await test_api_agent()
    await test_text2sql_agent()
    await test_text2case_agent()
    await test_rag_agent()
    await test_react_agent_func()
    await test_supervisor_agent()


async def main():
    """主函数 - 支持场景化单独测试或全部测试"""
    import sys
    
    print("🎯 LangGraph 客户端测试")
    print("📍 服务器地址: http://localhost:2025")
    print("📚 可用 Agents: sql_agent_hitl, sql_agent_graph, api_agent, text2sql_agent, text2case_agent, rag_agent, react_agent_func, supervisor_agent")
    print("")
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
        
        # 检查是否请求演示模式
        if agent_name == "--demo":
            print("🎭 运行单独智能体测试演示...")
            await demo_single_agent_testing()
            return
        
        # 检查是否请求特定智能体测试
        if agent_name in AGENT_TEST_FUNCTIONS:
            test_function = AGENT_TEST_FUNCTIONS[agent_name]
            print(f"🎯 场景化测试智能体: {agent_name}")
            
            # 检查是否有自定义问题
            if len(sys.argv) > 2:
                custom_question = " ".join(sys.argv[2:])
                await test_function(custom_question, verbose=True)
            else:
                await test_function(verbose=True)
        else:
            print(f"❌ 未知的智能体: {agent_name}")
            print("可用的智能体:")
            for name, question in AGENT_TESTS:
                print(f"  - {name}: {question}")
            print("\n使用方法:")
            print("  python client_example.py                    # 场景化测试所有智能体")
            print("  python client_example.py agent_name         # 场景化测试特定智能体")
            print("  python client_example.py agent_name '问题'  # 使用自定义问题场景化测试")
            print("  python client_example.py --demo             # 运行演示模式")
    else:
        # 没有参数，场景化测试所有智能体
        print("🎯 场景化测试所有智能体（每个 Agent 都是独立的场景）")
        await test_all_agents()


if __name__ == "__main__":
    asyncio.run(main())
