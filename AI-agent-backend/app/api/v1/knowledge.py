# -*- coding: utf-8 -*-
"""
知识库管理API
Author: Assistant
Date: 2024-01-01
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, get_current_active_user
from app.core.response import success_response, error_response
from app.models.user import User
from app.service.knowledge_service import KnowledgeService
from app.schemas.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate, 
    KnowledgeBaseResponse,
    DocumentCreate,
    DocumentResponse,
    DocumentSearchRequest,
    DocumentSearchResponse
)

router = APIRouter()

@router.post("/knowledge-bases", response_model=dict)
async def create_knowledge_base(
    request: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建知识库"""
    try:
        service = KnowledgeService(db)
        knowledge_base = await service.create_knowledge_base(request, current_user.id)
        return success_response(data=knowledge_base, message="知识库创建成功")
    except Exception as e:
        return error_response(message=f"创建知识库失败: {str(e)}")

@router.get("/knowledge-bases", response_model=dict)
async def get_knowledge_bases(
    page: int = 1,
    page_size: int = 10,
    name: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取知识库列表"""
    try:
        service = KnowledgeService(db)
        result = await service.get_knowledge_bases(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            name=name
        )
        return success_response(data=result, message="获取知识库列表成功")
    except Exception as e:
        return error_response(message=f"获取知识库列表失败: {str(e)}")

@router.get("/knowledge-bases/{kb_id}", response_model=dict)
async def get_knowledge_base(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取知识库详情"""
    try:
        service = KnowledgeService(db)
        knowledge_base = await service.get_knowledge_base(kb_id, current_user.id)
        if not knowledge_base:
            raise HTTPException(status_code=404, detail="知识库不存在")
        return success_response(data=knowledge_base, message="获取知识库详情成功")
    except HTTPException:
        raise
    except Exception as e:
        return error_response(message=f"获取知识库详情失败: {str(e)}")

@router.put("/knowledge-bases/{kb_id}", response_model=dict)
async def update_knowledge_base(
    kb_id: str,
    request: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新知识库"""
    try:
        service = KnowledgeService(db)
        knowledge_base = await service.update_knowledge_base(kb_id, request, current_user.id)
        return success_response(data=knowledge_base, message="知识库更新成功")
    except Exception as e:
        return error_response(message=f"更新知识库失败: {str(e)}")

@router.delete("/knowledge-bases/{kb_id}", response_model=dict)
async def delete_knowledge_base(
    kb_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除知识库"""
    try:
        service = KnowledgeService(db)
        await service.delete_knowledge_base(kb_id, current_user.id)
        return success_response(message="知识库删除成功")
    except Exception as e:
        return error_response(message=f"删除知识库失败: {str(e)}")

@router.post("/knowledge-bases/{kb_id}/documents", response_model=dict)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    title: str = Form(None),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传文档到知识库"""
    try:
        service = KnowledgeService(db)
        document = await service.upload_document(
            kb_id=kb_id,
            file=file,
            title=title,
            description=description,
            user_id=current_user.id
        )
        return success_response(data=document, message="文档上传成功")
    except Exception as e:
        return error_response(message=f"上传文档失败: {str(e)}")

@router.get("/knowledge-bases/{kb_id}/documents", response_model=dict)
async def get_documents(
    kb_id: str,
    page: int = 1,
    page_size: int = 10,
    title: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取知识库文档列表"""
    try:
        service = KnowledgeService(db)
        result = await service.get_documents(
            kb_id=kb_id,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            title=title
        )
        return success_response(data=result, message="获取文档列表成功")
    except Exception as e:
        return error_response(message=f"获取文档列表失败: {str(e)}")

@router.delete("/documents/{doc_id}", response_model=dict)
async def delete_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除文档"""
    try:
        service = KnowledgeService(db)
        await service.delete_document(doc_id, current_user.id)
        return success_response(message="文档删除成功")
    except Exception as e:
        return error_response(message=f"删除文档失败: {str(e)}")

@router.post("/knowledge-bases/{kb_id}/search", response_model=dict)
async def search_documents(
    kb_id: str,
    request: DocumentSearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """在知识库中搜索文档"""
    try:
        service = KnowledgeService(db)
        results = await service.search_documents(
            kb_id=kb_id,
            query=request.query,
            user_id=current_user.id,
            limit=request.limit or 10,
            similarity_threshold=request.similarity_threshold or 0.7
        )
        return success_response(data=results, message="文档搜索成功")
    except Exception as e:
        return error_response(message=f"文档搜索失败: {str(e)}")

@router.post("/chat-with-knowledge", response_model=dict)
async def chat_with_knowledge(
    kb_id: str,
    query: str,
    model_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """基于知识库的对话"""
    try:
        service = KnowledgeService(db)
        response = await service.chat_with_knowledge(
            kb_id=kb_id,
            query=query,
            user_id=current_user.id,
            model_id=model_id
        )
        return success_response(data=response, message="知识库对话成功")
    except Exception as e:
        return error_response(message=f"知识库对话失败: {str(e)}")
