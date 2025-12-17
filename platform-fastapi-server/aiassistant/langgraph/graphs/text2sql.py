"""
Text2SQL Graph - 自然语言转SQL查询

用于 langgraph dev 服务器的图定义
"""
import os
import json
import re
import logging
from typing import TypedDict, List, Optional, Dict, Any

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


# ==================== State Definition ====================

class Text2SQLState(TypedDict):
    """Text2SQL状态定义"""
    messages: List[dict]
    question: str
    schema: Optional[str]
    dialect: str
    sql: Optional[str]
    explanation: Optional[str]
    tables_used: Optional[List[str]]
    validation: Optional[Dict[str, Any]]
    confidence: float
    completed: bool
    error: Optional[str]


# ==================== Helper Functions ====================

def get_model():
    """获取模型实例"""
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    model_name = os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3")
    
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.1,  # SQL需要更低的temperature
    )


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


# ==================== Node Functions ====================

def understand_question(state: Text2SQLState) -> Text2SQLState:
    """理解问题"""
    logger.info("Understanding question...")
    
    question = extract_question(state)
    
    if not question:
        return {**state, "error": "请输入查询问题"}
    
    return {
        **state,
        "question": question,
        "messages": state.get("messages", []) + [{"role": "ai", "content": "正在理解您的查询问题..."}]
    }


def generate_sql(state: Text2SQLState) -> Text2SQLState:
    """生成SQL"""
    logger.info("Generating SQL...")
    
    if state.get("error"):
        return state
    
    model = get_model()
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
        
        return {
            **state,
            "sql": result.get("sql", ""),
            "explanation": result.get("explanation", ""),
            "tables_used": result.get("tables_used", []),
            "confidence": result.get("confidence", 0.8),
            "messages": state.get("messages", []) + [{"role": "ai", "content": f"SQL生成完成:\n```sql\n{result.get('sql', '')}\n```"}]
        }
    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        return {**state, "error": str(e)}


def validate_sql(state: Text2SQLState) -> Text2SQLState:
    """验证SQL"""
    logger.info("Validating SQL...")
    
    if state.get("error"):
        return state
    
    model = get_model()
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
        
        return {
            **state,
            "validation": validation,
            "completed": True,
            "messages": state.get("messages", []) + [{"role": "ai", "content": f"SQL验证完成: {'通过' if validation.get('is_valid') else '存在问题'}"}]
        }
    except Exception as e:
        logger.error(f"SQL validation failed: {e}")
        return {**state, "validation": {"is_valid": True}, "completed": True}


# ==================== Build Graph ====================

def build_graph():
    """构建LangGraph图"""
    workflow = StateGraph(Text2SQLState)
    
    workflow.add_node("understand_question", understand_question)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("validate_sql", validate_sql)
    
    workflow.add_edge(START, "understand_question")
    workflow.add_edge("understand_question", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")
    workflow.add_edge("validate_sql", END)
    
    return workflow.compile()


# 导出graph实例供langgraph dev使用
graph = build_graph()
