"""
验证工具

提供SQL语法检查、安全扫描等功能
"""

import re
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from langchain_core.tools import tool


class ValidationSeverity(str, Enum):
    """验证严重程度"""
    ERROR = "error"       # 阻止执行
    WARNING = "warning"   # 建议修复
    HINT = "hint"         # 优化建议


@dataclass
class ValidationIssue:
    """验证问题"""
    severity: ValidationSeverity
    code: str
    message: str
    position: int = -1  # 问题位置
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "code": self.code,
            "message": self.message,
            "position": self.position
        }


class SQLSecurityScanner:
    """SQL安全扫描器"""
    
    # 危险关键字
    DANGEROUS_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 
        'ALTER', 'CREATE', 'GRANT', 'REVOKE'
    ]
    
    # 危险函数
    DANGEROUS_FUNCTIONS = [
        'LOAD_FILE', 'INTO OUTFILE', 'INTO DUMPFILE',
        'BENCHMARK', 'SLEEP', 'WAITFOR'
    ]
    
    # SQL注入模式
    INJECTION_PATTERNS = [
        r";\s*--",           # 分号加注释
        r";\s*#",            # 分号加井号注释
        r"'\s*OR\s+'",       # OR注入
        r"'\s*OR\s+1\s*=\s*1", # 经典OR注入
        r"UNION\s+SELECT",   # UNION注入
        r"EXEC\s*\(",        # 执行存储过程
        r"xp_",              # SQL Server扩展存储过程
    ]
    
    @classmethod
    def scan(cls, sql: str) -> List[ValidationIssue]:
        """扫描SQL安全问题
        
        Args:
            sql: SQL语句
            
        Returns:
            安全问题列表
        """
        issues = []
        sql_upper = sql.upper()
        
        # 检查危险关键字
        for keyword in cls.DANGEROUS_KEYWORDS:
            pattern = rf'\b{keyword}\b'
            if re.search(pattern, sql_upper):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="SEC001",
                    message=f"检测到危险关键字: {keyword}"
                ))
        
        # 检查危险函数
        for func in cls.DANGEROUS_FUNCTIONS:
            if func.upper() in sql_upper:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="SEC002",
                    message=f"检测到危险函数: {func}"
                ))
        
        # 检查注入模式
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    code="SEC003",
                    message=f"检测到可能的SQL注入模式"
                ))
        
        # 检查多语句
        if ';' in sql.rstrip(';'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SEC004",
                message="检测到多语句，可能存在注入风险"
            ))
        
        return issues


class SQLSyntaxChecker:
    """SQL语法检查器"""
    
    @classmethod
    def check(cls, sql: str, schema_tables: List[str] = None) -> List[ValidationIssue]:
        """检查SQL语法
        
        Args:
            sql: SQL语句
            schema_tables: 已知的表名列表（用于验证表是否存在）
            
        Returns:
            语法问题列表
        """
        issues = []
        sql = sql.strip()
        
        # 检查是否为空
        if not sql:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYN001",
                message="SQL语句为空"
            ))
            return issues
        
        # 检查是否是SELECT语句
        if not sql.upper().startswith('SELECT'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYN002",
                message="只允许SELECT查询"
            ))
        
        # 检查括号匹配
        if sql.count('(') != sql.count(')'):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYN003",
                message="括号不匹配"
            ))
        
        # 检查引号匹配
        single_quotes = sql.count("'") - sql.count("\\'")
        if single_quotes % 2 != 0:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                code="SYN004",
                message="单引号不匹配"
            ))
        
        # 检查是否有FROM子句
        if 'SELECT' in sql.upper() and 'FROM' not in sql.upper():
            # 允许SELECT 1这样的简单查询
            if not re.search(r'SELECT\s+\d+', sql, re.IGNORECASE):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    code="SYN005",
                    message="SELECT语句缺少FROM子句"
                ))
        
        # 如果提供了schema，验证表名
        if schema_tables:
            tables_in_sql = cls._extract_tables(sql)
            for table in tables_in_sql:
                if table.lower() not in [t.lower() for t in schema_tables]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        code="SYN006",
                        message=f"表不存在: {table}"
                    ))
        
        return issues
    
    @classmethod
    def _extract_tables(cls, sql: str) -> List[str]:
        """提取表名"""
        tables = []
        
        # FROM子句
        from_match = re.search(r'\bFROM\s+([^\s,;(]+)', sql, re.IGNORECASE)
        if from_match:
            tables.append(from_match.group(1).strip('`"[]'))
        
        # JOIN子句
        join_matches = re.findall(r'\bJOIN\s+([^\s,;(]+)', sql, re.IGNORECASE)
        tables.extend(m.strip('`"[]') for m in join_matches)
        
        return list(set(tables))


class SQLPerformanceAnalyzer:
    """SQL性能分析器"""
    
    @classmethod
    def analyze(cls, sql: str) -> List[ValidationIssue]:
        """分析SQL性能
        
        Args:
            sql: SQL语句
            
        Returns:
            性能问题列表
        """
        issues = []
        sql_upper = sql.upper()
        
        # 检查SELECT *
        if re.search(r'SELECT\s+\*', sql, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HINT,
                code="PERF001",
                message="避免使用SELECT *，指定需要的列可提高性能"
            ))
        
        # 检查LIKE %开头
        if re.search(r"LIKE\s+['\"]%", sql, re.IGNORECASE):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HINT,
                code="PERF002",
                message="LIKE以%开头可能导致全表扫描"
            ))
        
        # 检查OR条件过多
        or_count = len(re.findall(r'\bOR\b', sql_upper))
        if or_count > 5:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="PERF003",
                message=f"OR条件过多({or_count}个)，可能影响性能"
            ))
        
        # 检查没有LIMIT
        if 'LIMIT' not in sql_upper:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.HINT,
                code="PERF004",
                message="建议添加LIMIT限制结果数量"
            ))
        
        # 检查子查询
        subquery_count = sql_upper.count('SELECT') - 1
        if subquery_count > 2:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                code="PERF005",
                message=f"子查询较多({subquery_count}个)，考虑使用JOIN优化"
            ))
        
        return issues


@tool
def validate_sql(
    sql: str, 
    schema_tables: List[str] = None
) -> Dict[str, Any]:
    """完整验证SQL语句
    
    Args:
        sql: SQL语句
        schema_tables: 已知表名列表
        
    Returns:
        验证结果
    """
    all_issues = []
    
    # 安全扫描
    security_issues = SQLSecurityScanner.scan(sql)
    all_issues.extend(security_issues)
    
    # 语法检查
    syntax_issues = SQLSyntaxChecker.check(sql, schema_tables)
    all_issues.extend(syntax_issues)
    
    # 性能分析
    perf_issues = SQLPerformanceAnalyzer.analyze(sql)
    all_issues.extend(perf_issues)
    
    # 统计
    errors = [i for i in all_issues if i.severity == ValidationSeverity.ERROR]
    warnings = [i for i in all_issues if i.severity == ValidationSeverity.WARNING]
    hints = [i for i in all_issues if i.severity == ValidationSeverity.HINT]
    
    return {
        "is_valid": len(errors) == 0,
        "sql": sql,
        "errors": [i.to_dict() for i in errors],
        "warnings": [i.to_dict() for i in warnings],
        "hints": [i.to_dict() for i in hints],
        "total_issues": len(all_issues)
    }


@tool
def check_security(sql: str) -> Dict[str, Any]:
    """安全检查
    
    Args:
        sql: SQL语句
        
    Returns:
        安全检查结果
    """
    issues = SQLSecurityScanner.scan(sql)
    
    return {
        "is_safe": len(issues) == 0,
        "issues": [i.to_dict() for i in issues]
    }


@tool
def analyze_performance(sql: str) -> Dict[str, Any]:
    """性能分析
    
    Args:
        sql: SQL语句
        
    Returns:
        性能分析结果
    """
    issues = SQLPerformanceAnalyzer.analyze(sql)
    
    return {
        "suggestions": [i.to_dict() for i in issues],
        "suggestion_count": len(issues)
    }


# ============ 方案 A: 数据库预执行验证 ============

def create_db_validation_tools(connection_id: int = 0) -> List:
    """创建带数据库连接的验证工具
    
    Args:
        connection_id: 数据库连接 ID
        
    Returns:
        工具列表
    """
    from ..database.db_manager import get_database_manager, DatabaseType
    
    @tool
    def validate_sql_with_db(sql: str) -> Dict[str, Any]:
        """使用数据库引擎验证 SQL 语法
        
        通过 EXPLAIN 或预编译验证 SQL 语法是否正确，不实际执行查询。
        
        Args:
            sql: SQL 语句
            
        Returns:
            验证结果，包含 is_valid、error 等字段
        """
        try:
            manager = get_database_manager(connection_id)
            db_type = manager.config.db_type
            
            # 根据数据库类型选择验证方式
            if db_type == DatabaseType.SQLITE:
                # SQLite 使用 EXPLAIN QUERY PLAN
                explain_sql = f"EXPLAIN QUERY PLAN {sql.rstrip(';')}"
            elif db_type in [DatabaseType.MYSQL, DatabaseType.POSTGRESQL]:
                # MySQL/PostgreSQL 使用 EXPLAIN
                explain_sql = f"EXPLAIN {sql.rstrip(';')}"
            else:
                # 其他数据库直接尝试执行
                explain_sql = f"EXPLAIN {sql.rstrip(';')}"
            
            result = manager.execute_query(explain_sql)
            
            if result.success:
                return {
                    "is_valid": True,
                    "sql": sql,
                    "message": "SQL 语法验证通过",
                    "explain_result": result.data[:5] if result.data else []  # 返回部分执行计划
                }
            else:
                return {
                    "is_valid": False,
                    "sql": sql,
                    "error": result.error,
                    "error_code": result.error_code,
                    "message": f"SQL 语法错误: {result.error}"
                }
                
        except Exception as e:
            return {
                "is_valid": False,
                "sql": sql,
                "error": str(e),
                "error_code": "VALIDATION_ERROR",
                "message": f"验证过程出错: {str(e)}"
            }
    
    @tool
    def get_table_columns(table_name: str) -> Dict[str, Any]:
        """获取指定表的列信息
        
        用于验证 SQL 中引用的列是否存在。
        
        Args:
            table_name: 表名
            
        Returns:
            表的列信息
        """
        try:
            manager = get_database_manager(connection_id)
            table_info = manager.get_table_info(table_name)
            
            return {
                "success": True,
                "table_name": table_name,
                "columns": [
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
    def list_all_tables() -> Dict[str, Any]:
        """列出数据库中所有表名
        
        用于验证 SQL 中引用的表是否存在。
        
        Returns:
            表名列表
        """
        try:
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
    
    return [validate_sql_with_db, get_table_columns, list_all_tables]


# 工具列表（基础静态验证）
VALIDATION_TOOLS = [
    validate_sql,
    check_security,
    analyze_performance
]


def get_enhanced_validation_tools(connection_id: int = 0) -> List:
    """获取增强版验证工具（包含数据库验证）
    
    Args:
        connection_id: 数据库连接 ID
        
    Returns:
        完整的验证工具列表
    """
    db_tools = create_db_validation_tools(connection_id)
    return VALIDATION_TOOLS + db_tools
