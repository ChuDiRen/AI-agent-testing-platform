"""
元数据Service
提供元数据的CRUD、缓存等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from apitest.model.ApiMetaModel import ApiMeta


class MetaService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_all(self) -> List[ApiMeta]:
        """查询所有元数据"""
        statement = select(ApiMeta).order_by(ApiMeta.meta_key)
        return self.session.exec(statement).all()
    
    def query_by_category(self, category: str) -> List[ApiMeta]:
        """根据分类查询元数据"""
        statement = select(ApiMeta).where(
            ApiMeta.meta_category == category
        ).order_by(ApiMeta.meta_key)
        
        return self.session.exec(statement).all()
    
    def get_by_key(self, meta_key: str) -> Optional[ApiMeta]:
        """根据key查询元数据"""
        statement = select(ApiMeta).where(ApiMeta.meta_key == meta_key)
        return self.session.exec(statement).first()
    
    def get_by_id(self, id: int) -> Optional[ApiMeta]:
        """根据ID查询元数据"""
        return self.session.get(ApiMeta, id)
    
    def create(self, **kwargs) -> ApiMeta:
        """创建元数据"""
        # 检查key是否已存在
        existing = self.get_by_key(kwargs.get("meta_key"))
        if existing:
            raise ValueError(f"元数据key已存在: {kwargs.get('meta_key')}")
        
        data = ApiMeta(
            **kwargs,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新元数据"""
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
        """删除元数据"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def get_value(self, meta_key: str, default: Any = None) -> Any:
        """获取元数据值"""
        meta = self.get_by_key(meta_key)
        if meta:
            return meta.meta_value
        return default
    
    def set_value(self, meta_key: str, meta_value: str, category: str = "system") -> ApiMeta:
        """设置元数据值（不存在则创建）"""
        meta = self.get_by_key(meta_key)
        
        if meta:
            meta.meta_value = meta_value
            meta.update_time = datetime.now()
            self.session.add(meta)
            self.session.commit()
            self.session.refresh(meta)
            return meta
        else:
            return self.create(
                meta_key=meta_key,
                meta_value=meta_value,
                meta_category=category
            )
    
    def batch_set(self, meta_dict: Dict[str, str], category: str = "system") -> List[ApiMeta]:
        """批量设置元数据"""
        results = []
        for key, value in meta_dict.items():
            meta = self.set_value(key, value, category)
            results.append(meta)
        return results
