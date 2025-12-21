"""
操作类型Service
提供操作类型的CRUD、分类管理等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select

from apitest.model.ApiOperationTypeModel import OperationType


class OperationTypeService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_all(self) -> List[OperationType]:
        """查询所有操作类型"""
        statement = select(OperationType).order_by(OperationType.id)
        return self.session.exec(statement).all()
    
    def get_by_id(self, id: int) -> Optional[OperationType]:
        """根据ID查询操作类型"""
        return self.session.get(OperationType, id)
    
    def get_by_name(self, operation_type_name: str) -> Optional[OperationType]:
        """根据名称查询"""
        statement = select(OperationType).where(
            OperationType.operation_type_name == operation_type_name
        )
        return self.session.exec(statement).first()
    
    def create(self, **kwargs) -> OperationType:
        """创建操作类型"""
        # 检查名称是否已存在
        existing = self.get_by_name(kwargs.get("operation_type_name"))
        if existing:
            raise ValueError(f"操作类型名称已存在: {kwargs.get('operation_type_name')}")
        
        data = OperationType(
            **kwargs,
            create_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新操作类型"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除操作类型"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def get_all_names(self) -> List[str]:
        """获取所有操作类型名称"""
        statement = select(OperationType.operation_type_name)
        results = self.session.exec(statement).all()
        return [r for r in results if r]
