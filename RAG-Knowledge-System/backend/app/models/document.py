"""
文档模型
"""
from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentPermission(str, Enum):
    """文档权限"""
    PUBLIC = "public"
    DEPARTMENT = "department"
    PRIVATE = "private"


class DocumentType(str, Enum):
    """文档类型"""
    PDF = "pdf"
    WORD = "docx"
    TXT = "txt"
    HTML = "html"


class Document(SQLModel, table=True):
    """文档表"""

    __tablename__ = "kb_document"

    id: Optional[int] = Field(default=None, primary_key=True, description="文档ID")
    doc_id: str = Field(max_length=64, unique=True, index=True, description="文档唯一标识")
    title: str = Field(max_length=200, description="文档标题")
    description: Optional[str] = Field(default=None, max_length=500, description="文档描述")
    file_type: DocumentType = Field(description="文件类型")
    file_path: str = Field(max_length=500, description="文件路径")
    file_size: int = Field(default=0, description="文件大小(字节）")
    content_hash: Optional[str] = Field(default=None, max_length=64, description="内容哈希")
    permission: DocumentPermission = Field(default=DocumentPermission.PRIVATE, description="权限")
    tags: Optional[str] = Field(default=None, max_length=500, description="标签(JSON数组字符串）")
    indexed: bool = Field(default=False, description="是否已索引")

    uploader_id: int = Field(foreign_key="sys_user.id", description="上传者ID")
    dept_id: Optional[int] = Field(default=None, foreign_key="sys_department.id", description="部门ID")

    create_time: datetime = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
    create_by: Optional[str] = Field(default=None, max_length=64, description="创建人")
    update_by: Optional[str] = Field(default=None, max_length=64, description="更新人")
    deleted: int = Field(default=0, description="删除标记")
