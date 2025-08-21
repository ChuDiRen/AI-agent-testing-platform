# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC Repository层基类
专门为RBAC实体设计的Repository基类
"""

from typing import Generic, TypeVar, Type, Optional, List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.logger import get_logger

# 定义泛型类型，不限制必须继承BaseEntity
EntityType = TypeVar("EntityType")

logger = get_logger(__name__)


class BaseRepository(Generic[EntityType]):
    """
    RBAC Repository基类
    提供通用的CRUD操作方法，适配RBAC实体
    """

    def __init__(self, db: Session, model: Type[EntityType]):
        """
        初始化Repository
        
        Args:
            db: 数据库会话
            model: 实体模型类
        """
        self.db = db
        self.model = model

    def create(self, entity: EntityType) -> EntityType:
        """
        创建新实体
        
        Args:
            entity: 要创建的实体对象
            
        Returns:
            创建后的实体对象
            
        Raises:
            SQLAlchemyError: 数据库操作异常
        """
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Created {self.model.__name__}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating {self.model.__name__}: {str(e)}")
            raise

    def get_by_id(self, entity_id: int) -> Optional[EntityType]:
        """
        根据ID获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            实体对象或None
        """
        try:
            # 动态获取主键字段名
            primary_key = self._get_primary_key_column()
            entity = self.db.query(self.model).filter(
                primary_key == entity_id
            ).first()
            
            if entity:
                logger.debug(f"Found {self.model.__name__} with id: {entity_id}")
            else:
                logger.debug(f"No {self.model.__name__} found with id: {entity_id}")
                
            return entity
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {entity_id}: {str(e)}")
            raise

    def get_all(self, skip: int = 0, limit: int = 100) -> List[EntityType]:
        """
        获取所有实体
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            
        Returns:
            实体列表
        """
        try:
            entities = self.db.query(self.model).offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(entities)} {self.model.__name__} entities")
            return entities
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            raise

    def update(self, entity: EntityType) -> EntityType:
        """
        更新实体
        
        Args:
            entity: 要更新的实体对象
            
        Returns:
            更新后的实体对象
        """
        try:
            self.db.commit()
            self.db.refresh(entity)
            
            logger.info(f"Updated {self.model.__name__}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error updating {self.model.__name__}: {str(e)}")
            raise

    def delete(self, entity_id: int) -> bool:
        """
        删除实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            是否删除成功
        """
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                logger.warning(f"No {self.model.__name__} found with id: {entity_id}")
                return False
            
            self.db.delete(entity)
            self.db.commit()
            logger.info(f"Deleted {self.model.__name__} with id: {entity_id}")
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {entity_id}: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error deleting {self.model.__name__} with id {entity_id}: {str(e)}")
            raise

    def count(self) -> int:
        """
        统计实体数量
        
        Returns:
            实体数量
        """
        try:
            count = self.db.query(self.model).count()
            logger.debug(f"Count of {self.model.__name__}: {count}")
            return count
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise

    def exists(self, entity_id: int) -> bool:
        """
        检查实体是否存在
        
        Args:
            entity_id: 实体ID
            
        Returns:
            是否存在
        """
        try:
            primary_key = self._get_primary_key_column()
            exists = self.db.query(self.model).filter(
                primary_key == entity_id
            ).first() is not None
            
            logger.debug(f"{self.model.__name__} with id {entity_id} exists: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {entity_id}: {str(e)}")
            raise

    def _get_primary_key_column(self):
        """
        获取主键列
        
        Returns:
            主键列对象
        """
        # 获取模型的主键列
        primary_keys = self.model.__table__.primary_key.columns
        if len(primary_keys) == 1:
            return list(primary_keys)[0]
        else:
            # 如果有复合主键，返回第一个
            return list(primary_keys)[0]
