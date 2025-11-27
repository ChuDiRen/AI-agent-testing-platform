"""
上下文压缩器

将长历史消息压缩为摘要，减少token使用
"""

from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage

from text2sql.config import get_model, LLMConfig


class ContextCompressor:
    """上下文压缩器
    
    将长对话历史压缩为简洁摘要
    """
    
    # 摘要生成提示词
    SUMMARY_PROMPT = """请将以下对话历史压缩为一个简洁的摘要。
保留关键信息：
- 用户的主要查询意图
- 重要的数据库表和字段
- 之前查询的结果要点
- 任何重要的上下文信息

对话历史：
{history}

请生成一个不超过200字的摘要："""

    def __init__(
        self,
        llm_config: Optional[LLMConfig] = None,
        max_tokens_before_compress: int = 6000,
        keep_recent_messages: int = 5
    ):
        """初始化压缩器
        
        Args:
            llm_config: LLM配置，用于生成摘要
            max_tokens_before_compress: 超过此token数时触发压缩
            keep_recent_messages: 压缩时保留的最近消息数
        """
        self.llm_config = llm_config
        self.max_tokens_before_compress = max_tokens_before_compress
        self.keep_recent_messages = keep_recent_messages
        self._model = None
        
    def _get_model(self):
        """懒加载LLM模型"""
        if self._model is None:
            self._model = get_model(self.llm_config)
        return self._model
    
    def _estimate_tokens(self, messages: List[BaseMessage]) -> int:
        """估算消息的token数"""
        total = 0
        for msg in messages:
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            total += len(content) // 2  # 保守估计
        return total
    
    def _format_history(self, messages: List[BaseMessage]) -> str:
        """格式化消息历史为文本"""
        lines = []
        for msg in messages:
            role = "用户" if isinstance(msg, HumanMessage) else "助手"
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            # 截断过长的内容
            if len(content) > 500:
                content = content[:500] + "..."
            lines.append(f"{role}: {content}")
        return "\n".join(lines)
    
    async def compress_async(
        self, 
        messages: List[BaseMessage]
    ) -> List[BaseMessage]:
        """异步压缩消息历史
        
        Args:
            messages: 原始消息列表
            
        Returns:
            压缩后的消息列表（摘要 + 最近消息）
        """
        # 检查是否需要压缩
        if self._estimate_tokens(messages) <= self.max_tokens_before_compress:
            return messages
            
        # 分离系统消息
        system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
        other_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
        
        if len(other_msgs) <= self.keep_recent_messages:
            return messages
            
        # 分离要压缩的消息和要保留的消息
        to_compress = other_msgs[:-self.keep_recent_messages]
        to_keep = other_msgs[-self.keep_recent_messages:]
        
        # 生成摘要
        history_text = self._format_history(to_compress)
        prompt = self.SUMMARY_PROMPT.format(history=history_text)
        
        try:
            model = self._get_model()
            response = await model.ainvoke([HumanMessage(content=prompt)])
            summary = response.content if isinstance(response.content, str) else str(response.content)
        except Exception as e:
            # 如果摘要生成失败，直接截断
            summary = f"[历史摘要生成失败: {e}]"
            
        # 构建新的消息列表
        summary_msg = SystemMessage(content=f"之前对话摘要: {summary}")
        
        return system_msgs + [summary_msg] + to_keep
    
    def compress(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """同步压缩消息历史
        
        对于同步场景，使用简单的截断策略
        """
        # 检查是否需要压缩
        if self._estimate_tokens(messages) <= self.max_tokens_before_compress:
            return messages
            
        # 分离系统消息
        system_msgs = [m for m in messages if isinstance(m, SystemMessage)]
        other_msgs = [m for m in messages if not isinstance(m, SystemMessage)]
        
        if len(other_msgs) <= self.keep_recent_messages:
            return messages
            
        # 简单压缩：创建摘要占位符
        to_compress = other_msgs[:-self.keep_recent_messages]
        to_keep = other_msgs[-self.keep_recent_messages:]
        
        # 创建简单摘要
        summary_parts = []
        for msg in to_compress[:3]:  # 只保留前3条的摘要
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            if len(content) > 100:
                content = content[:100] + "..."
            role = "用户" if isinstance(msg, HumanMessage) else "助手"
            summary_parts.append(f"- {role}: {content}")
            
        if len(to_compress) > 3:
            summary_parts.append(f"... (还有{len(to_compress) - 3}条历史消息)")
            
        summary = "\n".join(summary_parts)
        summary_msg = SystemMessage(content=f"之前对话摘要:\n{summary}")
        
        return system_msgs + [summary_msg] + to_keep


def compress_schema_info(
    schema_info: Dict[str, Any], 
    relevant_tables: List[str]
) -> Dict[str, Any]:
    """压缩Schema信息
    
    只保留与查询相关的表和列
    
    Args:
        schema_info: 完整的Schema信息
        relevant_tables: 相关的表名列表
        
    Returns:
        压缩后的Schema信息
    """
    if not relevant_tables:
        return schema_info
        
    relevant_set = {t.lower() for t in relevant_tables}
    
    compressed = {
        "tables": [],
        "columns": {},
        "relationships": [],
        "indexes": {}
    }
    
    # 过滤表
    for table in schema_info.get("tables", []):
        table_name = table.get("name", "").lower()
        if table_name in relevant_set:
            compressed["tables"].append(table)
            
    # 过滤列
    for table_name, columns in schema_info.get("columns", {}).items():
        if table_name.lower() in relevant_set:
            compressed["columns"][table_name] = columns
            
    # 过滤关系
    for rel in schema_info.get("relationships", []):
        from_table = rel.get("from_table", "").lower()
        to_table = rel.get("to_table", "").lower()
        if from_table in relevant_set or to_table in relevant_set:
            compressed["relationships"].append(rel)
            
    # 过滤索引
    for table_name, indexes in schema_info.get("indexes", {}).items():
        if table_name.lower() in relevant_set:
            compressed["indexes"][table_name] = indexes
            
    return compressed


def compress_results(
    results: List[Dict[str, Any]], 
    max_rows: int = 50,
    max_cell_length: int = 100
) -> Dict[str, Any]:
    """压缩查询结果
    
    对大结果集进行采样和截断
    
    Args:
        results: 查询结果列表
        max_rows: 最大保留行数
        max_cell_length: 单元格最大长度
        
    Returns:
        压缩后的结果信息
    """
    if len(results) <= max_rows:
        # 截断单元格内容
        compressed_results = []
        for row in results:
            compressed_row = {}
            for k, v in row.items():
                v_str = str(v) if v is not None else ""
                if len(v_str) > max_cell_length:
                    v_str = v_str[:max_cell_length] + "..."
                compressed_row[k] = v_str
            compressed_results.append(compressed_row)
        return {
            "data": compressed_results,
            "total_count": len(results),
            "truncated": False
        }
    
    # 保留前10条作为样本
    sample = results[:10]
    compressed_sample = []
    for row in sample:
        compressed_row = {}
        for k, v in row.items():
            v_str = str(v) if v is not None else ""
            if len(v_str) > max_cell_length:
                v_str = v_str[:max_cell_length] + "..."
            compressed_row[k] = v_str
        compressed_sample.append(compressed_row)
        
    return {
        "data": compressed_sample,
        "total_count": len(results),
        "truncated": True,
        "message": f"共{len(results)}条记录，显示前10条样本"
    }
