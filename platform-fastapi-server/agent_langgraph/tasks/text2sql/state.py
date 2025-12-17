"""
Text2SQL State Definition

SQL生成任务的状态定义
"""
from typing import TypedDict, List, Optional, Dict, Any


class Text2SQLState(TypedDict, total=False):
    """
    Text2SQL状态定义
    
    继承BaseState的通用字段，添加SQL特有字段
    """
    # 通用字段
    messages: List[Dict[str, Any]]
    completed: bool
    error: Optional[str]
    
    # SQL特有字段
    question: str                      # 用户问题
    schema: Optional[str]              # 数据库表结构
    dialect: str                       # SQL方言 (mysql/postgresql/sqlite等)
    sql: Optional[str]                 # 生成的SQL
    explanation: Optional[str]         # SQL解释
    tables_used: Optional[List[str]]   # 使用的表
    validation: Optional[Dict[str, Any]]  # 验证结果
    confidence: float                  # 置信度 0-1


def create_initial_state(
    question: str = "",
    schema: str = "",
    dialect: str = "mysql"
) -> Text2SQLState:
    """创建初始状态"""
    return Text2SQLState(
        messages=[],
        completed=False,
        error=None,
        question=question,
        schema=schema,
        dialect=dialect,
        sql=None,
        explanation=None,
        tables_used=None,
        validation=None,
        confidence=0.0,
    )
