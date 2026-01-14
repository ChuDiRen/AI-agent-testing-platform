#!/usr/bin/env python3
"""
记忆插件系统测试

验证插件架构的正确实现
"""

import asyncio
import tempfile
import os
from pathlib import Path

async def test_plugin_system():
    """测试插件系统"""
    print("🧪 开始测试记忆插件系统...")
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        # 测试1: 插件管理器
        print("📋 测试插件管理器...")
        from memory.plugins.manager import MemoryPluginManager
        from memory.plugins.checkpointer_plugin import CheckpointerPlugin
        from memory.plugins.store_plugin import StorePlugin
        from memory.plugins.user_memory_plugin import UserMemoryPlugin
        
        manager = MemoryPluginManager(db_path)
        
        # 注册插件
        manager.register(CheckpointerPlugin)
        manager.register(StorePlugin)
        manager.register(UserMemoryPlugin)
        
        plugins = manager.list_plugins()
        assert len(plugins) == 3, f"期望3个插件，实际{len(plugins)}"
        print(f"✅ 已注册插件: {[p['name'] for p in plugins]}")
        
        # 测试2: 启用插件
        print("🔌 测试插件启用...")
        await manager.enable_plugin("checkpointer")
        await manager.enable_plugin("store")
        await manager.enable_plugin("user_memory")
        
        for plugin_info in manager.list_plugins():
            assert plugin_info['state'] == 'enabled', f"插件{plugin_info['name']}未启用"
        print("✅ 所有插件已启用")
        
        # 测试3: Checkpointer插件
        print("💾 测试Checkpointer插件...")
        checkpointer_plugin = manager.get("checkpointer")
        saver = await checkpointer_plugin.get_saver()
        assert saver is not None, "Checkpointer saver为None"
        
        health = await checkpointer_plugin.health_check()
        assert health['status'] == 'healthy', f"Checkpointer健康检查失败: {health}"
        print("✅ Checkpointer插件工作正常")
        
        # 测试4: Store插件
        print("📚 测试Store插件...")
        store_plugin = manager.get("store")
        
        # 测试存储和获取
        await store_plugin.put(("test", "ns"), "key1", {"data": "value1"})
        item = await store_plugin.get(("test", "ns"), "key1")
        assert item is not None, "无法获取存储的数据"
        assert item.value["data"] == "value1", f"数据不匹配: {item.value}"
        
        # 测试搜索
        await store_plugin.put(("test", "ns"), "key2", {"data": "value2", "search": "test"})
        results = await store_plugin.search(("test",), query="value")
        assert len(results) >= 1, "搜索未返回结果"
        
        health = await store_plugin.health_check()
        assert health['status'] == 'healthy', f"Store健康检查失败: {health}"
        print("✅ Store插件工作正常")
        
        # 测试5: UserMemory插件
        print("👤 测试UserMemory插件...")
        user_plugin = manager.get("user_memory")
        
        # 测试用户画像
        profile = await user_plugin.get_or_create_profile("user1")
        assert profile["user_id"] == "user1", "用户画像创建失败"
        
        await user_plugin.update_profile("user1", name="测试用户", preferences='{"theme": "dark"}')
        profile = await user_plugin.get_or_create_profile("user1")
        assert profile["name"] == "测试用户", "用户画像更新失败"
        
        # 测试记忆功能
        memory_id = await user_plugin.remember("user1", "用户喜欢深色主题", "preference", 0.8)
        assert memory_id is not None, "记忆创建失败"
        
        memories = await user_plugin.recall("user1", query="深色")
        assert len(memories) >= 1, "记忆召回失败"
        
        health = await user_plugin.health_check()
        assert health['status'] == 'healthy', f"UserMemory健康检查失败: {health}"
        print("✅ UserMemory插件工作正常")
        
        # 测试6: 工厂函数
        print("🏭 测试工厂函数...")
        from memory.checkpointer import get_checkpointer
        from memory.store import get_store
        
        checkpointer = await get_checkpointer()
        store = await get_store()
        
        assert checkpointer is not None, "get_checkpointer返回None"
        assert store is not None, "get_store返回None"
        print("✅ 工厂函数工作正常")
        
        # 测试7: 数据库表结构
        print("🗄️ 测试数据库表结构...")
        import aiosqlite
        
        async with aiosqlite.connect(db_path) as conn:
            cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in await cursor.fetchall()]
            
            expected_tables = ['checkpoints', 'writes', 'long_term_memory', 'user_profiles', 'user_memories']
            for table in expected_tables:
                assert table in tables, f"缺少表: {table}"
        
        print(f"✅ 数据库表结构正确: {tables}")

        # 关闭所有插件，释放数据库文件句柄
        await manager.disable_all()

        print("\n🎉 所有测试通过！插件系统工作正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if os.path.exists(db_path):
            try:
                os.unlink(db_path)
            except PermissionError:
                pass
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_plugin_system())
    exit(0 if success else 1)
