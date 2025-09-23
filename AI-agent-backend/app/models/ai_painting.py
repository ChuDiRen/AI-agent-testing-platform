# -*- coding: utf-8 -*-
"""
AI绘画数据模型
Author: Assistant
Date: 2024-01-01
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base_class import Base


class AIPainting(Base):
    """AI绘画记录模型"""
    __tablename__ = "ai_paintings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    prompt = Column(Text, nullable=False, comment="绘画提示词")
    negative_prompt = Column(Text, comment="负面提示词")
    style = Column(String(50), nullable=False, comment="绘画风格")
    size = Column(String(20), nullable=False, comment="图片尺寸")
    model_name = Column(String(100), comment="使用的模型")
    seed = Column(Integer, comment="随机种子")
    steps = Column(Integer, default=20, comment="采样步数")
    cfg_scale = Column(Float, default=7.0, comment="CFG scale")
    sampler = Column(String(50), comment="采样器")
    
    # 生成结果
    status = Column(String(20), default="generating", comment="状态: generating, completed, failed")
    image_url = Column(String(500), comment="图片URL")
    image_path = Column(String(500), comment="图片存储路径")
    thumbnail_url = Column(String(500), comment="缩略图URL")
    
    # 统计信息
    generation_time = Column(Float, comment="生成时间(秒)")
    cost = Column(Float, comment="生成成本")
    width = Column(Integer, comment="图片宽度")
    height = Column(Integer, comment="图片高度")
    file_size = Column(Integer, comment="文件大小(字节)")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    completed_at = Column(DateTime(timezone=True), comment="完成时间")

    # 关系
    user = relationship("User")


class PaintingTemplate(Base):
    """绘画模板模型"""
    __tablename__ = "painting_templates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, comment="模板名称")
    description = Column(Text, comment="模板描述")
    category = Column(String(50), comment="模板分类")
    prompt_template = Column(Text, nullable=False, comment="提示词模板")
    negative_prompt_template = Column(Text, comment="负面提示词模板")
    recommended_style = Column(String(50), comment="推荐风格")
    recommended_size = Column(String(20), comment="推荐尺寸")
    preview_image = Column(String(500), comment="预览图片")
    tags = Column(Text, comment="标签(JSON格式)")
    usage_count = Column(Integer, default=0, comment="使用次数")
    is_public = Column(Boolean, default=True, comment="是否公开")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建用户ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    creator = relationship("User")


class PaintingCollection(Base):
    """绘画收藏模型"""
    __tablename__ = "painting_collections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name = Column(String(100), nullable=False, comment="收藏夹名称")
    description = Column(Text, comment="收藏夹描述")
    cover_image = Column(String(500), comment="封面图片")
    is_public = Column(Boolean, default=False, comment="是否公开")
    painting_count = Column(Integer, default=0, comment="绘画数量")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    # 关系
    user = relationship("User")
    paintings = relationship("CollectionPainting", back_populates="collection")


class CollectionPainting(Base):
    """收藏夹绘画关联模型"""
    __tablename__ = "collection_paintings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String(36), ForeignKey("painting_collections.id"), nullable=False, comment="收藏夹ID")
    painting_id = Column(String(36), ForeignKey("ai_paintings.id"), nullable=False, comment="绘画ID")
    added_at = Column(DateTime(timezone=True), server_default=func.now(), comment="添加时间")

    # 关系
    collection = relationship("PaintingCollection", back_populates="paintings")
    painting = relationship("AIPainting")
