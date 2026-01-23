"""
向量存储服务
"""
from typing import List, Optional
from sqlmodel import Session
from sentence_transformers import SentenceTransformer
from langchain.vectorstores.chroma import Chroma
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any

from models.document_chunk import DocumentChunk
from models.vector_store import VectorStore
from core.logger import setup_logger
from config.settings import settings
from core.database import engine

logger = setup_logger(__name__)


class VectorStoreService:
    """向量存储服务"""

    def __init__(self):
        # 初始化嵌入模型
        if settings.EMBEDDING_PROVIDER == "local":
            logger.info(f"加载本地嵌入模型: {settings.EMBEDDING_MODEL}")
            self.embeddings = SentenceTransformer(
                settings.EMBEDDING_MODEL,
                device=settings.EMBEDDING_DEVICE,
                cache_folder="./cache/models"
            )
        elif settings.EMBEDDING_PROVIDER == "openai":
            from langchain_openai import OpenAIEmbeddings
            logger.info(f"使用 OpenAI 嵌入模型: {settings.OPENAI_EMBEDDING_MODEL}")
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_EMBEDDING_MODEL
            )
        else:
            raise ValueError(f"不支持的嵌入提供者: {settings.EMBEDDING_PROVIDER}")
        
        # 初始化向量数据库
        if settings.VECTOR_STORE_TYPE == "chromadb":
            logger.info(f"初始化 ChromaDB 向量存储: {settings.CHROMA_PERSIST_DIRECTORY}")
            chroma_settings = ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                anonymized_usage_stats=True
            )
            self.vector_store = Chroma(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                collection_name=settings.CHROMA_COLLECTION_NAME,
                client_settings=chroma_settings,
                embedding_function=self.embeddings.embed_query
            )
        else:
            raise ValueError(f"不支持的向量存储类型: {settings.VECTOR_STORE_TYPE}")
        
        logger.info("向量存储服务初始化完成")
    
    async def index_document(self, doc_id: int, doc_uuid: str, file_path: str) -> List[dict]:
        """
        索引文档到向量数据库
        
        Args:
            doc_id: 文档ID
            doc_uuid: 文档UUID
            file_path: 文档文件路径
        
        Returns:
            生成的向量块列表
        """
        # 1. 解析文档
        from rag.document_parser import parse_document, extract_text_from_file
        from models.document_chunk import DocumentChunk
        from sqlmodel import Session, select
        
        try:
            with Session(engine) as session:
                # 获取文档
                doc_query = select(Document).where(Document.doc_id == doc_id)
                document = session.exec(doc_query).first()
                
                if not document:
                    raise ValueError(f"文档不存在: {doc_id}")
                
                logger.info(f"开始索引文档: {document.title} (ID: {doc_uuid})")
                
                # 解析文档
                parsed = parse_document(file_path)
                text = parsed["text"]
                metadata = parsed["metadata"]
                
                # 分块
                from rag.document_parser import DocumentParser
                parser = DocumentParser()
                chunks_data = parser.split_text_into_chunks(
                    text=text,
                    chunk_size=settings.CHUNK_SIZE,
                    overlap=settings.CHUNK_OVERLAP
                )
                
                logger.info(f"文档分割为 {len(chunks_data)} 个块")
                
                # 生成向量并保存
                indexed_chunks = []
                
                for chunk_data in chunks_data:
                    # 生成向量
                    vector = self.embeddings.embed_query(chunk_data["chunk_text"])
                    
                    # 保存到数据库
                    chunk = DocumentChunk(
                        chunk_id=f"{doc_uuid}_chunk_{chunk_data['chunk_index']}",
                        document_id=doc_id,
                        chunk_text=chunk_data["chunk_text"],
                        chunk_index=chunk_data["chunk_index"],
                        page_number=chunk_data.get("page_number"),
                        vector_id=f"{doc_uuid}_chunk_{chunk_data['chunk_index']}",
                        embedding=vector,
                        collection_name=settings.CHROMA_COLLECTION_NAME,
                        model_name=settings.EMBEDDING_MODEL,
                        metadata={
                            "source": doc_uuid,
                            "chunk_index": chunk_data['chunk_index'],
                            "file_name": Path(file_path).name,
                            "chunk_size": len(chunk_data["chunk_text"]),
                            "has_tables": len(parsed["tables"]) > 0
                        }
                    )
                    
                    session.add(chunk)
                    indexed_chunks.append({
                        "chunk_id": chunk.chunk_id,
                        "chunk_text": chunk_data["chunk_text"],
                        "chunk_index": chunk_data["chunk_index"],
                        "page_number": chunk_data.get("page_number"),
                        "vector_id": f"{doc_uuid}_chunk_{chunk_data['chunk_index']}"
                    })
                    
                    logger.info(f"块 {chunk_data['chunk_index']} 已向量化")
                
                # 更新文档索引状态
                from repositories.document_repository import DocumentRepository
                repository = DocumentRepository(session)
                repository.update_indexed_status(doc_id, indexed=True)
                
                logger.info(f"文档索引完成: {document.title} (共 {len(indexed_chunks)} 个块)")
                
                return indexed_chunks
                
        except Exception as e:
            logger.error(f"文档索引失败: {e}", exc_info=True)
            raise ValueError(f"文档索引失败: {str(e)}")
    
    def similarity_search(
        self, 
        query: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[dict]:
        """
        向量相似度搜索
        
        Args:
            query: 查询文本
            top_k: 返回最相似的 K 个结果
            threshold: 相似度阈值（0-1）
        
        Returns:
            相似度排序的结果列表
        """
        # 查询向量
        query_vector = self.embeddings.embed_query(query)
        
        # 搜索相似向量
        results = self.vector_store.similarity_search_with_score(
            query_vector=query_vector,
            k=top_k,
            filter={"collection_name": settings.CHROMA_COLLECTION_NAME},
            threshold=threshold
        )
        
        # 提取文档块信息
        chunks = []
        
        for result in results:
            # 获取文档块
            chunk_metadata = result["metadata"]
            doc_uuid = chunk_metadata.get("source")
            chunk_index_str = chunk_metadata.get("chunk_index", "").split("_chunk_")[1]
            
            # 查询数据库获取完整信息
            with Session(engine) as session:
                chunk = session.exec(
                    select(DocumentChunk)
                    .where(
                        and_(
                            DocumentChunk.chunk_id == chunk_metadata.get("chunk_id", ""),
                            DocumentChunk.deleted == 0
                        )
                    .where(DocumentChunk.document_id == chunk_metadata.get("source", ""))
                ).first()
            
            if chunk:
                # 查询文档
                doc_query = select(Document).where(Document.doc_id == chunk.document_id)
                document = session.exec(doc_query).first()
                
                if document:
                    chunks.append({
                        "chunk_id": chunk.chunk_id,
                        "chunk_text": chunk.chunk_text,
                        chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        doc_id": chunk.document_id,
                        doc_title: document.title,
                        similarity_score: float(result["score"]),
                        permission: document.permission,
                        metadata: chunk.metadata
                    })
        
        # 按相似度排序
        chunks.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        logger.info(f"向量检索完成: 查询='{query}', 返回 {len(chunks)} 个结果")
        return chunks[:top_k]
    
    def delete_by_document_id(self, doc_id: int) -> int:
        """删除文档的所有向量
        
        Args:
            doc_id: 文档ID
        
        Returns:
            删除的向量数量
        """
        try:
            from sqlmodel import select, delete
            from models.vector_store import VectorStore
            from core.database import Session
            
            with Session(engine) as session:
                # 获取所有相关的向量ID
                chunk_ids = session.exec(
                    select(DocumentChunk.chunk_id)
                    .where(
                        and_(
                            DocumentChunk.document_id == doc_id,
                            DocumentChunk.deleted == 0
                        )
                    )
                    .all()
                )
                
                if not chunk_ids:
                    return 0
                
                # 从向量数据库删除
                delete(VectorStore).where(
                    VectorStore.chunk_id.in_(chunk_ids))
                ).execution_options(synchronize_session="fetch")
                
                # 从数据库删除
                deleted = session.exec(
                    delete(DocumentChunk)
                    .where(
                        and_(
                            DocumentChunk.document_id == doc_id
                        )
                    )
                    .execution_options(synchronize_session="fetch")
                )
                
                logger.info(f"已删除文档 {doc_id} 的 {len(chunk_ids)} 个向量")
                return len(chunk_ids)
                
        except Exception as e:
            logger.error(f"删除向量失败: {e}", exc_info=True)
            raise ValueError(f"删除向量失败: {str(e)}")
    
    def get_chunk_by_chunk_id(self, chunk_id: str) -> Optional[dict]:
        """根据 chunk_id 获取文档块信息"""
        try:
            from sqlmodel import select
            from models.document_chunk import DocumentChunk
            from models.document import Document
            from core.database import Session
            
            with Session(engine) as session:
                # 获取文档块
                chunk = session.exec(
                    select(DocumentChunk)
                    .where(
                        and_(
                            DocumentChunk.chunk_id == chunk_id,
                            DocumentChunk.deleted == 0
                        )
                    .first()
                )
                
                if not chunk:
                    return None
                
                # 获取文档信息
                doc_query = select(Document).where(Document.doc_id == chunk.document_id).first()
                
                if not doc:
                    return None
                
                return {
                    "chunk_id": chunk.chunk_id,
                    "chunk_text": chunk.chunk_text,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    doc_id: chunk.document_id,
                    doc_title: doc.title,
                    permission: doc.permission,
                    metadata: chunk.metadata
                }
                
        except Exception as e:
            logger.error(f"获取块失败: {e}", exc_info=True)
            return None


# 全局实例（在应用启动时初始化）
vector_service = None


def init_vector_service():
    """初始化向量存储服务"""
    global vector_service
    vector_service = VectorStoreService()
    return vector_service
