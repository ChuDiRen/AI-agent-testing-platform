# Copyright (c) 2025 左岚. All rights reserved.
"""知识库API路由"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import os
import shutil
from pathlib import Path
from celery.result import AsyncResult

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentDetail,
    SearchRequest, SearchResponse,
    BatchDeleteRequest, BatchDeleteResponse
)
from app.schemas.task import TaskStatus, TaskSubmitResponse, BatchTaskSubmitResponse
from app.schemas.common import APIResponse
from app.services.knowledge_service import knowledge_service
from app.tasks.document_tasks import process_document_async, batch_process_documents

router = APIRouter(prefix="/knowledge", tags=["知识库"])

# 文件上传目录
UPLOAD_DIR = Path("./uploads/documents")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ==================== 知识库管理 ====================

@router.post("/bases", response_model=APIResponse[KnowledgeBaseResponse])
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建知识库"""
    try:
        kb = await knowledge_service.create_knowledge_base(db, kb_data, current_user.user_id)
        return APIResponse(success=True, data=kb, message="知识库创建成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bases", response_model=APIResponse[List[KnowledgeBaseResponse]])
async def list_knowledge_bases(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识库列表"""
    kbs = await knowledge_service.list_knowledge_bases(db, current_user.user_id, skip, limit)
    return APIResponse(success=True, data=kbs)


@router.get("/bases/{kb_id}", response_model=APIResponse[KnowledgeBaseResponse])
async def get_knowledge_base(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识库详情"""
    kb = await knowledge_service.get_knowledge_base(db, kb_id, current_user.user_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    return APIResponse(success=True, data=kb)


@router.put("/bases/{kb_id}", response_model=APIResponse[KnowledgeBaseResponse])
async def update_knowledge_base(
    kb_id: int,
    kb_data: KnowledgeBaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新知识库"""
    kb = await knowledge_service.update_knowledge_base(db, kb_id, kb_data, current_user.user_id)
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在或无权限")
    return APIResponse(success=True, data=kb, message="更新成功")


@router.delete("/bases/{kb_id}", response_model=APIResponse)
async def delete_knowledge_base(
    kb_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除知识库"""
    success = await knowledge_service.delete_knowledge_base(db, kb_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="知识库不存在或无权限")
    return APIResponse(success=True, message="删除成功")


# ==================== 文档管理 ====================

@router.post("/documents/upload", response_model=APIResponse[TaskSubmitResponse])
async def upload_document(
    kb_id: int = Form(...),
    file: UploadFile = File(...),
    use_async: bool = Form(True),  # 是否使用异步处理
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """上传文档"""
    try:
        # 检查文件类型
        file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
        from app.services.document_processor import document_processor
        if not document_processor.is_supported(file_ext):
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_ext}")

        # 保存文件
        file_path = UPLOAD_DIR / f"{current_user.user_id}_{kb_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 创建文档记录
        doc_data = DocumentCreate(
            kb_id=kb_id,
            name=file.filename,
            file_path=str(file_path),
            file_type=file_ext
        )
        doc = await knowledge_service.add_document(db, doc_data, current_user.user_id)

        # 异步处理文档
        if use_async:
            # 提交到Celery任务队列
            task = process_document_async.delay(doc.doc_id)
            return APIResponse(
                success=True,
                data=TaskSubmitResponse(
                    task_id=task.id,
                    doc_id=doc.doc_id,
                    message="文档已提交处理,请稍后查看进度"
                ),
                message="文档上传成功,正在后台处理"
            )
        else:
            # 同步处理(小文件)
            await knowledge_service.process_document(db, doc.doc_id, current_user.user_id)
            return APIResponse(
                success=True,
                data=TaskSubmitResponse(
                    task_id="",
                    doc_id=doc.doc_id,
                    message="文档处理完成"
                ),
                message="文档上传并处理成功"
            )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/documents/text", response_model=APIResponse[DocumentResponse])
async def add_text_document(
    kb_id: int,
    name: str,
    content: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加文本文档"""
    try:
        doc_data = DocumentCreate(
            kb_id=kb_id,
            name=name,
            file_type="txt",
            content=content
        )
        doc = await knowledge_service.add_document(db, doc_data, current_user.user_id)
        
        # 处理文档
        await knowledge_service.process_document(db, doc.doc_id, current_user.user_id)
        
        return APIResponse(success=True, data=doc, message="文档添加成功")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{doc_id}", response_model=APIResponse)
async def delete_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除文档"""
    success = await knowledge_service.delete_document(db, doc_id, current_user.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在或无权限")
    return APIResponse(success=True, message="删除成功")


@router.post("/documents/batch-delete", response_model=APIResponse[BatchDeleteResponse])
async def batch_delete_documents(
    request: BatchDeleteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量删除文档"""
    success_count = 0
    failed_ids = []
    
    for doc_id in request.doc_ids:
        success = await knowledge_service.delete_document(db, doc_id, current_user.user_id)
        if success:
            success_count += 1
        else:
            failed_ids.append(doc_id)
    
    result = BatchDeleteResponse(
        success_count=success_count,
        failed_count=len(failed_ids),
        failed_ids=failed_ids
    )
    
    return APIResponse(success=True, data=result, message=f"成功删除 {success_count} 个文档")


# ==================== 搜索功能 ====================

@router.post("/search", response_model=APIResponse[SearchResponse])
async def search_knowledge_base(
    search_req: SearchRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """搜索知识库"""
    try:
        result = await knowledge_service.search_knowledge_base(db, search_req, current_user.user_id)
        return APIResponse(success=True, data=result)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}/chunks", response_model=APIResponse)
async def get_document_chunks(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取文档分块"""
    chunks = await knowledge_service.get_document_chunks(db, doc_id, current_user.user_id)
    return APIResponse(success=True, data=chunks)


# ==================== 任务管理 ====================

@router.get("/tasks/{task_id}", response_model=APIResponse[TaskStatus])
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        task_result = AsyncResult(task_id)

        if task_result.state == 'PENDING':
            response = TaskStatus(
                task_id=task_id,
                state='PENDING',
                status='任务等待中...'
            )
        elif task_result.state == 'PROCESSING':
            info = task_result.info or {}
            response = TaskStatus(
                task_id=task_id,
                state='PROCESSING',
                current=info.get('current', 0),
                total=info.get('total', 100),
                status=info.get('status', '处理中...')
            )
        elif task_result.state == 'SUCCESS':
            response = TaskStatus(
                task_id=task_id,
                state='SUCCESS',
                current=100,
                total=100,
                status='处理完成',
                result=task_result.result
            )
        elif task_result.state == 'FAILURE':
            response = TaskStatus(
                task_id=task_id,
                state='FAILURE',
                status='处理失败',
                error=str(task_result.info)
            )
        else:
            response = TaskStatus(
                task_id=task_id,
                state=task_result.state,
                status=f'状态: {task_result.state}'
            )

        return APIResponse(success=True, data=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/batch-process", response_model=APIResponse[BatchTaskSubmitResponse])
async def batch_process_documents_api(
    doc_ids: List[int],
    current_user: User = Depends(get_current_user)
):
    """批量处理文档"""
    try:
        task = batch_process_documents.delay(doc_ids)

        return APIResponse(
            success=True,
            data=BatchTaskSubmitResponse(
                total=len(doc_ids),
                submitted=len(doc_ids),
                failed=0,
                task_ids=[task.id]
            ),
            message=f"已提交{len(doc_ids)}个文档处理任务"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

