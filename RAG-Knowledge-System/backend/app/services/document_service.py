"""
文档服务层
"""
import os
import uuid
import hashlib
from typing import Optional, List
from pathlib import Path
from fastapi import UploadFile
from sqlmodel import Session

from models.document import Document, DocumentPermission, DocumentType
from repositories.document_repository import DocumentRepository
from core.logger import setup_logger
from core.exceptions import (
    ValidationException,
    ResourceNotFoundException,
    BusinessException
)
from config.settings import settings

logger = setup_logger(__name__)


class DocumentService:
    """文档服务"""

    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    async def upload_document(
        self,
        file: UploadFile,
        title: str,
        description: Optional[str] = None,
        permission: DocumentPermission = DocumentPermission.PRIVATE,
        tags: Optional[List[str]] = None,
        uploader_id: int,
        dept_id: Optional[int] = None
    ) -> Document:
        """
        上传文档

        Args:
            file: 上传的文件
            title: 文档标题
            description: 文档描述
            permission: 权限
            tags: 标签列表
            uploader_id: 上传者ID
            dept_id: 部门ID

        Returns:
            创建的文档记录
        """
        # 验证文件大小
        file_size = 0
        chunk_size = 8192  # 8KB chunks
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_size += len(chunk)

        if file_size > settings.MAX_FILE_SIZE:
            raise ValidationException(
                f"文件大小超过限制（最大 {settings.MAX_FILE_SIZE / 1024 / 1024}MB）",
                field="file"
            )

        # 确定文件类型
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        
        file_type_map = {
            "pdf": DocumentType.PDF,
            "docx": DocumentType.WORD,
            "doc": DocumentType.WORD,
            "txt": DocumentType.TXT,
            "html": DocumentType.HTML,
        }
        
        file_type = file_type_map.get(ext)
        if not file_type:
            raise ValidationException(
                f"不支持的文件类型: {ext}",
                field="file"
            )

        # 生成文档唯一ID
        doc_uuid = str(uuid.uuid4()).replace("-", "")

        # 计算文件哈希
        file.seek(0)
        content_hash = hashlib.md5()
        while True:
            chunk = await file.read(8192)
            if not chunk:
                break
            content_hash.update(chunk)
        file_hash = content_hash.hexdigest()

        # 构建文件路径
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / f"{doc_uuid}_{filename}"
        
        # 保存文件
        file.seek(0)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"文件已保存: {file_path} (大小: {file_size} bytes)")

        # 构建文档数据
        doc_data = {
            "doc_id": doc_uuid,
            "title": title,
            "description": description,
            "file_type": file_type,
            "file_path": str(file_path.relative_to(upload_dir.parent)),
            "file_size": file_size,
            "content_hash": content_hash,
            "permission": permission,
            "tags": ",".join(tags) if tags else None,
            "uploader_id": uploader_id,
            "dept_id": dept_id,
            "indexed": False
        }

        # 创建文档记录
        document = self.repository.create(doc_data)

        logger.info(f"文档上传成功: {title} (ID: {document.id}, UUID: {doc_uuid})")
        return document

    def list_documents(
        self,
        user_id: Optional[int] = None,
        user_dept_id: Optional[int] = None,
        user_is_superuser: bool = False,
        keyword: Optional[str] = None,
        permission: Optional[DocumentPermission] = None,
        skip: int = 0,
        limit: int = 100
    ) -> dict:
        """
        获取文档列表（带权限过滤）

        Args:
            user_id: 用户ID
            user_dept_id: 用户部门ID
            user_is_superuser: 是否超级管理员
            keyword: 关键词
            permission: 权限筛选
            skip: 跳过数量
            limit: 每页数量

        Returns:
            包含文档列表和总数的字典
        """
        # 获取文档列表
        documents = self.repository.list_documents(
            keyword=keyword,
            permission=permission,
            dept_id=None if user_is_superuser else user_dept_id,
            skip=skip,
            limit=limit
        )

        # 统计总数
        total = self.repository.count_documents(
            keyword=keyword,
            permission=permission,
            dept_id=None if user_is_superuser else user_dept_id
        )

        # 过滤权限：非管理员只能看到公开、部门可见或自己上传的文档
        if not user_is_superuser:
            documents = [
                doc for doc in documents
                if doc.permission == DocumentPermission.PUBLIC
                or doc.permission == DocumentPermission.DEPARTMENT and doc.dept_id == user_dept_id
                or doc.uploader_id == user_id
            ]

        return {
            "items": documents,
            "total": total
        }

    def get_document(self, doc_id: int, user_id: Optional[int] = None, is_superuser: bool = False) -> Optional[Document]:
        """
        获取单个文档（带权限校验）

        Args:
            doc_id: 文档ID
            user_id: 用户ID
            is_superuser: 是否超级管理员

        Returns:
            文档对象或None
        """
        document = self.repository.get_by_id(doc_id)

        if not document or document.deleted == 1:
            raise ResourceNotFoundException(f"文档不存在: {doc_id}")

        # 权限校验
        if not is_superuser:
            if document.permission == DocumentPermission.PRIVATE and document.uploader_id != user_id:
                raise PermissionDeniedException("您没有权限访问此文档")
            if document.permission == DocumentPermission.DEPARTMENT and document.dept_id != document.uploader_id:
                # 这里需要查询用户的部门，暂时简化处理
                pass

        return document

    def delete_document(self, doc_id: int, user_id: Optional[int] = None, is_superuser: bool = False) -> bool:
        """
        删除文档（带权限校验）

        Args:
            doc_id: 文档ID
            user_id: 用户ID
            is_superuser: 是否超级管理员

        Returns:
            是否删除成功
        """
        document = self.repository.get_by_id(doc_id)

        if not document or document.deleted == 1:
            raise ResourceNotFoundException(f"文档不存在: {doc_id}")

        # 权限校验：只能删除自己上传的文档
        if not is_superuser and document.uploader_id != user_id:
            raise PermissionDeniedException("您没有权限删除此文档")

        return self.repository.delete(doc_id)

    def update_document(
        self,
        doc_id: int,
        user_id: int,
        is_superuser: bool = False,
        **kwargs
    ) -> Document:
        """
        更新文档

        Args:
            doc_id: 文档ID
            user_id: 用户ID
            is_superuser: 是否超级管理员
            **kwargs: 要更新的字段

        Returns:
            更新后的文档
        """
        document = self.repository.get_by_id(doc_id)

        if not document or document.deleted == 1:
            raise ResourceNotFoundException(f"文档不存在: {doc_id}")

        # 权限校验：只能更新自己上传的文档
        if not is_superuser and document.uploader_id != user_id:
            raise PermissionDeniedException("您没有权限修改此文档")

        return self.repository.update(document, kwargs)
