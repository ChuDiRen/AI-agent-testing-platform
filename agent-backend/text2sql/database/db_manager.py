"""
数据库管理器 - 纯异步实现

提供多数据库支持和统一的操作接口
"""

import time
import aiosqlite
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path

from ..models.schema_models import (
    TableInfo, ColumnInfo, IndexInfo, RelationshipInfo,
    DatabaseSchema, ColumnType
)
from ..models.result_models import QueryResult, QueryStatus, PaginationInfo


class DatabaseType(str, Enum):
    """支持的数据库类型（纯异步实现仅支持SQLite）"""
    SQLITE = "sqlite"


@dataclass
class DatabaseConfig:
    """数据库配置 - 纯异步实现（仅支持SQLite）"""
    db_type: DatabaseType = DatabaseType.SQLITE
    database: str = ""

    # 查询配置
    query_timeout: int = 30
    default_limit: int = 100
    max_limit: int = 1000


class DatabaseManager:
    """数据库管理器 - 纯异步实现

    提供统一的数据库操作接口，仅支持SQLite
    """

    # 类型映射
    TYPE_MAPPING = {
        "int": ColumnType.INTEGER,
        "integer": ColumnType.INTEGER,
        "bigint": ColumnType.INTEGER,
        "smallint": ColumnType.INTEGER,
        "float": ColumnType.FLOAT,
        "double": ColumnType.FLOAT,
        "decimal": ColumnType.FLOAT,
        "numeric": ColumnType.FLOAT,
        "varchar": ColumnType.STRING,
        "char": ColumnType.STRING,
        "nvarchar": ColumnType.STRING,
        "text": ColumnType.TEXT,
        "longtext": ColumnType.TEXT,
        "boolean": ColumnType.BOOLEAN,
        "bool": ColumnType.BOOLEAN,
        "date": ColumnType.DATE,
        "datetime": ColumnType.DATETIME,
        "timestamp": ColumnType.TIMESTAMP,
        "blob": ColumnType.BINARY,
        "binary": ColumnType.BINARY,
        "json": ColumnType.JSON,
        "jsonb": ColumnType.JSON,
    }

    def __init__(self, config: DatabaseConfig):
        """初始化数据库管理器

        Args:
            config: 数据库配置
        """
        self.config = config
        self._conn: Optional[aiosqlite.Connection] = None
        self._schema_cache: Optional[DatabaseSchema] = None

    async def _get_connection(self) -> aiosqlite.Connection:
        """获取异步数据库连接（带缓存）"""
        if self._conn is None:
            self._conn = await aiosqlite.connect(self.config.database, check_same_thread=False)
            self._conn.row_factory = aiosqlite.Row
        return self._conn

    def _map_column_type(self, type_str: str) -> ColumnType:
        """映射列类型"""
        type_lower = type_str.lower().split("(")[0].strip()
        return self.TYPE_MAPPING.get(type_lower, ColumnType.UNKNOWN)

    async def setup_database(self) -> None:
        """设置数据库（仅支持SQLite，异步）"""
        if self.config.db_type == DatabaseType.SQLITE:
            db_path = Path(self.config.database)

            # 检查数据库是否存在
            if db_path.exists():
                # 验证数据库
                try:
                    conn = await aiosqlite.connect(db_path)
                    cursor = await conn.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
                    result = await cursor.fetchone()
                    await conn.close()
                    if result[0] > 0:
                        return  # 数据库已存在且有效
                except Exception:
                    pass

            # 自动下载 Chinook 数据库
            from text2sql.database import setup_chinook
            await setup_chinook()
        else:
            raise NotImplementedError(f"数据库类型 {self.config.db_type} 不支持（纯异步实现仅支持 SQLite）")

    async def get_tables(self) -> List[str]:
        """获取所有表名 - 异步"""
        conn = await self._get_connection()
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    
    async def get_table_info(self, table_name: str) -> TableInfo:
        """获取表的详细信息 - 异步

        Args:
            table_name: 表名

        Returns:
            表信息对象
        """
        conn = await self._get_connection()

        # 获取列信息
        columns = []
        pk_columns = set()

        # 获取主键
        cursor = await conn.execute(f"PRAGMA table_info({table_name})")
        rows = await cursor.fetchall()
        for row in rows:
            if row[5]:  # pk column is 1 if primary key
                pk_columns.add(row[1])  # name is at index 1

        # 获取外键
        fk_map = {}
        cursor = await conn.execute(f"PRAGMA foreign_key_list({table_name})")
        fk_rows = await cursor.fetchall()
        for row in fk_rows:
            col_name = row[3]  # from column
            ref_table = row[2]  # to table
            ref_col = row[4]    # to column
            fk_map[col_name] = f"{ref_table}.{ref_col}"

        # 获取列详情
        for row in rows:
            col_info = ColumnInfo(
                name=row[1],  # name
                data_type=row[2],  # type
                column_type=self._map_column_type(row[2]),
                nullable=not row[3],  # notnull is True if not nullable
                primary_key=row[1] in pk_columns,
                foreign_key=fk_map.get(row[1]),
                default=row[4],  # dflt_value
                comment=None
            )
            columns.append(col_info)

        # 获取索引信息
        indexes = []
        cursor = await conn.execute(f"PRAGMA index_list({table_name})")
        idx_rows = await cursor.fetchall()
        for idx_row in idx_rows:
            idx_name = idx_row[1]  # name
            is_unique = bool(idx_row[2])  # unique

            # 获取索引列
            idx_col_cursor = await conn.execute(f"PRAGMA index_info({idx_name})")
            idx_col_rows = await idx_col_cursor.fetchall()
            idx_cols = [row[2] for row in idx_col_rows]  # name is at index 2

            index_info = IndexInfo(
                name=idx_name,
                columns=idx_cols,
                unique=is_unique
            )
            indexes.append(index_info)

        return TableInfo(
            name=table_name,
            columns=columns,
            indexes=indexes
        )
    
    async def get_schema(self, force_refresh: bool = False) -> DatabaseSchema:
        """获取完整的数据库Schema - 异步

        Args:
            force_refresh: 是否强制刷新缓存

        Returns:
            数据库Schema对象
        """
        if self._schema_cache and not force_refresh:
            return self._schema_cache

        tables = []
        relationships = []

        table_names = await self.get_tables()
        for table_name in table_names:
            table_info = await self.get_table_info(table_name)
            tables.append(table_info)

            # 提取关系信息
            for col in table_info.columns:
                if col.foreign_key:
                    parts = col.foreign_key.split(".")
                    if len(parts) == 2:
                        rel = RelationshipInfo(
                            from_table=table_name,
                            from_column=col.name,
                            to_table=parts[0],
                            to_column=parts[1]
                        )
                        relationships.append(rel)

        self._schema_cache = DatabaseSchema(
            database_name=self.config.database,
            tables=tables,
            relationships=relationships
        )

        return self._schema_cache

    async def execute_query(
        self,
        sql: str,
        params: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationInfo] = None
    ) -> QueryResult:
        """执行SQL查询 - 异步

        Args:
            sql: SQL语句
            params: 查询参数
            pagination: 分页信息

        Returns:
            查询结果
        """
        start_time = time.time()

        try:
            conn = await self._get_connection()
            cursor = await conn.execute(sql, params or {})

            # 获取列名
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            # 获取数据
            rows = await cursor.fetchall()
            data = [dict(zip(columns, row)) for row in rows]

            execution_time = (time.time() - start_time) * 1000

            return QueryResult(
                status=QueryStatus.SUCCESS,
                data=data,
                columns=columns,
                row_count=len(data),
                execution_time_ms=execution_time,
                sql=sql,
                pagination=pagination
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = str(e)

            # 识别错误类型
            error_code = "UNKNOWN_ERROR"
            if "timeout" in error_msg.lower():
                error_code = "TIMEOUT"
            elif "syntax" in error_msg.lower():
                error_code = "SYNTAX_ERROR"
            elif "exist" in error_msg.lower():
                error_code = "TABLE_NOT_FOUND"
            elif "permission" in error_msg.lower() or "access" in error_msg.lower():
                error_code = "PERMISSION_DENIED"

            return QueryResult(
                status=QueryStatus.ERROR,
                execution_time_ms=execution_time,
                sql=sql,
                error=error_msg,
                error_code=error_code
            )

    async def execute_query_with_pagination(
        self,
        sql: str,
        page: int = 1,
        page_size: int = 100,
        params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """执行带分页的查询 - 异步

        Args:
            sql: SQL语句（不含LIMIT/OFFSET）
            page: 页码
            page_size: 每页大小
            params: 查询参数

        Returns:
            分页查询结果
        """
        # 限制page_size
        page_size = min(page_size, self.config.max_limit)

        # 计算offset
        offset = (page - 1) * page_size

        # 添加分页子句
        paginated_sql = f"{sql.rstrip(';')} LIMIT {page_size} OFFSET {offset}"

        # 执行分页查询
        result = await self.execute_query(paginated_sql, params)

        if result.success:
            # 获取总数
            count_sql = f"SELECT COUNT(*) as cnt FROM ({sql.rstrip(';')}) as t"
            count_result = await self.execute_query(count_sql, params)

            total_count = 0
            if count_result.success and count_result.data:
                total_count = count_result.data[0].get("cnt", 0)

            # 更新分页信息
            result.pagination = PaginationInfo(
                page=page,
                page_size=page_size,
                total_count=total_count
            )

        return result

    async def test_connection(self) -> Tuple[bool, str]:
        """测试数据库连接 - 异步

        Returns:
            (成功标志, 消息)
        """
        try:
            conn = await self._get_connection()
            await conn.execute("SELECT 1")
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)

    async def close(self) -> None:
        """关闭数据库连接 - 异步"""
        if self._conn:
            await self._conn.close()
            self._conn = None

# 连接管理器 - 纯异步实现
_connections: Dict[int, DatabaseManager] = {}


def get_database_manager(
    connection_id: int,
    config: Optional[DatabaseConfig] = None
) -> DatabaseManager:
    """获取数据库管理器实例

    Args:
        connection_id: 连接ID
        config: 数据库配置（首次获取时需要）

    Returns:
        DatabaseManager实例
    """
    global _connections

    if connection_id not in _connections:
        if config is None:
            raise ValueError(f"Connection {connection_id} not found and no config provided")
        _connections[connection_id] = DatabaseManager(config)

    return _connections[connection_id]


def register_connection(connection_id: int, config: DatabaseConfig) -> DatabaseManager:
    """注册新的数据库连接

    Args:
        connection_id: 连接ID
        config: 数据库配置

    Returns:
        DatabaseManager实例
    """
    global _connections

    # 如果已存在，先关闭
    if connection_id in _connections:
        # 注意：这里无法直接调用 async close，所以标记为需要清理
        pass

    manager = DatabaseManager(config)
    _connections[connection_id] = manager
    return manager


async def close_connection(connection_id: int) -> None:
    """关闭指定连接 - 异步"""
    global _connections

    if connection_id in _connections:
        await _connections[connection_id].close()
        del _connections[connection_id]


async def close_all_connections() -> None:
    """关闭所有连接 - 异步"""
    global _connections

    for manager in _connections.values():
        await manager.close()
    _connections.clear()
