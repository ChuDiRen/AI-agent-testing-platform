#!/usr/bin/env python3
"""
自定义 Checkpointer 实现 - 支持长期记忆管理
"""

import json
import time
from typing import Any, Dict, List, Optional, Sequence, Union
from datetime import datetime, timedelta

from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig


class CustomCheckpointer(BaseCheckpointSaver):
    """自定义检查点实现，支持长期记忆管理"""
    
    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.custom_config = custom_config or {}
        self.memory_saver = MemorySaver()
        self.long_term_storage: Dict[str, Dict[str, Any]] = {}
        
        # 配置参数
        self.memory_threshold = self.custom_config.get('memory_threshold', 100)
        self.max_memory_age_days = self.custom_config.get('max_memory_age_days', 30)
        
        self.logger = self._get_logger()
        
    def _get_logger(self):
        """获取日志记录器"""
        import logging
        return logging.getLogger(__name__)
    
    def get(self, config: RunnableConfig, **kwargs) -> Optional[Checkpoint]:
        """获取检查点"""
        return self.memory_saver.get(config, **kwargs)
    
    def get_tuple(self, config: RunnableConfig, **kwargs) -> Optional[CheckpointTuple]:
        """获取检查点元组"""
        return self.memory_saver.get_tuple(config, **kwargs)
    
    def list(self, config: Optional[RunnableConfig], **kwargs) -> Sequence[CheckpointTuple]:
        """列出检查点"""
        return self.memory_saver.list(config, **kwargs)
    
    def put(
        self,
        config: RunnableConfig,
        checkpoint: Union[Checkpoint, Dict[str, Any]],
        metadata: Union[CheckpointMetadata, Dict[str, Any]],
        new_versions: Any,
    ) -> RunnableConfig:
        """存储检查点，处理长期记忆"""
        
        # 处理元数据，提取长期记忆
        processed_metadata = self._process_metadata(metadata, checkpoint)
        
        # 存储到内存检查点
        result = self.memory_saver.put(config, checkpoint, processed_metadata, new_versions)
        
        # 检查是否需要长期存储
        self._check_long_term_storage(config, checkpoint, processed_metadata)
        
        return result
    
    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[tuple[str, Any]],
        task_id: str,
    ) -> None:
        """存储写入操作"""
        self.memory_saver.put_writes(config, writes, task_id)
        
        # 分析写入内容，提取重要信息
        for channel, value in writes:
            if self._is_important_content(value):
                self._store_long_term_memory(channel, value, config)
    
    def _process_metadata(self, metadata: Union[CheckpointMetadata, Dict[str, Any]], checkpoint: Union[Checkpoint, Dict[str, Any]]) -> Dict[str, Any]:
        """处理元数据，添加记忆相关信息"""
        processed_metadata = dict(metadata) if metadata else {}
        
        # 添加时间戳
        processed_metadata['timestamp'] = datetime.now().isoformat()
        
        # 分析检查点内容
        if checkpoint and isinstance(checkpoint, dict):
            important_info = self._extract_important_info(checkpoint.get('channel_values', {}))
            if important_info:
                processed_metadata['important_info'] = important_info
        
        return processed_metadata
    
    def _extract_important_info(self, channel_values: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从通道值中提取重要信息"""
        important_info = []
        
        for channel, value in channel_values.items():
            if self._is_important_content(value):
                memory_info = {
                    'channel': channel,
                    'content': value,
                    'type': self._classify_content(value),
                    'importance_score': self._calculate_importance(value)
                }
                important_info.append(memory_info)
        
        return important_info
    
    def _is_important_content(self, content: Any) -> bool:
        """判断内容是否重要"""
        if not isinstance(content, str):
            return False
        
        importance_indicators = [
            '记住', '重要', '关键', '永远', '不要忘记',
            '我叫', '我的名字是', '我是',
            '喜欢', '讨厌', '需要', '必须', '不能'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in importance_indicators)
    
    def _classify_content(self, content: str) -> str:
        """分类内容类型"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['名字', '叫', '是', '身份']):
            return 'identity'
        elif any(word in content_lower for word in ['喜欢', '讨厌', '偏好', '爱好']):
            return 'preference'
        elif any(word in content_lower for word in ['需要', '必须', '要求', '不能']):
            return 'requirement'
        elif any(word in content_lower for word in ['记住', '重要', '关键', '事实']):
            return 'important_fact'
        elif any(word in content_lower for word in ['事件', '发生', '经历', '故事']):
            return 'event'
        else:
            return 'general'
    
    def _calculate_importance(self, content: str) -> float:
        """计算内容重要性分数"""
        score = 0.0
        content_lower = content.lower()
        
        # 高重要性关键词
        high_importance = ['永远', '记住', '关键', '重要', '必须', '喜欢', '讨厌', '名字', '叫']
        medium_importance = ['需要', '希望', '想要', '应该', '不要']
        low_importance = ['知道', '了解', '听说', '可能']
        
        for word in high_importance:
            if word in content_lower:
                score += 0.3
        
        for word in medium_importance:
            if word in content_lower:
                score += 0.2
        
        for word in low_importance:
            if word in content_lower:
                score += 0.1
        
        # 基于长度的重要性
        if len(content) > 50:
            score += 0.1
        
        return min(score, 1.0)
    
    def _check_long_term_storage(self, config: RunnableConfig, checkpoint: Union[Checkpoint, Dict[str, Any]], metadata: Union[CheckpointMetadata, Dict[str, Any]]):
        """检查是否需要长期存储"""
        if not metadata:
            return
        
        important_info = metadata.get('important_info', [])
        if important_info:
            thread_id = config.get('configurable', {}).get('thread_id', 'default')
            
            for info in important_info:
                if info.get('importance_score', 0) > 0.6:  # 高重要性内容
                    self._store_long_term_memory(info.get('channel', 'default'), info, config)
    
    def _store_long_term_memory(self, channel: str, content: Any, config: RunnableConfig):
        """存储到长期记忆"""
        thread_id = config.get('configurable', {}).get('thread_id', 'default')
        memory_key = f"{thread_id}:{channel}:{int(time.time())}"
        
        memory_item = {
            'content': content,
            'channel': channel,
            'thread_id': thread_id,
            'timestamp': datetime.now().isoformat(),
            'config': config
        }
        
        self.long_term_storage[memory_key] = memory_item
        
        # 清理过期记忆
        self._cleanup_old_memories()
    
    def _cleanup_old_memories(self):
        """清理过期记忆"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(days=self.max_memory_age_days)
        
        expired_keys = []
        for key, memory in self.long_term_storage.items():
            try:
                memory_time = datetime.fromisoformat(memory['timestamp'])
                if memory_time < cutoff_time:
                    expired_keys.append(key)
            except (ValueError, TypeError):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.long_term_storage[key]
        
        if expired_keys:
            self.logger.info(f"清理了 {len(expired_keys)} 条过期记忆")
    
    def get_long_term_memories(self, thread_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取长期记忆"""
        memories = []
        
        for key, memory in self.long_term_storage.items():
            if thread_id is None or memory.get('thread_id') == thread_id:
                memories.append(memory)
        
        # 按时间戳排序
        memories.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return memories
    
    def search_memories(self, query: str, thread_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """搜索长期记忆"""
        query_lower = query.lower()
        matching_memories = []
        
        for memory in self.get_long_term_memories(thread_id):
            content = str(memory.get('content', '')).lower()
            
            # 简单的关键词匹配
            if query_lower in content:
                # 计算相关性分数
                relevance_score = self._calculate_relevance(query_lower, content)
                memory['relevance_score'] = relevance_score
                matching_memories.append(memory)
        
        # 按相关性排序
        matching_memories.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return matching_memories[:limit]
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算查询与内容的相关性"""
        if not query or not content:
            return 0.0
        
        query_words = set(query.split())
        content_words = set(content.split())
        
        if not query_words:
            return 0.0
        
        overlap = query_words.intersection(content_words)
        return len(overlap) / len(query_words)


def get_checkpointer() -> CustomCheckpointer:
    """工厂函数 - 创建自定义检查点实例"""
    custom_config = {
        'memory_threshold': 100,
        'max_memory_age_days': 30
    }
    
    return CustomCheckpointer(custom_config)
