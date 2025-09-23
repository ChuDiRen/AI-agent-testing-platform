# -*- coding: utf-8 -*-
"""
知识库服务
Author: Assistant
Date: 2024-01-01
"""

import os
import json
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.knowledge import KnowledgeBase, Document, DocumentChunk, KnowledgeQuery
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate, KnowledgeBaseResponse,
    DocumentCreate, DocumentResponse, DocumentChunkResponse,
    DocumentSearchResponse, ChatWithKnowledgeResponse
)
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class KnowledgeService:
    """知识库服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_knowledge_base(
        self, 
        request: KnowledgeBaseCreate, 
        user_id: int
    ) -> KnowledgeBaseResponse:
        """创建知识库"""
        try:
            # 检查名称是否重复
            stmt = select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.name == request.name,
                    KnowledgeBase.user_id == user_id
                )
            )
            existing = await self.db.execute(stmt)
            if existing.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="知识库名称已存在")

            # 创建知识库
            kb = KnowledgeBase(
                name=request.name,
                description=request.description,
                user_id=user_id,
                embedding_model=request.embedding_model,
                chunk_size=request.chunk_size,
                chunk_overlap=request.chunk_overlap
            )
            
            self.db.add(kb)
            await self.db.commit()
            await self.db.refresh(kb)

            return KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                user_id=kb.user_id,
                status=kb.status,
                embedding_model=kb.embedding_model,
                chunk_size=kb.chunk_size,
                chunk_overlap=kb.chunk_overlap,
                document_count=0,
                total_chunks=0,
                created_at=kb.created_at,
                updated_at=kb.updated_at
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建知识库失败: {str(e)}")
            raise

    async def get_knowledge_bases(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取知识库列表"""
        try:
            # 构建查询条件
            conditions = [KnowledgeBase.user_id == user_id]
            if name:
                conditions.append(KnowledgeBase.name.ilike(f"%{name}%"))

            # 查询总数
            count_stmt = select(func.count(KnowledgeBase.id)).where(and_(*conditions))
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 查询数据
            stmt = (
                select(KnowledgeBase)
                .where(and_(*conditions))
                .offset((page - 1) * page_size)
                .limit(page_size)
                .order_by(KnowledgeBase.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            knowledge_bases = result.scalars().all()

            # 获取每个知识库的统计信息
            kb_list = []
            for kb in knowledge_bases:
                # 统计文档数量
                doc_count_stmt = select(func.count(Document.id)).where(
                    Document.knowledge_base_id == kb.id
                )
                doc_count_result = await self.db.execute(doc_count_stmt)
                doc_count = doc_count_result.scalar() or 0

                # 统计分块数量
                chunk_count_stmt = select(func.count(DocumentChunk.id)).join(
                    Document, DocumentChunk.document_id == Document.id
                ).where(Document.knowledge_base_id == kb.id)
                chunk_count_result = await self.db.execute(chunk_count_stmt)
                chunk_count = chunk_count_result.scalar() or 0

                kb_list.append(KnowledgeBaseResponse(
                    id=kb.id,
                    name=kb.name,
                    description=kb.description,
                    user_id=kb.user_id,
                    status=kb.status,
                    embedding_model=kb.embedding_model,
                    chunk_size=kb.chunk_size,
                    chunk_overlap=kb.chunk_overlap,
                    document_count=doc_count,
                    total_chunks=chunk_count,
                    created_at=kb.created_at,
                    updated_at=kb.updated_at
                ))

            return {
                "knowledge_bases": kb_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }

        except Exception as e:
            logger.error(f"获取知识库列表失败: {str(e)}")
            raise

    async def get_knowledge_base(self, kb_id: str, user_id: int) -> Optional[KnowledgeBaseResponse]:
        """获取知识库详情"""
        try:
            stmt = select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.id == kb_id,
                    KnowledgeBase.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            kb = result.scalar_one_or_none()
            
            if not kb:
                return None

            # 统计信息
            doc_count_stmt = select(func.count(Document.id)).where(
                Document.knowledge_base_id == kb_id
            )
            doc_count_result = await self.db.execute(doc_count_stmt)
            doc_count = doc_count_result.scalar() or 0

            chunk_count_stmt = select(func.count(DocumentChunk.id)).join(
                Document, DocumentChunk.document_id == Document.id
            ).where(Document.knowledge_base_id == kb_id)
            chunk_count_result = await self.db.execute(chunk_count_stmt)
            chunk_count = chunk_count_result.scalar() or 0

            return KnowledgeBaseResponse(
                id=kb.id,
                name=kb.name,
                description=kb.description,
                user_id=kb.user_id,
                status=kb.status,
                embedding_model=kb.embedding_model,
                chunk_size=kb.chunk_size,
                chunk_overlap=kb.chunk_overlap,
                document_count=doc_count,
                total_chunks=chunk_count,
                created_at=kb.created_at,
                updated_at=kb.updated_at
            )

        except Exception as e:
            logger.error(f"获取知识库详情失败: {str(e)}")
            raise

    async def update_knowledge_base(
        self, 
        kb_id: str, 
        request: KnowledgeBaseUpdate, 
        user_id: int
    ) -> KnowledgeBaseResponse:
        """更新知识库"""
        try:
            stmt = select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.id == kb_id,
                    KnowledgeBase.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            kb = result.scalar_one_or_none()
            
            if not kb:
                raise HTTPException(status_code=404, detail="知识库不存在")

            # 更新字段
            update_data = request.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(kb, field, value)

            await self.db.commit()
            await self.db.refresh(kb)

            return await self.get_knowledge_base(kb_id, user_id)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新知识库失败: {str(e)}")
            raise

    async def delete_knowledge_base(self, kb_id: str, user_id: int):
        """删除知识库"""
        try:
            stmt = select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.id == kb_id,
                    KnowledgeBase.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            kb = result.scalar_one_or_none()
            
            if not kb:
                raise HTTPException(status_code=404, detail="知识库不存在")

            await self.db.delete(kb)
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            logger.error(f"删除知识库失败: {str(e)}")
            raise

    async def upload_document(
        self, 
        kb_id: str, 
        file: UploadFile, 
        title: Optional[str] = None,
        description: Optional[str] = None,
        user_id: int = None
    ) -> DocumentResponse:
        """上传文档"""
        try:
            # 验证知识库
            kb_stmt = select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.id == kb_id,
                    KnowledgeBase.user_id == user_id
                )
            )
            kb_result = await self.db.execute(kb_stmt)
            kb = kb_result.scalar_one_or_none()
            
            if not kb:
                raise HTTPException(status_code=404, detail="知识库不存在")

            # 验证文件类型
            allowed_types = {'.txt', '.md', '.pdf', '.doc', '.docx'}
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in allowed_types:
                raise HTTPException(status_code=400, detail="不支持的文件类型")

            # 读取文件内容
            content = await file.read()
            file_size = len(content)
            
            # 限制文件大小 (10MB)
            if file_size > 10 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="文件大小不能超过10MB")

            # 创建文档记录
            document = Document(
                knowledge_base_id=kb_id,
                title=title or file.filename,
                description=description,
                file_name=file.filename,
                file_type=file.content_type,
                file_size=file_size,
                content=content.decode('utf-8', errors='ignore'),  # 简单处理，实际需要更复杂的文本提取
                user_id=user_id,
                status="processing"
            )

            self.db.add(document)
            await self.db.commit()
            await self.db.refresh(document)

            # TODO: 这里应该异步处理文档分块和向量化
            # 现在暂时标记为完成
            document.status = "completed"
            await self.db.commit()

            return DocumentResponse(
                id=document.id,
                knowledge_base_id=document.knowledge_base_id,
                title=document.title,
                description=document.description,
                file_name=document.file_name,
                file_type=document.file_type,
                file_size=document.file_size,
                user_id=document.user_id,
                status=document.status,
                chunk_count=document.chunk_count,
                created_at=document.created_at,
                updated_at=document.updated_at
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"上传文档失败: {str(e)}")
            raise

    async def search_documents(
        self, 
        kb_id: str, 
        query: str, 
        user_id: int,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> DocumentSearchResponse:
        """搜索文档（简单实现，实际需要向量搜索）"""
        try:
            start_time = datetime.now()

            # 验证知识库权限
            kb_stmt = select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.id == kb_id,
                    KnowledgeBase.user_id == user_id
                )
            )
            kb_result = await self.db.execute(kb_stmt)
            kb = kb_result.scalar_one_or_none()
            
            if not kb:
                raise HTTPException(status_code=404, detail="知识库不存在")

            # 简单的文本搜索（实际应该使用向量搜索）
            stmt = (
                select(DocumentChunk)
                .join(Document, DocumentChunk.document_id == Document.id)
                .where(
                    and_(
                        Document.knowledge_base_id == kb_id,
                        DocumentChunk.content.ilike(f"%{query}%")
                    )
                )
                .limit(limit)
            )
            
            result = await self.db.execute(stmt)
            chunks = result.scalars().all()

            response_time = (datetime.now() - start_time).total_seconds()

            chunk_responses = []
            for i, chunk in enumerate(chunks):
                chunk_responses.append(DocumentChunkResponse(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    metadata=json.loads(chunk.metadata) if chunk.metadata else {},
                    token_count=chunk.token_count,
                    similarity_score=0.8 - (i * 0.1)  # 模拟相似度得分
                ))

            return DocumentSearchResponse(
                query=query,
                total_results=len(chunk_responses),
                chunks=chunk_responses,
                response_time=response_time
            )

        except Exception as e:
            logger.error(f"搜索文档失败: {str(e)}")
            raise

    async def chat_with_knowledge(
        self,
        kb_id: str,
        query: str,
        user_id: int,
        model_id: Optional[str] = None
    ) -> ChatWithKnowledgeResponse:
        """基于知识库的对话（简单实现）"""
        try:
            start_time = datetime.now()

            # 搜索相关文档
            search_result = await self.search_documents(
                kb_id=kb_id,
                query=query,
                user_id=user_id,
                limit=5
            )

            # 构建上下文
            context = "\n\n".join([chunk.content for chunk in search_result.chunks])
            
            # 简单的响应生成（实际应该调用LLM API）
            response = f"基于知识库内容，我找到了以下相关信息：\n\n{context[:500]}..."
            
            response_time = (datetime.now() - start_time).total_seconds()

            # 记录查询
            query_record = KnowledgeQuery(
                knowledge_base_id=kb_id,
                user_id=user_id,
                query=query,
                response=response,
                model_id=model_id or "default",
                similarity_threshold=0.7,
                chunk_ids=json.dumps([chunk.id for chunk in search_result.chunks]),
                response_time=response_time,
                tokens_used=len(response.split()),  # 简单估算
                cost=0.01  # 模拟成本
            )
            
            self.db.add(query_record)
            await self.db.commit()

            return ChatWithKnowledgeResponse(
                query=query,
                response=response,
                model_id=model_id or "default",
                relevant_chunks=search_result.chunks,
                tokens_used=len(response.split()),
                cost=0.01,
                response_time=response_time
            )

        except Exception as e:
            await self.db.rollback()
            logger.error(f"知识库对话失败: {str(e)}")
            raise

    async def get_documents(
        self,
        kb_id: str,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取文档列表"""
        try:
            # 验证知识库权限
            kb_stmt = select(KnowledgeBase).where(
                and_(
                    KnowledgeBase.id == kb_id,
                    KnowledgeBase.user_id == user_id
                )
            )
            kb_result = await self.db.execute(kb_stmt)
            kb = kb_result.scalar_one_or_none()
            
            if not kb:
                raise HTTPException(status_code=404, detail="知识库不存在")

            # 构建查询条件
            conditions = [Document.knowledge_base_id == kb_id]
            if title:
                conditions.append(Document.title.ilike(f"%{title}%"))

            # 查询总数
            count_stmt = select(func.count(Document.id)).where(and_(*conditions))
            total_result = await self.db.execute(count_stmt)
            total = total_result.scalar()

            # 查询数据
            stmt = (
                select(Document)
                .where(and_(*conditions))
                .offset((page - 1) * page_size)
                .limit(page_size)
                .order_by(Document.created_at.desc())
            )
            
            result = await self.db.execute(stmt)
            documents = result.scalars().all()

            doc_list = [
                DocumentResponse(
                    id=doc.id,
                    knowledge_base_id=doc.knowledge_base_id,
                    title=doc.title,
                    description=doc.description,
                    file_name=doc.file_name,
                    file_type=doc.file_type,
                    file_size=doc.file_size,
                    user_id=doc.user_id,
                    status=doc.status,
                    chunk_count=doc.chunk_count,
                    created_at=doc.created_at,
                    updated_at=doc.updated_at
                )
                for doc in documents
            ]

            return {
                "documents": doc_list,
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size
            }

        except Exception as e:
            logger.error(f"获取文档列表失败: {str(e)}")
            raise

    async def delete_document(self, doc_id: str, user_id: int):
        """删除文档"""
        try:
            stmt = (
                select(Document)
                .join(KnowledgeBase, Document.knowledge_base_id == KnowledgeBase.id)
                .where(
                    and_(
                        Document.id == doc_id,
                        KnowledgeBase.user_id == user_id
                    )
                )
            )
            result = await self.db.execute(stmt)
            document = result.scalar_one_or_none()
            
            if not document:
                raise HTTPException(status_code=404, detail="文档不存在")

            await self.db.delete(document)
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            logger.error(f"删除文档失败: {str(e)}")
            raise
