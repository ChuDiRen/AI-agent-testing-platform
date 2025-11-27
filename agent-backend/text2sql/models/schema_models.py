"""
Schema数据模型

定义数据库结构相关的数据模型
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class ColumnType(str, Enum):
    """列数据类型"""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    TEXT = "text"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    TIMESTAMP = "timestamp"
    BINARY = "binary"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class ColumnInfo:
    """列信息"""
    name: str
    data_type: str
    column_type: ColumnType = ColumnType.UNKNOWN
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None  # 格式: "table.column"
    default: Optional[str] = None
    comment: Optional[str] = None
    max_length: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "data_type": self.data_type,
            "column_type": self.column_type.value,
            "nullable": self.nullable,
            "primary_key": self.primary_key,
            "foreign_key": self.foreign_key,
            "default": self.default,
            "comment": self.comment,
            "max_length": self.max_length
        }


@dataclass
class IndexInfo:
    """索引信息"""
    name: str
    columns: List[str]
    unique: bool = False
    primary: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "columns": self.columns,
            "unique": self.unique,
            "primary": self.primary
        }


@dataclass
class TableInfo:
    """表信息"""
    name: str
    schema: Optional[str] = None
    columns: List[ColumnInfo] = field(default_factory=list)
    indexes: List[IndexInfo] = field(default_factory=list)
    row_count: Optional[int] = None
    comment: Optional[str] = None
    
    def get_primary_key(self) -> Optional[str]:
        """获取主键列名"""
        for col in self.columns:
            if col.primary_key:
                return col.name
        return None
    
    def get_column(self, name: str) -> Optional[ColumnInfo]:
        """根据名称获取列信息"""
        for col in self.columns:
            if col.name.lower() == name.lower():
                return col
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "schema": self.schema,
            "columns": [c.to_dict() for c in self.columns],
            "indexes": [i.to_dict() for i in self.indexes],
            "row_count": self.row_count,
            "comment": self.comment
        }
    
    def to_schema_string(self) -> str:
        """转换为Schema字符串描述"""
        lines = [f"Table: {self.name}"]
        if self.comment:
            lines.append(f"  Comment: {self.comment}")
        lines.append("  Columns:")
        for col in self.columns:
            pk = " [PK]" if col.primary_key else ""
            fk = f" [FK -> {col.foreign_key}]" if col.foreign_key else ""
            nullable = " NULL" if col.nullable else " NOT NULL"
            lines.append(f"    - {col.name}: {col.data_type}{pk}{fk}{nullable}")
        return "\n".join(lines)


@dataclass
class RelationshipInfo:
    """表关系信息"""
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    relationship_type: str = "many_to_one"  # one_to_one, one_to_many, many_to_one, many_to_many
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_table": self.from_table,
            "from_column": self.from_column,
            "to_table": self.to_table,
            "to_column": self.to_column,
            "relationship_type": self.relationship_type
        }
    
    def to_join_condition(self) -> str:
        """生成JOIN条件"""
        return f"{self.from_table}.{self.from_column} = {self.to_table}.{self.to_column}"


@dataclass
class DatabaseSchema:
    """数据库Schema"""
    database_name: str
    tables: List[TableInfo] = field(default_factory=list)
    relationships: List[RelationshipInfo] = field(default_factory=list)
    
    def get_table(self, name: str) -> Optional[TableInfo]:
        """根据名称获取表信息"""
        for table in self.tables:
            if table.name.lower() == name.lower():
                return table
        return None
    
    def get_related_tables(self, table_name: str) -> List[str]:
        """获取与指定表相关的所有表"""
        related = set()
        for rel in self.relationships:
            if rel.from_table.lower() == table_name.lower():
                related.add(rel.to_table)
            elif rel.to_table.lower() == table_name.lower():
                related.add(rel.from_table)
        return list(related)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "database_name": self.database_name,
            "tables": [t.to_dict() for t in self.tables],
            "relationships": [r.to_dict() for r in self.relationships]
        }
