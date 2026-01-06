"""
完整的RAG引擎 - Full RAG Engine

功能：
- 6种检索模式的真实区分实现
- 知识图谱集成
- 多模态内容处理
- 向量检索和语义搜索
- 实体和关系查询
"""
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio

from core.models import RAGEntity, RAGRelationship, RAGChunk, RAGCitation
from core.knowledge_graph import KnowledgeGraphEngine
from core.entity_extractor import EntityExtractor
from core.relationship_extractor import RelationshipExtractor
from core.multimodal_processor import MultimodalDocumentProcessor
from core.logging_config import get_logger

logger = get_logger(__name__)


class RetrievalMode(str, Enum):
    """检索模式枚举"""
    LOCAL = "local"          # 本地实体检索
    GLOBAL = "global"        # 全局知识图谱
    HYBRID = "hybrid"        # 混合检索
    NAIVE = "naive"          # 向量相似性
    MIX = "mix"              # 综合检索（推荐）
    BYPASS = "bypass"        # 直接查询


@dataclass
class RetrievalResult:
    """检索结果"""
    query: str
    mode: str
    entities: List[RAGEntity]
    relationships: List[RAGRelationship]
    chunks: List[RAGChunk]
    citations: List[RAGCitation]
    confidence: float
    processing_time: float


class FullRAGEngine:
    """
    完整的RAG引擎
    
    核心功能：
    - 6种检索模式的真实区分实现
    - 知识图谱构建和查询
    - 多模态内容处理
    - 向量检索和语义搜索
    """
    
    def __init__(
        self,
        llm_service=None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        初始化完整RAG引擎
        
        Args:
            llm_service: LLM服务实例
            embedding_model: 嵌入模型名称
        """
        # 核心组件
        self.knowledge_graph = KnowledgeGraphEngine()
        self.entity_extractor = EntityExtractor(llm_service)
        self.relationship_extractor = RelationshipExtractor(llm_service)
        self.multimodal_processor = MultimodalDocumentProcessor()
        self.llm_service = llm_service
        
        # 向量存储
        self._init_vector_store(embedding_model)
        
        # 文档索引
        self.indexed_documents: Dict[str, Dict[str, Any]] = {}
        
        logger.info("完整RAG引擎初始化完成")
    
    def _init_vector_store(self, embedding_model: str):
        """初始化向量存储"""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection(
                name="rag_collection",
                metadata={"hnsw:space": "cosine"}
            )
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"向量存储初始化完成: {embedding_model}")
        except ImportError:
            logger.warning("ChromaDB不可用，向量检索功能受限")
            self.chroma_client = None
            self.collection = None
            self.embedding_model = None
    
    async def index_document(
        self,
        document_path: str,
        document_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        索引文档到知识库
        
        Args:
            document_path: 文档路径
            document_type: 文档类型
        
        Returns:
            索引结果
        """
        logger.info(f"开始索引文档: {document_path}")
        start_time = datetime.utcnow()
        
        # 1. 处理多模态内容
        doc_content = await self.multimodal_processor.process_document(document_path)
        
        # 2. 提取实体
        entity_result = await self.entity_extractor.extract_entities(
            text=doc_content.text,
            method="auto"
        )
        
        # 3. 提取关系
        rel_result = await self.relationship_extractor.extract_relationships(
            text=doc_content.text,
            entities=entity_result.entities,
            method="auto"
        )
        
        # 4. 构建知识图谱
        for entity in entity_result.entities:
            self.knowledge_graph.add_entity(entity)
        
        for relationship in rel_result.relationships:
            self.knowledge_graph.add_relationship(relationship)
        
        # 5. 向量化文本块
        if self.collection and self.embedding_model:
            chunks = self._chunk_text(doc_content.text)
            embeddings = self.embedding_model.encode(chunks)
            
            self.collection.add(
                documents=chunks,
                embeddings=embeddings.tolist(),
                ids=[f"doc_{document_path}_{i}" for i in range(len(chunks))]
            )
        
        # 6. 记录索引信息
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        index_info = {
            "document_path": document_path,
            "entities_count": len(entity_result.entities),
            "relationships_count": len(rel_result.relationships),
            "chunks_count": len(chunks) if self.collection else 0,
            "processing_time": processing_time,
            "indexed_at": datetime.utcnow().isoformat()
        }
        
        self.indexed_documents[document_path] = index_info
        
        logger.info(f"文档索引完成: {document_path}, 耗时: {processing_time:.2f}s")
        return index_info
    
    def _chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """将文本分块"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    async def query(
        self,
        query: str,
        mode: RetrievalMode = RetrievalMode.MIX,
        top_k: int = 10
    ) -> RetrievalResult:
        """
        执行查询（6种模式真实区分）
        
        Args:
            query: 查询文本
            mode: 检索模式
            top_k: 返回结果数
        
        Returns:
            检索结果
        """
        logger.info(f"执行查询: query={query}, mode={mode}, top_k={top_k}")
        start_time = datetime.utcnow()
        
        # 根据模式选择不同的检索策略
        if mode == RetrievalMode.LOCAL:
            result = await self._local_retrieval(query, top_k)
        elif mode == RetrievalMode.GLOBAL:
            result = await self._global_retrieval(query, top_k)
        elif mode == RetrievalMode.HYBRID:
            result = await self._hybrid_retrieval(query, top_k)
        elif mode == RetrievalMode.NAIVE:
            result = await self._naive_retrieval(query, top_k)
        elif mode == RetrievalMode.MIX:
            result = await self._mix_retrieval(query, top_k)
        elif mode == RetrievalMode.BYPASS:
            result = await self._bypass_retrieval(query, top_k)
        else:
            raise ValueError(f"未知的检索模式: {mode}")
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        result.processing_time = processing_time
        
        logger.info(f"查询完成: mode={mode}, 耗时: {processing_time:.2f}s")
        return result
    
    async def _local_retrieval(self, query: str, top_k: int) -> RetrievalResult:
        """
        本地实体检索
        
        策略：基于实体名称和类型的精确匹配
        """
        entities = []
        relationships = []
        
        # 从查询中提取关键词
        keywords = query.lower().split()
        
        # 搜索匹配的实体
        for node in self.knowledge_graph.nodes.values():
            entity = node.entity
            entity_name_lower = entity.entity_name.lower()
            
            # 检查是否匹配
            if any(kw in entity_name_lower for kw in keywords):
                entities.append(entity)
                
                # 获取相关关系
                neighbors = self.knowledge_graph.get_neighbors(entity.entity_name, depth=1)
                for neighbor in neighbors[:3]:  # 限制邻居数量
                    # 查找连接关系
                    # TODO: 实现关系查找逻辑
                    pass
        
        return RetrievalResult(
            query=query,
            mode=RetrievalMode.LOCAL,
            entities=entities[:top_k],
            relationships=relationships[:top_k],
            chunks=[],
            citations=[],
            confidence=0.8,
            processing_time=0.0
        )
    
    async def _global_retrieval(self, query: str, top_k: int) -> RetrievalResult:
        """
        全局知识图谱检索
        
        策略：基于图谱结构的全局搜索，考虑中心性和社区
        """
        # 计算节点中心性
        centrality = self.knowledge_graph.compute_centrality()
        
        # 检测社区
        communities = self.knowledge_graph.detect_communities()
        
        # 提取查询关键词
        keywords = query.lower().split()
        
        # 找到最相关的社区
        relevant_entities = []
        for community_id, node_ids in communities.items():
            community_entities = self.knowledge_graph.get_community_entities(community_id)
            
            # 计算社区相关性
            relevance = 0
            for entity in community_entities:
                if any(kw in entity.entity_name.lower() for kw in keywords):
                    relevance += 1
            
            if relevance > 0:
                # 按中心性排序
                sorted_entities = sorted(
                    community_entities,
                    key=lambda e: centrality.get(
                        self.knowledge_graph.entity_index.get(e.entity_name, ""), 0
                    ),
                    reverse=True
                )
                relevant_entities.extend(sorted_entities[:5])
        
        return RetrievalResult(
            query=query,
            mode=RetrievalMode.GLOBAL,
            entities=relevant_entities[:top_k],
            relationships=[],
            chunks=[],
            citations=[],
            confidence=0.75,
            processing_time=0.0
        )

    async def _hybrid_retrieval(self, query: str, top_k: int) -> RetrievalResult:
        """
        混合检索（向量 + 图谱）

        策略：结合向量相似性和图谱结构
        """
        # 1. 向量检索
        vector_results = await self._naive_retrieval(query, top_k * 2)

        # 2. 图谱检索
        graph_results = await self._local_retrieval(query, top_k * 2)

        # 3. 合并和重排序
        all_entities = {}

        # 向量结果权重0.6
        for entity in vector_results.entities:
            all_entities[entity.entity_name] = {
                "entity": entity,
                "score": 0.6
            }

        # 图谱结果权重0.4
        for entity in graph_results.entities:
            if entity.entity_name in all_entities:
                all_entities[entity.entity_name]["score"] += 0.4
            else:
                all_entities[entity.entity_name] = {
                    "entity": entity,
                    "score": 0.4
                }

        # 按分数排序
        sorted_entities = sorted(
            all_entities.values(),
            key=lambda x: x["score"],
            reverse=True
        )

        final_entities = [item["entity"] for item in sorted_entities[:top_k]]

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.HYBRID,
            entities=final_entities,
            relationships=[],
            chunks=vector_results.chunks[:top_k],
            citations=[],
            confidence=0.85,
            processing_time=0.0
        )

    async def _naive_retrieval(self, query: str, top_k: int) -> RetrievalResult:
        """
        纯向量相似性检索

        策略：基于嵌入向量的语义搜索
        """
        chunks = []
        entities = []

        if self.collection and self.embedding_model:
            # 向量化查询
            query_embedding = self.embedding_model.encode([query])[0]

            # 检索相似文本块
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k
            )

            # 构建文本块
            for i, (doc, distance) in enumerate(zip(
                results["documents"][0],
                results["distances"][0]
            )):
                chunk = RAGChunk(
                    chunk_id=f"chunk_{i}",
                    content=doc,
                    source_id="vector_search",
                    chunk_order=i,
                    token_count=len(doc.split())
                )
                chunks.append(chunk)

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.NAIVE,
            entities=entities,
            relationships=[],
            chunks=chunks,
            citations=[],
            confidence=0.7,
            processing_time=0.0
        )

    async def _mix_retrieval(self, query: str, top_k: int) -> RetrievalResult:
        """
        综合检索（推荐模式）

        策略：智能组合多种检索方法
        """
        # 并行执行多种检索
        results = await asyncio.gather(
            self._local_retrieval(query, top_k),
            self._naive_retrieval(query, top_k),
            self._global_retrieval(query, top_k // 2)
        )

        local_result, naive_result, global_result = results

        # 合并实体（去重）
        all_entities = {}
        for entity in local_result.entities:
            all_entities[entity.entity_name] = entity
        for entity in global_result.entities:
            all_entities[entity.entity_name] = entity

        # 合并文本块
        all_chunks = naive_result.chunks

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.MIX,
            entities=list(all_entities.values())[:top_k],
            relationships=[],
            chunks=all_chunks[:top_k],
            citations=[],
            confidence=0.9,
            processing_time=0.0
        )

    async def _bypass_retrieval(self, query: str, top_k: int) -> RetrievalResult:
        """
        直接LLM查询（绕过检索）

        策略：直接使用LLM生成答案
        """
        if not self.llm_service:
            logger.warning("LLM服务不可用，回退到混合检索")
            return await self._mix_retrieval(query, top_k)

        # 构建提示词
        prompt = f"""
基于你的知识回答以下问题：

问题：{query}

请提供详细的答案。
"""

        try:
            response = await self.llm_service.generate(prompt)

            # 将响应转换为文本块
            chunk = RAGChunk(
                chunk_id="llm_response",
                content=response,
                source_id="llm_direct",
                chunk_order=0,
                token_count=len(response.split())
            )

            return RetrievalResult(
                query=query,
                mode=RetrievalMode.BYPASS,
                entities=[],
                relationships=[],
                chunks=[chunk],
                citations=[],
                confidence=0.95,
                processing_time=0.0
            )

        except Exception as e:
            logger.error(f"LLM查询失败: {e}")
            return await self._mix_retrieval(query, top_k)

    def get_statistics(self) -> Dict[str, Any]:
        """获取RAG引擎统计信息"""
        graph_stats = self.knowledge_graph.get_statistics()

        return {
            "indexed_documents": len(self.indexed_documents),
            "knowledge_graph": graph_stats,
            "vector_store": {
                "available": self.collection is not None,
                "collection_name": "rag_collection" if self.collection else None
            }
        }

