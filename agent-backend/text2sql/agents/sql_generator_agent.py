"""
SQL 生成代理

根据 Schema 信息生成高质量 SQL 语句
集成长期记忆的查询模式功能
"""

from typing import Any, Dict, List, Optional
from typing_extensions import Annotated

from langgraph.prebuilt import create_react_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool, InjectedToolArg
from langgraph.store.base import BaseStore

from ..config import get_model
from ..prompts import load_prompt
from ..tools.sql_tools import SQL_TOOLS


def _create_memory_aware_sql_tools(dialect: str = "mysql") -> List:
    """创建带长期记忆支持的 SQL 工具"""
    from memory import get_memory_manager
    
    @tool
    def get_similar_patterns(
        user_id: str,
        current_query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """从长期记忆中获取相似的历史查询模式
        
        查找用户之前成功执行的相似查询，作为 SQL 生成的参考。
        
        Args:
            user_id: 用户 ID
            current_query: 当前自然语言查询
            limit: 最大返回数量
            
        Returns:
            相似查询模式列表
        """
        memory_manager = get_memory_manager()
        store = memory_manager.store
        
        namespace = ("query_patterns", user_id)
        items = store.search(namespace, query=current_query, limit=limit)
        
        print(f"[Query Patterns] 搜索 '{current_query[:30]}...'，找到 {len(items)} 个相似模式")
        
        return [
            {
                "pattern_id": item.key,
                "natural_query": item.value.get("natural_query"),
                "sql": item.value.get("sql"),
                "success": item.value.get("success"),
                "use_count": item.value.get("use_count", 0)
            }
            for item in items
        ]
    
    @tool
    def save_generated_sql(
        user_id: str,
        natural_query: str,
        sql: str,
        schema_tables: Optional[List[str]] = None
    ) -> str:
        """保存生成的 SQL 到长期记忆
        
        在 SQL 生成后保存，供未来参考。
        
        Args:
            user_id: 用户 ID
            natural_query: 自然语言查询
            sql: 生成的 SQL
            schema_tables: 涉及的表名列表
            
        Returns:
            操作结果消息
        """
        import hashlib
        from datetime import datetime
        
        memory_manager = get_memory_manager()
        store = memory_manager.store
        
        pattern_id = hashlib.md5(
            f"{user_id}:{natural_query}".encode()
        ).hexdigest()[:12]
        
        namespace = ("query_patterns", user_id)
        
        # 检查是否已存在
        existing = store.get(namespace, pattern_id)
        use_count = 1
        if existing:
            use_count = existing.value.get("use_count", 0) + 1
        
        store.put(namespace, pattern_id, {
            "natural_query": natural_query,
            "sql": sql,
            "dialect": dialect,
            "schema_tables": schema_tables or [],
            "success": True,  # 生成成功
            "created_at": datetime.now().isoformat(),
            "use_count": use_count
        })
        
        print(f"[Query Patterns] 已保存查询模式，ID: {pattern_id}")
        
        return f"SQL 模式已保存，ID: {pattern_id}"
    
    @tool
    def get_user_sql_preferences(
        user_id: str
    ) -> Dict[str, Any]:
        """获取用户的 SQL 偏好设置
        
        包括默认 LIMIT、排序偏好等。
        
        Args:
            user_id: 用户 ID
            
        Returns:
            用户偏好字典
        """
        memory_manager = get_memory_manager()
        store = memory_manager.store
        
        namespace = ("user_preferences", user_id)
        
        # 获取 SQL 相关偏好
        preferences = {}
        
        for key in ["default_limit", "preferred_order", "date_format", "null_handling"]:
            item = store.get(namespace, key)
            if item:
                preferences[key] = item.value.get("value")
        
        # 默认值
        if "default_limit" not in preferences:
            preferences["default_limit"] = 100
        
        return preferences
    
    return [get_similar_patterns, save_generated_sql, get_user_sql_preferences]


def create_sql_generator_agent(
    model: BaseChatModel = None,
    tools: List = None,
    dialect: str = "mysql",
    top_k: int = 100,
    with_memory: bool = True
) -> Any:
    """创建 SQL 生成代理
    
    Args:
        model: LLM 模型
        tools: 工具列表
        dialect: 数据库方言
        top_k: 默认 LIMIT 值
        with_memory: 是否启用长期记忆工具
        
    Returns:
        配置好的 React 代理
    """
    if model is None:
        model = get_model()
    
    if tools is None:
        tools = list(SQL_TOOLS)  # 复制基础工具
        
        # 添加记忆工具
        if with_memory:
            memory_tools = _create_memory_aware_sql_tools(dialect)
            tools.extend(memory_tools)
    
    # 加载并格式化提示词
    prompt = load_prompt("sql_generator", dialect=dialect, top_k=top_k)
    
    # 增强提示词，添加记忆使用说明
    if with_memory:
        memory_instructions = """

## 长期记忆使用指南

在生成 SQL 之前，你应该：
1. 使用 `get_similar_patterns` 工具查找用户之前的相似查询
2. 使用 `get_user_sql_preferences` 获取用户的 SQL 偏好设置
3. 参考历史成功的查询模式来生成更准确的 SQL

在 SQL 生成成功后：
1. 使用 `save_generated_sql` 保存查询模式供未来参考
"""
        if prompt:
            prompt = prompt + memory_instructions
    
    agent = create_react_agent(
        model=model,
        tools=tools,
        name="sql_expert",
        prompt=prompt
    )
    
    return agent


async def generate_sql(
    agent,
    query_analysis: Dict[str, Any],
    schema_info: Dict[str, Any],
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """生成 SQL 语句
    
    Args:
        agent: SQL 生成代理
        query_analysis: 查询分析结果
        schema_info: Schema 信息
        config: 运行配置（包含 thread_id, user_id）
        
    Returns:
        生成结果（包含 SQL）
    """
    # 构建 Schema 上下文
    schema_context = format_schema_for_prompt(schema_info)
    
    messages = [
        {
            "role": "user",
            "content": f"""根据以下信息生成 SQL 查询:

## 查询分析
{format_analysis(query_analysis)}

## 数据库 Schema
{schema_context}

请生成正确的 SQL 语句，注意:
1. 只生成 SELECT 语句
2. 添加适当的 LIMIT
3. 使用正确的列名和表名
4. 优化查询性能

在生成之前，请先查找相似的历史查询模式作为参考。
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config or {}
    )
    
    return result


async def generate_sql_with_memory(
    agent,
    user_query: str,
    schema_info: Dict[str, Any],
    thread_id: str,
    user_id: str = "default"
) -> Dict[str, Any]:
    """生成 SQL（带记忆支持）
    
    Args:
        agent: SQL 生成代理
        user_query: 用户自然语言查询
        schema_info: Schema 信息
        thread_id: 会话线程 ID（短期记忆）
        user_id: 用户 ID（长期记忆）
        
    Returns:
        生成结果
    """
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    schema_context = format_schema_for_prompt(schema_info)
    
    messages = [
        {
            "role": "user",
            "content": f"""请为以下查询生成 SQL:

用户查询: {user_query}

## 数据库 Schema
{schema_context}

请按以下步骤操作:
1. 首先使用 get_similar_patterns 查找相似的历史查询（user_id: {user_id}）
2. 使用 get_user_sql_preferences 获取用户偏好
3. 参考历史模式生成 SQL
4. 生成成功后使用 save_generated_sql 保存模式
"""
        }
    ]
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config
    )
    
    return result


def format_schema_for_prompt(schema_info: Dict[str, Any]) -> str:
    """格式化 Schema 信息为提示词"""
    # 处理带缓存标记的 schema
    if "data" in schema_info and "from_cache" in schema_info:
        schema_info = schema_info["data"]
    
    lines = []
    
    for table in schema_info.get("tables", []):
        table_name = table.get("name", "unknown")
        lines.append(f"### 表: {table_name}")
        
        columns = schema_info.get("columns", {}).get(table_name, [])
        if columns:
            lines.append("列:")
            for col in columns:
                col_str = f"  - {col['name']}: {col['data_type']}"
                if col.get("primary_key"):
                    col_str += " [PK]"
                if col.get("foreign_key"):
                    col_str += f" [FK -> {col['foreign_key']}]"
                lines.append(col_str)
        lines.append("")
    
    # 添加关系信息
    relationships = schema_info.get("relationships", [])
    if relationships:
        lines.append("### 表关系")
        for rel in relationships:
            lines.append(
                f"  - {rel['from_table']}.{rel['from_column']} -> "
                f"{rel['to_table']}.{rel['to_column']}"
            )
    
    return "\n".join(lines)


def format_analysis(analysis: Dict[str, Any]) -> str:
    """格式化分析结果"""
    lines = []
    
    if analysis.get("intent"):
        lines.append(f"意图: {analysis['intent']}")
    
    if analysis.get("relevant_tables"):
        lines.append(f"相关表: {', '.join(analysis['relevant_tables'])}")
    
    if analysis.get("filters"):
        lines.append(f"过滤条件: {', '.join(analysis['filters'])}")
    
    if analysis.get("aggregations"):
        lines.append(f"聚合函数: {', '.join(analysis['aggregations'])}")
    
    if analysis.get("ordering"):
        lines.append(f"排序: {', '.join(analysis['ordering'])}")
    
    return "\n".join(lines)
