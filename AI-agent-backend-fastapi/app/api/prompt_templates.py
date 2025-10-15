# Copyright (c) 2025 左岚. All rights reserved.
"""提示词模板API路由"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.prompt_template_service import PromptTemplateService
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
    PromptTemplateResponse
)
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("/", response_model=APIResponse[PromptTemplateResponse])
async def create_prompt_template(
    template_data: PromptTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PromptTemplateResponse]:
    """创建提示词模板"""
    service = PromptTemplateService(db)
    template = await service.create_template(template_data, current_user.user_id)
    
    return APIResponse(
        success=True,
        message="提示词模板创建成功",
        data=PromptTemplateResponse.model_validate(template)
    )


@router.get("/", response_model=APIResponse[List[PromptTemplateResponse]])
async def get_prompt_templates(
    template_type: Optional[str] = Query(None, description="模板类型"),
    test_type: Optional[str] = Query(None, description="测试类型"),
    is_active: Optional[bool] = Query(None, description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[List[PromptTemplateResponse]]:
    """获取提示词模板列表"""
    service = PromptTemplateService(db)
    templates = await service.get_templates(
        template_type=template_type,
        test_type=test_type,
        is_active=is_active
    )
    
    return APIResponse(
        success=True,
        data=[PromptTemplateResponse.model_validate(t) for t in templates]
    )


@router.get("/default", response_model=APIResponse[PromptTemplateResponse])
async def get_default_template(
    template_type: str = Query("testcase_generation", description="模板类型"),
    test_type: Optional[str] = Query(None, description="测试类型"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PromptTemplateResponse]:
    """获取默认提示词模板"""
    service = PromptTemplateService(db)
    template = await service.get_default_template(
        template_type=template_type,
        test_type=test_type
    )
    
    if not template:
        return APIResponse(
            success=False,
            message="未找到默认模板"
        )
    
    return APIResponse(
        success=True,
        data=PromptTemplateResponse.model_validate(template)
    )


@router.get("/{template_id}", response_model=APIResponse[PromptTemplateResponse])
async def get_prompt_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PromptTemplateResponse]:
    """获取提示词模板详情"""
    service = PromptTemplateService(db)
    template = await service.get_template(template_id)
    
    if not template:
        return APIResponse(
            success=False,
            message="提示词模板不存在"
        )
    
    return APIResponse(
        success=True,
        data=PromptTemplateResponse.model_validate(template)
    )


@router.put("/{template_id}", response_model=APIResponse[PromptTemplateResponse])
async def update_prompt_template(
    template_id: int,
    template_data: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PromptTemplateResponse]:
    """更新提示词模板"""
    service = PromptTemplateService(db)
    
    try:
        template = await service.update_template(template_id, template_data)
        return APIResponse(
            success=True,
            message="提示词模板更新成功",
            data=PromptTemplateResponse.model_validate(template)
        )
    except ValueError as e:
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.delete("/{template_id}", response_model=APIResponse[None])
async def delete_prompt_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[None]:
    """删除提示词模板"""
    service = PromptTemplateService(db)
    
    try:
        success = await service.delete_template(template_id)
        if not success:
            return APIResponse(
                success=False,
                message="提示词模板不存在"
            )
        
        return APIResponse(
            success=True,
            message="提示词模板删除成功"
        )
    except ValueError as e:
        return APIResponse(
            success=False,
            message=str(e)
        )


@router.post("/{template_id}/set-default", response_model=APIResponse[PromptTemplateResponse])
async def set_default_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> APIResponse[PromptTemplateResponse]:
    """设置为默认模板"""
    service = PromptTemplateService(db)
    
    try:
        template = await service.set_default_template(template_id)
        return APIResponse(
            success=True,
            message="已设置为默认模板",
            data=PromptTemplateResponse.model_validate(template)
        )
    except ValueError as e:
        return APIResponse(
            success=False,
            message=str(e)
        )

