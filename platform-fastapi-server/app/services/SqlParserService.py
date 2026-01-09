# -*- coding: utf-8 -*-
"""
SQL DDL 解析服务
解析 CREATE TABLE 语句，提取表结构信息
"""
import re
from typing import List, Dict, Optional
from app.logger.logger import get_logger

logger = get_logger(__name__)


class SqlParserService:
    """SQL DDL 解析服务"""
    
    # MySQL 类型到 Python 类型的映射
    TYPE_MAPPING = {
        'int': 'int',
        'integer': 'int',
        'tinyint': 'int',
        'smallint': 'int',
        'mediumint': 'int',
        'bigint': 'int',
        'float': 'float',
        'double': 'float',
        'decimal': 'float',
        'numeric': 'float',
        'char': 'str',
        'varchar': 'str',
        'text': 'str',
        'tinytext': 'str',
        'mediumtext': 'str',
        'longtext': 'str',
        'blob': 'bytes',
        'tinyblob': 'bytes',
        'mediumblob': 'bytes',
        'longblob': 'bytes',
        'date': 'date',
        'datetime': 'datetime',
        'timestamp': 'datetime',
        'time': 'time',
        'year': 'int',
        'boolean': 'bool',
        'bool': 'bool',
        'json': 'dict',
        'enum': 'str',
        'set': 'str',
    }
    
    def parse_sql_file(self, sql_content: str) -> List[Dict]:
        """
        解析 SQL 文件内容，提取所有 CREATE TABLE 语句
        
        Args:
            sql_content: SQL 文件内容
            
        Returns:
            表信息列表，每个元素包含 table_name, table_comment, columns
        """
        tables = []
        
        # 移除注释
        sql_content = self._remove_comments(sql_content)
        
        # 匹配 CREATE TABLE 语句
        create_table_pattern = re.compile(
            r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?[`"\']?(\w+)[`"\']?\s*\((.*?)\)([^;]*);',
            re.IGNORECASE | re.DOTALL
        )
        
        matches = create_table_pattern.findall(sql_content)
        
        for match in matches:
            table_name = match[0]
            columns_str = match[1]
            table_options = match[2] if len(match) > 2 else ''
            
            try:
                table_info = self._parse_table(table_name, columns_str, table_options)
                if table_info:
                    tables.append(table_info)
                    logger.info(f"成功解析表: {table_name}")
            except Exception as e:
                logger.warning(f"解析表 {table_name} 失败: {e}")
                continue
        
        return tables
    
    def _remove_comments(self, sql: str) -> str:
        """移除 SQL 注释"""
        # 移除单行注释 --
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        # 移除单行注释 #
        sql = re.sub(r'#.*$', '', sql, flags=re.MULTILINE)
        # 移除多行注释 /* */
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        return sql
    
    def _parse_table(self, table_name: str, columns_str: str, table_options: str) -> Optional[Dict]:
        """解析单个表"""
        # 提取表注释
        table_comment = self._extract_table_comment(table_options)
        
        # 解析字段
        columns = self._parse_columns(columns_str)
        
        if not columns:
            logger.warning(f"表 {table_name} 没有解析到字段")
            return None
        
        # 生成类名（驼峰命名）
        class_name = ''.join(x.title() for x in table_name.split('_'))
        business_name = table_name.lower()
        
        return {
            'table_name': table_name,
            'table_comment': table_comment or table_name,
            'class_name': class_name,
            'business_name': business_name,
            'function_name': table_comment or table_name,
            'columns': columns
        }
    
    def _extract_table_comment(self, table_options: str) -> str:
        """提取表注释"""
        # 匹配 COMMENT='xxx' 或 COMMENT "xxx"
        comment_pattern = re.compile(
            r"COMMENT\s*[=]?\s*['\"](.+?)['\"]",
            re.IGNORECASE
        )
        match = comment_pattern.search(table_options)
        return match.group(1) if match else ''
    
    def _parse_columns(self, columns_str: str) -> List[Dict]:
        """解析字段定义"""
        columns = []
        
        # 分割字段定义（注意处理括号内的逗号）
        column_defs = self._split_column_definitions(columns_str)
        
        sort_order = 0
        pk_columns = set()
        
        # 先找出主键
        for col_def in column_defs:
            col_def = col_def.strip()
            if col_def.upper().startswith('PRIMARY KEY'):
                pk_match = re.search(r'\(([^)]+)\)', col_def)
                if pk_match:
                    pk_cols = pk_match.group(1)
                    pk_columns = set(c.strip().strip('`"\'') for c in pk_cols.split(','))
        
        # 解析每个字段
        for col_def in column_defs:
            col_def = col_def.strip()
            
            # 跳过约束定义
            if self._is_constraint(col_def):
                continue
            
            column = self._parse_single_column(col_def, sort_order, pk_columns)
            if column:
                columns.append(column)
                sort_order += 1
        
        return columns
    
    def _split_column_definitions(self, columns_str: str) -> List[str]:
        """分割字段定义，处理括号内的逗号"""
        result = []
        current = ''
        depth = 0
        
        for char in columns_str:
            if char == '(':
                depth += 1
                current += char
            elif char == ')':
                depth -= 1
                current += char
            elif char == ',' and depth == 0:
                if current.strip():
                    result.append(current.strip())
                current = ''
            else:
                current += char
        
        if current.strip():
            result.append(current.strip())
        
        return result
    
    def _is_constraint(self, col_def: str) -> bool:
        """判断是否为约束定义"""
        constraint_keywords = [
            'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'INDEX', 'KEY',
            'CONSTRAINT', 'CHECK', 'FULLTEXT', 'SPATIAL'
        ]
        col_upper = col_def.upper().strip()
        return any(col_upper.startswith(kw) for kw in constraint_keywords)
    
    def _parse_single_column(self, col_def: str, sort_order: int, pk_columns: set) -> Optional[Dict]:
        """解析单个字段定义"""
        # 匹配字段名和类型
        pattern = re.compile(
            r'^[`"\']?(\w+)[`"\']?\s+(\w+)(?:\s*\(([^)]+)\))?(.*)$',
            re.IGNORECASE
        )
        
        match = pattern.match(col_def.strip())
        if not match:
            return None
        
        column_name = match.group(1)
        column_type_base = match.group(2).lower()
        column_length_str = match.group(3)
        column_options = match.group(4) or ''
        
        # 解析长度
        column_length = None
        if column_length_str:
            try:
                # 处理 decimal(10,2) 这种情况
                if ',' in column_length_str:
                    column_length = int(column_length_str.split(',')[0])
                else:
                    column_length = int(column_length_str)
            except ValueError:
                pass
        
        # 完整的列类型
        if column_length_str:
            column_type = f"{column_type_base}({column_length_str})"
        else:
            column_type = column_type_base
        
        # 获取 Python 类型
        python_type = self.TYPE_MAPPING.get(column_type_base, 'str')
        
        # 生成 Python 字段名（下划线转驼峰）
        python_field = self._to_camel_case(column_name)
        
        # 判断是否主键
        is_pk = '1' if column_name in pk_columns or 'PRIMARY KEY' in column_options.upper() else '0'
        
        # 判断是否自增
        is_increment = '1' if 'AUTO_INCREMENT' in column_options.upper() else '0'
        
        # 判断是否必填
        is_required = '1' if 'NOT NULL' in column_options.upper() else '0'
        
        # 提取字段注释
        column_comment = self._extract_column_comment(column_options)
        
        # 确定 HTML 类型
        html_type = self._get_html_type(column_type_base, column_length)
        
        # 确定是否为查询/列表/编辑字段
        is_query = '0'
        is_list = '1'
        is_edit = '1' if is_pk == '0' else '0'
        is_insert = '1' if is_pk == '0' or is_increment == '0' else '0'
        
        return {
            'column_name': column_name,
            'column_comment': column_comment or column_name,
            'column_type': column_type,
            'column_length': column_length,
            'python_type': python_type,
            'python_field': python_field,
            'is_pk': is_pk,
            'is_increment': is_increment,
            'is_required': is_required,
            'is_insert': is_insert,
            'is_edit': is_edit,
            'is_list': is_list,
            'is_query': is_query,
            'query_type': 'EQ',
            'html_type': html_type,
            'sort': sort_order
        }
    
    def _extract_column_comment(self, options: str) -> str:
        """提取字段注释"""
        comment_pattern = re.compile(
            r"COMMENT\s*['\"](.+?)['\"]",
            re.IGNORECASE
        )
        match = comment_pattern.search(options)
        return match.group(1) if match else ''
    
    def _to_camel_case(self, name: str) -> str:
        """下划线命名转驼峰命名"""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def _get_html_type(self, column_type: str, length: Optional[int]) -> str:
        """根据字段类型确定 HTML 控件类型"""
        if column_type in ('text', 'mediumtext', 'longtext'):
            return 'textarea'
        if column_type in ('datetime', 'timestamp'):
            return 'datetime'
        if column_type == 'date':
            return 'date'
        if column_type == 'time':
            return 'time'
        if column_type in ('tinyint',) and length == 1:
            return 'radio'
        return 'input'
