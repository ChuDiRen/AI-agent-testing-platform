"""
RAG引擎 - 整合文档解析、分块、向量化和检索
"""
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path

from rag.parsers.document_parser import get_parser, ParsedDocument
from rag.chunkers.text_chunker import TextChunker, TextChunk
from rag.embeddings.embedding_service import EmbeddingService
from rag.vector_stores.vector_store_service import VectorStoreService
from core.logger import setup_logger

logger = setup_logger(__name__)


class RAGEngine:
    """RAG引擎"""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        vector_store_service: Optional[VectorStoreService] = None,
        chunker: Optional[TextChunker] = None
    ):
        """
        初始化RAG引擎

        Args:
            embedding_service: 嵌入服务
            vector_store_service: 向量存储服务
            chunker: 文本分块器
        """
        self.embedding_service = embedding_service or EmbeddingService()

        if vector_store_service:
            self.vector_store = vector_store_service
        else:
            self.vector_store = VectorStoreService(self.embedding_service)

        self.chunker = chunker or TextChunker()

        logger.info("RAG引擎初始化完成")

    async def process_document(
        self,
        file_path: str,
        doc_id: str,
        file_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        处理文档：解析 -> 分块 -> 向量化 -> 存储

        Args:
            file_path: 文件路径
            doc_id: 文档ID
            file_type: 文件类型
            metadata: 额外的元数据

        Returns:
            处理结果字典
        """
        logger.info(f"开始处理文档: {file_path}, doc_id={doc_id}, file_type={file_type}")

        try:
            # 1. 解析文档
            logger.info(f"步骤1: 解析文档")
            parser = get_parser(file_type)
            parsed_doc = parser.parse(file_path)

            # 添加文档ID到元数据
            parsed_doc.metadata["document_id"] = doc_id
            if metadata:
                parsed_doc.metadata.update(metadata)

            # 2. 分块
            logger.info(f"步骤2: 文本分块")
            chunks = self.chunker.chunk_document(parsed_doc, doc_id)

            # 3. 向量化
            logger.info(f"步骤3: 生成向量嵌入")
            texts = [chunk.text for chunk in chunks]
            embeddings = self.embedding_service.embed_documents(texts)

            # 4. 存储到向量数据库
            logger.info(f"步骤4: 存储到向量数据库")
            vector_ids = self.vector_store.add_documents(chunks, embeddings)

            # 更新文档块的vector_id
            for chunk, vector_id in zip(chunks, vector_ids):
                chunk.metadata["vector_id"] = vector_id

            logger.info(f"文档处理完成: {len(chunks)} 个块已索引")

            return {
                "status": "success",
                "doc_id": doc_id,
                "file_path": file_path,
                "file_type": file_type,
                "chunks_count": len(chunks),
                "vector_ids": vector_ids,
                "parsed_metadata": parsed_doc.metadata,
                "chunks": [
                    {
                        "chunk_id": chunk.chunk_id,
                        "chunk_index": chunk.chunk_index,
                        "chunk_size": len(chunk.text),
                        "page_number": chunk.page_number,
                        "text_preview": chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text
                    }
                    for chunk in chunks
                ]
            }

        except Exception as e:
            logger.error(f"文档处理失败: {str(e)}")
            return {
                "status": "error",
                "doc_id": doc_id,
                "file_path": file_path,
                "error": str(e)
            }

    async def process_document_from_bytes(
        self,
        file_bytes: bytes,
        doc_id: str,
        file_type: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        从字节数组处理文档

        Args:
            file_bytes: 文件字节数组
            doc_id: 文档ID
            file_type: 文件类型
            filename: 文件名
            metadata: 额外的元数据

        Returns:
            处理结果字典
        """
        import tempfile
        import os

        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, filename)

        try:
            # 写入临时文件
            with open(temp_path, 'wb') as f:
                f.write(file_bytes)

            # 处理文档
            result = await self.process_document(
                temp_path,
                doc_id,
                file_type,
                metadata
            )

            return result

        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        向量搜索

        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter: 元数据过滤条件
            score_threshold: 相似度阈值

        Returns:
            搜索结果列表
        """
        logger.info(f"执行搜索: query='{query}', top_k={top_k}")

        results = self.vector_store.similarity_search(
            query=query,
            top_k=top_k,
            filter=filter,
            score_threshold=score_threshold
        )

        return results

    async def delete_document(self, doc_id: str) -> bool:
        """
        删除文档（从向量数据库中）

        Args:
            doc_id: 文档ID

        Returns:
            是否删除成功
        """
        logger.info(f"删除文档: {doc_id}")

        try:
            # 获取所有相关的文档块
            results = self.vector_store.similarity_search(
                query="",
                top_k=10000,
                filter={"document_id": doc_id}
            )

            # 提取vector_id
            vector_ids = [r["metadata"].get("vector_id") for r in results if r["metadata"].get("vector_id")]

            if vector_ids:
                success = self.vector_store.delete_by_ids(vector_ids)
                logger.info(f"删除文档成功: {doc_id}, 删除了 {len(vector_ids)} 个块")
                return success
            else:
                logger.info(f"文档不存在或没有相关块: {doc_id}")
                return True

        except Exception as e:
            logger.error(f"删除文档失败: {str(e)}")
            return False

    async def reindex_document(
        self,
        file_path: str,
        doc_id: str,
        file_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        重新索引文档（删除旧的，添加新的）

        Args:
            file_path: 文件路径
            doc_id: 文档ID
            file_type: 文件类型
            metadata: 额外的元数据

        Returns:
            处理结果字典
        """
        logger.info(f"重新索引文档: {doc_id}")

        # 先删除旧的
        await self.delete_document(doc_id)

        # 处理新的
        result = await self.process_document(
            file_path,
            doc_id,
            file_type,
            metadata
        )

        return result

    def get_stats(self) -> Dict[str, Any]:
        """
        获取RAG引擎统计信息

        Returns:
            统计信息字典
        """
        vector_stats = self.vector_store.get_collection_stats()

        return {
            "vector_store": vector_stats,
            "chunker": {
                "chunk_size": self.chunker.chunk_size,
                "chunk_overlap": self.chunker.chunk_overlap,
            },
            "embedding": {
                "dimension": self.embedding_service.embedding_dimension,
            }
        }

    async def retrieve_with_context(
        self,
        query: str,
        top_k: int = 5,
        context_window: int = 200
    ) -> Dict[str, Any]:
        """
        检索并提供上下文

        Args:
            query: 查询文本
            top_k: 返回结果数量
            context_window: 上下文窗口大小（字符数）

        Returns:
            包含检索结果和上下文的字典
        """
        results = await self.search(query, top_k)

        # 为每个结果添加上下文
        for result in results:
            text = result["text"]
            metadata = result["metadata"]

            # 提取上下文（简单的文本扩展）
            # 在实际应用中，可以根据page_number等元数据从原文中提取更多上下文
            result["context"] = text[:context_window] if len(text) > context_window else text

        return {
            "query": query,
            "results": results,
            "context": "\n\n".join([r["text"] for r in results])
        }
