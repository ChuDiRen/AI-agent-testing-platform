# -*- coding: utf-8 -*-
"""
AI绘画API
Author: Assistant
Date: 2024-01-01
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user
from app.core.response import success_response, error_response
from app.models.user import User
from app.service.ai_painting_service import AIPaintingService
from app.schemas.ai_painting import (
    PaintingRequest,
    PaintingResponse,
    PaintingHistoryResponse
)

router = APIRouter()

@router.post("/ai-painting/generate", response_model=dict)
async def generate_image(
    request: PaintingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """生成AI图片"""
    try:
        service = AIPaintingService(db)
        result = await service.generate_image(request, current_user.id)
        return success_response(data=result, message="图片生成成功")
    except Exception as e:
        return error_response(message=f"图片生成失败: {str(e)}")

@router.get("/ai-painting/history", response_model=dict)
async def get_painting_history(
    page: int = 1,
    page_size: int = 10,
    style: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取绘画历史"""
    try:
        service = AIPaintingService(db)
        result = await service.get_painting_history(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            style=style
        )
        return success_response(data=result, message="获取绘画历史成功")
    except Exception as e:
        return error_response(message=f"获取绘画历史失败: {str(e)}")

@router.get("/ai-painting/{painting_id}", response_model=dict)
async def get_painting_detail(
    painting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取绘画详情"""
    try:
        service = AIPaintingService(db)
        result = await service.get_painting_detail(painting_id, current_user.id)
        if not result:
            raise HTTPException(status_code=404, detail="绘画记录不存在")
        return success_response(data=result, message="获取绘画详情成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取绘画详情失败: {str(e)}")

@router.delete("/ai-painting/{painting_id}", response_model=dict)
async def delete_painting(
    painting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除绘画记录"""
    try:
        service = AIPaintingService(db)
        await service.delete_painting(painting_id, current_user.id)
        return success_response(message="绘画记录删除成功")
    except Exception as e:
        return error_response(message=f"删除绘画记录失败: {str(e)}")

@router.post("/ai-painting/{painting_id}/regenerate", response_model=dict)
async def regenerate_image(
    painting_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """重新生成图片"""
    try:
        service = AIPaintingService(db)
        result = await service.regenerate_image(painting_id, current_user.id)
        return success_response(data=result, message="图片重新生成成功")
    except Exception as e:
        return error_response(message=f"重新生成图片失败: {str(e)}")

@router.get("/ai-painting/styles/list", response_model=dict)
async def get_painting_styles():
    """获取支持的绘画风格列表"""
    try:
        service = AIPaintingService(None)
        styles = service.get_available_styles()
        return success_response(data={"styles": styles}, message="获取绘画风格列表成功")
    except Exception as e:
        return error_response(message=f"获取绘画风格列表失败: {str(e)}")

@router.get("/ai-painting/models/list", response_model=dict)
async def get_painting_models():
    """获取支持的绘画模型列表"""
    try:
        service = AIPaintingService(None)
        models = service.get_available_models()
        return success_response(data={"models": models}, message="获取绘画模型列表成功")
    except Exception as e:
        return error_response(message=f"获取绘画模型列表失败: {str(e)}")
