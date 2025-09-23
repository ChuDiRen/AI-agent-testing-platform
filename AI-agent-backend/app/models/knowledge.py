# -*- coding: utf-8 -*-
"""
知识库数据模型
Author: Assistant
Date: 2024-01-01
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class KnowledgeBase(Base):
    """知识库模型"""
    __tablename__ = "knowledge_bases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, comment="知识库名称")
    description = Column(Text, comment="知识库描述")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="创建用户ID")
    status = Column(String(20), default="active", comment="状态: active, inactive")
    embedding_model = Column(String(100), default="text-embedding-ada-002", comment="嵌入模型")
    chunk_size = Column(Integer, default=1000, comment="文本分块大小")
    chunk_overlap = Column(Integer, default=200, comment="分块重叠大小")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User", back_populates="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_base_id = Column(String(36), ForeignKey("knowledge_bases.id"), nullable=False, comment="知识库ID")
    title = Column(String(200), nullable=False, comment="文档标题")
    description = Column(Text, comment="文档描述")
    file_name = Column(String(200), comment="原始文件名")
    file_path = Column(String(500), comment="文件存储路径")
    file_type = Column(String(50), comment="文件类型")
    file_size = Column(Integer, comment="文件大小(字节)")
    content = Column(Text, comment="文档内容")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="上传用户ID")
    status = Column(String(20), default="processing", comment="状态: processing, completed, failed")
    chunk_count = Column(Integer, default=0, comment="分块数量")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    user = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """文档分块模型"""
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id"), nullable=False, comment="文档ID")
    chunk_index = Column(Integer, nullable=False, comment="分块索引")
    content = Column(Text, nullable=False, comment="分块内容")
    embedding = Column(Text, comment="向量嵌入(JSON格式)")
    metadata = Column(Text, comment="元数据(JSON格式)")
    token_count = Column(Integer, comment="Token数量")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系
    document = relationship("Document", back_populates="chunks")


class KnowledgeQuery(Base):
    """知识库查询记录"""
    __tablename__ = "knowledge_queries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    knowledge_base_id = Column(String(36), ForeignKey("knowledge_bases.id"), nullable=False, comment="知识库ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="查询用户ID")
    query = Column(Text, nullable=False, comment="查询内容")
    response = Column(Text, comment="响应内容")
    model_id = Column(String(100), comment="使用的模型ID")
    similarity_threshold = Column(Float, default=0.7, comment="相似度阈值")
    chunk_ids = Column(Text, comment="匹配的分块ID列表(JSON格式)")
    response_time = Column(Float, comment="响应时间(秒)")
    tokens_used = Column(Integer, comment="使用的Token数量")
    cost = Column(Float, comment="查询成本")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    # 关系
    knowledge_base = relationship("KnowledgeBase")
    user = relationship("User")
