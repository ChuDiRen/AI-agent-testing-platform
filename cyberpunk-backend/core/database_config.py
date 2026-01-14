"""
数据库配置 - SQLite/PostgreSQL配置

职责：
- 数据库连接配置
- 连接池管理
- 数据库迁移
- 事务管理
- 性能优化
"""
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
import json

# 数据库相关导入
try:
    import asyncpg
    import asyncpg.pool
    import asyncpg.transaction
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import aiosqlite
    import aiosqlite.pool
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

from core.logging_config import get_logger

logger = get_logger(__name__)


class DatabaseType(str, Enum):
    """数据库类型枚举"""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class IsolationLevel(str, Enum):
    """事务隔离级别"""
    READ_COMMITTED = "read committed"
    REPEATABLE_READ = "repeatable read"
    SERIALIZABLE = "serializable"


@dataclass
class DatabaseConfig:
    """数据库配置数据模型"""
    db_type: DatabaseType
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_string: Optional[str] = None
    max_connections: int = 10
    min_connections: int = 1
    connection_timeout: int = 30
    query_timeout: int = 60
    ssl_mode: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    ssl_ca: Optional[str] = None
    pool_recycle: int = 3600  # 1小时
    pool_pre_ping: bool = True
    echo: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """验证配置"""
        if self.db_type == DatabaseType.POSTGRESQL:
            if not POSTGRES_AVAILABLE:
                raise ImportError("asyncpg not available. Install with: pip install asyncpg")
            
            # PostgreSQL需要连接字符串或基本参数
            if not self.connection_string:
                if not all([self.host, self.database, self.username]):
                    raise ValueError("PostgreSQL requires connection_string or (host, database, username)")
        elif self.db_type == DatabaseType.SQLITE:
            if not SQLITE_AVAILABLE:
                raise ImportError("aiosqlite not available. Install with: pip install aiosqlite")
            
            # SQLite需要数据库文件路径
            if not self.connection_string and not self.database:
                raise ValueError("SQLite requires database file path")

    def get_connection_string(self) -> str:
        """获取数据库连接字符串"""
        if self.connection_string:
            return self.connection_string
        
        if self.db_type == DatabaseType.POSTGRESQL:
            # 构建PostgreSQL连接字符串
            parts = []
            if self.host:
                parts.append(f"host={self.host}")
            if self.port:
                parts.append(f"port={self.port}")
            if self.database:
                parts.append(f"database={self.database}")
            if self.username:
                parts.append(f"user={self.username}")
            if self.password:
                parts.append(f"password={self.password}")
            if self.ssl_mode:
                parts.append(f"sslmode={self.ssl_mode}")
            
            return " ".join(parts)
        
        elif self.db_type == DatabaseType.SQLITE:
            # SQLite使用文件路径
            return self.database or "api_automation.db"
        
        return ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（隐藏敏感信息）"""
        config_dict = {
            "db_type": self.db_type.value,
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "username": self.username,
            "max_connections": self.max_connections,
            "min_connections": self.min_connections,
            "connection_timeout": self.connection_timeout,
            "query_timeout": self.query_timeout,
            "ssl_mode": self.ssl_mode,
            "pool_recycle": self.pool_recycle,
            "pool_pre_ping": self.pool_pre_ping,
            "echo": self.echo,
            "metadata": self.metadata
        }
        
        # 不包含密码
        config_dict.pop("password", None)
        
        return config_dict


class DatabaseConnection:
    """数据库连接包装器"""

    def __init__(self, config: DatabaseConfig):
        """初始化数据库连接"""
        self.config = config
        self.connection = None
        self.pool = None

    async def connect(self) -> bool:
        """建立数据库连接"""
        try:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                self.connection = await asyncpg.connect(
                    self.config.get_connection_string(),
                    server_settings={
                        "application_name": "api_automation_platform"
                    }
                )
            elif self.config.db_type == DatabaseType.SQLITE:
                self.connection = await aiosqlite.connect(
                    self.config.get_connection_string(),
                    check_same_thread=False
                )
            
            logger.info(f"数据库连接成功: {self.config.db_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"数据库连接失败: {e}", exc_info=e)
            return False

    async def disconnect(self):
        """断开数据库连接"""
        try:
            if self.connection:
                await self.connection.close()
                logger.info("数据库连接已断开")
        except Exception as e:
            logger.error(f"断开数据库连接失败: {e}", exc_info=e)

    async def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """执行查询"""
        try:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                if params:
                    rows = await self.connection.fetch(query, *params)
                else:
                    rows = await self.connection.fetch(query)
                return [dict(row) for row in rows]
            
            elif self.config.db_type == DatabaseType.SQLITE:
                if params:
                    cursor = await self.connection.execute(query, params)
                else:
                    cursor = await self.connection.execute(query)
                
                # 获取结果
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                    rows = await cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    return [{"affected_rows": cursor.rowcount}]
        
        except Exception as e:
            logger.error(f"执行查询失败: {e}", exc_info=e)
            raise

    async def execute_transaction(self, queries: List[tuple]) -> List[Dict[str, Any]]:
        """执行事务"""
        results = []
        
        try:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                async with self.connection.transaction():
                    for query, params in queries:
                        row = await self.connection.fetchrow(query, *params)
                        results.append(dict(row) if row else {})
            
            elif self.config.db_type == DatabaseType.SQLITE:
                async with self.connection.execute("BEGIN"):
                    try:
                        for query, params in queries:
                            cursor = await self.connection.execute(query, params)
                            if cursor.description:
                                columns = [desc[0] for desc in cursor.description]
                                row = await cursor.fetchone()
                                results.append(dict(zip(columns, row)) if row else {})
                            else:
                                results.append({"affected_rows": cursor.rowcount})
                        
                        await self.connection.execute("COMMIT")
                    except Exception:
                        await self.connection.execute("ROLLBACK")
                        raise
        
        except Exception as e:
            logger.error(f"执行事务失败: {e}", exc_info=e)
            raise

    async def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """创建表"""
        try:
            # 构建CREATE TABLE语句
            column_defs = []
            for col_name, col_type in columns.items():
                column_defs.append(f"{col_name} {col_type}")
            
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {", ".join(column_defs)}
            )
            """
            
            await self.execute_query(create_sql)
            logger.info(f"表创建成功: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"创建表失败: {e}", exc_info=e)
            return False

    async def table_exists(self, table_name: str) -> bool:
        """检查表是否存在"""
        try:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                query = """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = $1
                )
                """
                result = await self.execute_query(query, (table_name,))
            else:
                query = """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=?
                """
                result = await self.execute_query(query, (table_name,))
            
            return len(result) > 0 and result[0].get("exists") or len(result) > 0
            
        except Exception as e:
            logger.error(f"检查表存在性失败: {e}", exc_info=e)
            return False


class DatabasePool:
    """数据库连接池管理器"""

    def __init__(self, config: DatabaseConfig):
        """初始化连接池"""
        self.config = config
        self.pool = None

    async def initialize_pool(self) -> bool:
        """初始化连接池"""
        try:
            if self.config.db_type == DatabaseType.POSTGRESQL:
                self.pool = await asyncpg.create_pool(
                    self.config.get_connection_string(),
                    min_size=self.config.min_connections,
                    max_size=self.config.max_connections,
                    command_timeout=self.config.query_timeout,
                    server_settings={
                        "application_name": "api_automation_platform"
                    }
                )
            elif self.config.db_type == DatabaseType.SQLITE:
                # SQLite连接池（实际上是单连接）
                self.pool = await aiosqlite.connect(
                    self.config.get_connection_string(),
                    check_same_thread=False
                )
            
            logger.info(f"数据库连接池初始化成功: {self.config.db_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"初始化连接池失败: {e}", exc_info=e)
            return False

    async def get_connection(self) -> DatabaseConnection:
        """获取数据库连接"""
        if not self.pool:
            raise RuntimeError("连接池未初始化")
        
        if self.config.db_type == DatabaseType.POSTGRESQL:
            connection = await self.pool.acquire()
            return DatabaseConnection(self.config)
        else:
            return DatabaseConnection(self.config)

    async def close_pool(self):
        """关闭连接池"""
        try:
            if self.pool:
                if self.config.db_type == DatabaseType.POSTGRESQL:
                    await self.pool.close()
                else:
                    await self.pool.close()
                logger.info("数据库连接池已关闭")
        except Exception as e:
            logger.error(f"关闭连接池失败: {e}", exc_info=e)


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        """初始化数据库管理器"""
        self.configs: Dict[str, DatabaseConfig] = {}
        self.pools: Dict[str, DatabasePool] = {}
        self.connections: Dict[str, DatabaseConnection] = {}
        
        logger.info("数据库管理器初始化完成")

    def register_database(self, name: str, config: DatabaseConfig):
        """注册数据库配置"""
        self.configs[name] = config
        logger.info(f"数据库配置已注册: {name} ({config.db_type.value})")

    async def initialize_database(self, name: str) -> bool:
        """初始化数据库"""
        if name not in self.configs:
            raise ValueError(f"数据库配置不存在: {name}")
        
        config = self.configs[name]
        
        # 创建连接池
        pool = DatabasePool(config)
        success = await pool.initialize_pool()
        
        if success:
            self.pools[name] = pool
            logger.info(f"数据库初始化成功: {name}")
        else:
            logger.error(f"数据库初始化失败: {name}")
        
        return success

    async def get_connection(self, name: str) -> DatabaseConnection:
        """获取数据库连接"""
        if name not in self.pools:
            await self.initialize_database(name)
        
        # 对于SQLite，直接返回连接
        if self.configs[name].db_type == DatabaseType.SQLITE:
            if name not in self.connections:
                connection = DatabaseConnection(self.configs[name])
                await connection.connect()
                self.connections[name] = connection
            return self.connections[name]
        
        # 对于PostgreSQL，从池中获取
        return await self.pools[name].get_connection()

    async def execute_query(
        self, 
        db_name: str, 
        query: str, 
        params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """执行查询"""
        connection = await self.get_connection(db_name)
        return await connection.execute_query(query, params)

    async def execute_transaction(
        self, 
        db_name: str, 
        queries: List[tuple]
    ) -> List[Dict[str, Any]]:
        """执行事务"""
        connection = await self.get_connection(db_name)
        return await connection.execute_transaction(queries)

    async def create_table(
        self, 
        db_name: str, 
        table_name: str, 
        columns: Dict[str, str]
    ) -> bool:
        """创建表"""
        connection = await self.get_connection(db_name)
        return await connection.create_table(table_name, columns)

    async def table_exists(self, db_name: str, table_name: str) -> bool:
        """检查表是否存在"""
        connection = await self.get_connection(db_name)
        return await connection.table_exists(table_name)

    async def close_all(self):
        """关闭所有数据库连接"""
        try:
            # 关闭连接池
            for pool in self.pools.values():
                await pool.close_pool()
            
            # 关闭单连接
            for connection in self.connections.values():
                await connection.disconnect()
            
            self.pools.clear()
            self.connections.clear()
            
            logger.info("所有数据库连接已关闭")
            
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}", exc_info=e)

    def get_database_config(self, name: str) -> Optional[DatabaseConfig]:
        """获取数据库配置"""
        return self.configs.get(name)

    def list_databases(self) -> List[str]:
        """列出已配置的数据库"""
        return list(self.configs.keys())


# 预定义数据库配置
def create_sqlite_config(database_path: str = "api_automation.db") -> DatabaseConfig:
    """创建SQLite配置"""
    return DatabaseConfig(
        db_type=DatabaseType.SQLITE,
        database=database_path,
        max_connections=5,
        min_connections=1,
        connection_timeout=30,
        query_timeout=60,
        metadata={
            "description": "SQLite数据库配置",
            "use_case": "development, testing"
        }
    )


def create_postgresql_config(
    host: str = "localhost",
    port: int = 5432,
    database: str = "api_automation",
    username: str = "postgres",
    password: str = "",
    **kwargs
) -> DatabaseConfig:
    """创建PostgreSQL配置"""
    return DatabaseConfig(
        db_type=DatabaseType.POSTGRESQL,
        host=host,
        port=port,
        database=database,
        username=username,
        password=password,
        max_connections=10,
        min_connections=2,
        connection_timeout=30,
        query_timeout=60,
        pool_recycle=3600,
        pool_pre_ping=True,
        **kwargs
    )


# 数据库管理器实例
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """获取全局数据库管理器实例"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def create_database_manager() -> DatabaseManager:
    """创建新的数据库管理器实例"""
    return DatabaseManager()


# 上下文管理器
@asynccontextmanager
async def database_connection(db_name: str):
    """数据库连接上下文管理器"""
    db_manager = get_database_manager()
    connection = None
    
    try:
        connection = await db_manager.get_connection(db_name)
        yield connection
    finally:
        # 连接由管理器管理，这里不需要显式关闭
        pass


# 数据库迁移相关
class DatabaseMigration:
    """数据库迁移管理器"""

    def __init__(self, db_manager: DatabaseManager):
        """初始化迁移管理器"""
        self.db_manager = db_manager
        self.migrations_table = "schema_migrations"

    async def create_migrations_table(self, db_name: str) -> bool:
        """创建迁移记录表"""
        columns = {
            "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "version": "VARCHAR(255) NOT NULL UNIQUE",
            "description": "TEXT",
            "applied_at": "DATETIME DEFAULT CURRENT_TIMESTAMP",
            "checksum": "VARCHAR(64)"
        }
        
        return await self.db_manager.create_table(db_name, self.migrations_table, columns)

    async def apply_migration(
        self, 
        db_name: str, 
        version: str, 
        description: str, 
        sql: str
    ) -> bool:
        """应用迁移"""
        try:
            # 检查迁移是否已应用
            query = f"SELECT version FROM {self.migrations_table} WHERE version = ?"
            existing = await self.db_manager.execute_query(db_name, query, (version,))
            
            if existing:
                logger.info(f"迁移已存在，跳过: {version}")
                return True
            
            # 执行迁移SQL
            await self.db_manager.execute_query(db_name, sql)
            
            # 记录迁移
            insert_query = f"""
            INSERT INTO {self.migrations_table} (version, description) 
            VALUES (?, ?)
            """
            await self.db_manager.execute_query(db_name, insert_query, (version, description))
            
            logger.info(f"迁移应用成功: {version} - {description}")
            return True
            
        except Exception as e:
            logger.error(f"应用迁移失败: {version} - {e}", exc_info=e)
            return False

    async def get_applied_migrations(self, db_name: str) -> List[Dict[str, Any]]:
        """获取已应用的迁移"""
        query = f"SELECT version, description, applied_at FROM {self.migrations_table} ORDER BY version"
        return await self.db_manager.execute_query(db_name, query)


# 预定义迁移
PREDEFINED_MIGRATIONS = {
    "001_create_tasks_table": {
        "description": "创建任务管理表",
        "sql": """
        CREATE TABLE IF NOT EXISTS tasks (
            id VARCHAR(255) PRIMARY KEY,
            task_type VARCHAR(100) NOT NULL,
            task_name VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            progress FLOAT DEFAULT 0.0,
            result TEXT,
            error_message TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
        """
    },
    "002_create_test_results_table": {
        "description": "创建测试结果表",
        "sql": """
        CREATE TABLE IF NOT EXISTS test_results (
            id VARCHAR(255) PRIMARY KEY,
            task_id VARCHAR(255),
            test_name VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL,
            duration_ms INTEGER,
            error_message TEXT,
            result_data TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id)
        )
        """
    },
    "003_create_api_endpoints_table": {
        "description": "创建API端点表",
        "sql": """
        CREATE TABLE IF NOT EXISTS api_endpoints (
            id VARCHAR(255) PRIMARY KEY,
            path VARCHAR(500) NOT NULL,
            method VARCHAR(10) NOT NULL,
            operation_id VARCHAR(255),
            summary TEXT,
            description TEXT,
            parameters TEXT,
            request_body TEXT,
            responses TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    }
}


# 使用示例
async def setup_default_databases():
    """设置默认数据库"""
    db_manager = get_database_manager()
    
    # 注册开发数据库（SQLite）
    sqlite_config = create_sqlite_config("data/api_automation.db")
    db_manager.register_database("development", sqlite_config)
    
    # 注册生产数据库（PostgreSQL）
    postgresql_config = create_postgresql_config(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "api_automation"),
        username=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )
    db_manager.register_database("production", postgresql_config)
    
    # 初始化数据库
    for db_name in db_manager.list_databases():
        await db_manager.initialize_database(db_name)
        
        # 应用预定义迁移
        migration = DatabaseMigration(db_manager)
        await migration.create_migrations_table(db_name)
        
        for version, migration_info in PREDEFINED_MIGRATIONS.items():
            await migration.apply_migration(
                db_name,
                version,
                migration_info["description"],
                migration_info["sql"]
            )


if __name__ == "__main__":
    # 测试数据库配置
    import asyncio
    
    async def test_database_config():
        # 创建SQLite配置
        sqlite_config = create_sqlite_config("test.db")
        print(f"SQLite配置: {sqlite_config.to_dict()}")
        
        # 创建PostgreSQL配置
        postgresql_config = create_postgresql_config(
            host="localhost",
            database="test_db",
            username="test_user"
        )
        print(f"PostgreSQL配置: {postgresql_config.to_dict()}")
        
        # 测试数据库管理器
        db_manager = create_database_manager()
        db_manager.register_database("test_sqlite", sqlite_config)
        
        print(f"已配置的数据库: {db_manager.list_databases()}")
    
    asyncio.run(test_database_config())
