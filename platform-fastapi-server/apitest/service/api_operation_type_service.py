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
        statement = select(OperationType).order_by(OperationType.sort_order, OperationType.id)
        return self.session.exec(statement).all()
    
    def query_by_category(self, category: str) -> List[OperationType]:
        """根据分类查询操作类型"""
        statement = select(OperationType).where(
            OperationType.operation_category == category
        ).order_by(OperationType.sort_order, OperationType.id)
        
        return self.session.exec(statement).all()
    
    def get_by_id(self, id: int) -> Optional[OperationType]:
        """根据ID查询操作类型"""
        return self.session.get(OperationType, id)
    
    def get_by_code(self, operation_code: str) -> Optional[OperationType]:
        """根据操作码查询"""
        statement = select(OperationType).where(
            OperationType.operation_code == operation_code
        )
        return self.session.exec(statement).first()
    
    def create(self, **kwargs) -> OperationType:
        """创建操作类型"""
        # 检查操作码是否已存在
        existing = self.get_by_code(kwargs.get("operation_code"))
        if existing:
            raise ValueError(f"操作码已存在: {kwargs.get('operation_code')}")
        
        data = OperationType(
            **kwargs,
            create_time=datetime.now(),
            update_time=datetime.now()
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
        data.update_time = datetime.now()
        
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
    
    def batch_update_order(self, order_updates: List[Dict[str, int]]) -> bool:
        """批量更新排序"""
        for update in order_updates:
            type_id = update.get("id")
            new_order = update.get("sort_order")
            
            if type_id and new_order is not None:
                op_type = self.get_by_id(type_id)
                if op_type:
                    op_type.sort_order = new_order
                    op_type.update_time = datetime.now()
                    self.session.add(op_type)
        
        self.session.commit()
        return True
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        statement = select(OperationType.operation_category).distinct()
        results = self.session.exec(statement).all()
        return [r for r in results if r]
