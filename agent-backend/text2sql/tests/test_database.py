"""
数据库管理器测试
"""

import pytest
import tempfile
import os

from sqlalchemy import text

from ..database.db_manager import DatabaseManager, DatabaseConfig, DatabaseType
from ..database.pagination import PaginationHandler, add_pagination_to_sql, get_count_sql


class TestDatabaseConfig:
    """数据库配置测试"""
    
    def test_sqlite_connection_url(self):
        """测试SQLite连接URL生成"""
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            database="/path/to/db.sqlite"
        )
        url = config.get_connection_url()
        assert url == "sqlite:////path/to/db.sqlite"
        
    def test_mysql_connection_url(self):
        """测试MySQL连接URL生成"""
        config = DatabaseConfig(
            db_type=DatabaseType.MYSQL,
            host="localhost",
            port=3306,
            database="test_db",
            username="user",
            password="pass"
        )
        url = config.get_connection_url()
        assert "mysql+pymysql://" in url
        assert "user:pass" in url
        assert "localhost:3306" in url
        assert "test_db" in url


class TestDatabaseManager:
    """数据库管理器测试"""
    
    @pytest.fixture
    def temp_sqlite(self):
        """创建临时SQLite数据库"""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
            
        config = DatabaseConfig(
            db_type=DatabaseType.SQLITE,
            database=db_path
        )
        
        manager = DatabaseManager(config)
        
        # 创建测试表
        with manager.get_connection() as conn:
            conn.execute(text("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE
                )
            """))
            conn.execute(text("""
                CREATE TABLE orders (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    amount REAL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            conn.execute(text("""
                INSERT INTO users (id, name, email) VALUES
                (1, 'Alice', 'alice@test.com'),
                (2, 'Bob', 'bob@test.com')
            """))
            conn.execute(text("""
                INSERT INTO orders (id, user_id, amount) VALUES
                (1, 1, 100.0),
                (2, 1, 200.0),
                (3, 2, 150.0)
            """))
            conn.commit()
            
        yield manager
        
        manager.close()
        os.unlink(db_path)
        
    def test_get_tables(self, temp_sqlite):
        """测试获取表列表"""
        tables = temp_sqlite.get_tables()
        assert "users" in tables
        assert "orders" in tables
        
    def test_get_table_info(self, temp_sqlite):
        """测试获取表信息"""
        table_info = temp_sqlite.get_table_info("users")
        
        assert table_info.name == "users"
        assert len(table_info.columns) == 3
        
        # 检查主键
        id_col = table_info.get_column("id")
        assert id_col is not None
        assert id_col.primary_key is True
        
    def test_get_schema(self, temp_sqlite):
        """测试获取完整Schema"""
        schema = temp_sqlite.get_schema()
        
        assert len(schema.tables) == 2
        assert len(schema.relationships) >= 1
        
        # 检查关系
        order_table = schema.get_table("orders")
        assert order_table is not None
        
    def test_execute_query(self, temp_sqlite):
        """测试执行查询"""
        result = temp_sqlite.execute_query("SELECT * FROM users")
        
        assert result.success is True
        assert result.row_count == 2
        assert "name" in result.columns
        
    def test_execute_query_with_pagination(self, temp_sqlite):
        """测试分页查询"""
        result = temp_sqlite.execute_query_with_pagination(
            "SELECT * FROM users",
            page=1,
            page_size=1
        )
        
        assert result.success is True
        assert result.row_count == 1
        assert result.pagination is not None
        assert result.pagination.total_count == 2
        assert result.pagination.has_next is True
        
    def test_query_error(self, temp_sqlite):
        """测试查询错误"""
        result = temp_sqlite.execute_query("SELECT * FROM nonexistent")
        
        assert result.success is False
        assert result.error is not None
        
    def test_connection(self, temp_sqlite):
        """测试连接"""
        success, msg = temp_sqlite.test_connection()
        assert success is True


class TestPaginationHandler:
    """分页处理器测试"""
    
    def test_add_pagination(self):
        """测试添加分页"""
        handler = PaginationHandler()
        
        sql = "SELECT * FROM users"
        paginated = handler.add_pagination(sql, page=2, page_size=10)
        
        assert "LIMIT 10" in paginated
        assert "OFFSET 10" in paginated
        
    def test_remove_pagination(self):
        """测试移除分页"""
        handler = PaginationHandler()
        
        sql = "SELECT * FROM users LIMIT 10 OFFSET 20"
        clean = handler.remove_pagination(sql)
        
        assert "LIMIT" not in clean
        assert "OFFSET" not in clean
        
    def test_generate_count_sql(self):
        """测试生成计数SQL"""
        handler = PaginationHandler()
        
        sql = "SELECT * FROM users ORDER BY id"
        count_sql = handler.generate_count_sql(sql)
        
        assert "COUNT(*)" in count_sql
        assert "ORDER BY" not in count_sql
        
    def test_paginate_results(self):
        """测试结果分页"""
        handler = PaginationHandler()
        
        results = [{"id": i} for i in range(25)]
        
        paginated, meta = handler.paginate_results(results, page=2, page_size=10)
        
        assert len(paginated) == 10
        assert meta["total_count"] == 25
        assert meta["total_pages"] == 3
        assert meta["has_next"] is True
        assert meta["has_prev"] is True
        
    def test_convenience_functions(self):
        """测试便捷函数"""
        sql = "SELECT * FROM users"
        
        paginated = add_pagination_to_sql(sql, page=1, page_size=50)
        assert "LIMIT 50" in paginated
        
        count = get_count_sql(sql)
        assert "COUNT(*)" in count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
