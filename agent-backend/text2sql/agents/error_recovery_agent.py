"""
错误恢复代理

智能错误分析和自动修复
"""

import re
from typing import Any, Dict, List
from difflib import get_close_matches

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from ..config import get_model
from ..prompts import load_prompt


def create_recovery_tools(connection_id: int = 0) -> List:
    """创建恢复工具（增强版）
    
    Args:
        connection_id: 数据库连接 ID
        
    Returns:
        工具列表
    """
    
    @tool
    def analyze_error(error_message: str, sql: str) -> Dict[str, Any]:
        """分析错误信息
        
        详细分析 SQL 执行错误，提取错误类型、位置和可能的原因。
        
        Args:
            error_message: 错误消息
            sql: 相关SQL
            
        Returns:
            错误分析结果
        """
        error_lower = error_message.lower()
        
        # 识别错误类型和详细信息
        error_type = "UNKNOWN"
        recoverable = False
        error_details = {}
        
        if "syntax" in error_lower or "near" in error_lower:
            error_type = "SYNTAX_ERROR"
            recoverable = True
            # 尝试提取错误位置
            near_match = re.search(r'near\s*["\']([^"\']+)["\']', error_message, re.IGNORECASE)
            if near_match:
                error_details["error_near"] = near_match.group(1)
                
        elif "no such table" in error_lower:
            error_type = "TABLE_NOT_FOUND"
            recoverable = True
            # 提取表名
            table_match = re.search(r'no such table:\s*(\w+)', error_message, re.IGNORECASE)
            if table_match:
                error_details["missing_table"] = table_match.group(1)
                
        elif "no such column" in error_lower:
            error_type = "COLUMN_NOT_FOUND"
            recoverable = True
            # 提取列名
            col_match = re.search(r'no such column:\s*(\w+\.)?(\w+)', error_message, re.IGNORECASE)
            if col_match:
                error_details["missing_column"] = col_match.group(2)
                if col_match.group(1):
                    error_details["table_prefix"] = col_match.group(1).rstrip('.')
                    
        elif "ambiguous" in error_lower:
            error_type = "AMBIGUOUS_COLUMN"
            recoverable = True
            col_match = re.search(r'ambiguous column[:\s]+(\w+)', error_message, re.IGNORECASE)
            if col_match:
                error_details["ambiguous_column"] = col_match.group(1)
                
        elif "not exist" in error_lower or "unknown" in error_lower:
            error_type = "NOT_FOUND"
            recoverable = True
            
        elif "timeout" in error_lower:
            error_type = "TIMEOUT"
            recoverable = True
            
        elif "permission" in error_lower or "access" in error_lower:
            error_type = "PERMISSION_DENIED"
            recoverable = False
            
        elif "security" in error_lower:
            error_type = "SECURITY_VIOLATION"
            recoverable = False
        
        return {
            "error_type": error_type,
            "recoverable": recoverable,
            "original_error": error_message,
            "sql": sql,
            "details": error_details
        }
    
    @tool
    def suggest_fix(error_type: str, sql: str, context: str = "") -> Dict[str, Any]:
        """建议修复方案
        
        根据错误类型提供修复建议。
        
        Args:
            error_type: 错误类型
            sql: 原始SQL
            context: 额外上下文（如可用的表名、列名）
            
        Returns:
            修复建议
        """
        suggestions = {
            "SYNTAX_ERROR": [
                "检查 SQL 关键字拼写（SELECT, FROM, WHERE, JOIN, ON 等）",
                "检查括号和引号是否匹配",
                "检查逗号分隔是否正确",
                "检查 AS 别名语法"
            ],
            "TABLE_NOT_FOUND": [
                "检查表名拼写是否正确",
                "检查表名大小写（SQLite 区分大小写）",
                "使用 list_available_tables 工具查看可用表"
            ],
            "COLUMN_NOT_FOUND": [
                "检查列名拼写是否正确",
                "检查列名大小写",
                "确认列属于正确的表",
                "使用 get_table_schema 工具查看表结构"
            ],
            "AMBIGUOUS_COLUMN": [
                "为列名添加表别名前缀（如 t.column_name）",
                "确保 JOIN 的表都有别名"
            ],
            "NOT_FOUND": [
                "检查表名是否正确",
                "检查列名是否存在",
                "检查大小写是否匹配"
            ],
            "TIMEOUT": [
                "添加 LIMIT 限制结果数量",
                "减少 JOIN 数量",
                "添加 WHERE 条件过滤数据"
            ],
            "PERMISSION_DENIED": [
                "联系数据库管理员",
                "检查用户权限"
            ],
            "SECURITY_VIOLATION": [
                "不允许执行此操作"
            ]
        }
        
        return {
            "error_type": error_type,
            "suggestions": suggestions.get(error_type, ["无法确定修复方案"]),
            "auto_fixable": error_type in ["SYNTAX_ERROR", "TABLE_NOT_FOUND", "COLUMN_NOT_FOUND", "AMBIGUOUS_COLUMN", "TIMEOUT"]
        }
    
    @tool
    def auto_fix_sql(
        sql: str,
        error_type: str,
        error_details: Dict[str, Any] = None,
        available_tables: List[str] = None,
        available_columns: Dict[str, List[str]] = None
    ) -> Dict[str, Any]:
        """自动修复 SQL 语法错误
        
        根据错误类型和上下文信息，尝试自动修复 SQL。
        
        Args:
            sql: 原始 SQL
            error_type: 错误类型
            error_details: 错误详情（从 analyze_error 获取）
            available_tables: 可用的表名列表
            available_columns: 表的列信息 {"table_name": ["col1", "col2"]}
            
        Returns:
            修复结果
        """
        fixed_sql = sql
        fixes_applied = []
        
        error_details = error_details or {}
        available_tables = available_tables or []
        available_columns = available_columns or {}
        
        # 1. 修复表名不存在
        if error_type == "TABLE_NOT_FOUND" and "missing_table" in error_details:
            missing = error_details["missing_table"]
            matches = get_close_matches(missing, available_tables, n=1, cutoff=0.6)
            if matches:
                fixed_sql = re.sub(
                    rf'\b{re.escape(missing)}\b',
                    matches[0],
                    fixed_sql,
                    flags=re.IGNORECASE
                )
                fixes_applied.append(f"表名 '{missing}' → '{matches[0]}'")
        
        # 2. 修复列名不存在
        if error_type == "COLUMN_NOT_FOUND" and "missing_column" in error_details:
            missing_col = error_details["missing_column"]
            table_prefix = error_details.get("table_prefix", "")
            
            # 在所有表中查找相似列名
            for table, columns in available_columns.items():
                if table_prefix and table.lower() != table_prefix.lower():
                    continue
                matches = get_close_matches(missing_col, columns, n=1, cutoff=0.6)
                if matches:
                    if table_prefix:
                        fixed_sql = re.sub(
                            rf'\b{re.escape(table_prefix)}\.{re.escape(missing_col)}\b',
                            f"{table_prefix}.{matches[0]}",
                            fixed_sql,
                            flags=re.IGNORECASE
                        )
                    else:
                        fixed_sql = re.sub(
                            rf'\b{re.escape(missing_col)}\b',
                            matches[0],
                            fixed_sql,
                            flags=re.IGNORECASE
                        )
                    fixes_applied.append(f"列名 '{missing_col}' → '{matches[0]}'")
                    break
        
        # 3. 修复歧义列名
        if error_type == "AMBIGUOUS_COLUMN" and "ambiguous_column" in error_details:
            ambiguous_col = error_details["ambiguous_column"]
            # 找到包含该列的第一个表
            for table, columns in available_columns.items():
                if ambiguous_col.lower() in [c.lower() for c in columns]:
                    # 为该列添加表前缀
                    fixed_sql = re.sub(
                        rf'(?<![.\w])\b{re.escape(ambiguous_col)}\b(?![.\w])',
                        f"{table}.{ambiguous_col}",
                        fixed_sql,
                        flags=re.IGNORECASE
                    )
                    fixes_applied.append(f"添加表前缀 '{ambiguous_col}' → '{table}.{ambiguous_col}'")
                    break
        
        # 4. 常见语法修复
        if error_type == "SYNTAX_ERROR":
            # 修复双逗号
            if ",," in fixed_sql:
                fixed_sql = re.sub(r',\s*,', ',', fixed_sql)
                fixes_applied.append("移除多余逗号")
            
            # 修复末尾逗号（在 FROM/WHERE/ORDER BY 之前）
            fixed_sql = re.sub(r',\s*(FROM|WHERE|ORDER|GROUP|HAVING|LIMIT)', r' \1', fixed_sql, flags=re.IGNORECASE)
            if fixed_sql != sql:
                fixes_applied.append("移除子句前的逗号")
            
            # 修复缺少空格
            fixed_sql = re.sub(r'(\w)(SELECT|FROM|WHERE|AND|OR|JOIN|ON|ORDER|GROUP|HAVING|LIMIT)', r'\1 \2', fixed_sql, flags=re.IGNORECASE)
        
        # 5. 添加 LIMIT（如果缺失且是超时错误）
        if error_type == "TIMEOUT" and "LIMIT" not in fixed_sql.upper():
            fixed_sql = fixed_sql.rstrip(';') + " LIMIT 100;"
            fixes_applied.append("添加 LIMIT 100")
        
        return {
            "success": len(fixes_applied) > 0,
            "original_sql": sql,
            "fixed_sql": fixed_sql,
            "fixes_applied": fixes_applied,
            "message": f"应用了 {len(fixes_applied)} 个修复" if fixes_applied else "未能自动修复"
        }
    
    @tool
    def list_available_tables() -> Dict[str, Any]:
        """列出所有可用的表名
        
        用于错误恢复时查找正确的表名。
        
        Returns:
            表名列表
        """
        try:
            from ..database.db_manager import get_database_manager
            manager = get_database_manager(connection_id)
            tables = manager.get_tables()
            return {
                "success": True,
                "tables": tables,
                "count": len(tables)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @tool
    def get_table_schema(table_name: str) -> Dict[str, Any]:
        """获取表的 Schema 信息
        
        用于错误恢复时查找正确的列名。
        
        Args:
            table_name: 表名
            
        Returns:
            表结构信息
        """
        try:
            from ..database.db_manager import get_database_manager
            manager = get_database_manager(connection_id)
            table_info = manager.get_table_info(table_name)
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": [col.name for col in table_info.columns],
                "column_details": [
                    {
                        "name": col.name,
                        "type": col.data_type,
                        "nullable": col.nullable,
                        "primary_key": col.primary_key
                    }
                    for col in table_info.columns
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "table_name": table_name,
                "error": str(e)
            }
    
    @tool
    def validate_fixed_sql(sql: str) -> Dict[str, Any]:
        """验证修复后的 SQL 是否正确
        
        使用数据库引擎验证 SQL 语法。
        
        Args:
            sql: 修复后的 SQL
            
        Returns:
            验证结果
        """
        try:
            from ..database.db_manager import get_database_manager, DatabaseType
            manager = get_database_manager(connection_id)
            db_type = manager.config.db_type
            
            if db_type == DatabaseType.SQLITE:
                explain_sql = f"EXPLAIN QUERY PLAN {sql.rstrip(';')}"
            else:
                explain_sql = f"EXPLAIN {sql.rstrip(';')}"
            
            result = manager.execute_query(explain_sql)
            
            return {
                "is_valid": result.success,
                "sql": sql,
                "error": result.error if not result.success else None
            }
        except Exception as e:
            return {
                "is_valid": False,
                "sql": sql,
                "error": str(e)
            }
    
    return [
        analyze_error,
        suggest_fix,
        auto_fix_sql,
        list_available_tables,
        get_table_schema,
        validate_fixed_sql
    ]


def create_error_recovery_agent(
    model: BaseChatModel = None,
    connection_id: int = 0,
    retry_count: int = 0,
    max_retries: int = 3
) -> Any:
    """创建错误恢复代理（增强版）
    
    Args:
        model: LLM模型
        connection_id: 数据库连接 ID（用于查询表结构和验证 SQL）
        retry_count: 当前重试次数
        max_retries: 最大重试次数
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    # 使用增强版工具（带数据库连接）
    tools = create_recovery_tools(connection_id)
    
    prompt = load_prompt(
        "error_recovery",
        retry_count=retry_count,
        max_retries=max_retries
    )
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="recovery_expert",
        prompt=prompt
    )
    
    return agent


async def attempt_recovery(
    agent,
    error: str,
    sql: str,
    schema_info: Dict[str, Any] = None,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """尝试恢复错误
    
    Args:
        agent: 恢复代理
        error: 错误消息
        sql: 原始SQL
        schema_info: Schema信息
        config: 运行配置
        
    Returns:
        恢复结果
    """
    schema_str = ""
    if schema_info:
        tables = [t.get("name", "") for t in schema_info.get("tables", [])]
        schema_str = f"\n可用的表: {', '.join(tables)}"
    
    messages = [
        {
            "role": "user",
            "content": f"""请分析以下错误并尝试修复:

错误信息: {error}

原始SQL:
```sql
{sql}
```
{schema_str}

请:
1. 分析错误原因
2. 判断是否可恢复
3. 如果可恢复，提供修复后的SQL
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result
