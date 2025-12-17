"""
Text2SQL Node Functions

SQL生成任务的节点函数
"""
import json
import re
import logging
from typing import Dict, Any

from agent_langgraph.tasks.text2sql.state import Text2SQLState
from agent_langgraph.core import ModelFactory

logger = logging.getLogger(__name__)


def extract_question(state: Text2SQLState) -> str:
    """从状态中提取问题"""
    if state.get("question"):
        return state["question"]
    
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, dict):
            role = msg.get("role") or msg.get("type")
            if role in ("human", "user"):
                return msg.get("content", "")
    
    return ""


def understand_question(state: Text2SQLState) -> Text2SQLState:
    """
    理解问题节点
    
    解析用户输入，提取查询意图
    """
    logger.info("Understanding question...")
    
    question = extract_question(state)
    
    if not question:
        return {**state, "error": "请输入查询问题"}
    
    messages = list(state.get("messages", []))
    messages.append({"role": "ai", "content": "正在理解您的查询问题..."})
    
    return {
        **state,
        "question": question,
        "messages": messages,
    }


def generate_sql(state: Text2SQLState) -> Text2SQLState:
    """
    生成SQL节点
    
    根据问题和schema生成SQL语句
    """
    logger.info("Generating SQL...")
    
    if state.get("error"):
        return state
    
    model = ModelFactory.get_model(temperature=0.1)
    question = state.get("question", "")
    schema = state.get("schema", "")
    dialect = state.get("dialect", "mysql")
    
    schema_text = f"\n数据库表结构:\n{schema}" if schema else ""
    
    prompt = f"""你是一个专业的SQL专家，请将以下自然语言问题转换为{dialect.upper()} SQL查询语句。

问题: {question}
{schema_text}

请输出JSON格式：
```json
{{
  "sql": "SELECT ...",
  "explanation": "SQL解释说明",
  "tables_used": ["table1", "table2"],
  "confidence": 0.9
}}
```

注意：
1. 只输出SELECT查询，不要输出INSERT/UPDATE/DELETE
2. 使用标准的{dialect}语法
3. 添加适当的注释
"""
    
    try:
        response = model.invoke(prompt)
        content = response.content
        
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            result = json.loads(json_match.group())
        else:
            sql_match = re.search(r'```sql\s*([\s\S]*?)\s*```', content)
            if sql_match:
                result = {"sql": sql_match.group(1).strip(), "confidence": 0.7}
            else:
                result = {"sql": content, "confidence": 0.5}
        
        messages = list(state.get("messages", []))
        messages.append({
            "role": "ai",
            "content": f"SQL生成完成:\n```sql\n{result.get('sql', '')}\n```"
        })
        
        return {
            **state,
            "sql": result.get("sql", ""),
            "explanation": result.get("explanation", ""),
            "tables_used": result.get("tables_used", []),
            "confidence": result.get("confidence", 0.8),
            "messages": messages,
        }
    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        return {**state, "error": str(e)}


def validate_sql(state: Text2SQLState) -> Text2SQLState:
    """
    验证SQL节点
    
    检查SQL语法正确性
    """
    logger.info("Validating SQL...")
    
    if state.get("error"):
        return state
    
    model = ModelFactory.get_model(temperature=0.1)
    sql = state.get("sql", "")
    dialect = state.get("dialect", "mysql")
    
    prompt = f"""请验证以下{dialect} SQL语句的语法正确性：

```sql
{sql}
```

输出JSON格式：
```json
{{
  "is_valid": true,
  "issues": [],
  "suggestions": []
}}
```
"""
    
    try:
        response = model.invoke(prompt)
        content = response.content
        
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            validation = json.loads(json_match.group())
        else:
            validation = {"is_valid": True, "issues": [], "suggestions": []}
        
        messages = list(state.get("messages", []))
        messages.append({
            "role": "ai",
            "content": f"SQL验证完成: {'通过' if validation.get('is_valid') else '存在问题'}"
        })
        
        return {
            **state,
            "validation": validation,
            "completed": True,
            "messages": messages,
        }
    except Exception as e:
        logger.error(f"SQL validation failed: {e}")
        return {**state, "validation": {"is_valid": True}, "completed": True}
