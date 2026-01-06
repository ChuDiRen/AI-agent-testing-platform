"""
简化版RAG引擎 - 核心知识检索功能

专注于核心功能的简化实现：
- 基于ChromaDB的向量检索
- 6种检索模式（local/global/hybrid/naive/mix/bypass）
- 基础实体和关系管理
- 文本文档索引和查询
"""
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import uuid
import json
import asyncio

# 向量存储和嵌入
try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from core.models import RAGEntity, RAGRelationship, RAGChunk, RAGCitation
from core.logging_config import get_logger

logger = get_logger(__name__)


class RetrievalMode:
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


class AnythingChatRAGEngine:
    """
    简化版AnythingChatRAG引擎
    
    核心功能：
    - 文档索引和检索
    - 向量相似性搜索
    - 实体和关系管理
    - 6种检索模式
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/chromadb",
        collection_name: str = "api_knowledge",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        """初始化RAG引擎"""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # 初始化ChromaDB
        if CHROMADB_AVAILABLE:
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # 初始化嵌入模型
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"RAG引擎初始化完成: {embedding_model}")
        else:
            logger.warning("ChromaDB不可用，使用内存模式")
            self.collection = None
            self.embedding_model = None
        
        # 知识存储（内存）
        self.entities: Dict[str, RAGEntity] = {}
        self.relationships: List[RAGRelationship] = []
        self.chunks: List[RAGChunk] = []
    
    def _chunk_text(self, text: str, source: str) -> List[RAGChunk]:
        """将文本分块"""
        chunks = []
        text_length = len(text)
        start = 0
        chunk_index = 0
        
        while start < text_length:
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            chunk = RAGChunk(
                chunk_id=f"{source}_{chunk_index}",
                content=chunk_text,
                source=source,
                chunk_type="text",
                metadata={"start": start, "end": end, "index": chunk_index},
                score=0.0
            )
            chunks.append(chunk)
            
            start = end - self.chunk_overlap
            chunk_index += 1
        
        return chunks
    
    async def index_document(
        self,
        document_path: str,
        document_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        索引文档到知识库
        
        Args:
            document_path: 文档路径
            document_type: 文档类型
            metadata: 元数据
        
        Returns:
            索引结果统计
        """
        logger.info(f"开始索引文档: {document_path}")
        
        # 读取文档内容
        file_path = Path(document_path)
        if not file_path.exists():
            raise FileNotFoundError(f"文档不存在: {document_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分块
        chunks = self._chunk_text(content, str(file_path))
        
        # 生成嵌入并存储到ChromaDB
        if self.collection and self.embedding_model:
            chunk_ids = [c.chunk_id for c in chunks]
            chunk_texts = [c.content for c in chunks]
            chunk_metadatas = [c.metadata for c in chunks]
            
            # 生成嵌入
            embeddings = self.embedding_model.encode(chunk_texts).tolist()
            
            # 存储到ChromaDB
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunk_texts,
                metadatas=chunk_metadatas
            )
        
        # 存储到内存
        self.chunks.extend(chunks)
        
        # 简单的实体提取（基于关键词）
        entities = self._extract_simple_entities(content, str(file_path))
        for entity in entities:
            self.entities[entity.entity_id] = entity
        
        logger.info(f"文档索引完成: {len(chunks)} 个文本块, {len(entities)} 个实体")
        
        return {
            "indexed_chunks": len(chunks),
            "extracted_entities": len(entities),
            "document_path": document_path
        }

    def _extract_simple_entities(self, text: str, source: str) -> List[RAGEntity]:
        """简单的实体提取（基于关键词匹配）"""
        entities = []

        # API相关关键词
        api_keywords = ["GET", "POST", "PUT", "DELETE", "PATCH", "API", "endpoint", "接口"]

        # 简单提取：查找包含关键词的句子
        sentences = text.split('.')
        for idx, sentence in enumerate(sentences):
            for keyword in api_keywords:
                if keyword in sentence:
                    entity = RAGEntity(
                        entity_id=f"{source}_entity_{idx}",
                        entity_name=keyword,
                        entity_type="api_keyword",
                        description=sentence.strip(),
                        properties={"source": source, "index": idx}
                    )
                    entities.append(entity)
                    break

        return entities

    async def aquery(
        self,
        query: str,
        mode: str = RetrievalMode.MIX,
        top_k: int = 10,
        chunk_top_k: int = 5,
        enable_rerank: bool = True
    ) -> RetrievalResult:
        """
        异步查询知识库

        Args:
            query: 查询文本
            mode: 检索模式
            top_k: 返回的最大实体数
            chunk_top_k: 返回的最大文本块数
            enable_rerank: 是否启用重排序

        Returns:
            检索结果
        """
        start_time = datetime.utcnow()

        # 根据模式执行不同的检索策略
        if mode == RetrievalMode.NAIVE:
            result = await self._naive_retrieval(query, chunk_top_k)
        elif mode == RetrievalMode.LOCAL:
            result = await self._local_retrieval(query, top_k, chunk_top_k)
        elif mode == RetrievalMode.GLOBAL:
            result = await self._global_retrieval(query, top_k, chunk_top_k)
        elif mode == RetrievalMode.HYBRID:
            result = await self._hybrid_retrieval(query, top_k, chunk_top_k)
        elif mode == RetrievalMode.MIX:
            result = await self._mix_retrieval(query, top_k, chunk_top_k)
        elif mode == RetrievalMode.BYPASS:
            result = await self._bypass_retrieval(query)
        else:
            result = await self._mix_retrieval(query, top_k, chunk_top_k)

        # 计算处理时间
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        result.processing_time = processing_time

        return result

    async def _naive_retrieval(self, query: str, chunk_top_k: int) -> RetrievalResult:
        """朴素检索：仅基于向量相似性"""
        chunks = []

        if self.collection and self.embedding_model:
            # 生成查询嵌入
            query_embedding = self.embedding_model.encode([query])[0].tolist()

            # 查询ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=chunk_top_k
            )

            # 构建结果
            if results['ids']:
                for idx, (chunk_id, document, metadata, distance) in enumerate(zip(
                    results['ids'][0],
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    chunk = RAGChunk(
                        chunk_id=chunk_id,
                        content=document,
                        source=metadata.get('source', ''),
                        chunk_type="text",
                        metadata=metadata,
                        score=1.0 - distance  # 转换为相似度分数
                    )
                    chunks.append(chunk)

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.NAIVE,
            entities=[],
            relationships=[],
            chunks=chunks,
            citations=[],
            confidence=0.7,
            processing_time=0.0
        )

    async def _local_retrieval(self, query: str, top_k: int, chunk_top_k: int) -> RetrievalResult:
        """本地检索：基于实体匹配"""
        entities = []
        chunks = []

        # 简单的关键词匹配
        query_lower = query.lower()
        for entity in self.entities.values():
            if query_lower in entity.entity_name.lower() or query_lower in entity.description.lower():
                entities.append(entity)
                if len(entities) >= top_k:
                    break

        # 获取相关文本块
        naive_result = await self._naive_retrieval(query, chunk_top_k)
        chunks = naive_result.chunks

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.LOCAL,
            entities=entities,
            relationships=[],
            chunks=chunks,
            citations=[],
            confidence=0.75,
            processing_time=0.0
        )

    async def _global_retrieval(self, query: str, top_k: int, chunk_top_k: int) -> RetrievalResult:
        """全局检索：基于知识图谱"""
        # 简化实现：返回所有实体和关系
        entities = list(self.entities.values())[:top_k]
        relationships = self.relationships[:top_k]

        # 获取相关文本块
        naive_result = await self._naive_retrieval(query, chunk_top_k)
        chunks = naive_result.chunks

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.GLOBAL,
            entities=entities,
            relationships=relationships,
            chunks=chunks,
            citations=[],
            confidence=0.8,
            processing_time=0.0
        )

    async def _hybrid_retrieval(self, query: str, top_k: int, chunk_top_k: int) -> RetrievalResult:
        """混合检索：结合本地和全局"""
        local_result = await self._local_retrieval(query, top_k // 2, chunk_top_k // 2)
        global_result = await self._global_retrieval(query, top_k // 2, chunk_top_k // 2)

        # 合并结果
        entities = local_result.entities + global_result.entities
        chunks = local_result.chunks + global_result.chunks

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.HYBRID,
            entities=entities[:top_k],
            relationships=global_result.relationships,
            chunks=chunks[:chunk_top_k],
            citations=[],
            confidence=0.85,
            processing_time=0.0
        )

    async def _mix_retrieval(self, query: str, top_k: int, chunk_top_k: int) -> RetrievalResult:
        """综合检索：推荐模式，结合所有策略"""
        # 执行多种检索
        naive_result = await self._naive_retrieval(query, chunk_top_k)
        local_result = await self._local_retrieval(query, top_k, 0)

        # 合并并去重
        entities = local_result.entities[:top_k]
        chunks = naive_result.chunks[:chunk_top_k]

        return RetrievalResult(
            query=query,
            mode=RetrievalMode.MIX,
            entities=entities,
            relationships=[],
            chunks=chunks,
            citations=[],
            confidence=0.9,
            processing_time=0.0
        )

    async def _bypass_retrieval(self, query: str) -> RetrievalResult:
        """旁路检索：直接返回查询，不进行检索"""
        return RetrievalResult(
            query=query,
            mode=RetrievalMode.BYPASS,
            entities=[],
            relationships=[],
            chunks=[],
            citations=[],
            confidence=1.0,
            processing_time=0.0
        )

    def get_entities(self, entity_type: Optional[str] = None, limit: int = 50) -> List[RAGEntity]:
        """获取实体列表"""
        entities = list(self.entities.values())

        if entity_type:
            entities = [e for e in entities if e.entity_type == entity_type]

        return entities[:limit]

    def get_relationships(
        self,
        entity_id: Optional[str] = None,
        relationship_type: Optional[str] = None
    ) -> List[RAGRelationship]:
        """获取关系列表"""
        relationships = self.relationships

        if entity_id:
            relationships = [
                r for r in relationships
                if r.source_id == entity_id or r.target_id == entity_id
            ]

        if relationship_type:
            relationships = [r for r in relationships if r.relationship_type == relationship_type]

        return relationships


# 全局实例
_rag_instance: Optional[AnythingChatRAGEngine] = None


def get_anything_rag_instance(**kwargs) -> AnythingChatRAGEngine:
    """获取全局RAG引擎实例"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = AnythingChatRAGEngine(**kwargs)
    return _rag_instance


