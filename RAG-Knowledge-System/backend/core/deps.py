"""
依赖注入
"""
from functools import lru_cache
from typing import Generator
from sqlmodel import Session

from db.session import engine
from rag.rag_engine import RAGEngine
from rag.embeddings.embedding_service import EmbeddingService
from rag.vector_stores.vector_store_service import VectorStoreService
from services.llm_service import LLMService
from services.chat_service import ChatService
from config.settings import get_settings

settings = get_settings()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话

    用于FastAPI依赖注入
    """
    with Session(engine) as session:
        yield session


@lru_cache()
def get_embedding_service() -> EmbeddingService:
    """
    获取嵌入服务（单例）

    用于FastAPI依赖注入
    """
    return EmbeddingService()


@lru_cache()
def get_vector_store_service() -> VectorStoreService:
    """
    获取向量存储服务（单例）

    用于FastAPI依赖注入
    """
    embedding_service = get_embedding_service()
    return VectorStoreService(
        embedding_service=embedding_service,
        collection_name=settings.CHROMA_COLLECTION_NAME,
        persist_directory=settings.CHROMA_PERSIST_DIRECTORY
    )


@lru_cache()
def get_rag_engine() -> RAGEngine:
    """
    获取RAG引擎（单例）

    用于FastAPI依赖注入
    """
    return RAGEngine()


@lru_cache()
def get_llm_service() -> LLMService:
    """
    获取LLM服务（单例）

    用于FastAPI依赖注入
    """
    return LLMService()


@lru_cache()
def get_chat_service() -> ChatService:
    """
    获取聊天服务（单例）

    用于FastAPI依赖注入
    """
    rag_engine = get_rag_engine()
    llm_service = get_llm_service()
    return ChatService(
        rag_engine=rag_engine,
        llm_service=llm_service
    )


# 清除缓存的函数（用于测试或需要重新初始化时）
def clear_service_cache():
    """清除服务缓存"""
    get_embedding_service.cache_clear()
    get_vector_store_service.cache_clear()
    get_rag_engine.cache_clear()
    get_llm_service.cache_clear()
    get_chat_service.cache_clear()
