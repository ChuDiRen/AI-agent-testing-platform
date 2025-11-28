"""
上下文管理器

整合消息裁剪和上下文压缩的统一接口
"""

from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage, SystemMessage

from .trimmer import MessageTrimmer, trim_messages
from .compressor import (
    ContextCompressor, 
    compress_schema_info, 
    compress_results
)
from ..config import LLMConfig


class ContextManager:
    """上下文管理器
    
    提供消息裁剪、上下文压缩和Schema压缩的统一接口
    """
    
    def __init__(
        self,
        max_tokens: int = 8000,
        max_messages: int = 20,
        keep_recent_messages: int = 5,
        llm_config: Optional[LLMConfig] = None,
        enable_compression: bool = True
    ):
        """初始化上下文管理器
        
        Args:
            max_tokens: 最大token数
            max_messages: 最大消息数
            keep_recent_messages: 压缩时保留的最近消息数
            llm_config: LLM配置（用于生成摘要）
            enable_compression: 是否启用压缩
        """
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.keep_recent_messages = keep_recent_messages
        self.enable_compression = enable_compression
        
        self._trimmer = MessageTrimmer(
            max_tokens=max_tokens,
            max_messages=max_messages,
            strategy="smart",
            include_system=True
        )
        
        self._compressor = ContextCompressor(
            llm_config=llm_config,
            max_tokens_before_compress=int(max_tokens * 0.75),
            keep_recent_messages=keep_recent_messages
        )
        
    def process_messages(
        self, 
        messages: List[BaseMessage],
        use_compression: Optional[bool] = None
    ) -> List[BaseMessage]:
        """处理消息列表
        
        根据配置进行裁剪或压缩
        
        Args:
            messages: 原始消息列表
            use_compression: 是否使用压缩（None则使用默认配置）
            
        Returns:
            处理后的消息列表
        """
        if not messages:
            return messages
            
        compress = use_compression if use_compression is not None else self.enable_compression
        
        if compress:
            # 使用压缩策略
            return self._compressor.compress(messages)
        else:
            # 使用裁剪策略
            return self._trimmer.trim(messages)
            
    async def process_messages_async(
        self, 
        messages: List[BaseMessage],
        use_compression: Optional[bool] = None
    ) -> List[BaseMessage]:
        """异步处理消息列表
        
        Args:
            messages: 原始消息列表
            use_compression: 是否使用压缩
            
        Returns:
            处理后的消息列表
        """
        if not messages:
            return messages
            
        compress = use_compression if use_compression is not None else self.enable_compression
        
        if compress:
            return await self._compressor.compress_async(messages)
        else:
            return self._trimmer.trim(messages)
            
    def prepare_schema_context(
        self,
        schema_info: Dict[str, Any],
        query: str,
        relevant_tables: Optional[List[str]] = None
    ) -> str:
        """准备Schema上下文
        
        根据查询压缩Schema信息
        
        Args:
            schema_info: 完整Schema信息
            query: 用户查询
            relevant_tables: 相关表列表（可选，用于精确过滤）
            
        Returns:
            格式化的Schema上下文字符串
        """
        # 如果指定了相关表，进行压缩
        if relevant_tables:
            schema_info = compress_schema_info(schema_info, relevant_tables)
            
        # 格式化为字符串
        lines = ["## 数据库Schema信息\n"]
        
        for table in schema_info.get("tables", []):
            table_name = table.get("name", "unknown")
            lines.append(f"### 表: {table_name}")
            
            if table.get("comment"):
                lines.append(f"描述: {table['comment']}")
                
            columns = schema_info.get("columns", {}).get(table_name, [])
            if columns:
                lines.append("列:")
                for col in columns:
                    col_info = f"  - {col['name']}: {col['data_type']}"
                    if col.get("primary_key"):
                        col_info += " [PK]"
                    if col.get("foreign_key"):
                        col_info += f" [FK -> {col['foreign_key']}]"
                    lines.append(col_info)
                    
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
            lines.append("")
            
        return "\n".join(lines)
        
    def prepare_results_context(
        self,
        results: List[Dict[str, Any]],
        max_rows: int = 50
    ) -> Dict[str, Any]:
        """准备结果上下文
        
        压缩大结果集
        
        Args:
            results: 查询结果
            max_rows: 最大行数
            
        Returns:
            压缩后的结果信息
        """
        return compress_results(results, max_rows=max_rows)
        
    def estimate_tokens(self, messages: List[BaseMessage]) -> int:
        """估算消息的token数
        
        Args:
            messages: 消息列表
            
        Returns:
            估算的token数
        """
        total = 0
        for msg in messages:
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            total += len(content) // 2
        return total
        
    def is_context_too_large(self, messages: List[BaseMessage]) -> bool:
        """检查上下文是否过大
        
        Args:
            messages: 消息列表
            
        Returns:
            是否超过限制
        """
        return self.estimate_tokens(messages) > self.max_tokens


# 默认上下文管理器实例
_context_manager: Optional[ContextManager] = None


def get_context_manager(
    max_tokens: int = 8000,
    max_messages: int = 20
) -> ContextManager:
    """获取全局上下文管理器
    
    Args:
        max_tokens: 最大token数
        max_messages: 最大消息数
        
    Returns:
        ContextManager实例
    """
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager(
            max_tokens=max_tokens,
            max_messages=max_messages
        )
    return _context_manager
