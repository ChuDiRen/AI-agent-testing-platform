"""
Schema相关工具

提供表结构检索、值映射等功能
"""

from typing import Any, Dict, List, Optional
from langchain_core.tools import tool

from text2sql.database.db_manager import get_database_manager, DatabaseManager
from text2sql.models.schema_models import TableInfo, DatabaseSchema


def _get_manager(connection_id: int) -> DatabaseManager:
    """获取数据库管理器"""
    return get_database_manager(connection_id)


@tool
def get_tables(connection_id: int) -> List[str]:
    """获取数据库中所有表的列表
    
    Args:
        connection_id: 数据库连接ID
        
    Returns:
        表名列表
    """
    manager = _get_manager(connection_id)
    return manager.get_tables()


@tool
def get_table_schema(connection_id: int, table_name: str) -> Dict[str, Any]:
    """获取指定表的详细结构
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        
    Returns:
        表结构信息，包含列、类型、约束等
    """
    manager = _get_manager(connection_id)
    table_info = manager.get_table_info(table_name)
    return table_info.to_dict()


@tool
def get_table_columns(connection_id: int, table_name: str) -> List[Dict[str, Any]]:
    """获取表的列信息
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        
    Returns:
        列信息列表
    """
    manager = _get_manager(connection_id)
    table_info = manager.get_table_info(table_name)
    return [col.to_dict() for col in table_info.columns]


@tool
def get_primary_key(connection_id: int, table_name: str) -> Optional[str]:
    """获取表的主键列名
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        
    Returns:
        主键列名，如果没有主键返回None
    """
    manager = _get_manager(connection_id)
    table_info = manager.get_table_info(table_name)
    return table_info.get_primary_key()


@tool
def get_foreign_keys(connection_id: int, table_name: str) -> List[Dict[str, str]]:
    """获取表的外键信息
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        
    Returns:
        外键信息列表
    """
    manager = _get_manager(connection_id)
    table_info = manager.get_table_info(table_name)
    
    fks = []
    for col in table_info.columns:
        if col.foreign_key:
            parts = col.foreign_key.split(".")
            if len(parts) == 2:
                fks.append({
                    "column": col.name,
                    "references_table": parts[0],
                    "references_column": parts[1]
                })
    return fks


@tool
def get_related_tables(connection_id: int, table_name: str) -> List[str]:
    """获取与指定表相关的所有表
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        
    Returns:
        相关表名列表
    """
    manager = _get_manager(connection_id)
    schema = manager.get_schema()
    return schema.get_related_tables(table_name)


@tool
def get_database_schema(connection_id: int) -> Dict[str, Any]:
    """获取完整的数据库Schema
    
    Args:
        connection_id: 数据库连接ID
        
    Returns:
        数据库Schema信息
    """
    manager = _get_manager(connection_id)
    schema = manager.get_schema()
    return schema.to_dict()


@tool
def search_column_values(
    connection_id: int, 
    table_name: str, 
    column_name: str,
    search_term: str,
    limit: int = 10
) -> List[Any]:
    """在指定列中搜索匹配的值
    
    用于值映射，将用户输入映射到实际的数据库值
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        column_name: 列名
        search_term: 搜索词
        limit: 最大返回数量
        
    Returns:
        匹配的值列表
    """
    manager = _get_manager(connection_id)
    
    # 使用LIKE搜索
    sql = f"""
        SELECT DISTINCT {column_name} 
        FROM {table_name} 
        WHERE {column_name} LIKE :term
        LIMIT :limit
    """
    
    result = manager.execute_query(sql, {
        "term": f"%{search_term}%",
        "limit": limit
    })
    
    if result.success:
        return [row[column_name] for row in result.data]
    return []


@tool
def get_sample_data(
    connection_id: int, 
    table_name: str, 
    limit: int = 5
) -> List[Dict[str, Any]]:
    """获取表的样本数据
    
    用于理解表的数据结构和内容
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        limit: 样本数量
        
    Returns:
        样本数据列表
    """
    manager = _get_manager(connection_id)
    
    sql = f"SELECT * FROM {table_name} LIMIT :limit"
    result = manager.execute_query(sql, {"limit": limit})
    
    if result.success:
        return result.data
    return []


@tool  
def get_column_statistics(
    connection_id: int,
    table_name: str,
    column_name: str
) -> Dict[str, Any]:
    """获取列的统计信息
    
    Args:
        connection_id: 数据库连接ID
        table_name: 表名
        column_name: 列名
        
    Returns:
        统计信息（类型、唯一值数量、NULL数量等）
    """
    manager = _get_manager(connection_id)
    
    sql = f"""
        SELECT 
            COUNT(*) as total_count,
            COUNT(DISTINCT {column_name}) as unique_count,
            COUNT(*) - COUNT({column_name}) as null_count
        FROM {table_name}
    """
    
    result = manager.execute_query(sql)
    
    if result.success and result.data:
        stats = result.data[0]
        stats["table_name"] = table_name
        stats["column_name"] = column_name
        return stats
    
    return {
        "table_name": table_name,
        "column_name": column_name,
        "error": "Failed to get statistics"
    }


# 工具列表
SCHEMA_TOOLS = [
    get_tables,
    get_table_schema,
    get_table_columns,
    get_primary_key,
    get_foreign_keys,
    get_related_tables,
    get_database_schema,
    search_column_values,
    get_sample_data,
    get_column_statistics
]
