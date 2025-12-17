"""
BaseGraphBuilder - Graph构建器基类

提供统一的Graph构建接口，子类只需定义节点和边
"""
import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Any, List, Tuple, Optional, Callable, Type

from langgraph.graph import StateGraph, START, END

logger = logging.getLogger(__name__)

StateType = TypeVar("StateType", bound=Dict[str, Any])


class BaseGraphBuilder(ABC, Generic[StateType]):
    """
    Graph构建器基类
    
    子类需要实现：
    - get_state_class(): 返回State类型
    - get_nodes(): 返回节点字典
    - get_edges(): 返回边定义
    - get_conditional_edges(): 返回条件边定义（可选）
    """
    
    task_type: str = "base"
    
    @abstractmethod
    def get_state_class(self) -> Type[StateType]:
        """返回State类型"""
        pass
    
    @abstractmethod
    def get_nodes(self) -> Dict[str, Callable[[StateType], StateType]]:
        """
        返回节点字典
        
        Returns:
            {node_name: node_function}
        """
        pass
    
    @abstractmethod
    def get_edges(self) -> List[Tuple[str, str]]:
        """
        返回边定义
        
        Returns:
            [(from_node, to_node), ...]
            使用 "START" 和 "END" 表示起止
        """
        pass
    
    def get_conditional_edges(self) -> List[Tuple[str, Callable, Dict[str, str]]]:
        """
        返回条件边定义（可选）
        
        Returns:
            [(from_node, condition_func, {result: target_node}), ...]
        """
        return []
    
    def build(self, checkpointer=None) -> StateGraph:
        """
        构建Graph
        
        Args:
            checkpointer: 可选的checkpointer
            
        Returns:
            编译后的Graph
        """
        state_class = self.get_state_class()
        workflow = StateGraph(state_class)
        
        # 添加节点
        nodes = self.get_nodes()
        for node_name, node_func in nodes.items():
            workflow.add_node(node_name, node_func)
            logger.debug(f"Added node: {node_name}")
        
        # 添加边
        edges = self.get_edges()
        for from_node, to_node in edges:
            from_ref = START if from_node == "START" else from_node
            to_ref = END if to_node == "END" else to_node
            workflow.add_edge(from_ref, to_ref)
            logger.debug(f"Added edge: {from_node} -> {to_node}")
        
        # 添加条件边
        conditional_edges = self.get_conditional_edges()
        for from_node, condition_func, mapping in conditional_edges:
            resolved_mapping = {}
            for key, target in mapping.items():
                resolved_mapping[key] = END if target == "END" else target
            workflow.add_conditional_edges(from_node, condition_func, resolved_mapping)
            logger.debug(f"Added conditional edge from: {from_node}")
        
        # 编译
        if checkpointer:
            return workflow.compile(checkpointer=checkpointer)
        return workflow.compile()
    
    def get_graph(self, checkpointer=None):
        """便捷方法：构建并返回Graph"""
        return self.build(checkpointer)


class SimpleGraphBuilder(BaseGraphBuilder[StateType]):
    """
    简单Graph构建器
    
    适用于线性流程的Graph，只需提供节点列表即可自动生成边
    """
    
    def __init__(
        self,
        state_class: Type[StateType],
        nodes: List[Tuple[str, Callable]],
        task_type: str = "simple"
    ):
        """
        Args:
            state_class: State类型
            nodes: 按顺序排列的节点列表 [(name, func), ...]
            task_type: 任务类型
        """
        self._state_class = state_class
        self._nodes = nodes
        self.task_type = task_type
    
    def get_state_class(self) -> Type[StateType]:
        return self._state_class
    
    def get_nodes(self) -> Dict[str, Callable]:
        return {name: func for name, func in self._nodes}
    
    def get_edges(self) -> List[Tuple[str, str]]:
        """自动生成线性边"""
        edges = []
        node_names = [name for name, _ in self._nodes]
        
        if node_names:
            edges.append(("START", node_names[0]))
            for i in range(len(node_names) - 1):
                edges.append((node_names[i], node_names[i + 1]))
            edges.append((node_names[-1], "END"))
        
        return edges
