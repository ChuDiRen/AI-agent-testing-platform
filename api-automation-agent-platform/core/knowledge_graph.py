"""
完整的知识图谱引擎 - Knowledge Graph Engine

功能：
- 实体提取和关系建模
- 图谱构建和查询
- 社区检测和聚类
- 图谱可视化支持
"""
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid
import networkx as nx
from collections import defaultdict

from core.models import RAGEntity, RAGRelationship
from core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class GraphNode:
    """图节点"""
    node_id: str
    entity: RAGEntity
    neighbors: Set[str] = field(default_factory=set)
    community_id: Optional[int] = None
    centrality: float = 0.0


@dataclass
class GraphEdge:
    """图边"""
    edge_id: str
    relationship: RAGRelationship
    weight: float = 1.0


class KnowledgeGraphEngine:
    """
    知识图谱引擎
    
    核心功能：
    - 实体和关系管理
    - 图谱构建和查询
    - 社区检测
    - 路径查找
    - 中心性计算
    """
    
    def __init__(self):
        """初始化知识图谱引擎"""
        # 使用NetworkX构建图
        self.graph = nx.DiGraph()
        
        # 节点和边存储
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, GraphEdge] = {}
        
        # 实体索引
        self.entity_index: Dict[str, str] = {}  # entity_name -> node_id
        self.entity_type_index: Dict[str, Set[str]] = defaultdict(set)  # entity_type -> node_ids
        
        # 关系索引
        self.relationship_index: Dict[str, Set[str]] = defaultdict(set)  # relationship_type -> edge_ids
        
        # 社区信息
        self.communities: Dict[int, Set[str]] = {}  # community_id -> node_ids
        
        logger.info("知识图谱引擎初始化完成")
    
    def add_entity(self, entity: RAGEntity) -> str:
        """
        添加实体到图谱
        
        Args:
            entity: RAG实体
        
        Returns:
            节点ID
        """
        # 检查是否已存在
        if entity.entity_name in self.entity_index:
            return self.entity_index[entity.entity_name]
        
        # 创建节点
        node_id = str(uuid.uuid4())
        node = GraphNode(
            node_id=node_id,
            entity=entity
        )
        
        # 添加到图
        self.graph.add_node(node_id, **{
            "entity_name": entity.entity_name,
            "entity_type": entity.entity_type,
            "description": entity.description
        })
        
        # 更新索引
        self.nodes[node_id] = node
        self.entity_index[entity.entity_name] = node_id
        self.entity_type_index[entity.entity_type].add(node_id)
        
        logger.debug(f"添加实体: {entity.entity_name} (ID: {node_id})")
        return node_id
    
    def add_relationship(self, relationship: RAGRelationship) -> str:
        """
        添加关系到图谱
        
        Args:
            relationship: RAG关系
        
        Returns:
            边ID
        """
        # 获取源节点和目标节点
        src_node_id = self.entity_index.get(relationship.src_id)
        tgt_node_id = self.entity_index.get(relationship.tgt_id)
        
        if not src_node_id or not tgt_node_id:
            logger.warning(f"关系的实体不存在: {relationship.src_id} -> {relationship.tgt_id}")
            return ""
        
        # 创建边
        edge_id = str(uuid.uuid4())
        edge = GraphEdge(
            edge_id=edge_id,
            relationship=relationship,
            weight=relationship.weight
        )
        
        # 添加到图
        self.graph.add_edge(src_node_id, tgt_node_id, **{
            "edge_id": edge_id,
            "description": relationship.description,
            "weight": relationship.weight,
            "keywords": relationship.keywords
        })
        
        # 更新邻居关系
        self.nodes[src_node_id].neighbors.add(tgt_node_id)
        
        # 更新索引
        self.edges[edge_id] = edge
        self.relationship_index[relationship.description].add(edge_id)
        
        logger.debug(f"添加关系: {relationship.src_id} -> {relationship.tgt_id}")
        return edge_id
    
    def get_entity_by_name(self, entity_name: str) -> Optional[RAGEntity]:
        """根据名称获取实体"""
        node_id = self.entity_index.get(entity_name)
        if node_id:
            return self.nodes[node_id].entity
        return None
    
    def get_entities_by_type(self, entity_type: str) -> List[RAGEntity]:
        """根据类型获取实体列表"""
        node_ids = self.entity_type_index.get(entity_type, set())
        return [self.nodes[nid].entity for nid in node_ids]
    
    def get_neighbors(self, entity_name: str, depth: int = 1) -> List[RAGEntity]:
        """
        获取实体的邻居
        
        Args:
            entity_name: 实体名称
            depth: 邻居深度（1=直接邻居，2=二度邻居）
        
        Returns:
            邻居实体列表
        """
        node_id = self.entity_index.get(entity_name)
        if not node_id:
            return []
        
        neighbors = set()
        current_level = {node_id}
        
        for _ in range(depth):
            next_level = set()
            for nid in current_level:
                for neighbor_id in self.graph.successors(nid):
                    if neighbor_id not in neighbors and neighbor_id != node_id:
                        neighbors.add(neighbor_id)
                        next_level.add(neighbor_id)
            current_level = next_level
        
        return [self.nodes[nid].entity for nid in neighbors]
    
    def find_path(self, source: str, target: str, max_length: int = 5) -> List[List[str]]:
        """
        查找两个实体之间的路径
        
        Args:
            source: 源实体名称
            target: 目标实体名称
            max_length: 最大路径长度
        
        Returns:
            路径列表（每个路径是实体名称列表）
        """
        src_id = self.entity_index.get(source)
        tgt_id = self.entity_index.get(target)
        
        if not src_id or not tgt_id:
            return []
        
        try:
            # 查找所有简单路径
            paths = nx.all_simple_paths(
                self.graph, 
                src_id, 
                tgt_id, 
                cutoff=max_length
            )
            
            # 转换为实体名称
            result = []
            for path in paths:
                entity_path = [self.nodes[nid].entity.entity_name for nid in path]
                result.append(entity_path)
            
            return result
        except nx.NetworkXNoPath:
            return []
    
    def compute_centrality(self) -> Dict[str, float]:
        """
        计算节点中心性
        
        Returns:
            节点ID到中心性分数的映射
        """
        if len(self.graph.nodes) == 0:
            return {}
        
        # 计算PageRank中心性
        centrality = nx.pagerank(self.graph)
        
        # 更新节点中心性
        for node_id, score in centrality.items():
            if node_id in self.nodes:
                self.nodes[node_id].centrality = score
        
        return centrality
    
    def detect_communities(self) -> Dict[int, Set[str]]:
        """
        检测社区（使用Louvain算法）
        
        Returns:
            社区ID到节点ID集合的映射
        """
        if len(self.graph.nodes) == 0:
            return {}
        
        # 转换为无向图进行社区检测
        undirected = self.graph.to_undirected()
        
        # 使用贪心模块化社区检测
        communities_generator = nx.community.greedy_modularity_communities(undirected)
        
        # 构建社区映射
        self.communities = {}
        for idx, community in enumerate(communities_generator):
            self.communities[idx] = community
            # 更新节点的社区ID
            for node_id in community:
                if node_id in self.nodes:
                    self.nodes[node_id].community_id = idx
        
        logger.info(f"检测到 {len(self.communities)} 个社区")
        return self.communities
    
    def get_community_entities(self, community_id: int) -> List[RAGEntity]:
        """获取社区中的所有实体"""
        node_ids = self.communities.get(community_id, set())
        return [self.nodes[nid].entity for nid in node_ids if nid in self.nodes]
    
    def get_subgraph(self, entity_names: List[str], depth: int = 1) -> 'KnowledgeGraphEngine':
        """
        提取子图
        
        Args:
            entity_names: 实体名称列表
            depth: 扩展深度
        
        Returns:
            子图引擎
        """
        # 收集所有相关节点
        node_ids = set()
        for name in entity_names:
            node_id = self.entity_index.get(name)
            if node_id:
                node_ids.add(node_id)
                # 添加邻居
                for _ in range(depth):
                    neighbors = set()
                    for nid in node_ids:
                        neighbors.update(self.graph.successors(nid))
                        neighbors.update(self.graph.predecessors(nid))
                    node_ids.update(neighbors)
        
        # 创建子图
        subgraph_engine = KnowledgeGraphEngine()
        
        # 添加节点
        for node_id in node_ids:
            if node_id in self.nodes:
                subgraph_engine.add_entity(self.nodes[node_id].entity)
        
        # 添加边
        for src_id in node_ids:
            for tgt_id in self.graph.successors(src_id):
                if tgt_id in node_ids:
                    edge_data = self.graph.edges[src_id, tgt_id]
                    edge_id = edge_data.get("edge_id")
                    if edge_id and edge_id in self.edges:
                        subgraph_engine.add_relationship(self.edges[edge_id].relationship)
        
        return subgraph_engine
    
    def export_to_dict(self) -> Dict[str, Any]:
        """导出图谱为字典"""
        return {
            "nodes": [
                {
                    "id": node.node_id,
                    "entity": {
                        "name": node.entity.entity_name,
                        "type": node.entity.entity_type,
                        "description": node.entity.description
                    },
                    "centrality": node.centrality,
                    "community_id": node.community_id
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "id": edge.edge_id,
                    "source": edge.relationship.src_id,
                    "target": edge.relationship.tgt_id,
                    "description": edge.relationship.description,
                    "weight": edge.weight
                }
                for edge in self.edges.values()
            ],
            "statistics": {
                "num_nodes": len(self.nodes),
                "num_edges": len(self.edges),
                "num_communities": len(self.communities)
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取图谱统计信息"""
        return {
            "num_entities": len(self.nodes),
            "num_relationships": len(self.edges),
            "num_communities": len(self.communities),
            "entity_types": {
                etype: len(nodes) 
                for etype, nodes in self.entity_type_index.items()
            },
            "avg_degree": sum(dict(self.graph.degree()).values()) / len(self.nodes) if self.nodes else 0,
            "density": nx.density(self.graph) if self.nodes else 0
        }

