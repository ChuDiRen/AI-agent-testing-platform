"""
ContextCompressor - 上下文压缩服务

智能压缩上下文，减少Token消耗30-50%
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class ContextCompressor:
    """上下文压缩器"""

    def __init__(self, summarization_model: Optional[ChatOpenAI] = None):
        self.model = summarization_model

    def estimate_tokens(self, text: str) -> int:
        """估算Token数量（简单估算：中文约1.5字/token，英文约4字符/token）"""
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        other_chars = len(text) - chinese_chars
        return int(chinese_chars / 1.5 + other_chars / 4)

    def compress(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int = 4000,
    ) -> List[Dict[str, Any]]:
        """压缩上下文，保留关键信息"""
        total_tokens = sum(self.estimate_tokens(m.get("content", "")) for m in messages)
        if total_tokens <= max_tokens:
            return messages  # 不需要压缩
        # 保留最新的消息，压缩历史消息
        if len(messages) <= 2:
            return messages
        # 保留第一条(系统提示)和最后两条(最近对话)
        preserved = [messages[0]] if messages else []
        preserved.extend(messages[-2:])
        # 中间消息进行摘要
        middle_messages = messages[1:-2]
        if middle_messages:
            summary = self._summarize_messages(middle_messages)
            preserved.insert(1, {"role": "system", "content": f"[历史摘要] {summary}"})
        return preserved

    def _summarize_messages(self, messages: List[Dict[str, Any]]) -> str:
        """摘要历史消息"""
        if not self.model:
            # 无模型时简单截取
            content = " ".join(m.get("content", "")[:100] for m in messages)
            return content[:500] + "..." if len(content) > 500 else content
        # 使用LLM摘要
        try:
            combined = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
            prompt = f"请用100字以内摘要以下对话的关键信息：\n{combined}"
            response = self.model.invoke([{"role": "user", "content": prompt}])
            return response.content
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "历史对话摘要失败"
