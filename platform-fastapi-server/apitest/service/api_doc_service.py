"""
文档管理Service
提供文档的CRUD、版本管理、搜索等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_

from apitest.model.ApiDocModel import ApiDoc


class DocService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                     doc_name: Optional[str] = None, doc_type: Optional[str] = None) -> tuple[List[ApiDoc], int]:
        """分页查询文档"""
        statement = select(ApiDoc)
        
        # 条件筛选
        if project_id:
            statement = statement.where(ApiDoc.project_id == project_id)
        if doc_name:
            statement = statement.where(ApiDoc.doc_name.contains(doc_name))
        if doc_type:
            statement = statement.where(ApiDoc.doc_type == doc_type)
        
        # 排序
        statement = statement.order_by(ApiDoc.update_time.desc(), ApiDoc.id.desc())
        
        # 查询总数
        total_statement = select(ApiDoc)
        if project_id:
            total_statement = total_statement.where(ApiDoc.project_id == project_id)
        if doc_name:
            total_statement = total_statement.where(ApiDoc.doc_name.contains(doc_name))
        if doc_type:
            total_statement = total_statement.where(ApiDoc.doc_type == doc_type)
        
        total = len(self.session.exec(total_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[ApiDoc]:
        """根据ID查询文档"""
        return self.session.get(ApiDoc, id)
    
    def create(self, **kwargs) -> ApiDoc:
        """创建文档"""
        data = ApiDoc(
            **kwargs,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新文档"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if hasattr(data, key):
                setattr(data, key, value)
        data.update_time = datetime.now()
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除文档"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def query_by_project(self, project_id: int) -> List[ApiDoc]:
        """查询项目的所有文档"""
        statement = select(ApiDoc).where(
            ApiDoc.project_id == project_id
        ).order_by(ApiDoc.update_time.desc(), ApiDoc.id.desc())
        
        return self.session.exec(statement).all()
    
    def search(self, keyword: str, project_id: Optional[int] = None) -> List[ApiDoc]:
        """搜索文档"""
        statement = select(ApiDoc).where(
            or_(
                ApiDoc.doc_name.contains(keyword),
                ApiDoc.doc_content.contains(keyword)
            )
        )
        
        if project_id:
            statement = statement.where(ApiDoc.project_id == project_id)
        
        statement = statement.order_by(ApiDoc.update_time.desc())
        
        return self.session.exec(statement).all()
    
    def get_by_type(self, doc_type: str, project_id: Optional[int] = None) -> List[ApiDoc]:
        """根据类型获取文档"""
        statement = select(ApiDoc).where(ApiDoc.doc_type == doc_type)
        
        if project_id:
            statement = statement.where(ApiDoc.project_id == project_id)
        
        statement = statement.order_by(ApiDoc.update_time.desc())
        
        return self.session.exec(statement).all()
    
    def get_latest_by_type(self, doc_type: str, project_id: int) -> Optional[ApiDoc]:
        """获取最新版本的指定类型文档"""
        statement = select(ApiDoc).where(
            and_(
                ApiDoc.doc_type == doc_type,
                ApiDoc.project_id == project_id
            )
        ).order_by(ApiDoc.update_time.desc()).limit(1)
        
        return self.session.exec(statement).first()
