"""
测试插件式记忆系统

"""

import asyncio
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.checkpointer import get_checkpointer
from memory.store import get_store
from memory.plugins.manager import MemoryPluginManager
from memory.plugins.checkpointer_plugin import CheckpointerPlugin
from memory.plugins.store_plugin import StorePlugin
from memory.plugins.user_memory_plugin import UserMemoryPlugin
from memory.interface import get_memory_system


async def test_checkpointer_plugin():
    """测试检查点插件"""
    print("\n=== 测试 Checkpointer 插件 ===")
    manager = MemoryPluginManager("data/test_memory.db")
    manager.register(CheckpointerPlugin)
    await manager.enable_plugin("checkpointer")

    plugin = manager.get("checkpointer")
    health = await plugin.health_check()
    print(f"健康检查: {health}")

    # 测试获取 saver
    saver = await plugin.get_saver()
    print(f"Saver 类型: {type(saver)}")


async def test_store_plugin():
    """测试存储插件"""
    print("\n=== 测试 Store 插件 ===")
    manager = MemoryPluginManager("data/test_memory.db")
    manager.register(StorePlugin)
    await manager.enable_plugin("store")

    plugin = manager.get("store")

    # 测试 put/get
    await plugin.put(("test", "namespace"), "key1", {"value": "测试数据"})
    item = await plugin.get(("test", "namespace"), "key1")
    print(f"获取数据: {item.value}")

    # 测试 search
    results = await plugin.search(("test",), limit=5)
    print(f"搜索结果: {len(results)} 条")

    # 健康检查
    health = await plugin.health_check()
    print(f"健康检查: {health}")


async def test_user_memory_plugin():
    """测试用户记忆插件"""
    print("\n=== 测试 UserMemory 插件 ===")
    manager = MemoryPluginManager("data/test_memory.db")
    manager.register(UserMemoryPlugin)
    await manager.enable_plugin("user_memory")

    plugin = manager.get("user_memory")

    # 获取或创建用户画像
    profile = await plugin.get_or_create_profile("user_001")
    print(f"用户画像: {profile}")

    # 更新用户画像
    await plugin.update_profile(
        "user_001", 
        name="张三", 
        preferences={"theme": "dark", "language": "zh"}
    )
    profile = await plugin.get_or_create_profile("user_001")
    print(f"更新后画像: {profile}")

    # 记忆操作
    memory_id = await plugin.remember(
        "user_001", 
        "用户喜欢 Python 编程", 
        category="preference", 
        importance=0.8
    )
    print(f"记住记忆 ID: {memory_id}")

    # 回忆记忆
    memories = await plugin.recall("user_001", category="preference")
    print(f"回忆记忆: {len(memories)} 条")
    for m in memories:
        print(f"  - {m['content']} (重要性: {m['importance']})")

    # 健康检查
    health = await plugin.health_check()
    print(f"健康检查: {health}")


async def test_unified_interface():
    """测试统一接口"""
    print("\n=== 测试统一接口 ===")
    system = await get_memory_system()

    # 测试各个组件
    checkpointer = await system.get_checkpointer()
    store = await system.get_store()
    user_memory = await system.get_user_memory()

    print(f"Checkpointer: {type(checkpointer)}")
    print(f"Store: {type(store)}")
    print(f"UserMemory: {type(user_memory)}")

    # 健康检查
    health = await system.health_check()
    print(f"系统健康检查: {health}")


async def test_langgraph_api():
    """测试 LangGraph API 接口"""
    print("\n=== 测试 LangGraph API 接口 ===")

    # 这些函数在 langgraph.json 中配置
    checkpointer = await get_checkpointer()
    print(f"LangGraph Checkpointer: {type(checkpointer)}")

    store = await get_store()
    print(f"LangGraph Store: {type(store)}")


async def main():
    """运行所有测试"""
    print("=" * 50)
    print("插件式记忆系统测试")
    print("=" * 50)

    try:
        await test_checkpointer_plugin()
        await test_store_plugin()
        await test_user_memory_plugin()
        await test_unified_interface()
        await test_langgraph_api()

        print("\n" + "=" * 50)
        print("所有测试通过!")
        print("=" * 50)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

