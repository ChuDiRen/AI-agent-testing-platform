# Copyright (c) 2025 左岚. All rights reserved.
"""知识库模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "t_knowledge_base"

    kb_id = Column(Integer, primary_key=True, autoincrement=True, comment="知识库ID")  # 主键ID
    name = Column(String(200), nullable=False, comment="知识库名称")  # 知识库名称
    description = Column(Text, nullable=True, comment="知识库描述")  # 知识库描述
    embedding_model = Column(String(100), nullable=False, default="bge-large-zh-v1.5", comment="向量模型")  # 向量模型
    vector_dimension = Column(Integer, nullable=False, default=1024, comment="向量维度")  # 向量维度
    chunk_size = Column(Integer, nullable=False, default=500, comment="分块大小")  # 分块大小
    chunk_overlap = Column(Integer, nullable=False, default=50, comment="分块重叠")  # 分块重叠
    user_id = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="创建者ID")  # 创建者ID
    is_public = Column(Boolean, default=False, comment="是否公开")  # 是否公开
    status = Column(String(20), nullable=False, default="active", comment="状态")  # active/processing/error
    config = Column(JSON, nullable=True, comment="配置信息")  # 配置信息
    
    # 统计信息
    document_count = Column(Integer, default=0, comment="文档数量")  # 文档数量
    chunk_count = Column(Integer, default=0, comment="分块数量")  # 分块数量
    total_size = Column(Integer, default=0, comment="总大小(字节)")  # 总大小
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")  # 更新时间
    
    # 关系
    user = relationship("User", foreign_keys=[user_id], backref="knowledge_bases")  # 用户关系
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")  # 文档关系


class Document(Base):
    """文档表"""
    __tablename__ = "t_document"

    doc_id = Column(Integer, primary_key=True, autoincrement=True, comment="文档ID")  # 主键ID
    kb_id = Column(Integer, ForeignKey("t_knowledge_base.kb_id"), nullable=False, comment="知识库ID")  # 知识库ID
    name = Column(String(500), nullable=False, comment="文档名称")  # 文档名称
    file_path = Column(String(1000), nullable=True, comment="文件路径")  # 文件路径
    file_type = Column(String(50), nullable=False, comment="文件类型")  # pdf/docx/txt/md等
    file_size = Column(Integer, nullable=False, default=0, comment="文件大小(字节)")  # 文件大小
    content = Column(Text, nullable=True, comment="文档内容")  # 文档内容(小文件直接存储)
    
    # 处理状态
    status = Column(String(20), nullable=False, default="pending", comment="状态")  # pending/processing/completed/error
    error_message = Column(Text, nullable=True, comment="错误信息")  # 错误信息
    
    # 统计信息
    chunk_count = Column(Integer, default=0, comment="分块数量")  # 分块数量
    char_count = Column(Integer, default=0, comment="字符数")  # 字符数
    
    # 元数据
    doc_metadata = Column(JSON, nullable=True, comment="元数据")  # 元数据（重命名避免与SQLAlchemy的metadata冲突）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")  # 更新时间
    processed_at = Column(DateTime, nullable=True, comment="处理完成时间")  # 处理完成时间
    
    # 关系
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")  # 知识库关系
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")  # 分块关系


class DocumentChunk(Base):
    """文档分块表"""
    __tablename__ = "t_document_chunk"

    chunk_id = Column(Integer, primary_key=True, autoincrement=True, comment="分块ID")  # 主键ID
    doc_id = Column(Integer, ForeignKey("t_document.doc_id"), nullable=False, comment="文档ID")  # 文档ID
    kb_id = Column(Integer, ForeignKey("t_knowledge_base.kb_id"), nullable=False, comment="知识库ID")  # 知识库ID
    
    # 分块内容
    content = Column(Text, nullable=False, comment="分块内容")  # 分块内容
    chunk_index = Column(Integer, nullable=False, comment="分块索引")  # 分块索引(从0开始)
    
    # 向量信息
    vector_id = Column(String(100), nullable=True, comment="向量ID")  # Qdrant中的向量ID
    
    # 位置信息
    start_pos = Column(Integer, nullable=True, comment="起始位置")  # 起始位置
    end_pos = Column(Integer, nullable=True, comment="结束位置")  # 结束位置
    
    # 统计信息
    char_count = Column(Integer, nullable=False, default=0, comment="字符数")  # 字符数
    token_count = Column(Integer, nullable=True, comment="Token数")  # Token数
    
    # 元数据
    doc_metadata = Column(JSON, nullable=True, comment="元数据")  # 元数据（重命名避免与SQLAlchemy的metadata冲突）
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    
    # 关系
    document = relationship("Document", back_populates="chunks")  # 文档关系
    knowledge_base = relationship("KnowledgeBase")  # 知识库关系


class SearchHistory(Base):
    """搜索历史表"""
    __tablename__ = "t_search_history"

    search_id = Column(Integer, primary_key=True, autoincrement=True, comment="搜索ID")  # 主键ID
    kb_id = Column(Integer, ForeignKey("t_knowledge_base.kb_id"), nullable=False, comment="知识库ID")  # 知识库ID
    user_id = Column(Integer, ForeignKey("t_user.user_id"), nullable=False, comment="用户ID")  # 用户ID
    query = Column(Text, nullable=False, comment="搜索查询")  # 搜索查询
    result_count = Column(Integer, default=0, comment="结果数量")  # 结果数量
    top_score = Column(Float, nullable=True, comment="最高相似度")  # 最高相似度
    search_time = Column(Float, nullable=True, comment="搜索耗时(秒)")  # 搜索耗时
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")  # 创建时间
    
    # 关系
    knowledge_base = relationship("KnowledgeBase")  # 知识库关系
    user = relationship("User")  # 用户关系

