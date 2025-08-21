"""
Service层基类
实现通用的业务逻辑处理
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.repository.base import BaseRepository
from app.entity.base import BaseEntity
from app.core.logger import get_logger
from app.utils.exceptions import ValidationException, BusinessException

# 定义泛型类型
EntityType = TypeVar("EntityType", bound=BaseEntity)
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)

logger = get_logger(__name__)


class BaseService(Generic[EntityType, RepositoryType], ABC):
    """
    Service基类
    提供通用的业务逻辑处理方法
    """

    def __init__(self, repository: RepositoryType):
        """
        初始化Service
        
        Args:
            repository: Repository实例
        """
        self.repository = repository

    def create(self, entity_data: Dict[str, Any]) -> EntityType:
        """
        创建实体
        
        Args:
            entity_data: 实体数据字典
            
        Returns:
            创建后的实体对象
            
        Raises:
            ValidationException: 数据验证异常
            BusinessException: 业务逻辑异常
        """
        try:
            # 业务验证
            self._validate_create_data(entity_data)
            
            # 创建前的业务处理
            processed_data = self._before_create(entity_data)
            
            # 创建实体对象
            entity = self._create_entity_from_data(processed_data)
            
            # 保存到数据库
            created_entity = self.repository.create(entity)
            
            # 创建后的业务处理
            self._after_create(created_entity)
            
            logger.info(f"Successfully created entity with id: {created_entity.id}")
            return created_entity
            
        except ValidationException:
            raise
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error creating entity: {str(e)}")
            raise BusinessException(f"Failed to create entity: {str(e)}")

    def get_by_id(self, entity_id: int) -> Optional[EntityType]:
        """
        根据ID获取实体
        
        Args:
            entity_id: 实体ID
            
        Returns:
            实体对象或None
        """
        try:
            entity = self.repository.get_by_id(entity_id)
            
            if entity:
                # 获取后的业务处理
                self._after_get(entity)
                
            return entity
            
        except Exception as e:
            logger.error(f"Error getting entity by id {entity_id}: {str(e)}")
            raise BusinessException(f"Failed to get entity: {str(e)}")

    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> List[EntityType]:
        """
        获取所有实体
        
        Args:
            skip: 跳过的记录数
            limit: 限制返回的记录数
            **filters: 额外的过滤条件
            
        Returns:
            实体列表
        """
        try:
            # 应用业务过滤器
            processed_filters = self._apply_business_filters(filters)
            
            entities = self.repository.get_all(skip, limit)
            
            # 应用业务过滤
            filtered_entities = self._filter_entities(entities, processed_filters)
            
            return filtered_entities
            
        except Exception as e:
            logger.error(f"Error getting all entities: {str(e)}")
            raise BusinessException(f"Failed to get entities: {str(e)}")

    def update(self, entity_id: int, update_data: Dict[str, Any]) -> Optional[EntityType]:
        """
        更新实体
        
        Args:
            entity_id: 实体ID
            update_data: 更新数据字典
            
        Returns:
            更新后的实体对象或None
            
        Raises:
            ValidationException: 数据验证异常
            BusinessException: 业务逻辑异常
        """
        try:
            # 检查实体是否存在
            existing_entity = self.repository.get_by_id(entity_id)
            if not existing_entity:
                raise BusinessException(f"Entity with id {entity_id} not found")
            
            # 业务验证
            self._validate_update_data(entity_id, update_data)
            
            # 更新前的业务处理
            processed_data = self._before_update(existing_entity, update_data)
            
            # 更新实体
            updated_entity = self.repository.update(entity_id, processed_data)
            
            if updated_entity:
                # 更新后的业务处理
                self._after_update(updated_entity)
                
                logger.info(f"Successfully updated entity with id: {entity_id}")
            
            return updated_entity
            
        except ValidationException:
            raise
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error updating entity with id {entity_id}: {str(e)}")
            raise BusinessException(f"Failed to update entity: {str(e)}")

    def delete(self, entity_id: int, soft_delete: bool = True) -> bool:
        """
        删除实体
        
        Args:
            entity_id: 实体ID
            soft_delete: 是否软删除
            
        Returns:
            是否删除成功
            
        Raises:
            BusinessException: 业务逻辑异常
        """
        try:
            # 检查实体是否存在
            existing_entity = self.repository.get_by_id(entity_id)
            if not existing_entity:
                raise BusinessException(f"Entity with id {entity_id} not found")
            
            # 删除前的业务验证
            self._validate_delete(existing_entity)
            
            # 删除前的业务处理
            self._before_delete(existing_entity)
            
            # 执行删除
            success = self.repository.delete(entity_id, soft_delete)
            
            if success:
                # 删除后的业务处理
                self._after_delete(existing_entity)
                
                logger.info(f"Successfully deleted entity with id: {entity_id}")
            
            return success
            
        except BusinessException:
            raise
        except Exception as e:
            logger.error(f"Error deleting entity with id {entity_id}: {str(e)}")
            raise BusinessException(f"Failed to delete entity: {str(e)}")

    def count(self, **filters) -> int:
        """
        统计实体数量
        
        Args:
            **filters: 过滤条件
            
        Returns:
            实体数量
        """
        try:
            # 这里可以添加业务过滤逻辑
            return self.repository.count()
            
        except Exception as e:
            logger.error(f"Error counting entities: {str(e)}")
            raise BusinessException(f"Failed to count entities: {str(e)}")

    def exists(self, entity_id: int) -> bool:
        """
        检查实体是否存在
        
        Args:
            entity_id: 实体ID
            
        Returns:
            是否存在
        """
        try:
            return self.repository.exists(entity_id)
            
        except Exception as e:
            logger.error(f"Error checking entity existence with id {entity_id}: {str(e)}")
            raise BusinessException(f"Failed to check entity existence: {str(e)}")

    # 抽象方法，子类必须实现
    @abstractmethod
    def _create_entity_from_data(self, data: Dict[str, Any]) -> EntityType:
        """
        从数据字典创建实体对象
        子类必须实现此方法
        """
        pass

    # 钩子方法，子类可以重写
    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """
        验证创建数据
        子类可以重写此方法实现自定义验证逻辑
        """
        pass

    def _validate_update_data(self, entity_id: int, data: Dict[str, Any]) -> None:
        """
        验证更新数据
        子类可以重写此方法实现自定义验证逻辑
        """
        pass

    def _validate_delete(self, entity: EntityType) -> None:
        """
        验证删除操作
        子类可以重写此方法实现自定义验证逻辑
        """
        pass

    def _before_create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建前的业务处理
        子类可以重写此方法实现自定义逻辑
        """
        return data

    def _after_create(self, entity: EntityType) -> None:
        """
        创建后的业务处理
        子类可以重写此方法实现自定义逻辑
        """
        pass

    def _after_get(self, entity: EntityType) -> None:
        """
        获取后的业务处理
        子类可以重写此方法实现自定义逻辑
        """
        pass

    def _before_update(self, entity: EntityType, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新前的业务处理
        子类可以重写此方法实现自定义逻辑
        """
        return data

    def _after_update(self, entity: EntityType) -> None:
        """
        更新后的业务处理
        子类可以重写此方法实现自定义逻辑
        """
        pass

    def _before_delete(self, entity: EntityType) -> None:
        """
        删除前的业务处理
        子类可以重写此方法实现自定义逻辑
        """
        pass

    def _after_delete(self, entity: EntityType) -> None:
        """
        删除后的业务处理
        子类可以重写此方法实现自定义逻辑
        """
        pass

    def _apply_business_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用业务过滤器
        子类可以重写此方法实现自定义过滤逻辑
        """
        return filters

    def _filter_entities(self, entities: List[EntityType], 
                        filters: Dict[str, Any]) -> List[EntityType]:
        """
        过滤实体列表
        子类可以重写此方法实现自定义过滤逻辑
        """
        return entities
