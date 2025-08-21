"""
Entity层基类
定义实体对象的基础功能和通用方法
"""

from abc import ABC, abstractmethod, ABCMeta
from typing import Dict, Any, Optional
from datetime import datetime
from app.db.base import Base
from sqlalchemy.ext.declarative import DeclarativeMeta


class CombinedMeta(DeclarativeMeta, ABCMeta):
    """
    组合SQLAlchemy和ABC的元类
    """
    pass


class BaseEntity(Base, ABC, metaclass=CombinedMeta):
    """
    实体基类
    所有业务实体都应该继承此类
    提供通用的实体操作方法
    """
    __abstract__ = True  # 标记为抽象类，不会创建对应的数据库表
    __allow_unmapped__ = True  # 允许未映射的注解

    def validate(self) -> bool:
        """
        验证实体数据的有效性
        子类可以重写此方法实现自定义验证逻辑
        """
        return True

    def before_save(self) -> None:
        """
        保存前的钩子方法
        子类可以重写此方法实现保存前的处理逻辑
        """
        pass

    def after_save(self) -> None:
        """
        保存后的钩子方法
        子类可以重写此方法实现保存后的处理逻辑
        """
        pass

    def before_update(self) -> None:
        """
        更新前的钩子方法
        子类可以重写此方法实现更新前的处理逻辑
        """
        self.updated_at = datetime.utcnow()

    def after_update(self) -> None:
        """
        更新后的钩子方法
        子类可以重写此方法实现更新后的处理逻辑
        """
        pass

    def before_delete(self) -> None:
        """
        删除前的钩子方法
        子类可以重写此方法实现删除前的处理逻辑
        """
        pass

    def after_delete(self) -> None:
        """
        删除后的钩子方法
        子类可以重写此方法实现删除后的处理逻辑
        """
        pass

    def soft_delete(self) -> None:
        """
        软删除实体
        将is_deleted字段设置为1，而不是真正删除记录
        """
        self.is_deleted = 1
        self.updated_at = datetime.utcnow()

    def restore(self) -> None:
        """
        恢复软删除的实体
        将is_deleted字段设置为0
        """
        self.is_deleted = 0
        self.updated_at = datetime.utcnow()

    def is_soft_deleted(self) -> bool:
        """
        检查实体是否被软删除
        """
        return self.is_deleted == 1

    def to_dict_with_relations(self, include_relations: bool = False) -> Dict[str, Any]:
        """
        将实体转换为字典，可选择是否包含关联对象
        """
        result = self.to_dict()
        
        if include_relations:
            # 这里可以添加关联对象的处理逻辑
            # 子类可以重写此方法来处理特定的关联关系
            pass
            
        return result

    @classmethod
    def get_table_name(cls) -> str:
        """
        获取表名
        """
        return cls.__tablename__

    @classmethod
    def get_primary_key_name(cls) -> str:
        """
        获取主键字段名
        """
        return "id"

    def get_primary_key_value(self) -> Any:
        """
        获取主键值
        """
        return getattr(self, self.get_primary_key_name())

    def __eq__(self, other) -> bool:
        """
        实体相等性比较
        基于主键值进行比较
        """
        if not isinstance(other, self.__class__):
            return False
        return self.get_primary_key_value() == other.get_primary_key_value()

    def __hash__(self) -> int:
        """
        实体哈希值
        基于类名和主键值
        """
        return hash((self.__class__.__name__, self.get_primary_key_value()))
