"""
错误恢复代理

智能错误分析和自动修复
"""

from typing import Any, Dict, List

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool

from ..config import get_model
from ..prompts import load_prompt


def create_recovery_tools() -> List:
    """创建恢复工具"""
    
    @tool
    def analyze_error(error_message: str, sql: str) -> Dict[str, Any]:
        """分析错误信息
        
        Args:
            error_message: 错误消息
            sql: 相关SQL
            
        Returns:
            错误分析结果
        """
        error_lower = error_message.lower()
        
        # 识别错误类型
        if "syntax" in error_lower:
            error_type = "SYNTAX_ERROR"
            recoverable = True
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
        else:
            error_type = "UNKNOWN"
            recoverable = False
        
        return {
            "error_type": error_type,
            "recoverable": recoverable,
            "original_error": error_message,
            "sql": sql
        }
    
    @tool
    def suggest_fix(error_type: str, sql: str, context: str = "") -> Dict[str, Any]:
        """建议修复方案
        
        Args:
            error_type: 错误类型
            sql: 原始SQL
            context: 额外上下文
            
        Returns:
            修复建议
        """
        suggestions = {
            "SYNTAX_ERROR": [
                "检查SQL关键字拼写",
                "检查括号和引号匹配",
                "检查列名和表名"
            ],
            "NOT_FOUND": [
                "检查表名是否正确",
                "检查列名是否存在",
                "检查大小写是否匹配"
            ],
            "TIMEOUT": [
                "添加LIMIT限制结果数量",
                "减少JOIN数量",
                "添加索引条件过滤"
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
            "auto_fixable": error_type in ["SYNTAX_ERROR", "NOT_FOUND", "TIMEOUT"]
        }
    
    return [analyze_error, suggest_fix]


def create_error_recovery_agent(
    model: BaseChatModel = None,
    retry_count: int = 0,
    max_retries: int = 3
) -> Any:
    """创建错误恢复代理
    
    Args:
        model: LLM模型
        retry_count: 当前重试次数
        max_retries: 最大重试次数
        
    Returns:
        配置好的React代理
    """
    if model is None:
        model = get_model()
    
    tools = create_recovery_tools()
    
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
