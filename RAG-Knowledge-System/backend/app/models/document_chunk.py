"""
文档块数据模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class DocumentChunk(SQLModel, table=True):
    """文档块表"""
    
    __tablename__ = "kb_document_chunk"
    
    id: Optional[int] = Field(default=None, primary_key=True, description="块ID")
    chunk_id: str = Field(max_length=64, unique=True, index=True, description="块唯一标识")
    document_id: int = Field(foreign_key="kb_document.id", index=True, description="文档ID")
    chunk_text: str = Field(description="块文本内容")
    chunk_index: int = Field(default=0, description="块索引")
    page_number: Optional[int] = Field(default=None, description="页码")
    vector_id: Optional[str] = Field(default=None, description="向量ID")
    metadata: Optional[str] = Field(default=None, description="元数据（JSON字符串）")
    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    deleted: int = Field(default=0, description="删除标记")
