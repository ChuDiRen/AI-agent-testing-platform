# Copyright (c) 2025 左岚. All rights reserved.
"""文档处理异步任务"""
import os
import time
from datetime import datetime
from typing import Dict, Any
from celery import Task
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker

from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.knowledge import Document, DocumentChunk, KnowledgeBase
from app.services.document_processor import document_processor
from app.services.vector_store import vector_store


# 创建同步数据库会话(Celery worker中使用)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite"),
    echo=False
)
SyncSessionLocal = sessionmaker(bind=sync_engine)


class DocumentProcessTask(Task):
    """文档处理任务基类"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败回调"""
        print(f"❌ 任务失败: {task_id}, 错误: {exc}")
        
        # 更新文档状态为失败
        doc_id = args[0] if args else kwargs.get('doc_id')
        if doc_id:
            with SyncSessionLocal() as db:
                stmt = (
                    update(Document)
                    .where(Document.doc_id == doc_id)
                    .values(
                        status="error",
                        error_message=str(exc),
                        updated_at=datetime.now()
                    )
                )
                db.execute(stmt)
                db.commit()
    
    def on_success(self, retval, task_id, args, kwargs):
        """任务成功回调"""
        print(f"✅ 任务成功: {task_id}")


@celery_app.task(
    bind=True,
    base=DocumentProcessTask,
    name="app.tasks.document_tasks.process_document_async",
    max_retries=3,
    default_retry_delay=60
)
def process_document_async(self, doc_id: int) -> Dict[str, Any]:
    """
    异步处理文档任务
    
    Args:
        doc_id: 文档ID
        
    Returns:
        处理结果
    """
    start_time = time.time()
    
    try:
        with SyncSessionLocal() as db:
            # 获取文档
            doc = db.execute(
                select(Document).where(Document.doc_id == doc_id)
            ).scalar_one_or_none()
            
            if not doc:
                raise ValueError(f"文档不存在: {doc_id}")
            
            # 获取知识库配置
            kb = db.execute(
                select(KnowledgeBase).where(KnowledgeBase.kb_id == doc.kb_id)
            ).scalar_one_or_none()
            
            if not kb:
                raise ValueError(f"知识库不存在: {doc.kb_id}")
            
            # 更新状态为处理中
            self.update_state(
                state='PROCESSING',
                meta={'current': 0, 'total': 100, 'status': '正在解析文档...'}
            )
            
            doc.status = "processing"
            db.commit()
            
            # 解析文档
            if doc.file_path and os.path.exists(doc.file_path):
                chunks, metadata = document_processor.process_document(
                    doc.file_path,
                    doc.file_type,
                    kb.chunk_size,
                    kb.chunk_overlap
                )
                doc.file_size = os.path.getsize(doc.file_path)
            elif doc.content:
                # 直接分块内容
                chunks = document_processor.split_text(
                    doc.content,
                    kb.chunk_size,
                    kb.chunk_overlap
                )
                metadata = {"source": "direct_content"}
                doc.file_size = len(doc.content)
            else:
                raise ValueError("文档无内容")
            
            # 更新进度
            self.update_state(
                state='PROCESSING',
                meta={'current': 30, 'total': 100, 'status': f'已解析,共{len(chunks)}个分块'}
            )
            
            # 创建分块记录
            chunk_records = []
            for i, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    doc_id=doc.doc_id,
                    kb_id=doc.kb_id,
                    content=chunk_text,
                    chunk_index=i,
                    char_count=len(chunk_text),
                    metadata={"doc_name": doc.name, **metadata}
                )
                chunk_records.append(chunk)
                db.add(chunk)
            
            db.commit()
            
            # 刷新获取chunk_id
            for chunk in chunk_records:
                db.refresh(chunk)
            
            # 更新进度
            self.update_state(
                state='PROCESSING',
                meta={'current': 50, 'total': 100, 'status': '正在向量化...'}
            )
            
            # 向量化并存储
            collection_name = f"kb_{doc.kb_id}"
            texts = [chunk.content for chunk in chunk_records]
            metadatas = [
                {
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "kb_id": chunk.kb_id,
                    "chunk_index": chunk.chunk_index,
                    "doc_name": doc.name
                }
                for chunk in chunk_records
            ]
            
            # 批量向量化(显示进度)
            batch_size = 10
            vector_ids = []
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_metadatas = metadatas[i:i + batch_size]
                
                batch_vector_ids = vector_store.add_documents(
                    collection_name,
                    batch_texts,
                    batch_metadatas
                )
                vector_ids.extend(batch_vector_ids)
                
                # 更新进度
                progress = 50 + int((i + batch_size) / len(texts) * 40)
                self.update_state(
                    state='PROCESSING',
                    meta={
                        'current': min(progress, 90),
                        'total': 100,
                        'status': f'向量化进度: {i + batch_size}/{len(texts)}'
                    }
                )
            
            # 更新向量ID
            for chunk, vector_id in zip(chunk_records, vector_ids):
                chunk.vector_id = vector_id
            
            # 更新文档和知识库统计
            doc.status = "completed"
            doc.chunk_count = len(chunks)
            doc.char_count = sum(len(c) for c in chunks)
            doc.processed_at = datetime.now()
            
            kb.document_count += 1
            kb.chunk_count += len(chunks)
            kb.total_size += doc.file_size
            
            db.commit()
            
            # 计算耗时
            elapsed_time = time.time() - start_time
            
            return {
                "success": True,
                "doc_id": doc_id,
                "chunk_count": len(chunks),
                "elapsed_time": elapsed_time,
                "message": f"文档处理成功,共{len(chunks)}个分块"
            }
            
    except Exception as e:
        # 记录错误
        print(f"❌ 处理文档失败: {e}")
        
        # 更新文档状态
        with SyncSessionLocal() as db:
            stmt = (
                update(Document)
                .where(Document.doc_id == doc_id)
                .values(
                    status="error",
                    error_message=str(e),
                    updated_at=datetime.now()
                )
            )
            db.execute(stmt)
            db.commit()
        
        # 重试
        raise self.retry(exc=e, countdown=60)


@celery_app.task(name="app.tasks.document_tasks.cleanup_expired_results")
def cleanup_expired_results():
    """清理过期的任务结果"""
    # TODO: 实现清理逻辑
    print("🧹 清理过期任务结果...")
    return {"success": True, "message": "清理完成"}


@celery_app.task(name="app.tasks.document_tasks.batch_process_documents")
def batch_process_documents(doc_ids: list) -> Dict[str, Any]:
    """
    批量处理文档
    
    Args:
        doc_ids: 文档ID列表
        
    Returns:
        处理结果
    """
    results = []
    for doc_id in doc_ids:
        try:
            result = process_document_async.delay(doc_id)
            results.append({
                "doc_id": doc_id,
                "task_id": result.id,
                "status": "submitted"
            })
        except Exception as e:
            results.append({
                "doc_id": doc_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "success": True,
        "total": len(doc_ids),
        "results": results
    }

