"""
SQL相关工具

提供SQL解析、优化等功能
"""

import re
from typing import Any, Dict, List, Optional, Tuple
from langchain_core.tools import tool


class SQLParser:
    """SQL解析器"""
    
    # 关键字模式
    SELECT_PATTERN = re.compile(r'\bSELECT\b', re.IGNORECASE)
    FROM_PATTERN = re.compile(r'\bFROM\b', re.IGNORECASE)
    WHERE_PATTERN = re.compile(r'\bWHERE\b', re.IGNORECASE)
    JOIN_PATTERN = re.compile(r'\b(INNER|LEFT|RIGHT|FULL|CROSS)?\s*JOIN\b', re.IGNORECASE)
    GROUP_BY_PATTERN = re.compile(r'\bGROUP\s+BY\b', re.IGNORECASE)
    ORDER_BY_PATTERN = re.compile(r'\bORDER\s+BY\b', re.IGNORECASE)
    LIMIT_PATTERN = re.compile(r'\bLIMIT\b', re.IGNORECASE)
    
    # 聚合函数
    AGGREGATE_FUNCTIONS = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'GROUP_CONCAT']
    
    @classmethod
    def parse(cls, sql: str) -> Dict[str, Any]:
        """解析SQL语句
        
        Args:
            sql: SQL语句
            
        Returns:
            解析结果
        """
        sql = sql.strip()
        
        return {
            "type": cls._get_query_type(sql),
            "has_select": bool(cls.SELECT_PATTERN.search(sql)),
            "has_from": bool(cls.FROM_PATTERN.search(sql)),
            "has_where": bool(cls.WHERE_PATTERN.search(sql)),
            "has_join": bool(cls.JOIN_PATTERN.search(sql)),
            "has_group_by": bool(cls.GROUP_BY_PATTERN.search(sql)),
            "has_order_by": bool(cls.ORDER_BY_PATTERN.search(sql)),
            "has_limit": bool(cls.LIMIT_PATTERN.search(sql)),
            "has_aggregation": cls._has_aggregation(sql),
            "tables": cls._extract_tables(sql),
            "join_count": len(cls.JOIN_PATTERN.findall(sql))
        }
    
    @classmethod
    def _get_query_type(cls, sql: str) -> str:
        """获取查询类型"""
        sql_upper = sql.upper().strip()
        if sql_upper.startswith("SELECT"):
            return "SELECT"
        elif sql_upper.startswith("INSERT"):
            return "INSERT"
        elif sql_upper.startswith("UPDATE"):
            return "UPDATE"
        elif sql_upper.startswith("DELETE"):
            return "DELETE"
        elif sql_upper.startswith("CREATE"):
            return "CREATE"
        elif sql_upper.startswith("DROP"):
            return "DROP"
        elif sql_upper.startswith("ALTER"):
            return "ALTER"
        return "UNKNOWN"
    
    @classmethod
    def _has_aggregation(cls, sql: str) -> bool:
        """检查是否包含聚合函数"""
        sql_upper = sql.upper()
        for func in cls.AGGREGATE_FUNCTIONS:
            if f"{func}(" in sql_upper:
                return True
        return False
    
    @classmethod
    def _extract_tables(cls, sql: str) -> List[str]:
        """提取表名（简单实现）"""
        tables = []
        
        # 从FROM子句提取
        from_match = re.search(
            r'\bFROM\s+([^\s,;(]+)',
            sql,
            re.IGNORECASE
        )
        if from_match:
            tables.append(from_match.group(1).strip('`"[]'))
        
        # 从JOIN子句提取
        join_matches = re.findall(
            r'\bJOIN\s+([^\s,;(]+)',
            sql,
            re.IGNORECASE
        )
        for match in join_matches:
            tables.append(match.strip('`"[]'))
        
        return list(set(tables))


@tool
def parse_sql(sql: str) -> Dict[str, Any]:
    """解析SQL语句，获取结构信息
    
    Args:
        sql: SQL语句
        
    Returns:
        解析结果，包含查询类型、表名、是否有聚合等
    """
    return SQLParser.parse(sql)


@tool
def format_sql(sql: str) -> str:
    """格式化SQL语句
    
    Args:
        sql: SQL语句
        
    Returns:
        格式化后的SQL
    """
    # 简单格式化：关键字大写，添加换行
    keywords = [
        'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'JOIN',
        'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'OUTER JOIN',
        'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT', 'OFFSET',
        'ON', 'AS', 'DISTINCT', 'UNION', 'EXCEPT', 'INTERSECT'
    ]
    
    formatted = sql.strip()
    
    # 关键字大写
    for kw in keywords:
        pattern = re.compile(rf'\b{kw}\b', re.IGNORECASE)
        formatted = pattern.sub(kw, formatted)
    
    # 在主要关键字前添加换行
    for kw in ['FROM', 'WHERE', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN', 
               'INNER JOIN', 'GROUP BY', 'ORDER BY', 'HAVING', 'LIMIT']:
        formatted = re.sub(rf'\s+{kw}\b', f'\n{kw}', formatted)
    
    return formatted.strip()


@tool
def add_limit(sql: str, limit: int = 100) -> str:
    """为SQL添加LIMIT子句
    
    如果已有LIMIT则不添加
    
    Args:
        sql: SQL语句
        limit: 限制数量
        
    Returns:
        添加LIMIT后的SQL
    """
    sql = sql.strip().rstrip(';')
    
    if re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
        return sql + ';'
    
    return f"{sql} LIMIT {limit};"


@tool
def validate_select_only(sql: str) -> Tuple[bool, str]:
    """验证SQL是否只是SELECT语句
    
    Args:
        sql: SQL语句
        
    Returns:
        (是否有效, 错误消息)
    """
    parsed = SQLParser.parse(sql)
    
    if parsed["type"] != "SELECT":
        return False, f"Only SELECT statements are allowed, got: {parsed['type']}"
    
    # 检查危险关键字
    dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 'ALTER', 'CREATE']
    sql_upper = sql.upper()
    
    for kw in dangerous:
        if f' {kw} ' in f' {sql_upper} ':
            return False, f"Dangerous keyword detected: {kw}"
    
    return True, ""


@tool
def optimize_sql(sql: str) -> Dict[str, Any]:
    """分析SQL并提供优化建议
    
    Args:
        sql: SQL语句
        
    Returns:
        优化建议
    """
    parsed = SQLParser.parse(sql)
    suggestions = []
    
    # 检查SELECT *
    if re.search(r'\bSELECT\s+\*', sql, re.IGNORECASE):
        suggestions.append({
            "type": "performance",
            "message": "避免使用SELECT *，只查询需要的列"
        })
    
    # 检查JOIN数量
    if parsed["join_count"] > 3:
        suggestions.append({
            "type": "performance",
            "message": f"JOIN数量较多({parsed['join_count']}个)，可能影响性能"
        })
    
    # 检查是否有WHERE子句
    if not parsed["has_where"] and not parsed["has_limit"]:
        suggestions.append({
            "type": "warning",
            "message": "没有WHERE条件和LIMIT限制，可能返回大量数据"
        })
    
    # 检查是否有LIMIT
    if not parsed["has_limit"]:
        suggestions.append({
            "type": "suggestion",
            "message": "建议添加LIMIT限制结果数量"
        })
    
    # 检查聚合查询是否有GROUP BY
    if parsed["has_aggregation"] and not parsed["has_group_by"]:
        if not re.search(r'\bCOUNT\s*\(\s*\*\s*\)', sql, re.IGNORECASE):
            suggestions.append({
                "type": "warning", 
                "message": "聚合查询可能需要GROUP BY子句"
            })
    
    return {
        "original_sql": sql,
        "parsed": parsed,
        "suggestions": suggestions,
        "suggestion_count": len(suggestions)
    }


@tool
def extract_parameters(sql: str) -> List[str]:
    """提取SQL中的参数占位符
    
    Args:
        sql: SQL语句
        
    Returns:
        参数名列表
    """
    # 匹配:param形式的参数
    named_params = re.findall(r':(\w+)', sql)
    
    # 匹配%s形式的参数（位置参数）
    positional_count = sql.count('%s')
    
    if named_params:
        return named_params
    elif positional_count > 0:
        return [f"param_{i}" for i in range(positional_count)]
    
    return []


# 工具列表
SQL_TOOLS = [
    parse_sql,
    format_sql,
    add_limit,
    validate_select_only,
    optimize_sql,
    extract_parameters
]
