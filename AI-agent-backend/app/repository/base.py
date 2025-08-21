"""
Repository层基类
封装通用的数据库CRUD操作
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import SQLAlchemyError
from app.entity.base import BaseEntity
from app.core.logger import get_logger

# 定义泛型类型
EntityType = TypeVar("EntityType", bound=BaseEntity)

logger = get_logger(__name__)


class BaseRepository(Generic[EntityType]):
    """
    Repository基类
    提供通用的CRUD操作方法
    """

    def __init__(self, model: Type[EntityType], db: Session):
        """
        初始化Repository
        
        Args:
            model: 实体模型类
            db: 数据库会话
        """
        self.model = model
        self.db = db

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
            # 执行保存前钩子
            entity.before_save()
            
            # 验证实体数据
            if not entity.validate():
                raise ValueError("Entity validation failed")
            
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            
            # 执行保存后钩子
            entity.after_save()
            
            logger.info(f"Created {self.model.__name__} with id: {entity.id}")
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
            entity = self.db.query(self.model).filter(
                and_(
                    self.model.id == entity_id,
                    self.model.is_deleted == 0
                )
            ).first()
            
            if entity:
                logger.debug(f"Found {self.model.__name__} with id: {entity_id}")
            else:
                logger.debug(f"No {self.model.__name__} found with id: {entity_id}")
                
            return entity
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting {self.model.__name__} by id {entity_id}: {str(e)}")
            raise

    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[EntityType]:
        """
        获取所有实体
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            include_deleted: 是否包含已删除的记录
            
        Returns:
            实体列表
        """
        try:
            query = self.db.query(self.model)
            
            if not include_deleted:
                query = query.filter(self.model.is_deleted == 0)
                
            entities = query.offset(skip).limit(limit).all()
            
            logger.debug(f"Retrieved {len(entities)} {self.model.__name__} entities")
            return entities
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting all {self.model.__name__}: {str(e)}")
            raise

    def update(self, entity_id: int, update_data: Dict[str, Any]) -> Optional[EntityType]:
        """
        更新实体
        
        Args:
            entity_id: 实体ID
            update_data: 更新数据字典
            
        Returns:
            更新后的实体对象或None
        """
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                logger.warning(f"No {self.model.__name__} found with id: {entity_id}")
                return None
            
            # 执行更新前钩子
            entity.before_update()
            
            # 更新字段
            for field, value in update_data.items():
                if hasattr(entity, field) and field not in ['id', 'created_at']:
                    setattr(entity, field, value)
            
            # 验证更新后的数据
            if not entity.validate():
                raise ValueError("Entity validation failed after update")
            
            self.db.commit()
            self.db.refresh(entity)
            
            # 执行更新后钩子
            entity.after_update()
            
            logger.info(f"Updated {self.model.__name__} with id: {entity_id}")
            return entity
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} with id {entity_id}: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error updating {self.model.__name__} with id {entity_id}: {str(e)}")
            raise

    def delete(self, entity_id: int, soft_delete: bool = True) -> bool:
        """
        删除实体
        
        Args:
            entity_id: 实体ID
            soft_delete: 是否软删除
            
        Returns:
            是否删除成功
        """
        try:
            entity = self.get_by_id(entity_id)
            if not entity:
                logger.warning(f"No {self.model.__name__} found with id: {entity_id}")
                return False
            
            # 执行删除前钩子
            entity.before_delete()
            
            if soft_delete:
                entity.soft_delete()
                self.db.commit()
                logger.info(f"Soft deleted {self.model.__name__} with id: {entity_id}")
            else:
                self.db.delete(entity)
                self.db.commit()
                logger.info(f"Hard deleted {self.model.__name__} with id: {entity_id}")
            
            # 执行删除后钩子
            entity.after_delete()
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with id {entity_id}: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error deleting {self.model.__name__} with id {entity_id}: {str(e)}")
            raise

    def count(self, include_deleted: bool = False) -> int:
        """
        统计实体数量
        
        Args:
            include_deleted: 是否包含已删除的记录
            
        Returns:
            实体数量
        """
        try:
            query = self.db.query(func.count(self.model.id))
            
            if not include_deleted:
                query = query.filter(self.model.is_deleted == 0)
                
            count = query.scalar()
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
            exists = self.db.query(
                self.db.query(self.model).filter(
                    and_(
                        self.model.id == entity_id,
                        self.model.is_deleted == 0
                    )
                ).exists()
            ).scalar()
            
            logger.debug(f"{self.model.__name__} with id {entity_id} exists: {exists}")
            return exists
            
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__} with id {entity_id}: {str(e)}")
            raise

    def find_by_field(self, field_name: str, field_value: Any, 
                     include_deleted: bool = False) -> List[EntityType]:
        """
        根据字段值查找实体
        
        Args:
            field_name: 字段名
            field_value: 字段值
            include_deleted: 是否包含已删除的记录
            
        Returns:
            实体列表
        """
        try:
            if not hasattr(self.model, field_name):
                raise ValueError(f"Field '{field_name}' does not exist in {self.model.__name__}")
            
            query = self.db.query(self.model).filter(
                getattr(self.model, field_name) == field_value
            )
            
            if not include_deleted:
                query = query.filter(self.model.is_deleted == 0)
                
            entities = query.all()
            
            logger.debug(f"Found {len(entities)} {self.model.__name__} entities with {field_name}={field_value}")
            return entities
            
        except SQLAlchemyError as e:
            logger.error(f"Error finding {self.model.__name__} by {field_name}={field_value}: {str(e)}")
            raise

    def batch_create(self, entities: List[EntityType]) -> List[EntityType]:
        """
        批量创建实体
        
        Args:
            entities: 实体列表
            
        Returns:
            创建后的实体列表
        """
        try:
            created_entities = []
            
            for entity in entities:
                # 执行保存前钩子
                entity.before_save()
                
                # 验证实体数据
                if not entity.validate():
                    raise ValueError(f"Entity validation failed for {entity}")
                
                self.db.add(entity)
                created_entities.append(entity)
            
            self.db.commit()
            
            # 刷新所有实体
            for entity in created_entities:
                self.db.refresh(entity)
                # 执行保存后钩子
                entity.after_save()
            
            logger.info(f"Batch created {len(created_entities)} {self.model.__name__} entities")
            return created_entities
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error batch creating {self.model.__name__}: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error batch creating {self.model.__name__}: {str(e)}")
            raise
