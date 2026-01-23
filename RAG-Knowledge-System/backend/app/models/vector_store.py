"""
向量数据库模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class VectorStore(SQLModel, table=True):
    """向量数据库表"""
    
    __tablename__ = "kb_vector_store"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="向量ID")
    vector_id: str = Field(max_length=64, unique=True, index=True, description="向量唯一标识")
    chunk_id: str = Field(max_length=64, foreign_key="kb_document_chunk.chunk_id", description="文档块ID")
    embedding: list[float] = Field(description="向量嵌入值（OpenAI 1536 维）")
    collection_name: str = Field(default="enterprise_rag_kb", max_length=100, description="集合名称")
    model_name: str = Field(default="bge-large-zh-v1.5", max_length=100, description="嵌入模型名称")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    deleted: int = Field(default=0, description="删除标记")
