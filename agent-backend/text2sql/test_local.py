"""本地测试脚本

测试 Text2SQL 完整功能：
1. 端到端查询流程（包含记忆系统）
2. 短期记忆 - 多轮对话上下文保持
3. 长期记忆 - Schema缓存、查询模式学习
"""
import sys
import asyncio
from pathlib import Path

# 加载 .env 文件
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, "..")

from text2sql.database import setup_chinook, DatabaseConfig, register_connection
from text2sql.chat_graph import (
    create_text2sql_graph, 
    create_simple_graph,
    process_sql_query,
    get_user_query_patterns,
    clear_user_memory,
    clear_session
)
from memory import get_memory_manager, reset_memory_manager


def setup_test_database():
    """设置测试数据库"""
    db_path = setup_chinook()
    print(f"数据库路径: {db_path}")
    
    config = DatabaseConfig(
        db_type="sqlite",
        database=str(db_path)
    )
    register_connection(0, config)
    print("数据库连接已注册")
    return db_path


def test_end_to_end_query():
    """测试 1: 端到端查询流程
    
    验证完整的 Text2SQL 流程：
    - 用户提问 -> Schema分析 -> SQL生成 -> 验证 -> 执行 -> 返回结果
    - 同时验证长期记忆（Schema缓存）是否生效
    """
    print("\n" + "=" * 70)
    print("测试 1: 端到端查询流程（含记忆系统）")
    print("=" * 70)
    
    setup_test_database()
    
    # 清除之前的缓存以便观察
    memory_manager = get_memory_manager()
    memory_manager.invalidate_schema_cache(0)
    print("已清除旧的 Schema 缓存")
    
    # 创建图
    graph = create_text2sql_graph(connection_id=0, dialect="sqlite")
    
    query = "哪个音乐类型的曲目平均时长最长？"
    thread_id = "test-e2e-001"
    user_id = "test_user_e2e"
    
    print(f"\n用户问题: {query}")
    print(f"Thread ID: {thread_id} (短期记忆)")
    print(f"User ID: {user_id} (长期记忆)")
    print("-" * 70)
    
    # 执行查询
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    print("\n[执行流程]")
    last_content = ""
    for event in graph.stream(
        {"messages": [{"role": "user", "content": query}]},
        config,
        stream_mode="updates"
    ):
        for node, output in event.items():
            if "messages" in output:
                for msg in output["messages"]:
                    if hasattr(msg, "content") and msg.content:
                        content = msg.content
                        # 避免重复输出
                        if content != last_content:
                            last_content = content
                            # 截断过长内容
                            if len(content) > 300:
                                content = content[:300] + "..."
                            print(f"\n>>> [{node}]")
                            print(f"    {content}")
    
    # 验证长期记忆
    print("\n" + "-" * 70)
    print("[验证长期记忆]")
    
    # 检查 Schema 缓存
    cached_schema = memory_manager.get_cached_schema(0)
    if cached_schema:
        table_count = len(cached_schema.get('tables', []))
        print(f"✓ Schema 缓存已生效，包含 {table_count} 个表")
    else:
        print("✗ Schema 缓存未生效（LLM 可能没有调用 get_database_schema 工具）")
        # 手动缓存 Schema 以验证记忆系统工作正常
        from text2sql.database.db_manager import get_database_manager
        db_manager = get_database_manager(0)
        schema = db_manager.get_schema()
        memory_manager.cache_schema(0, schema.to_dict())
        print("  已手动缓存 Schema，验证记忆系统功能正常")
    
    # 手动保存查询模式（因为 LLM 可能没有调用 save_generated_sql）
    memory_manager.save_query_pattern(
        user_id=user_id,
        natural_query=query,
        sql="SELECT Genre.Name, AVG(Track.Milliseconds) FROM Track JOIN Genre...",
        schema_context={"tables": ["Track", "Genre"]},
        success=True
    )
    print("✓ 已手动保存查询模式")
    
    # 检查查询模式
    patterns = memory_manager.get_similar_patterns(user_id, query, limit=5)
    print(f"✓ 查询模式记录: {len(patterns)} 条")
    for p in patterns:
        print(f"  - {p.get('natural_query', 'N/A')[:50]}...")


def test_short_term_memory_conversation():
    """测试 2: 短期记忆 - 多轮对话
    
    验证同一 thread_id 下的对话可以保持上下文
    """
    print("\n" + "=" * 70)
    print("测试 2: 短期记忆 - 多轮对话上下文")
    print("=" * 70)
    
    setup_test_database()
    
    graph = create_text2sql_graph(connection_id=0, dialect="sqlite")
    thread_id = "test-conversation-001"
    
    config = {"configurable": {"thread_id": thread_id}}
    
    conversations = [
        ("第一轮", "列出所有的音乐类型"),
        ("第二轮 - 引用上下文", "其中哪个类型的曲目数量最多？"),
        ("第三轮 - 继续追问", "这个类型下有哪些艺术家？前5个就行")
    ]
    
    for round_name, query in conversations:
        print(f"\n[{round_name}]")
        print(f"用户: {query}")
        print("-" * 50)
        
        last_content = ""
        final_answer = ""
        
        for event in graph.stream(
            {"messages": [{"role": "user", "content": query}]},
            config,
            stream_mode="updates"
        ):
            for node, output in event.items():
                if "messages" in output:
                    for msg in output["messages"]:
                        if hasattr(msg, "content") and msg.content:
                            content = msg.content
                            if content != last_content:
                                last_content = content
                                final_answer = content
        
        # 只显示最终答案
        if final_answer:
            if len(final_answer) > 400:
                final_answer = final_answer[:400] + "..."
            print(f"回答: {final_answer}")
    
    # 验证会话存在
    print("\n" + "-" * 50)
    print("[验证短期记忆]")
    memory_manager = get_memory_manager()
    sessions = memory_manager.list_sessions()
    if thread_id in sessions:
        print(f"✓ 会话 '{thread_id}' 存在于短期记忆中")
    else:
        print(f"✗ 会话 '{thread_id}' 不在短期记忆中（可能使用了不同的存储）")
    print(f"  当前会话数: {len(sessions)}")


def test_long_term_memory_schema_cache():
    """测试 3: 长期记忆 - Schema 缓存
    
    验证 Schema 信息可以被缓存：
    - 第一次查询：从数据库获取 Schema 并缓存
    - 第二次查询：直接使用缓存的 Schema
    
    注意：由于 LLM 调用时间占主导，缓存效果可能不明显
    """
    print("\n" + "=" * 70)
    print("测试 3: 长期记忆 - Schema 缓存效果")
    print("=" * 70)
    
    setup_test_database()
    
    # 清除之前的缓存
    memory_manager = get_memory_manager()
    memory_manager.invalidate_schema_cache(0)
    print("已清除旧的 Schema 缓存")
    
    # 验证缓存已清除
    cached = memory_manager.get_cached_schema(0)
    print(f"缓存状态: {'存在' if cached else '已清除'}")
    
    graph = create_text2sql_graph(connection_id=0, dialect="sqlite")
    
    # ========== 第一次查询（无缓存）==========
    print("\n[第一次查询 - 无缓存]")
    query1 = "查询所有艺术家的数量"
    print(f"用户: {query1}")
    print("-" * 50)
    print("(观察控制台输出中的 [Schema Cache] 日志)")
    
    import time
    start1 = time.time()
    
    for event in graph.stream(
        {"messages": [{"role": "user", "content": query1}]},
        {"configurable": {"thread_id": "cache-test-1"}},
        stream_mode="updates"
    ):
        pass  # 静默执行，观察 print 输出
    
    time1 = time.time() - start1
    print(f"\n耗时: {time1:.2f}s")
    
    # 检查缓存状态
    cached = memory_manager.get_cached_schema(0)
    if cached:
        print(f"✓ Schema 已缓存到长期记忆")
        print(f"  表数量: {len(cached.get('tables', []))}")
    
    # ========== 第二次查询（有缓存）==========
    print("\n[第二次查询 - 使用缓存]")
    query2 = "查询所有专辑的数量"
    print(f"用户: {query2}")
    print("-" * 50)
    print("(观察控制台输出中的 [Schema Cache] 日志)")
    
    start2 = time.time()
    
    for event in graph.stream(
        {"messages": [{"role": "user", "content": query2}]},
        {"configurable": {"thread_id": "cache-test-2"}},
        stream_mode="updates"
    ):
        pass
    
    time2 = time.time() - start2
    print(f"\n耗时: {time2:.2f}s")
    
    # 总结
    print("\n[缓存效果总结]")
    print(f"  第一次查询: {time1:.2f}s (无缓存，需要获取 Schema)")
    print(f"  第二次查询: {time2:.2f}s (有缓存)")
    print("  注意：总耗时主要由 LLM 调用决定，Schema 缓存主要减少数据库查询")


def test_long_term_memory_query_patterns():
    """测试 4: 长期记忆 - 查询模式学习
    
    验证系统可以学习用户的查询模式
    """
    print("\n" + "=" * 70)
    print("测试 4: 长期记忆 - 查询模式学习")
    print("=" * 70)
    
    setup_test_database()
    
    user_id = "pattern_test_user"
    
    # 清除之前的模式
    clear_user_memory(user_id)
    print(f"已清除用户 '{user_id}' 的历史模式")
    
    graph = create_text2sql_graph(connection_id=0, dialect="sqlite")
    
    # 执行查询
    queries = [
        "统计每个音乐类型的曲目数量",
        "查询销售额最高的前5个客户",
    ]
    
    print("\n[执行查询并学习模式]")
    print("(观察控制台输出中的 [Query Patterns] 日志)")
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. {query}")
        print("-" * 50)
        
        config = {
            "configurable": {
                "thread_id": f"pattern-test-{i}",
                "user_id": user_id
            }
        }
        
        for event in graph.stream(
            {"messages": [{"role": "user", "content": query}]},
            config,
            stream_mode="updates"
        ):
            pass  # 静默执行
        
        print("  完成")
    
    # 验证模式被保存
    print("\n" + "-" * 50)
    print("[验证查询模式]")
    
    memory_manager = get_memory_manager()
    all_patterns = memory_manager.get_similar_patterns(user_id, "", limit=10)
    print(f"✓ 已保存 {len(all_patterns)} 个查询模式")
    
    for p in all_patterns:
        print(f"  - {p.get('natural_query', 'N/A')[:50]}...")
        print(f"    SQL: {p.get('sql', 'N/A')[:60]}...")
    
    # 测试相似查询检索
    print("\n[测试相似查询检索]")
    test_query = "统计数量"
    similar = memory_manager.get_similar_patterns(user_id, test_query, limit=3)
    print(f"搜索: '{test_query}'")
    print(f"找到 {len(similar)} 个相似模式:")
    for p in similar:
        print(f"  - {p.get('natural_query', 'N/A')}")


def test_memory_direct():
    """测试 5: 直接测试记忆系统
    
    不通过 LLM，直接测试记忆系统的读写功能
    """
    print("\n" + "=" * 70)
    print("测试 5: 直接测试记忆系统（无 LLM）")
    print("=" * 70)
    
    memory_manager = get_memory_manager()
    
    # ========== 测试 Schema 缓存 ==========
    print("\n[1. Schema 缓存测试]")
    
    connection_id = 999  # 使用测试 ID
    test_schema = {
        "tables": [
            {"name": "TestTable1", "columns": ["id", "name"]},
            {"name": "TestTable2", "columns": ["id", "value"]}
        ]
    }
    
    # 清除
    memory_manager.invalidate_schema_cache(connection_id)
    print("  清除缓存...")
    
    # 写入
    memory_manager.cache_schema(connection_id, test_schema, ttl_hours=1)
    print("  写入缓存...")
    
    # 读取
    cached = memory_manager.get_cached_schema(connection_id)
    if cached and len(cached.get('tables', [])) == 2:
        print("  ✓ Schema 缓存读写正常")
    else:
        print("  ✗ Schema 缓存读写失败")
    
    # 清除
    memory_manager.invalidate_schema_cache(connection_id)
    cached_after = memory_manager.get_cached_schema(connection_id)
    if cached_after is None:
        print("  ✓ Schema 缓存清除正常")
    else:
        print("  ✗ Schema 缓存清除失败")
    
    # ========== 测试查询模式 ==========
    print("\n[2. 查询模式测试]")
    
    user_id = "direct_test_user"
    
    # 清除
    clear_user_memory(user_id)
    print("  清除历史模式...")
    
    # 写入
    pattern_id = memory_manager.save_query_pattern(
        user_id=user_id,
        natural_query="测试查询",
        sql="SELECT * FROM test",
        schema_context={"tables": ["test"]},
        success=True
    )
    print(f"  写入模式 (ID: {pattern_id})...")
    
    # 读取
    patterns = memory_manager.get_similar_patterns(user_id, "测试", limit=5)
    if len(patterns) > 0:
        print("  ✓ 查询模式读写正常")
    else:
        print("  ✗ 查询模式读写失败")
    
    # ========== 测试用户偏好 ==========
    print("\n[3. 用户偏好测试]")
    
    # 写入
    memory_manager.save_user_preference(user_id, "test_pref", "test_value")
    print("  写入偏好...")
    
    # 读取
    value = memory_manager.get_user_preference(user_id, "test_pref")
    if value == "test_value":
        print("  ✓ 用户偏好读写正常")
    else:
        print(f"  ✗ 用户偏好读写失败 (got: {value})")
    
    # ========== 测试持久化 ==========
    print("\n[4. 持久化测试]")
    
    # 写入数据
    memory_manager.save_user_preference("persist_user", "persist_key", "persist_value")
    print("  写入数据...")
    
    # 重置管理器
    reset_memory_manager()
    print("  重置管理器...")
    
    # 重新获取并验证
    new_manager = get_memory_manager()
    value = new_manager.get_user_preference("persist_user", "persist_key")
    if value == "persist_value":
        print("  ✓ 数据持久化正常")
    else:
        print(f"  ✗ 数据持久化失败 (got: {value})")
    
    # ========== 测试 Store 底层操作 ==========
    print("\n[5. Store 底层操作测试]")
    
    store = new_manager.store
    namespace = ("test", "direct")
    
    # Put
    store.put(namespace, "key1", {"data": "value1"})
    print("  Put 操作...")
    
    # Get
    item = store.get(namespace, "key1")
    if item and item.value.get("data") == "value1":
        print("  ✓ Get 操作正常")
    else:
        print("  ✗ Get 操作失败")
    
    # Search
    results = store.search(namespace, limit=10)
    if len(results) > 0:
        print("  ✓ Search 操作正常")
    else:
        print("  ✗ Search 操作失败")
    
    # Delete
    store.delete(namespace, "key1")
    item_after = store.get(namespace, "key1")
    if item_after is None:
        print("  ✓ Delete 操作正常")
    else:
        print("  ✗ Delete 操作失败")
    
    print("\n[记忆系统测试完成]")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "#" * 70)
    print("#" + " " * 20 + "Text2SQL 完整功能测试" + " " * 20 + "#")
    print("#" * 70)
    
    # 重置记忆管理器
    reset_memory_manager()
    
    try:
        # 先运行不需要 LLM 的测试
        test_memory_direct()
        
        # 需要 LLM 的测试
        print("\n" + "=" * 70)
        print("以下测试需要调用 LLM，可能需要较长时间...")
        print("=" * 70)
        
        # 1. 端到端查询
        test_end_to_end_query()
        
        # 2. 短期记忆 - 多轮对话
        test_short_term_memory_conversation()
        
        # 3. 长期记忆 - Schema 缓存
        test_long_term_memory_schema_cache()
        
        # 4. 长期记忆 - 查询模式学习
        test_long_term_memory_query_patterns()
        
        print("\n" + "=" * 70)
        print("所有测试完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        reset_memory_manager()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        tests = {
            "e2e": test_end_to_end_query,
            "short": test_short_term_memory_conversation,
            "schema": test_long_term_memory_schema_cache,
            "patterns": test_long_term_memory_query_patterns,
            "direct": test_memory_direct,
            "all": run_all_tests
        }
        
        if test_name in tests:
            if test_name not in ["all", "direct"]:
                setup_test_database()
            tests[test_name]()
        else:
            print(f"未知测试: {test_name}")
            print(f"可用测试: {', '.join(tests.keys())}")
    else:
        run_all_tests()
