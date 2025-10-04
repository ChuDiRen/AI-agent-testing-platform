# Copyright (c) 2025 左岚. All rights reserved.
"""知识库服务"""
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, update
from datetime import datetime
import time
import os

from app.models.knowledge import KnowledgeBase, Document, DocumentChunk, SearchHistory
from app.schemas.knowledge import (
    KnowledgeBaseCreate, KnowledgeBaseUpdate,
    DocumentCreate, DocumentUpdate,
    SearchRequest, SearchResult, SearchResponse
)
from app.services.vector_store import vector_store
from app.services.document_processor import document_processor


class KnowledgeService:
    """知识库服务"""
    
    # ==================== 知识库管理 ====================
    
    async def create_knowledge_base(
        self,
        db: AsyncSession,
        kb_data: KnowledgeBaseCreate,
        user_id: int
    ) -> KnowledgeBase:
        """创建知识库"""
        # 创建数据库记录
        kb = KnowledgeBase(
            name=kb_data.name,
            description=kb_data.description,
            embedding_model=kb_data.embedding_model,
            vector_dimension=1024,  # BGE-large-zh-v1.5
            chunk_size=kb_data.chunk_size,
            chunk_overlap=kb_data.chunk_overlap,
            user_id=user_id,
            is_public=kb_data.is_public,
            status="active"
        )
        
        db.add(kb)
        await db.commit()
        await db.refresh(kb)
        
        # 创建向量集合
        collection_name = f"kb_{kb.kb_id}"
        vector_store.create_collection(collection_name, kb.vector_dimension)
        
        return kb
    
    async def get_knowledge_base(
        self,
        db: AsyncSession,
        kb_id: int,
        user_id: int
    ) -> Optional[KnowledgeBase]:
        """获取知识库"""
        result = await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.kb_id == kb_id,
                (KnowledgeBase.user_id == user_id) | (KnowledgeBase.is_public == True)
            )
        )
        return result.scalar_one_or_none()
    
    async def list_knowledge_bases(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[KnowledgeBase]:
        """获取知识库列表"""
        result = await db.execute(
            select(KnowledgeBase)
            .where(
                (KnowledgeBase.user_id == user_id) | (KnowledgeBase.is_public == True)
            )
            .offset(skip)
            .limit(limit)
            .order_by(KnowledgeBase.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def update_knowledge_base(
        self,
        db: AsyncSession,
        kb_id: int,
        kb_data: KnowledgeBaseUpdate,
        user_id: int
    ) -> Optional[KnowledgeBase]:
        """更新知识库"""
        kb = await self.get_knowledge_base(db, kb_id, user_id)
        if not kb or kb.user_id != user_id:
            return None
        
        update_data = kb_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(kb, key, value)
        
        kb.updated_at = datetime.now()
        await db.commit()
        await db.refresh(kb)
        
        return kb
    
    async def delete_knowledge_base(
        self,
        db: AsyncSession,
        kb_id: int,
        user_id: int
    ) -> bool:
        """删除知识库"""
        kb = await self.get_knowledge_base(db, kb_id, user_id)
        if not kb or kb.user_id != user_id:
            return False
        
        # 删除向量集合
        collection_name = f"kb_{kb_id}"
        vector_store.delete_collection(collection_name)
        
        # 删除数据库记录(级联删除文档和分块)
        await db.delete(kb)
        await db.commit()
        
        return True
    
    # ==================== 文档管理 ====================
    
    async def add_document(
        self,
        db: AsyncSession,
        doc_data: DocumentCreate,
        user_id: int
    ) -> Document:
        """添加文档"""
        # 检查知识库权限
        kb = await self.get_knowledge_base(db, doc_data.kb_id, user_id)
        if not kb or kb.user_id != user_id:
            raise ValueError("无权限访问该知识库")
        
        # 创建文档记录
        doc = Document(
            kb_id=doc_data.kb_id,
            name=doc_data.name,
            file_path=doc_data.file_path,
            file_type=doc_data.file_type,
            file_size=0,
            content=doc_data.content,
            status="pending",
            metadata=doc_data.metadata
        )
        
        db.add(doc)
        await db.commit()
        await db.refresh(doc)
        
        return doc
    
    async def process_document(
        self,
        db: AsyncSession,
        doc_id: int,
        user_id: int
    ) -> bool:
        """处理文档: 解析、分块、向量化"""
        # 获取文档
        result = await db.execute(
            select(Document).where(Document.doc_id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return False
        
        # 检查权限
        kb = await self.get_knowledge_base(db, doc.kb_id, user_id)
        if not kb or kb.user_id != user_id:
            return False
        
        try:
            # 更新状态
            doc.status = "processing"
            await db.commit()
            
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
            
            await db.commit()
            
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
            
            vector_ids = vector_store.add_documents(
                collection_name,
                texts,
                metadatas
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
            
            await db.commit()
            
            return True
            
        except Exception as e:
            doc.status = "error"
            doc.error_message = str(e)
            await db.commit()
            print(f"❌ 处理文档失败: {e}")
            return False
    
    async def delete_document(
        self,
        db: AsyncSession,
        doc_id: int,
        user_id: int
    ) -> bool:
        """删除文档"""
        # 获取文档
        result = await db.execute(
            select(Document).where(Document.doc_id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return False
        
        # 检查权限
        kb = await self.get_knowledge_base(db, doc.kb_id, user_id)
        if not kb or kb.user_id != user_id:
            return False
        
        # 删除向量
        collection_name = f"kb_{doc.kb_id}"
        vector_store.delete_by_filter(collection_name, {"doc_id": doc_id})
        
        # 更新知识库统计
        kb.document_count = max(0, kb.document_count - 1)
        kb.chunk_count = max(0, kb.chunk_count - doc.chunk_count)
        kb.total_size = max(0, kb.total_size - doc.file_size)
        
        # 删除文档(级联删除分块)
        await db.delete(doc)
        await db.commit()
        
        return True

    # ==================== 搜索功能 ====================

    async def search_knowledge_base(
        self,
        db: AsyncSession,
        search_req: SearchRequest,
        user_id: int
    ) -> SearchResponse:
        """搜索知识库"""
        start_time = time.time()

        # 检查权限
        kb = await self.get_knowledge_base(db, search_req.kb_id, user_id)
        if not kb:
            raise ValueError("知识库不存在或无权限访问")

        # 向量搜索
        collection_name = f"kb_{search_req.kb_id}"
        vector_results = vector_store.search(
            collection_name,
            search_req.query,
            top_k=search_req.top_k,
            score_threshold=search_req.score_threshold,
            filter_conditions={"kb_id": search_req.kb_id}
        )

        # 格式化结果
        results = []
        for vector_id, score, payload in vector_results:
            result = SearchResult(
                chunk_id=payload.get("chunk_id"),
                doc_id=payload.get("doc_id"),
                doc_name=payload.get("doc_name", ""),
                content=payload.get("text", "") if search_req.with_content else "",
                score=score,
                chunk_index=payload.get("chunk_index", 0),
                metadata=payload
            )
            results.append(result)

        search_time = time.time() - start_time

        # 记录搜索历史
        history = SearchHistory(
            kb_id=search_req.kb_id,
            user_id=user_id,
            query=search_req.query,
            result_count=len(results),
            top_score=results[0].score if results else 0.0,
            search_time=search_time
        )
        db.add(history)
        await db.commit()

        return SearchResponse(
            query=search_req.query,
            results=results,
            total=len(results),
            search_time=search_time
        )

    async def get_document_chunks(
        self,
        db: AsyncSession,
        doc_id: int,
        user_id: int
    ) -> List[DocumentChunk]:
        """获取文档的所有分块"""
        # 获取文档
        result = await db.execute(
            select(Document).where(Document.doc_id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return []

        # 检查权限
        kb = await self.get_knowledge_base(db, doc.kb_id, user_id)
        if not kb:
            return []

        # 获取分块
        result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.doc_id == doc_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())


# 全局知识库服务实例
knowledge_service = KnowledgeService()

