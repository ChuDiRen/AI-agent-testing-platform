"""
关键字Service
提供关键字的CRUD、搜索、统计等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_

from apitest.model.ApiKeyWordModel import ApiKeyWord


class KeyWordService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int,
                     keyword_name: Optional[str] = None, operation_type_id: Optional[int] = None,
                     plugin_id: Optional[int] = None, plugin_code: Optional[str] = None) -> tuple[List[ApiKeyWord], int]:
        """分页查询关键字"""
        statement = select(ApiKeyWord)
        
        # 条件筛选
        if keyword_name:
            statement = statement.where(ApiKeyWord.name.contains(keyword_name))
        if operation_type_id:
            statement = statement.where(ApiKeyWord.operation_type_id == operation_type_id)
        if plugin_id:
            statement = statement.where(ApiKeyWord.plugin_id == plugin_id)
        if plugin_code:
            statement = statement.where(ApiKeyWord.plugin_code == plugin_code)
        
        # 排序
        statement = statement.order_by(ApiKeyWord.id.desc())
        
        # 查询总数
        total_statement = select(ApiKeyWord)
        if keyword_name:
            total_statement = total_statement.where(ApiKeyWord.name.contains(keyword_name))
        if operation_type_id:
            total_statement = total_statement.where(ApiKeyWord.operation_type_id == operation_type_id)
        if plugin_id:
            total_statement = total_statement.where(ApiKeyWord.plugin_id == plugin_id)
        if plugin_code:
            total_statement = total_statement.where(ApiKeyWord.plugin_code == plugin_code)
        
        total = len(self.session.exec(total_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[ApiKeyWord]:
        """根据ID查询关键字"""
        return self.session.get(ApiKeyWord, id)
    
    def create(self, **kwargs) -> ApiKeyWord:
        """创建关键字"""
        data = ApiKeyWord(
            **kwargs,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新关键字"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        data.update_time = datetime.now()
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除关键字"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def query_all(self) -> List[ApiKeyWord]:
        """查询所有关键字"""
        statement = select(ApiKeyWord).order_by(ApiKeyWord.id.desc())
        return self.session.exec(statement).all()
    
    def search(self, keyword: str) -> List[ApiKeyWord]:
        """搜索关键字"""
        statement = select(ApiKeyWord).where(
            or_(
                ApiKeyWord.name.contains(keyword),
                ApiKeyWord.keyword_desc.contains(keyword)
            )
        )
        
        statement = statement.order_by(ApiKeyWord.id.desc())
        
        return self.session.exec(statement).all()
    
    def get_by_operation_type(self, operation_type_id: int) -> List[ApiKeyWord]:
        """根据操作类型获取关键字"""
        statement = select(ApiKeyWord).where(ApiKeyWord.operation_type_id == operation_type_id)
        statement = statement.order_by(ApiKeyWord.id.desc())
        
        return self.session.exec(statement).all()
    
    def batch_create(self, keywords_data: List[Dict[str, Any]]) -> List[ApiKeyWord]:
        """批量创建关键字"""
        created_keywords = []
        for keyword_data in keywords_data:
            keyword = self.create(**keyword_data)
            created_keywords.append(keyword)
        return created_keywords
    
    def batch_delete(self, keyword_ids: List[int]) -> int:
        """批量删除关键字"""
        deleted_count = 0
        for keyword_id in keyword_ids:
            if self.delete(keyword_id):
                deleted_count += 1
        return deleted_count
