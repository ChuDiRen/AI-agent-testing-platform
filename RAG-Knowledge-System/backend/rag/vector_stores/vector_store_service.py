"""
向量存储服务（基于ChromaDB）
"""
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from chromadb import ChromaDB, Collection, PersistentClient
from chromadb.config import Settings

from rag.embeddings.embedding_service import EmbeddingService
from rag.chunkers.text_chunker import TextChunk
from core.logger import setup_logger
from config.settings import settings

logger = setup_logger(__name__)


class VectorStoreService:
    """向量存储服务"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        collection_name: str = "enterprise_rag_kb",
        persist_directory: Optional[str] = None
    ):
        """
        初始化向量存储服务

        Args:
            embedding_service: 嵌入服务
            collection_name: 集合名称
            persist_directory: 持久化目录
        """
        self.embedding_service = embedding_service
        self.collection_name = collection_name

        # 设置持久化目录
        if persist_directory is None:
            persist_directory = settings.VECTOR_DB_PATH

        # 创建持久化目录
        persist_path = Path(persist_directory)
        persist_path.mkdir(parents=True, exist_ok=True)

        # 初始化ChromaDB客户端
        self.client = PersistentClient(
            path=str(persist_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 获取或创建集合
        self.collection = self._get_or_create_collection()

        logger.info(f"向量存储服务初始化成功: {collection_name} (路径: {persist_path})")

    def _get_or_create_collection(self) -> Collection:
        """
        获取或创建集合

        Returns:
            ChromaDB集合
        """
        try:
            # 尝试获取现有集合
            collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"使用现有集合: {self.collection_name}")
            return collection
        except Exception:
            # 集合不存在，创建新集合
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Enterprise RAG Knowledge Base"}
            )
            logger.info(f"创建新集合: {self.collection_name}")
            return collection

    def add_documents(
        self,
        chunks: List[TextChunk],
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """
        添加文档块到向量存储

        Args:
            chunks: 文本块列表
            embeddings: 嵌入向量列表（如果为None则自动生成）

        Returns:
            向量ID列表
        """
        if not chunks:
            return []

        logger.info(f"开始添加 {len(chunks)} 个文档块到向量存储")

        # 生成嵌入向量
        if embeddings is None:
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_service.embed_documents(texts)

        # 准备数据
        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            documents.append(chunk.text)

            # 构建元数据
            metadata = {
                "chunk_id": chunk.chunk_id,
                "chunk_index": chunk.chunk_index,
                "chunk_size": len(chunk.text),
            }

            # 添加自定义元数据
            if chunk.metadata:
                metadata.update(chunk.metadata)

            # 如果有页码，添加到元数据
            if chunk.page_number is not None:
                metadata["page_number"] = chunk.page_number

            metadatas.append(metadata)

        # 批量添加到向量数据库
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        logger.info(f"成功添加 {len(ids)} 个文档块到向量存储")
        return ids

    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter: 元数据过滤条件
            score_threshold: 相似度阈值（0-1）

        Returns:
            搜索结果列表，每个结果包含chunk_id, text, metadata, score
        """
        logger.info(f"执行相似度搜索: query='{query[:50]}...', top_k={top_k}")

        # 嵌入查询
        query_embedding = self.embedding_service.embed_query(query)

        # 执行搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter,
        )

        # 格式化结果
        formatted_results = []

        if results["ids"] and len(results["ids"][0]) > 0:
            for i, chunk_id in enumerate(results["ids"][0]):
                score = results.get("distances", [[0.0]])[0][i] if results.get("distances") else 0.0

                # ChromaDB使用欧氏距离，转换为相似度分数
                similarity_score = max(0.0, 1.0 - score)

                # 应用阈值过滤
                if score_threshold and similarity_score < score_threshold:
                    continue

                formatted_results.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                    "score": similarity_score,
                })

        logger.info(f"搜索完成: 返回 {len(formatted_results)} 个结果")
        return formatted_results

    def similarity_search_with_score(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """
        相似度搜索（返回分数）

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter: 元数据过滤条件

        Returns:
            搜索结果列表，每个元素是(document, score)的元组
        """
        results = self.similarity_search(query, top_k, filter)
        return [(r["text"], r["score"]) for r in results]

    def delete_by_ids(self, ids: List[str]) -> bool:
        """
        根据ID删除文档块

        Args:
            ids: 文档块ID列表

        Returns:
            是否删除成功
        """
        try:
            self.collection.delete(ids=ids)
            logger.info(f"成功删除 {len(ids)} 个文档块")
            return True
        except Exception as e:
            logger.error(f"删除文档块失败: {str(e)}")
            return False

    def delete_by_document_id(self, document_id: int) -> int:
        """
        根据文档ID删除所有相关文档块

        Args:
            document_id: 文档ID

        Returns:
            删除的文档块数量
        """
        # 查询所有相关的文档块
        results = self.collection.get(
            where={"document_id": document_id}
        )

        if results["ids"]:
            ids = results["ids"]
            success = self.delete_by_ids(ids)
            return len(ids) if success else 0

        return 0

    def get_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
        """
        根据ID获取文档块

        Args:
            ids: 文档块ID列表

        Returns:
            文档块列表
        """
        results = self.collection.get(ids=ids)

        formatted_results = []

        if results["ids"]:
            for i, chunk_id in enumerate(results["ids"]):
                formatted_results.append({
                    "chunk_id": chunk_id,
                    "text": results["documents"][i] if results.get("documents") else "",
                    "metadata": results["metadatas"][i] if results.get("metadatas") else {},
                    "embedding": results["embeddings"][i] if results.get("embeddings") else [],
                })

        return formatted_results

    def update_document(
        self,
        chunk_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新文档块

        Args:
            chunk_id: 文档块ID
            text: 新的文本内容
            metadata: 新的元数据

        Returns:
            是否更新成功
        """
        try:
            # 先删除旧的
            self.collection.delete(ids=[chunk_id])

            # 生成新的嵌入
            embedding = self.embedding_service.embed_query(text)

            # 添加新的
            self.collection.add(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata or {}]
            )

            logger.info(f"成功更新文档块: {chunk_id}")
            return True

        except Exception as e:
            logger.error(f"更新文档块失败: {str(e)}")
            return False

    def count(self) -> int:
        """
        获取向量存储中的文档块总数

        Returns:
            文档块数量
        """
        return self.collection.count()

    def clear_collection(self) -> bool:
        """
        清空集合

        Returns:
            是否清空成功
        """
        try:
            # 删除并重新创建集合
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Enterprise RAG Knowledge Base"}
            )
            logger.info(f"成功清空集合: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"清空集合失败: {str(e)}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        获取集合统计信息

        Returns:
            统计信息字典
        """
        stats = {
            "collection_name": self.collection_name,
            "count": self.collection.count(),
            "embedding_dimension": self.embedding_service.embedding_dimension,
        }

        return stats
