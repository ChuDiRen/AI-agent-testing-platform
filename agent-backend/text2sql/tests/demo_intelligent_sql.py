"""
Text2SQL 演示脚本

展示如何使用Text2SQL系统
"""

import asyncio
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


async def demo_basic_query():
    """演示基本查询"""
    print("=" * 50)
    print("演示1: 基本自然语言查询")
    print("=" * 50)
    
    from text2sql.chat_graph import process_sql_query
    
    # 模拟查询（需要先配置数据库连接）
    query = "查询所有用户"
    
    print(f"查询: {query}")
    print("注意: 需要先配置数据库连接才能执行实际查询")
    print()


async def demo_streaming():
    """演示流式查询"""
    print("=" * 50)
    print("演示2: 流式查询")
    print("=" * 50)
    
    from text2sql.chat_graph import stream_sql_query
    
    query = "统计每个部门的员工数量"
    
    print(f"查询: {query}")
    print("流式输出:")
    
    # 模拟流式输出
    print("  [开始处理...]")
    print("  [分析Schema...]")
    print("  [生成SQL...]")
    print("  [验证SQL...]")
    print("  [执行查询...]")
    print("  [完成]")
    print()


async def demo_pagination():
    """演示分页查询"""
    print("=" * 50)
    print("演示3: 分页查询")
    print("=" * 50)
    
    from text2sql.database.pagination import PaginationHandler
    
    handler = PaginationHandler()
    
    # 演示SQL分页
    sql = "SELECT * FROM users ORDER BY id"
    paginated = handler.add_pagination(sql, page=2, page_size=10)
    
    print(f"原始SQL: {sql}")
    print(f"分页后: {paginated}")
    print()


async def demo_validation():
    """演示SQL验证"""
    print("=" * 50)
    print("演示4: SQL验证")
    print("=" * 50)
    
    from text2sql.tools.validation_tools import validate_sql
    
    # 测试有效SQL
    valid_sql = "SELECT id, name FROM users WHERE status = 'active' LIMIT 100"
    result = validate_sql.invoke({"sql": valid_sql})
    
    print(f"SQL: {valid_sql}")
    print(f"有效: {result['is_valid']}")
    print(f"问题数: {result['total_issues']}")
    print()
    
    # 测试危险SQL
    dangerous_sql = "SELECT * FROM users; DROP TABLE users;"
    result = validate_sql.invoke({"sql": dangerous_sql})
    
    print(f"SQL: {dangerous_sql}")
    print(f"有效: {result['is_valid']}")
    print(f"错误: {result['errors']}")
    print()


async def demo_chart():
    """演示图表生成"""
    print("=" * 50)
    print("演示5: 图表生成")
    print("=" * 50)
    
    from text2sql.tools.chart_tools import generate_chart, recommend_chart_type
    
    # 模拟查询结果
    data = [
        {"department": "销售", "count": 50},
        {"department": "研发", "count": 80},
        {"department": "市场", "count": 30},
        {"department": "人事", "count": 20}
    ]
    columns = ["department", "count"]
    
    # 推荐图表类型
    recommendation = recommend_chart_type.invoke({
        "data": data,
        "columns": columns
    })
    
    print(f"数据: {data}")
    print(f"推荐图表类型: {recommendation['recommended_type']}")
    print(f"原因: {recommendation['reason']}")
    
    # 生成图表
    chart = generate_chart.invoke({
        "data": data,
        "columns": columns,
        "title": "部门人员分布"
    })
    
    print(f"图表配置: {chart['chart_type']}")
    print()


async def demo_context_management():
    """演示上下文管理"""
    print("=" * 50)
    print("演示6: 上下文管理（防爆炸）")
    print("=" * 50)
    
    from text2sql.context.trimmer import MessageTrimmer
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    
    # 模拟长对话
    messages = [SystemMessage(content="系统提示")]
    for i in range(30):
        messages.append(HumanMessage(content=f"用户消息 {i}"))
        messages.append(AIMessage(content=f"助手回复 {i}"))
    
    print(f"原始消息数: {len(messages)}")
    
    # 裁剪消息
    trimmer = MessageTrimmer(max_messages=10, strategy="smart")
    trimmed = trimmer.trim(messages)
    
    print(f"裁剪后消息数: {len(trimmed)}")
    print(f"保留了系统消息: {isinstance(trimmed[0], SystemMessage)}")
    print()


async def demo_memory():
    """演示记忆系统"""
    print("=" * 50)
    print("演示7: 记忆系统")
    print("=" * 50)
    
    import tempfile
    import os
    
    # 使用临时数据库
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_memory.db")
        
        from text2sql.memory.manager import MemoryManager
        
        manager = MemoryManager(db_path=db_path)
        
        # 缓存Schema
        schema_info = {"tables": [{"name": "users"}, {"name": "orders"}]}
        manager.cache_schema(1, schema_info)
        
        cached = manager.get_cached_schema(1)
        print(f"Schema缓存成功: {cached is not None}")
        
        # 保存用户偏好
        manager.save_user_preference("user1", "default_limit", 50)
        pref = manager.get_user_preference("user1", "default_limit")
        print(f"用户偏好: default_limit = {pref}")
        
        manager.close()
    
    print()


async def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("Text2SQL 系统演示")
    print("=" * 50 + "\n")
    
    await demo_basic_query()
    await demo_streaming()
    await demo_pagination()
    await demo_validation()
    await demo_chart()
    await demo_context_management()
    await demo_memory()
    
    print("=" * 50)
    print("演示完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
