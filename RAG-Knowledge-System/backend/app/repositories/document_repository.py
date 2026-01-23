"""
文档仓储层
"""
from typing import Optional, List
from sqlmodel import Session, select, and_
from models.document import Document, DocumentPermission, DocumentType
from core.logger import setup_logger

logger = setup_logger(__name__)


class DocumentRepository:
    """文档仓储"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, doc_id: int) -> Optional[Document]:
        """根据ID获取文档"""
        return self.db.get(Document, doc_id)

    def get_by_doc_id(self, doc_uuid: str) -> Optional[Document]:
        """根据文档UUID获取文档"""
        statement = select(Document).where(Document.doc_id == doc_uuid)
        return self.db.exec(statement).first()

    def get_by_uploader(self, uploader_id: int, skip: int = 0, limit: int = 100) -> List[Document]:
        """获取用户上传的文档列表"""
        statement = (
            select(Document)
            .where(
                and_(
                    Document.uploader_id == uploader_id,
                    Document.deleted == 0
                )
            )
            .order_by(Document.create_time.desc())
            .offset(skip)
            .limit(limit)
        )
        return self.db.exec(statement).all()

    def list_documents(
        self,
        keyword: Optional[str] = None,
        permission: Optional[DocumentPermission] = None,
        dept_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Document]:
        """
        获取文档列表（支持筛选）

        Args:
            keyword: 关键词搜索
            permission: 权限筛选
            dept_id: 部门筛选
            skip: 跳过数量
            limit: 每页数量
        """
        statement = select(Document).where(Document.deleted == 0)

        if keyword:
            statement = statement.where(
                or_(
                    Document.title.contains(keyword),
                    Document.description.contains(keyword)
                )
            )

        if permission:
            statement = statement.where(Document.permission == permission)

        if dept_id:
            statement = statement.where(Document.dept_id == dept_id)

        statement = statement.order_by(Document.create_time.desc())
        statement = statement.offset(skip).limit(limit)

        return self.db.exec(statement).all()

    def count_documents(
        self,
        keyword: Optional[str] = None,
        permission: Optional[DocumentPermission] = None,
        dept_id: Optional[int] = None
    ) -> int:
        """统计文档数量"""
        statement = select(Document).where(Document.deleted == 0)

        if keyword:
            statement = statement.where(
                or_(
                    Document.title.contains(keyword),
                    Document.description.contains(keyword)
                )
            )

        if permission:
            statement = statement.where(Document.permission == permission)

        if dept_id:
            statement = statement.where(Document.dept_id == dept_id)

        # 使用子查询统计
        from sqlmodel import func
        count_statement = select(func.count()).select_from(statement)
        result = self.db.exec(count_statement).one()

        return result[0] if result else 0

    def create(self, doc_data: dict) -> Document:
        """创建文档"""
        document = Document(**doc_data)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        logger.info(f"文档创建成功: {document.title} (ID: {document.id})")
        return document

    def update(self, document: Document, update_data: dict) -> Document:
        """更新文档"""
        for field, value in update_data.items():
            setattr(document, field, value)

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        logger.info(f"文档更新成功: {document.title} (ID: {document.id})")
        return document

    def delete(self, doc_id: int) -> bool:
        """删除文档（软删除）"""
        document = self.get_by_id(doc_id)
        if not document:
            logger.warning(f"文档不存在，无法删除: {doc_id}")
            return False

        document.deleted = 1
        self.db.commit()
        logger.info(f"文档已删除: {document.title} (ID: {doc_id})")
        return True

    def update_indexed_status(self, doc_id: int, indexed: bool) -> bool:
        """更新索引状态"""
        document = self.get_by_id(doc_id)
        if not document:
            logger.warning(f"文档不存在，无法更新索引状态: {doc_id}")
            return False

        document.indexed = indexed
        self.db.add(document)
        self.db.commit()
        logger.info(f"文档索引状态已更新: {document.title} -> indexed={indexed}")
        return True

    def get_unindexed_documents(self, limit: int = 100) -> List[Document]:
        """获取未索引的文档"""
        statement = (
            select(Document)
            .where(
                and_(
                    Document.indexed == False,
                    Document.deleted == 0
                )
            )
            .order_by(Document.create_time.desc())
            .limit(limit)
        )
        return self.db.exec(statement).all()
