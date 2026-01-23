"""
文档索引API
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session

from rag.rag_engine import RAGEngine
from services.document_service import DocumentService
from repositories.document_repository import DocumentRepository
from db.session import get_db
from core.deps import get_current_user
from models.user import User
from core.resp_model import ResponseModel

router = APIRouter(prefix="/documents", tags=["文档索引"])


@router.post("/{doc_id}/index", response_model=ResponseModel)
async def index_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rag_engine: RAGEngine = Depends()
):
    """
    索引文档（将文档添加到向量数据库）

    需要认证
    """
    try:
        # 获取文档信息
        doc_service = DocumentService(DocumentRepository(db))
        document = doc_service.get_document(doc_id, current_user.id, current_user.is_superuser)

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 检查是否已索引
        if document.indexed:
            return ResponseModel.success(
                data={"doc_id": doc_id, "message": "文档已索引"},
                message="文档已经索引过了"
            )

        # 处理文档
        result = await rag_engine.process_document(
            file_path=document.file_path,
            doc_id=document.doc_id,
            file_type=document.file_type.value,
            metadata={
                "doc_id": doc_id,
                "doc_name": document.title,
                "file_type": document.file_type.value,
                "uploader_id": document.uploader_id,
                "dept_id": document.dept_id,
                "permission": document.permission.value,
                "tags": document.tags
            }
        )

        # 更新文档索引状态
        doc_service.update_document(
            doc_id=doc_id,
            user_id=current_user.id,
            is_superuser=current_user.is_superuser,
            indexed=True
        )

        return ResponseModel.success(
            data=result,
            message="文档索引成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"索引失败: {str(e)}")


@router.post("/{doc_id}/reindex", response_model=ResponseModel)
async def reindex_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rag_engine: RAGEngine = Depends()
):
    """
    重新索引文档

    需要认证
    """
    try:
        # 获取文档信息
        doc_service = DocumentService(DocumentRepository(db))
        document = doc_service.get_document(doc_id, current_user.id, current_user.is_superuser)

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 重新索引
        result = await rag_engine.reindex_document(
            file_path=document.file_path,
            doc_id=document.doc_id,
            file_type=document.file_type.value,
            metadata={
                "doc_id": doc_id,
                "doc_name": document.title,
                "file_type": document.file_type.value,
                "uploader_id": document.uploader_id,
                "dept_id": document.dept_id,
                "permission": document.permission.value,
                "tags": document.tags
            }
        )

        # 更新文档索引状态
        doc_service.update_document(
            doc_id=doc_id,
            user_id=current_user.id,
            is_superuser=current_user.is_superuser,
            indexed=True
        )

        return ResponseModel.success(
            data=result,
            message="文档重新索引成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新索引失败: {str(e)}")


@router.delete("/{doc_id}/index", response_model=ResponseModel)
async def delete_document_index(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rag_engine: RAGEngine = Depends()
):
    """
    删除文档索引

    需要认证
    """
    try:
        # 获取文档信息
        doc_service = DocumentService(DocumentRepository(db))
        document = doc_service.get_document(doc_id, current_user.id, current_user.is_superuser)

        if not document:
            raise HTTPException(status_code=404, detail="文档不存在")

        # 从向量数据库删除
        success = await rag_engine.delete_document(document.doc_id)

        if not success:
            raise HTTPException(status_code=500, detail="删除索引失败")

        # 更新文档索引状态
        doc_service.update_document(
            doc_id=doc_id,
            user_id=current_user.id,
            is_superuser=current_user.is_superuser,
            indexed=False
        )

        return ResponseModel.success(
            data={"doc_id": doc_id},
            message="索引删除成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除索引失败: {str(e)}")


@router.post("/batch-index", response_model=ResponseModel)
async def batch_index_documents(
    doc_ids: list[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    rag_engine: RAGEngine = Depends()
):
    """
    批量索引文档

    需要认证
    """
    try:
        results = []
        failed = []

        for doc_id in doc_ids:
            try:
                # 获取文档信息
                doc_service = DocumentService(DocumentRepository(db))
                document = doc_service.get_document(doc_id, current_user.id, current_user.is_superuser)

                if not document:
                    failed.append({"doc_id": doc_id, "error": "文档不存在"})
                    continue

                # 如果已索引，跳过
                if document.indexed:
                    results.append({"doc_id": doc_id, "status": "already_indexed"})
                    continue

                # 索引文档
                await rag_engine.process_document(
                    file_path=document.file_path,
                    doc_id=document.doc_id,
                    file_type=document.file_type.value,
                    metadata={
                        "doc_id": doc_id,
                        "doc_name": document.title,
                        "file_type": document.file_type.value,
                        "uploader_id": document.uploader_id,
                        "dept_id": document.dept_id,
                        "permission": document.permission.value,
                        "tags": document.tags
                    }
                )

                # 更新索引状态
                doc_service.update_document(
                    doc_id=doc_id,
                    user_id=current_user.id,
                    is_superuser=current_user.is_superuser,
                    indexed=True
                )

                results.append({"doc_id": doc_id, "status": "success"})

            except Exception as e:
                failed.append({"doc_id": doc_id, "error": str(e)})

        return ResponseModel.success(
            data={
                "total": len(doc_ids),
                "success_count": len(results),
                "failed_count": len(failed),
                "results": results,
                "failed": failed
            },
            message=f"批量索引完成: 成功 {len(results)} 个, 失败 {len(failed)} 个"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量索引失败: {str(e)}")
