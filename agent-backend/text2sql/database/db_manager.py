"""
数据库管理器

提供多数据库支持和统一的操作接口
"""

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum
from contextlib import contextmanager
import asyncio

from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from ..models.schema_models import (
    TableInfo, ColumnInfo, IndexInfo, RelationshipInfo, 
    DatabaseSchema, ColumnType
)
from ..models.result_models import QueryResult, QueryStatus, PaginationInfo


class DatabaseType(str, Enum):
    """支持的数据库类型"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    ORACLE = "oracle"
    MSSQL = "mssql"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    CLICKHOUSE = "clickhouse"
    DUCKDB = "duckdb"


@dataclass
class DatabaseConfig:
    """数据库配置"""
    db_type: DatabaseType = DatabaseType.SQLITE
    host: str = "localhost"
    port: int = 3306
    database: str = ""
    username: str = ""
    password: str = ""
    
    # 连接池配置
    pool_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # 查询配置
    query_timeout: int = 30
    default_limit: int = 100
    max_limit: int = 1000
    
    # 额外参数
    extra_params: Dict[str, Any] = field(default_factory=dict)
    
    def get_connection_url(self) -> str:
        """生成数据库连接URL"""
        if self.db_type == DatabaseType.SQLITE:
            return f"sqlite:///{self.database}"
        elif self.db_type == DatabaseType.MYSQL:
            return (
                f"mysql+pymysql://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        elif self.db_type == DatabaseType.POSTGRESQL:
            return (
                f"postgresql+psycopg2://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        elif self.db_type == DatabaseType.ORACLE:
            return (
                f"oracle+cx_oracle://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        elif self.db_type == DatabaseType.MSSQL:
            return (
                f"mssql+pyodbc://{self.username}:{self.password}"
                f"@{self.host}:{self.port}/{self.database}"
            )
        elif self.db_type == DatabaseType.DUCKDB:
            return f"duckdb:///{self.database}"
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


class DatabaseManager:
    """数据库管理器
    
    提供统一的数据库操作接口，支持多种数据库类型
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
        self._engine: Optional[Engine] = None
        self._schema_cache: Optional[DatabaseSchema] = None
        
    def _get_engine(self) -> Engine:
        """获取数据库引擎（带缓存）"""
        if self._engine is None:
            self._engine = create_engine(
                self.config.get_connection_url(),
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle
            )
        return self._engine
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        engine = self._get_engine()
        conn = engine.connect()
        try:
            yield conn
        finally:
            conn.close()
            
    def _map_column_type(self, type_str: str) -> ColumnType:
        """映射列类型"""
        type_lower = type_str.lower().split("(")[0].strip()
        return self.TYPE_MAPPING.get(type_lower, ColumnType.UNKNOWN)
    
    def get_tables(self) -> List[str]:
        """获取所有表名"""
        engine = self._get_engine()
        inspector = inspect(engine)
        return inspector.get_table_names()
    
    def get_table_info(self, table_name: str) -> TableInfo:
        """获取表的详细信息
        
        Args:
            table_name: 表名
            
        Returns:
            表信息对象
        """
        engine = self._get_engine()
        inspector = inspect(engine)
        
        # 获取列信息
        columns = []
        pk_columns = set()
        
        # 获取主键
        pk_constraint = inspector.get_pk_constraint(table_name)
        if pk_constraint:
            pk_columns = set(pk_constraint.get("constrained_columns", []))
        
        # 获取外键
        fk_map = {}
        for fk in inspector.get_foreign_keys(table_name):
            for i, col in enumerate(fk.get("constrained_columns", [])):
                ref_cols = fk.get("referred_columns", [])
                ref_table = fk.get("referred_table", "")
                if i < len(ref_cols):
                    fk_map[col] = f"{ref_table}.{ref_cols[i]}"
        
        # 获取列详情
        for col in inspector.get_columns(table_name):
            col_info = ColumnInfo(
                name=col["name"],
                data_type=str(col["type"]),
                column_type=self._map_column_type(str(col["type"])),
                nullable=col.get("nullable", True),
                primary_key=col["name"] in pk_columns,
                foreign_key=fk_map.get(col["name"]),
                default=str(col.get("default")) if col.get("default") else None,
                comment=col.get("comment")
            )
            columns.append(col_info)
        
        # 获取索引信息
        indexes = []
        for idx in inspector.get_indexes(table_name):
            index_info = IndexInfo(
                name=idx["name"],
                columns=idx.get("column_names", []),
                unique=idx.get("unique", False)
            )
            indexes.append(index_info)
        
        return TableInfo(
            name=table_name,
            columns=columns,
            indexes=indexes
        )
    
    def get_schema(self, force_refresh: bool = False) -> DatabaseSchema:
        """获取完整的数据库Schema
        
        Args:
            force_refresh: 是否强制刷新缓存
            
        Returns:
            数据库Schema对象
        """
        if self._schema_cache and not force_refresh:
            return self._schema_cache
        
        tables = []
        relationships = []
        
        for table_name in self.get_tables():
            table_info = self.get_table_info(table_name)
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
    
    def execute_query(
        self, 
        sql: str, 
        params: Optional[Dict[str, Any]] = None,
        pagination: Optional[PaginationInfo] = None
    ) -> QueryResult:
        """执行SQL查询
        
        Args:
            sql: SQL语句
            params: 查询参数
            pagination: 分页信息
            
        Returns:
            查询结果
        """
        start_time = time.time()
        
        try:
            with self.get_connection() as conn:
                # 执行查询
                result = conn.execute(text(sql), params or {})
                
                # 获取列名
                columns = list(result.keys())
                
                # 获取数据
                rows = result.fetchall()
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
                
        except SQLAlchemyError as e:
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
    
    def execute_query_with_pagination(
        self,
        sql: str,
        page: int = 1,
        page_size: int = 100,
        params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """执行带分页的查询
        
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
        result = self.execute_query(paginated_sql, params)
        
        if result.success:
            # 获取总数
            count_sql = f"SELECT COUNT(*) as cnt FROM ({sql.rstrip(';')}) as t"
            count_result = self.execute_query(count_sql, params)
            
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
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试数据库连接
        
        Returns:
            (成功标志, 消息)
        """
        try:
            with self.get_connection() as conn:
                conn.execute(text("SELECT 1"))
            return True, "Connection successful"
        except Exception as e:
            return False, str(e)
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# 连接管理器
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
        _connections[connection_id].close()
    
    manager = DatabaseManager(config)
    _connections[connection_id] = manager
    return manager


def close_connection(connection_id: int) -> None:
    """关闭指定连接"""
    global _connections
    
    if connection_id in _connections:
        _connections[connection_id].close()
        del _connections[connection_id]


def close_all_connections() -> None:
    """关闭所有连接"""
    global _connections
    
    for manager in _connections.values():
        manager.close()
    _connections.clear()
