"""
BaseTask - 任务基类

提供任务执行的通用接口和便捷方法
"""
import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, Optional
from dataclasses import dataclass

from agent_langgraph.core import ModelFactory, ModelConfig

logger = logging.getLogger(__name__)

StateType = TypeVar("StateType", bound=Dict[str, Any])


@dataclass
class TaskResult:
    """任务执行结果"""
    success: bool
    state: Dict[str, Any]
    output: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def is_error(self) -> bool:
        return self.error is not None


class BaseTask(ABC, Generic[StateType]):
    """
    任务基类
    
    提供统一的任务执行接口
    """
    
    task_type: str = "base"
    
    def __init__(self, model_config: Optional[ModelConfig] = None):
        """
        初始化任务
        
        Args:
            model_config: 模型配置，为None时使用默认配置
        """
        if model_config:
            ModelFactory.set_default_config(model_config)
    
    @abstractmethod
    def get_graph(self):
        """获取编译后的Graph"""
        pass
    
    @abstractmethod
    def create_initial_state(self, **kwargs) -> StateType:
        """创建初始状态"""
        pass
    
    def run(self, **kwargs) -> TaskResult:
        """
        同步执行任务
        
        Args:
            **kwargs: 传递给create_initial_state的参数
            
        Returns:
            TaskResult
        """
        import asyncio
        return asyncio.run(self.arun(**kwargs))
    
    async def arun(self, **kwargs) -> TaskResult:
        """
        异步执行任务
        
        Args:
            **kwargs: 传递给create_initial_state的参数
            
        Returns:
            TaskResult
        """
        try:
            graph = self.get_graph()
            initial_state = self.create_initial_state(**kwargs)
            
            logger.info(f"Starting task: {self.task_type}")
            final_state = await graph.ainvoke(initial_state)
            
            success = final_state.get("completed", False) and not final_state.get("error")
            
            return TaskResult(
                success=success,
                state=final_state,
                output=final_state.get("output"),
                error=final_state.get("error"),
            )
        except Exception as e:
            logger.error(f"Task {self.task_type} failed: {e}")
            return TaskResult(
                success=False,
                state={},
                error=str(e),
            )
    
    def stream(self, **kwargs):
        """
        流式执行任务
        
        Yields:
            (node_name, state) 元组
        """
        graph = self.get_graph()
        initial_state = self.create_initial_state(**kwargs)
        
        for output in graph.stream(initial_state):
            for node_name, state in output.items():
                yield node_name, state
