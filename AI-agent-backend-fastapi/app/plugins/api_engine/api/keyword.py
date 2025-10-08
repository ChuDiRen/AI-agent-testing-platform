# Copyright (c) 2025 左岚. All rights reserved.
"""
关键字API路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse

from ..services.keyword_loader import KeywordLoader
from ..schemas.keyword import KeywordListResponse

router = APIRouter()


@router.get("/", response_model=APIResponse[KeywordListResponse])
async def get_keywords(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有关键字(内置+自定义)"""
    service = KeywordLoader(db)
    keywords = await service.load_all_keywords()
    
    return APIResponse(
        success=True,
        data=KeywordListResponse(
            total=len(keywords),
            items=keywords
        )
    )


@router.get("/builtin", response_model=APIResponse[list])
async def get_builtin_keywords(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取内置关键字"""
    service = KeywordLoader(db)
    keywords = await service.load_builtin_keywords()
    
    return APIResponse(success=True, data=keywords)

