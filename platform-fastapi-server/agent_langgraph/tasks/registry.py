"""
TaskRegistry - 任务注册表

统一管理所有任务类型的Graph，支持动态获取
"""
import logging
from typing import Dict, Any, Optional, Type

from agent_langgraph.core import BaseGraphBuilder

logger = logging.getLogger(__name__)


class TaskRegistry:
    """
    任务注册表
    
    管理所有任务类型的GraphBuilder
    """
    
    _builders: Dict[str, Type[BaseGraphBuilder]] = {}
    _graphs: Dict[str, Any] = {}
    
    @classmethod
    def register(cls, task_type: str, builder_class: Type[BaseGraphBuilder]):
        """
        注册任务类型
        
        Args:
            task_type: 任务类型标识
            builder_class: GraphBuilder类
        """
        cls._builders[task_type] = builder_class
        logger.info(f"Registered task: {task_type}")
    
    @classmethod
    def get_builder(cls, task_type: str) -> Optional[Type[BaseGraphBuilder]]:
        """获取GraphBuilder类"""
        return cls._builders.get(task_type)
    
    @classmethod
    def get_graph(cls, task_type: str, checkpointer=None, use_cache: bool = True):
        """
        获取编译后的Graph
        
        Args:
            task_type: 任务类型
            checkpointer: 可选的checkpointer
            use_cache: 是否使用缓存
        """
        cache_key = f"{task_type}:{id(checkpointer) if checkpointer else 'none'}"
        
        if use_cache and cache_key in cls._graphs:
            return cls._graphs[cache_key]
        
        builder_class = cls._builders.get(task_type)
        if not builder_class:
            raise ValueError(f"Unknown task type: {task_type}")
        
        builder = builder_class()
        graph = builder.build(checkpointer)
        
        if use_cache:
            cls._graphs[cache_key] = graph
        
        return graph
    
    @classmethod
    def list_tasks(cls) -> list:
        """列出所有注册的任务类型"""
        return list(cls._builders.keys())
    
    @classmethod
    def clear_cache(cls):
        """清除Graph缓存"""
        cls._graphs.clear()


def get_graph(task_type: str, checkpointer=None):
    """便捷函数：获取指定任务类型的Graph"""
    return TaskRegistry.get_graph(task_type, checkpointer)


def get_all_graphs() -> Dict[str, Any]:
    """获取所有任务类型的Graph"""
    return {
        task_type: TaskRegistry.get_graph(task_type)
        for task_type in TaskRegistry.list_tasks()
    }
