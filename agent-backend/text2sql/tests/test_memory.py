"""
记忆和上下文管理模块测试
"""

import pytest
import tempfile
import os
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


class TestMessageTrimmer:
    """消息裁剪器测试"""
    
    def test_trim_last_strategy(self):
        """测试保留最后N条消息"""
        from ..context.trimmer import MessageTrimmer
        
        trimmer = MessageTrimmer(max_messages=3, strategy="last")
        messages = [
            HumanMessage(content="msg1"),
            AIMessage(content="msg2"),
            HumanMessage(content="msg3"),
            AIMessage(content="msg4"),
            HumanMessage(content="msg5"),
        ]
        
        result = trimmer.trim(messages)
        assert len(result) == 3
        assert result[0].content == "msg3"
        assert result[-1].content == "msg5"
        
    def test_preserve_system_messages(self):
        """测试保留系统消息"""
        from ..context.trimmer import MessageTrimmer
        
        trimmer = MessageTrimmer(max_messages=2, strategy="last", include_system=True)
        messages = [
            SystemMessage(content="system"),
            HumanMessage(content="msg1"),
            AIMessage(content="msg2"),
            HumanMessage(content="msg3"),
        ]
        
        result = trimmer.trim(messages)
        assert len(result) == 3  # 1 system + 2 last
        assert isinstance(result[0], SystemMessage)
        
    def test_smart_trim_strategy(self):
        """测试智能裁剪策略"""
        from ..context.trimmer import MessageTrimmer
        
        trimmer = MessageTrimmer(max_messages=3, strategy="smart")
        messages = [
            HumanMessage(content="first user msg"),
            AIMessage(content="first ai msg"),
            HumanMessage(content="second user msg"),
            AIMessage(content="second ai msg"),
            HumanMessage(content="last user msg"),
        ]
        
        result = trimmer.trim(messages)
        # 应保留第一条用户消息和最后2条
        assert len(result) == 3
        

class TestContextCompressor:
    """上下文压缩器测试"""
    
    def test_compress_schema_info(self):
        """测试Schema信息压缩"""
        from ..context.compressor import compress_schema_info
        
        schema_info = {
            "tables": [
                {"name": "users"},
                {"name": "orders"},
                {"name": "products"}
            ],
            "columns": {
                "users": [{"name": "id"}, {"name": "name"}],
                "orders": [{"name": "id"}, {"name": "user_id"}],
                "products": [{"name": "id"}, {"name": "price"}]
            },
            "relationships": [
                {"from_table": "orders", "from_column": "user_id", 
                 "to_table": "users", "to_column": "id"}
            ],
            "indexes": {}
        }
        
        # 只保留users表
        compressed = compress_schema_info(schema_info, ["users"])
        
        assert len(compressed["tables"]) == 1
        assert compressed["tables"][0]["name"] == "users"
        assert "users" in compressed["columns"]
        assert "products" not in compressed["columns"]
        
    def test_compress_results(self):
        """测试结果压缩"""
        from ..context.compressor import compress_results
        
        # 大结果集
        results = [{"id": i, "name": f"item{i}"} for i in range(100)]
        
        compressed = compress_results(results, max_rows=50)
        
        assert compressed["truncated"] is True
        assert compressed["total_count"] == 100
        assert len(compressed["data"]) == 10  # 样本数
        

class TestMemoryManager:
    """记忆管理器测试"""
    
    @pytest.fixture
    def temp_db(self):
        """创建临时数据库"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_memory.db")
            yield db_path
            
    def test_schema_cache(self, temp_db):
        """测试Schema缓存"""
        from ..memory.manager import MemoryManager
        
        manager = MemoryManager(db_path=temp_db)
        
        schema_info = {"tables": [{"name": "test"}]}
        manager.cache_schema(1, schema_info)
        
        cached = manager.get_cached_schema(1)
        assert cached is not None
        assert cached["tables"][0]["name"] == "test"
        
        manager.close()
        
    def test_user_preferences(self, temp_db):
        """测试用户偏好"""
        from ..memory.manager import MemoryManager
        
        manager = MemoryManager(db_path=temp_db)
        
        manager.save_user_preference("user1", "default_limit", 50)
        manager.save_user_preference("user1", "theme", "dark")
        
        assert manager.get_user_preference("user1", "default_limit") == 50
        assert manager.get_user_preference("user1", "theme") == "dark"
        
        prefs = manager.get_all_user_preferences("user1")
        assert len(prefs) == 2
        
        manager.close()


class TestContextManager:
    """上下文管理器测试"""
    
    def test_process_messages(self):
        """测试消息处理"""
        from ..context.manager import ContextManager
        
        manager = ContextManager(max_messages=5, enable_compression=False)
        
        messages = [
            SystemMessage(content="system"),
            HumanMessage(content="msg1"),
            AIMessage(content="msg2"),
            HumanMessage(content="msg3"),
            AIMessage(content="msg4"),
            HumanMessage(content="msg5"),
            AIMessage(content="msg6"),
        ]
        
        result = manager.process_messages(messages)
        
        # 应该被裁剪
        assert len(result) < len(messages)
        # 系统消息应保留
        assert isinstance(result[0], SystemMessage)
        
    def test_prepare_schema_context(self):
        """测试Schema上下文准备"""
        from ..context.manager import ContextManager
        
        manager = ContextManager()
        
        schema_info = {
            "tables": [{"name": "users", "comment": "用户表"}],
            "columns": {
                "users": [
                    {"name": "id", "data_type": "INT", "primary_key": True},
                    {"name": "name", "data_type": "VARCHAR(100)"}
                ]
            },
            "relationships": [],
            "indexes": {}
        }
        
        context = manager.prepare_schema_context(schema_info, "查询用户")
        
        assert "users" in context
        assert "id" in context
        assert "INT" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
