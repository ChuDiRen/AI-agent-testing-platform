#!/usr/bin/env python3
"""
自定义 Store 实现 - 支持长期记忆管理
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, AsyncIterator
from datetime import datetime, timedelta
from dataclasses import dataclass

from langgraph.store.base import BaseStore, Item
from langgraph.store.memory import InMemoryStore


@dataclass
class MemoryItem:
    """记忆项数据结构"""
    namespace: str
    key: str
    value: Dict[str, Any]
    timestamp: str
    importance_score: float
    memory_type: str
    tags: List[str]
    access_count: int
    thread_id: Optional[str] = None


class CustomStore(BaseStore):
    """自定义存储实现，支持长期记忆管理"""
    
    def __init__(self, custom_config: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.custom_config = custom_config or {}
        self.memory_store = InMemoryStore()
        self.long_term_memories: Dict[str, MemoryItem] = {}
        
        # 配置参数
        self.importance_threshold = self.custom_config.get('importance_threshold', 0.5)
        self.max_memories = self.custom_config.get('max_memories', 1000)
        self.max_memories_per_namespace = self.custom_config.get('max_memories_per_namespace', 1000)
        self.max_memory_age_days = self.custom_config.get('max_memory_age_days', 90)
        
        logger = self._get_logger()
        
    def _get_logger(self):
        """获取日志记录器"""
        import logging
        return logging.getLogger(__name__)
    
    async def get(self, namespace: str, key: str) -> Optional[Item]:
        """获取存储项"""
        # 先查内存存储
        try:
            item = await self.memory_store.get(namespace, key)
            if item:
                # 更新访问统计
                self._update_access_stats(namespace, key)
                return item
        except Exception:
            pass
        
        # 查长期记忆
        memory_key = f"{namespace}:{key}"
        memory_item = self.long_term_memories.get(memory_key)
        
        if memory_item:
            # 更新访问统计
            memory_item.access_count += 1
            memory_item.last_accessed = datetime.now().isoformat()
            
            # 转换为Item格式
            current_time = datetime.now()
            return Item(
                value=memory_item.value,
                key=memory_item.key,
                namespace=(memory_item.namespace,),
                created_at=datetime.fromisoformat(memory_item.timestamp),
                updated_at=current_time
            )
        
        return None
    
    async def put(self, namespace: str, key: str, value: Dict[str, Any]) -> None:
        """存储项"""
        # 判断是否需要长期存储
        importance_score = self._calculate_importance(value)
        memory_type = self._classify_memory(value)
        tags = self._extract_tags(value)
        
        if importance_score >= self.importance_threshold:
            # 存储到长期记忆
            memory_item = MemoryItem(
                namespace=namespace,
                key=key,
                value=value,
                timestamp=datetime.now().isoformat(),
                importance_score=importance_score,
                memory_type=memory_type,
                tags=tags,
                access_count=1,
                thread_id=self._extract_thread_id(value)
            )
            
            memory_key = f"{namespace}:{key}"
            self.long_term_memories[memory_key] = memory_item
            
            # 检查是否需要清理
            self._cleanup_namespace_memories(namespace)
        
        # 同时存储到内存存储（用于快速访问）
        try:
            if hasattr(self.memory_store, 'put'):
                await self.memory_store.put(namespace, key, value)
        except Exception as e:
            # 内存存储失败不影响长期记忆存储
            pass
    
    async def delete(self, namespace: str, key: str) -> None:
        """删除项"""
        # 从内存存储删除
        try:
            await self.memory_store.delete(namespace, key)
        except Exception:
            pass
        
        # 从长期记忆删除
        memory_key = f"{namespace}:{key}"
        self.long_term_memories.pop(memory_key, None)
    
    async def list(self, namespace: str, limit: int = 10, before: Optional[str] = None) -> AsyncIterator[Item]:
        """列出存储项"""
        # 先从内存存储获取
        try:
            async for item in self.memory_store.list(namespace, limit, before):
                yield item
        except Exception:
            pass
        
        # 从长期记忆获取
        namespace_memories = [
            mem for mem in self.long_term_memories.values()
            if mem.namespace == namespace
        ]
        
        # 按时间戳排序
        namespace_memories.sort(key=lambda x: x.timestamp, reverse=True)
        
        # 应用限制
        if before:
            namespace_memories = [mem for mem in namespace_memories if mem.timestamp < before]
        
        for memory_item in namespace_memories[:limit]:
            current_time = datetime.now()
            yield Item(
                value=memory_item.value,
                key=memory_item.key,
                namespace=(memory_item.namespace,),
                created_at=datetime.fromisoformat(memory_item.timestamp),
                updated_at=current_time
            )
    
    async def search(self, query: str, namespace: Optional[str] = None, limit: int = 10) -> AsyncIterator[Item]:
        """搜索记忆"""
        query_lower = query.lower()
        matching_memories = []
        
        for memory_item in self.long_term_memories.values():
            # 命名空间过滤
            if namespace and memory_item.namespace != namespace:
                continue
            
            # 内容匹配
            content_text = self._extract_searchable_text(memory_item.value)
            if query_lower in content_text.lower():
                # 计算相关性分数
                relevance = self._calculate_relevance(query_lower, content_text.lower())
                memory_item.search_relevance = relevance
                matching_memories.append(memory_item)
        
        # 按相关性排序
        matching_memories.sort(key=lambda x: getattr(x, 'search_relevance', 0), reverse=True)
        
        # 返回结果
        for memory_item in matching_memories[:limit]:
            current_time = datetime.now()
            yield Item(
                value=memory_item.value,
                key=memory_item.key,
                namespace=(memory_item.namespace,),
                created_at=datetime.fromisoformat(memory_item.timestamp),
                updated_at=current_time
            )
    
    async def get_memories_by_type(self, memory_type: str, limit: int = 20) -> List[Dict[str, Any]]:
        """按类型获取记忆"""
        memories = [
            {
                'namespace': mem.namespace,
                'key': mem.key,
                'value': mem.value,
                'timestamp': mem.timestamp,
                'importance_score': mem.importance_score,
                'tags': mem.tags,
                'access_count': mem.access_count
            }
            for mem in self.long_term_memories.values()
            if mem.memory_type == memory_type
        ]
        
        # 按重要性排序
        memories.sort(key=lambda x: x['importance_score'], reverse=True)
        
        return memories[:limit]
    
    async def get_memories_by_tags(self, tags: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """按标签获取记忆"""
        memories = []
        
        for mem in self.long_term_memories.values():
            mem_tags = mem.tags
            if any(tag in mem_tags for tag in tags):
                memories.append({
                    'namespace': mem.namespace,
                    'key': mem.key,
                    'value': mem.value,
                    'timestamp': mem.timestamp,
                    'importance_score': mem.importance_score,
                    'tags': mem.tags,
                    'access_count': mem.access_count
                })
        
        # 按重要性排序
        memories.sort(key=lambda x: x['importance_score'], reverse=True)
        
        return memories[:limit]
    
    async def get_thread_memories(self, thread_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取线程的所有记忆"""
        memories = [
            {
                'namespace': mem.namespace,
                'key': mem.key,
                'value': mem.value,
                'timestamp': mem.timestamp,
                'importance_score': mem.importance_score,
                'tags': mem.tags,
                'access_count': mem.access_count
            }
            for mem in self.long_term_memories.values()
            if mem.thread_id == thread_id
        ]
        
        # 按时间排序
        memories.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return memories[:limit]
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        total_memories = len(self.long_term_memories)
        
        # 按类型统计
        type_stats = {}
        for mem in self.long_term_memories.values():
            mem_type = mem.memory_type
            type_stats[mem_type] = type_stats.get(mem_type, 0) + 1
        
        # 按命名空间统计
        namespace_stats = {}
        for mem in self.long_term_memories.values():
            namespace = mem.namespace
            namespace_stats[namespace] = namespace_stats.get(namespace, 0) + 1
        
        # 访问统计
        total_access = sum(mem.access_count for mem in self.long_term_memories.values())
        
        return {
            'total_memories': total_memories,
            'type_distribution': type_stats,
            'namespace_distribution': namespace_stats,
            'total_access_count': total_access,
            'average_importance': sum(mem.importance_score for mem in self.long_term_memories.values()) / total_memories if total_memories > 0 else 0
        }
    
    async def close(self):
        """关闭存储，清理资源"""
        pass
    
    async def batch(self, operations: List[tuple[str, str, Any]]) -> List[Item]:
        """批量操作"""
        results = []
        for op in operations:
            namespace, key, value = op
            item = await self.get(namespace, key)
            if item:
                results.append(item)
            else:
                current_time = datetime.now()
                results.append(Item(
                    value=value,
                    key=key,
                    namespace=(namespace,),
                    created_at=current_time,
                    updated_at=current_time
                ))
        return results
    
    async def abatch(self, operations: List[tuple[str, str, Any]]) -> List[Item]:
        """异步批量操作"""
        return await self.batch(operations)
    
    def _calculate_importance(self, value: Dict[str, Any]) -> float:
        """计算重要性分数"""
        score = 0.0
        content_lower = self._extract_searchable_text(value).lower()
        
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
        content_text = self._extract_searchable_text(value)
        if len(content_text) > 100:
            score += 0.1
        elif len(content_text) > 50:
            score += 0.05
        
        return min(score, 1.0)
    
    def _classify_memory(self, value: Dict[str, Any]) -> str:
        """分类记忆类型"""
        content_lower = self._extract_searchable_text(value).lower()
        
        memory_types = {
            'identity': ['名字', '叫', '是', '身份'],
            'preference': ['喜欢', '讨厌', '偏好', '爱好'],
            'requirement': ['需要', '必须', '要求', '不能'],
            'important_fact': ['记住', '重要', '关键', '事实'],
            'event': ['事件', '发生', '经历', '故事']
        }
        
        for mem_type, keywords in memory_types.items():
            if any(word in content_lower for word in keywords):
                return mem_type
        
        return 'general'
    
    def _extract_tags(self, value: Dict[str, Any]) -> List[str]:
        """提取标签"""
        tags = []
        content_lower = self._extract_searchable_text(value).lower()
        
        # 基于内容提取标签
        if '咖啡' in content_lower:
            tags.append('咖啡')
        if '茶' in content_lower:
            tags.append('茶')
        if '食物' in content_lower or '吃' in content_lower:
            tags.append('食物')
        if '工作' in content_lower:
            tags.append('work')
        if '家庭' in content_lower or '家人' in content_lower:
            tags.append('家庭')
        if '学习' in content_lower:
            tags.append('学习')
        if '运动' in content_lower:
            tags.append('运动')
        
        return tags
    
    def _extract_searchable_text(self, value: Any) -> str:
        """提取可搜索的文本"""
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            # 递归提取字典中的所有字符串值
            texts = []
            for v in value.values():
                texts.append(self._extract_searchable_text(v))
            return ' '.join(texts)
        elif isinstance(value, list):
            # 提取列表中的所有字符串
            texts = []
            for item in value:
                texts.append(self._extract_searchable_text(item))
            return ' '.join(texts)
        else:
            return str(value)
    
    def _calculate_relevance(self, query: str, content: str) -> float:
        """计算搜索相关性"""
        if not query or not content:
            return 0.0
        
        query_words = set(query.split())
        content_words = set(content.split())
        
        if not query_words:
            return 0.0
        
        overlap = query_words.intersection(content_words)
        return len(overlap) / len(query_words)
    
    def _update_access_stats(self, namespace: str, key: str):
        """更新访问统计"""
        memory_key = f"{namespace}:{key}"
        memory_item = self.long_term_memories.get(memory_key)
        
        if memory_item:
            memory_item.access_count += 1
            memory_item.last_accessed = datetime.now().isoformat()
    
    def _extract_thread_id(self, value: Dict[str, Any]) -> Optional[str]:
        """提取线程ID"""
        return value.get('thread_id')
    
    def _cleanup_namespace_memories(self, namespace: str):
        """清理命名空间中的过多记忆"""
        namespace_memories = [
            mem for mem in self.long_term_memories.values()
            if mem.namespace == namespace
        ]
        
        if len(namespace_memories) > self.max_memories_per_namespace:
            # 按重要性和访问时间排序
            namespace_memories.sort(key=lambda x: (x.importance_score, x.access_count))
            
            # 删除超出限制的记忆
            memories_to_delete = namespace_memories[:-self.max_memories_per_namespace]
            
            for mem in memories_to_delete:
                memory_key = f"{mem.namespace}:{mem.key}"
                if memory_key in self.long_term_memories:
                    del self.long_term_memories[memory_key]
    
    def _cleanup_expired_memories(self):
        """清理过期记忆"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(days=self.max_memory_age_days)
        
        expired_keys = []
        for key, memory in self.long_term_memories.items():
            try:
                memory_time = datetime.fromisoformat(memory.timestamp)
                if memory_time < cutoff_time:
                    expired_keys.append(key)
            except (ValueError, TypeError):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.long_term_memories.pop(key, key=None)
        
        if expired_keys:
            self.logger.info(f"清理了 {len(expired_keys)} 条过期记忆")


def get_store() -> CustomStore:
    """工厂函数 - 创建自定义存储实例"""
    custom_config = {
        'importance_threshold': 0.5,
        'max_memories': 1000,
        'max_memory_age_days': 90
    }
    
    return CustomStore(custom_config)
