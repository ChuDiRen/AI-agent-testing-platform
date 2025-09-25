# -*- coding: utf-8 -*-
"""
知识库相关Schema
Author: Assistant
Date: 2024-01-01
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str = Field(..., max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    embedding_model: Optional[str] = Field("text-embedding-ada-002", description="嵌入模型")
    chunk_size: Optional[int] = Field(1000, ge=100, le=4000, description="文本分块大小")
    chunk_overlap: Optional[int] = Field(200, ge=0, le=1000, description="分块重叠大小")


class KnowledgeBaseUpdate(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = Field(None, max_length=100, description="知识库名称")
    description: Optional[str] = Field(None, description="知识库描述")
    status: Optional[str] = Field(None, description="状态")
    embedding_model: Optional[str] = Field(None, description="嵌入模型")
    chunk_size: Optional[int] = Field(None, ge=100, le=4000, description="文本分块大小")
    chunk_overlap: Optional[int] = Field(None, ge=0, le=1000, description="分块重叠大小")


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: str
    name: str
    description: Optional[str]
    user_id: int
    status: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    document_count: Optional[int] = 0
    total_chunks: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    """创建文档请求"""
    title: str = Field(..., max_length=200, description="文档标题")
    description: Optional[str] = Field(None, description="文档描述")
    content: Optional[str] = Field(None, description="文档内容")


class DocumentResponse(BaseModel):
    """文档响应"""
    id: str
    knowledge_base_id: str
    title: str
    description: Optional[str]
    file_name: Optional[str]
    file_type: Optional[str]
    file_size: Optional[int]
    user_id: int
    status: str
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentChunkResponse(BaseModel):
    """文档分块响应"""
    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata: Optional[Dict[str, Any]]
    token_count: Optional[int]
    similarity_score: Optional[float] = None  # 搜索时的相似度得分

    class Config:
        from_attributes = True


class DocumentSearchRequest(BaseModel):
    """文档搜索请求"""
    query: str = Field(..., description="搜索查询")
    limit: Optional[int] = Field(10, ge=1, le=50, description="返回结果数量")
    similarity_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="相似度阈值")


class DocumentSearchResponse(BaseModel):
    """文档搜索响应"""
    query: str
    total_results: int
    chunks: List[DocumentChunkResponse]
    response_time: float


class ChatWithKnowledgeRequest(BaseModel):
    """基于知识库的对话请求"""
    kb_id: str = Field(..., description="知识库ID")
    query: str = Field(..., description="用户查询")
    large_model_id: Optional[str] = Field(None, description="使用的模型ID")
    similarity_threshold: Optional[float] = Field(0.7, description="相似度阈值")
    max_chunks: Optional[int] = Field(5, description="最大使用的分块数")
    temperature: Optional[float] = Field(0.7, description="模型温度")


class ChatWithKnowledgeResponse(BaseModel):
    """基于知识库的对话响应"""
    query: str
    response: str
    large_model_id: str
    relevant_chunks: List[DocumentChunkResponse]
    tokens_used: Optional[int]
    cost: Optional[float]
    response_time: float


class KnowledgeQueryResponse(BaseModel):
    """知识库查询记录响应"""
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    id: str
    knowledge_base_id: str
    query: str
    response: Optional[str]
    model_id: Optional[str]
    similarity_threshold: float
    response_time: Optional[float]
    tokens_used: Optional[int]
    cost: Optional[float]
    created_at: datetime

    


class KnowledgeStatistics(BaseModel):
    """知识库统计信息"""
    total_knowledge_bases: int
    total_documents: int
    total_chunks: int
    total_queries: int
    storage_used: int  # 存储使用量(字节)
    recent_queries: List[KnowledgeQueryResponse]
