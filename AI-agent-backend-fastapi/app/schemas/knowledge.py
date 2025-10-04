# Copyright (c) 2025 左岚. All rights reserved.
"""知识库Schema"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== 知识库 ====================

class KnowledgeBaseBase(BaseModel):
    """知识库基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model: str = Field("bge-large-zh-v1.5", description="向量模型")
    chunk_size: int = Field(500, ge=100, le=2000, description="分块大小")
    chunk_overlap: int = Field(50, ge=0, le=500, description="分块重叠")
    is_public: bool = Field(False, description="是否公开")


class KnowledgeBaseCreate(KnowledgeBaseBase):
    """创建知识库"""
    pass


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    chunk_size: Optional[int] = Field(None, ge=100, le=2000)
    chunk_overlap: Optional[int] = Field(None, ge=0, le=500)
    is_public: Optional[bool] = None
    status: Optional[str] = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """知识库响应"""
    kb_id: int
    user_id: int
    status: str
    document_count: int
    chunk_count: int
    total_size: int
    vector_dimension: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==================== 文档 ====================

class DocumentBase(BaseModel):
    """文档基础模型"""
    name: str = Field(..., min_length=1, max_length=500, description="文档名称")
    file_type: str = Field(..., description="文件类型")


class DocumentCreate(DocumentBase):
    """创建文档"""
    kb_id: int = Field(..., description="知识库ID")
    file_path: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentUpdate(BaseModel):
    """更新文档"""
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(DocumentBase):
    """文档响应"""
    doc_id: int
    kb_id: int
    file_path: Optional[str] = None
    file_size: int
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    char_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentDetail(DocumentResponse):
    """文档详情"""
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ==================== 文档分块 ====================

class DocumentChunkBase(BaseModel):
    """文档分块基础模型"""
    content: str = Field(..., description="分块内容")
    chunk_index: int = Field(..., ge=0, description="分块索引")


class DocumentChunkCreate(DocumentChunkBase):
    """创建文档分块"""
    doc_id: int
    kb_id: int
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentChunkResponse(DocumentChunkBase):
    """文档分块响应"""
    chunk_id: int
    doc_id: int
    kb_id: int
    vector_id: Optional[str] = None
    char_count: int
    token_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== 搜索 ====================

class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., min_length=1, description="搜索查询")
    kb_id: int = Field(..., description="知识库ID")
    top_k: int = Field(5, ge=1, le=20, description="返回结果数量")
    score_threshold: float = Field(0.5, ge=0.0, le=1.0, description="相似度阈值")
    with_content: bool = Field(True, description="是否返回内容")


class SearchResult(BaseModel):
    """搜索结果"""
    chunk_id: int
    doc_id: int
    doc_name: str
    content: str
    score: float
    chunk_index: int
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str
    results: List[SearchResult]
    total: int
    search_time: float


# ==================== 文档上传 ====================

class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    kb_id: int = Field(..., description="知识库ID")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    doc_id: int
    upload_url: Optional[str] = None
    message: str


# ==================== 批量操作 ====================

class BatchDeleteRequest(BaseModel):
    """批量删除请求"""
    doc_ids: List[int] = Field(..., min_items=1, description="文档ID列表")


class BatchDeleteResponse(BaseModel):
    """批量删除响应"""
    success_count: int
    failed_count: int
    failed_ids: List[int] = []


# ==================== 统计信息 ====================

class KnowledgeBaseStats(BaseModel):
    """知识库统计"""
    kb_id: int
    name: str
    document_count: int
    chunk_count: int
    total_size: int
    avg_chunk_size: float
    recent_searches: int
    created_at: datetime


class DocumentStats(BaseModel):
    """文档统计"""
    total_documents: int
    by_type: Dict[str, int]
    by_status: Dict[str, int]
    total_size: int
    avg_size: float

