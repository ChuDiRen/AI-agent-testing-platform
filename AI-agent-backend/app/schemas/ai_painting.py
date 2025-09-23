# -*- coding: utf-8 -*-
"""
AI绘画相关Schema
Author: Assistant
Date: 2024-01-01
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PaintingRequest(BaseModel):
    """绘画请求"""
    prompt: str = Field(..., min_length=1, max_length=2000, description="绘画提示词")
    negative_prompt: Optional[str] = Field(None, max_length=1000, description="负面提示词")
    style: str = Field(..., description="绘画风格")
    size: str = Field(..., description="图片尺寸")
    model_name: Optional[str] = Field("stable-diffusion", description="使用的模型")
    seed: Optional[int] = Field(None, ge=-1, description="随机种子，-1为随机")
    steps: Optional[int] = Field(20, ge=1, le=150, description="采样步数")
    cfg_scale: Optional[float] = Field(7.0, ge=1.0, le=30.0, description="CFG scale")
    sampler: Optional[str] = Field("DPM++ 2M Karras", description="采样器")


class PaintingResponse(BaseModel):
    """绘画响应"""
    id: str
    user_id: int
    prompt: str
    negative_prompt: Optional[str]
    style: str
    size: str
    model_name: Optional[str]
    seed: Optional[int]
    steps: int
    cfg_scale: float
    sampler: Optional[str]
    status: str
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    generation_time: Optional[float]
    cost: Optional[float]
    width: Optional[int]
    height: Optional[int]
    file_size: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaintingHistoryResponse(BaseModel):
    """绘画历史响应"""
    paintings: List[PaintingResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaintingTemplateResponse(BaseModel):
    """绘画模板响应"""
    id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    prompt_template: str
    negative_prompt_template: Optional[str]
    recommended_style: Optional[str]
    recommended_size: Optional[str]
    preview_image: Optional[str]
    tags: Optional[List[str]]
    usage_count: int
    is_public: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaintingCollectionCreate(BaseModel):
    """创建绘画收藏夹请求"""
    name: str = Field(..., min_length=1, max_length=100, description="收藏夹名称")
    description: Optional[str] = Field(None, max_length=500, description="收藏夹描述")
    is_public: Optional[bool] = Field(False, description="是否公开")


class PaintingCollectionResponse(BaseModel):
    """绘画收藏夹响应"""
    id: str
    user_id: int
    name: str
    description: Optional[str]
    cover_image: Optional[str]
    is_public: bool
    painting_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaintingStyleInfo(BaseModel):
    """绘画风格信息"""
    key: str
    name: str
    description: str
    preview_image: Optional[str] = None
    recommended_settings: Optional[Dict[str, Any]] = None


class PaintingModelInfo(BaseModel):
    """绘画模型信息"""
    key: str
    name: str
    description: str
    version: Optional[str] = None
    supported_sizes: List[str]
    supported_styles: List[str]
    max_steps: int = 150
    default_cfg_scale: float = 7.0


class PaintingStatistics(BaseModel):
    """绘画统计信息"""
    total_paintings: int
    completed_paintings: int
    failed_paintings: int
    total_generation_time: float
    total_cost: float
    favorite_style: Optional[str]
    recent_paintings: List[PaintingResponse]


class RegenerateRequest(BaseModel):
    """重新生成请求"""
    modify_prompt: Optional[str] = Field(None, description="修改后的提示词")
    modify_negative_prompt: Optional[str] = Field(None, description="修改后的负面提示词")
    new_seed: Optional[int] = Field(None, description="新的随机种子")
    new_steps: Optional[int] = Field(None, description="新的采样步数")
    new_cfg_scale: Optional[float] = Field(None, description="新的CFG scale")
