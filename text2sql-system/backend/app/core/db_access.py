"""
数据库访问层 - 支持多种数据库类型
"""
import os
import sqlite3
import asyncio
from typing import Optional, Any
from contextlib import contextmanager

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from loguru import logger


class DBAccess:
    """
    数据库访问类，支持多种数据库类型
    
    支持的数据库:
    - SQLite: 轻量级文件数据库
    - MySQL: 开源关系型数据库
    - PostgreSQL: 高级开源数据库
    """

    def __init__(self, database_url: str, database_type: str = "sqlite"):
        """
        初始化数据库访问

        Args:
            database_url: 数据库连接URL
            database_type: 数据库类型 (sqlite, mysql, postgresql)
        """
        self.database_url = database_url
        self.database_type = database_type.lower()
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()

    def _initialize_connection(self):
        """初始化数据库连接"""
        try:
            if self.database_type == "sqlite":
                # SQLite连接
                self._init_sqlite_connection()
            elif self.database_type == "mysql":
                # MySQL连接
                self._init_mysql_connection()
            elif self.database_type == "postgresql":
                # PostgreSQL连接
                self._init_postgresql_connection()
            else:
                raise ValueError(f"不支持的数据库类型: {self.database_type}")

            logger.info(f"数据库连接初始化成功: {self.database_type}")

        except Exception as e:
            logger.error(f"数据库连接初始化失败: {str(e)}")
            raise

    def _init_sqlite_connection(self):
        """初始化SQLite连接"""
        # 确保数据目录存在
        db_path = self.database_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)

        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        # 检查数据库文件是否存在，不存在则尝试下载Chinook示例数据库
        if not os.path.exists(db_path):
            logger.info(f"数据库文件不存在: {db_path}")
            logger.info("将使用空数据库，请在data目录放置chinook.db文件")

        # 创建SQLAlchemy引擎
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _init_mysql_connection(self):
        """初始化MySQL连接"""
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def _init_postgresql_connection(self):
        """初始化PostgreSQL连接"""
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    @contextmanager
    def get_session(self):
        """获取数据库会话上下文管理器"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def run_sql(self, sql: str) -> Optional[pd.DataFrame]:
        """
        执行SQL查询并返回DataFrame

        Args:
            sql: SQL查询语句

        Returns:
            pandas DataFrame包含查询结果，如果失败则返回None
        """
        try:
            # 使用pandas执行SQL查询
            result_df = pd.read_sql_query(
                sql,
                self.engine
            )
            logger.info(f"SQL执行成功: 返回{len(result_df)}行数据")
            return result_df

        except Exception as e:
            logger.error(f"SQL执行失败: {str(e)}")
            logger.error(f"SQL语句: {sql}")
            raise

    async def run_sql_async(self, sql: str) -> Any:
        """
        异步执行SQL查询

        Args:
            sql: SQL查询语句

        Returns:
            查询结果
        """
        try:
            # 在线程池中执行同步SQL
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,  # 使用默认的executor
                self.run_sql,
                sql
            )
            return result

        except Exception as e:
            logger.error(f"异步SQL执行失败: {str(e)}")
            raise

    def get_table_schema(self, table_name: str) -> Optional[dict]:
        """
        获取表结构信息

        Args:
            table_name: 表名

        Returns:
            表结构字典
        """
        try:
            query = f"PRAGMA table_info({table_name})" if self.database_type == "sqlite" else f"DESCRIBE {table_name}"
            result_df = self.run_sql(query)
            
            if result_df is not None and not result_df.empty:
                return {
                    "table_name": table_name,
                    "columns": result_df.to_dict('records'),
                    "database_type": self.database_type
                }
            return None

        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            return None

    def get_database_schema(self) -> dict:
        """
        获取完整数据库schema

        Returns:
            数据库schema字典
        """
        try:
            if self.database_type == "sqlite":
                # SQLite获取所有表
                query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            else:
                # MySQL/PostgreSQL获取所有表
                query = "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()"

            tables_df = self.run_sql(query)
            
            tables = []
            if tables_df is not None and not tables_df.empty:
                table_names = tables_df.iloc[:, 0].tolist()
                
                # 获取每个表的结构
                for table_name in table_names:
                    table_schema = self.get_table_schema(table_name)
                    if table_schema:
                        tables.append(table_schema)

            return {
                "database_type": self.database_type,
                "tables": tables,
                "table_count": len(tables)
            }

        except Exception as e:
            logger.error(f"获取数据库schema失败: {str(e)}")
            return {
                "database_type": self.database_type,
                "tables": [],
                "table_count": 0,
                "error": str(e)
            }

    def test_connection(self) -> bool:
        """
        测试数据库连接

        Returns:
            连接是否成功
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("数据库连接测试成功")
            return True

        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False

    def close(self):
        """关闭数据库连接"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {str(e)}")


# 全局数据库访问实例（延迟初始化）
_db_access_instance: Optional[DBAccess] = None


def get_db_access(database_url: str, database_type: str = "sqlite") -> DBAccess:
    """
    获取数据库访问实例（单例模式）

    Args:
        database_url: 数据库URL
        database_type: 数据库类型

    Returns:
        DBAccess实例
    """
    global _db_access_instance

    if _db_access_instance is None:
        _db_access_instance = DBAccess(database_url, database_type)

    return _db_access_instance
