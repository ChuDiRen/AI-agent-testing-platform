"""
应用配置文件
"""
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""

    # ===== 应用配置 =====
    APP_NAME: str = "RAG Knowledge System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # ===== 数据库配置 =====
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/rag_knowledge_system"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600

    # ===== JWT 配置 =====
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 天

    # ===== Redis 配置 =====
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # ===== MinIO 配置 =====
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "enterprise-rag-kb"
    MINIO_SECURE: bool = False

    # ===== RAG 配置 =====
    # 文档处理
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64  # 512 * 0.125
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB

    # 向量检索
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    RERANK_ENABLED: bool = False
    RERANK_TOP_K: int = 3

    # OCR 配置
    ENABLE_OCR: bool = False
    TESSERACT_PATH: Optional[str] = None

    # ===== 向量数据库配置 =====
    VECTOR_STORE_TYPE: str = "chromadb"  # chromadb, pinecone, weaviate
    VECTOR_DB_PATH: str = "./data/chromadb"  # 向量数据库存储路径

    # ChromaDB 配置
    CHROMA_PERSIST_DIRECTORY: str = "./data/chromadb"
    CHROMA_COLLECTION_NAME: str = "enterprise_rag_kb"

    # Pinecone 配置
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: Optional[str] = "enterprise-rag-kb"

    # Weaviate 配置
    WEAVIATE_URL: Optional[str] = None
    WEAVIATE_API_KEY: Optional[str] = None

    # ===== 嵌入模型配置 =====
    EMBEDDING_PROVIDER: str = "local"  # local, openai
    EMBEDDING_MODEL: str = "BAAI/bge-large-zh-v1.5"
    EMBEDDING_DEVICE: str = "cpu"  # cpu, cuda
    EMBEDDING_BATCH_SIZE: int = 32

    # OpenAI Embedding 配置
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    OPENAI_EMBEDDING_API_KEY: Optional[str] = None

    # ===== LLM 配置 =====
    LLM_PROVIDER: str = "openai"  # openai, anthropic, deepseek
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 60

    # OpenAI 配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None

    # Anthropic 配置
    ANTHROPIC_API_KEY: Optional[str] = None

    # DeepSeek 配置
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    # ===== 日志配置 =====
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    LOG_FILE_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    # ===== 文件存储配置 =====
    UPLOAD_DIR: str = "./data/uploads"
    PARSED_DIR: str = "./data/parsed"

    # ===== 权限配置 =====
    DEFAULT_USER_ROLE: str = "user"
    DEFAULT_DEPT_ID: Optional[int] = None

    # ===== API 限流配置 =====
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


settings = get_settings()
