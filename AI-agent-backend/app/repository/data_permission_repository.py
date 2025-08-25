# Copyright (c) 2025 左岚. All rights reserved.
"""
数据权限Repository
提供数据权限规则的数据访问功能
"""

from typing import List, Optional, Dict, Any

from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.entity.permission_cache import DataPermissionRule
from app.repository.base import BaseRepository

logger = get_logger(__name__)


class DataPermissionRepository(BaseRepository[DataPermissionRule]):
    """
    数据权限Repository
    提供数据权限规则的CRUD操作和查询功能
    """

    def __init__(self, db: Session):
        super().__init__(db, DataPermissionRule)
        self.logger = get_logger(self.__class__.__name__)

    def create_data_permission_rule(
        self, rule_name: str, rule_code: str, resource_type: str,
        permission_type: str, rule_expression: Optional[str] = None,
        dept_ids: Optional[str] = None, role_ids: Optional[str] = None,
        user_ids: Optional[str] = None, priority: int = 0,
        description: Optional[str] = None
    ) -> DataPermissionRule:
        """
        创建数据权限规则
        
        Args:
            rule_name: 规则名称
            rule_code: 规则代码
            resource_type: 资源类型
            permission_type: 权限类型
            rule_expression: 规则表达式
            dept_ids: 部门ID列表
            role_ids: 角色ID列表
            user_ids: 用户ID列表
            priority: 优先级
            description: 描述
            
        Returns:
            创建的数据权限规则对象
        """
        try:
            rule = DataPermissionRule(
                RULE_NAME=rule_name,
                RULE_CODE=rule_code,
                RESOURCE_TYPE=resource_type,
                PERMISSION_TYPE=permission_type,
                RULE_EXPRESSION=rule_expression,
                DEPT_IDS=dept_ids,
                ROLE_IDS=role_ids,
                USER_IDS=user_ids,
                PRIORITY=priority,
                DESCRIPTION=description,
                IS_ACTIVE=1
            )
            
            return self.create(rule)
            
        except Exception as e:
            self.logger.error(f"Create data permission rule error: {str(e)}")
            raise

    def get_rules_by_resource_type(self, resource_type: str) -> List[DataPermissionRule]:
        """
        根据资源类型获取数据权限规则
        
        Args:
            resource_type: 资源类型
            
        Returns:
            数据权限规则列表
        """
        try:
            return self.db.query(DataPermissionRule).filter(
                and_(
                    DataPermissionRule.RESOURCE_TYPE == resource_type,
                    DataPermissionRule.IS_ACTIVE == 1,
                    DataPermissionRule.is_deleted == 0
                )
            ).order_by(desc(DataPermissionRule.PRIORITY)).all()
            
        except Exception as e:
            self.logger.error(f"Get rules by resource type error: {str(e)}")
            return []

    def get_rules_by_user_id(self, user_id: int, resource_type: str) -> List[DataPermissionRule]:
        """
        根据用户ID获取适用的数据权限规则
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            
        Returns:
            数据权限规则列表
        """
        try:
            user_id_str = str(user_id)
            
            return self.db.query(DataPermissionRule).filter(
                and_(
                    DataPermissionRule.RESOURCE_TYPE == resource_type,
                    DataPermissionRule.IS_ACTIVE == 1,
                    DataPermissionRule.is_deleted == 0,
                    or_(
                        DataPermissionRule.USER_IDS.like(f"%{user_id_str}%"),
                        DataPermissionRule.USER_IDS.is_(None)
                    )
                )
            ).order_by(desc(DataPermissionRule.PRIORITY)).all()
            
        except Exception as e:
            self.logger.error(f"Get rules by user id error: {str(e)}")
            return []

    def get_rules_by_role_ids(self, role_ids: List[int], resource_type: str) -> List[DataPermissionRule]:
        """
        根据角色ID列表获取适用的数据权限规则
        
        Args:
            role_ids: 角色ID列表
            resource_type: 资源类型
            
        Returns:
            数据权限规则列表
        """
        try:
            if not role_ids:
                return []
            
            role_conditions = []
            for role_id in role_ids:
                role_id_str = str(role_id)
                role_conditions.append(DataPermissionRule.ROLE_IDS.like(f"%{role_id_str}%"))
            
            return self.db.query(DataPermissionRule).filter(
                and_(
                    DataPermissionRule.RESOURCE_TYPE == resource_type,
                    DataPermissionRule.IS_ACTIVE == 1,
                    DataPermissionRule.is_deleted == 0,
                    or_(*role_conditions)
                )
            ).order_by(desc(DataPermissionRule.PRIORITY)).all()
            
        except Exception as e:
            self.logger.error(f"Get rules by role ids error: {str(e)}")
            return []

    def get_rules_by_dept_ids(self, dept_ids: List[int], resource_type: str) -> List[DataPermissionRule]:
        """
        根据部门ID列表获取适用的数据权限规则
        
        Args:
            dept_ids: 部门ID列表
            resource_type: 资源类型
            
        Returns:
            数据权限规则列表
        """
        try:
            if not dept_ids:
                return []
            
            dept_conditions = []
            for dept_id in dept_ids:
                dept_id_str = str(dept_id)
                dept_conditions.append(DataPermissionRule.DEPT_IDS.like(f"%{dept_id_str}%"))
            
            return self.db.query(DataPermissionRule).filter(
                and_(
                    DataPermissionRule.RESOURCE_TYPE == resource_type,
                    DataPermissionRule.IS_ACTIVE == 1,
                    DataPermissionRule.is_deleted == 0,
                    or_(*dept_conditions)
                )
            ).order_by(desc(DataPermissionRule.PRIORITY)).all()
            
        except Exception as e:
            self.logger.error(f"Get rules by dept ids error: {str(e)}")
            return []

    def get_user_applicable_rules(
        self, user_id: int, role_ids: List[int], dept_id: Optional[int], resource_type: str
    ) -> List[DataPermissionRule]:
        """
        获取用户适用的所有数据权限规则
        
        Args:
            user_id: 用户ID
            role_ids: 角色ID列表
            dept_id: 部门ID
            resource_type: 资源类型
            
        Returns:
            数据权限规则列表
        """
        try:
            conditions = []
            
            # 用户直接分配的规则
            user_id_str = str(user_id)
            conditions.append(DataPermissionRule.USER_IDS.like(f"%{user_id_str}%"))
            
            # 角色分配的规则
            if role_ids:
                for role_id in role_ids:
                    role_id_str = str(role_id)
                    conditions.append(DataPermissionRule.ROLE_IDS.like(f"%{role_id_str}%"))
            
            # 部门分配的规则
            if dept_id:
                dept_id_str = str(dept_id)
                conditions.append(DataPermissionRule.DEPT_IDS.like(f"%{dept_id_str}%"))
            
            if not conditions:
                return []
            
            return self.db.query(DataPermissionRule).filter(
                and_(
                    DataPermissionRule.RESOURCE_TYPE == resource_type,
                    DataPermissionRule.IS_ACTIVE == 1,
                    DataPermissionRule.is_deleted == 0,
                    or_(*conditions)
                )
            ).order_by(desc(DataPermissionRule.PRIORITY)).all()
            
        except Exception as e:
            self.logger.error(f"Get user applicable rules error: {str(e)}")
            return []

    def get_rule_by_code(self, rule_code: str) -> Optional[DataPermissionRule]:
        """
        根据规则代码获取数据权限规则
        
        Args:
            rule_code: 规则代码
            
        Returns:
            数据权限规则对象或None
        """
        try:
            return self.db.query(DataPermissionRule).filter(
                and_(
                    DataPermissionRule.RULE_CODE == rule_code,
                    DataPermissionRule.is_deleted == 0
                )
            ).first()
            
        except Exception as e:
            self.logger.error(f"Get rule by code error: {str(e)}")
            return None

    def update_rule_status(self, rule_id: int, is_active: int) -> bool:
        """
        更新规则状态
        
        Args:
            rule_id: 规则ID
            is_active: 是否激活
            
        Returns:
            是否更新成功
        """
        try:
            rule = self.get_by_id(rule_id)
            if not rule:
                return False
            
            rule.IS_ACTIVE = is_active
            self.update(rule)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Update rule status error: {str(e)}")
            return False

    def search_rules(self, filters: Dict[str, Any], page: int = 1, size: int = 20) -> tuple[List[DataPermissionRule], int]:
        """
        搜索数据权限规则
        
        Args:
            filters: 搜索条件字典
            page: 页码
            size: 每页大小
            
        Returns:
            数据权限规则列表和总数
        """
        try:
            query = self.db.query(DataPermissionRule).filter(DataPermissionRule.is_deleted == 0)
            
            # 规则名称过滤
            if filters.get('rule_name'):
                query = query.filter(DataPermissionRule.RULE_NAME.like(f"%{filters['rule_name']}%"))
            
            # 规则代码过滤
            if filters.get('rule_code'):
                query = query.filter(DataPermissionRule.RULE_CODE.like(f"%{filters['rule_code']}%"))
            
            # 资源类型过滤
            if filters.get('resource_type'):
                query = query.filter(DataPermissionRule.RESOURCE_TYPE == filters['resource_type'])
            
            # 权限类型过滤
            if filters.get('permission_type'):
                query = query.filter(DataPermissionRule.PERMISSION_TYPE == filters['permission_type'])
            
            # 状态过滤
            if filters.get('is_active') is not None:
                query = query.filter(DataPermissionRule.IS_ACTIVE == filters['is_active'])
            
            # 关键词搜索
            if filters.get('keyword'):
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    or_(
                        DataPermissionRule.RULE_NAME.like(keyword),
                        DataPermissionRule.RULE_CODE.like(keyword),
                        DataPermissionRule.description.like(keyword)
                    )
                )
            
            query = query.order_by(desc(DataPermissionRule.PRIORITY), desc(DataPermissionRule.created_at))
            
            total = query.count()
            rules = query.offset((page - 1) * size).limit(size).all()
            
            return rules, total
            
        except Exception as e:
            self.logger.error(f"Search rules error: {str(e)}")
            return [], 0

    def get_all_resource_types(self) -> List[str]:
        """
        获取所有资源类型
        
        Returns:
            资源类型列表
        """
        try:
            result = self.db.query(DataPermissionRule.RESOURCE_TYPE).filter(
                and_(
                    DataPermissionRule.IS_ACTIVE == 1,
                    DataPermissionRule.is_deleted == 0
                )
            ).distinct().all()
            
            return [row.RESOURCE_TYPE for row in result]
            
        except Exception as e:
            self.logger.error(f"Get all resource types error: {str(e)}")
            return []

    def get_all_permission_types(self) -> List[str]:
        """
        获取所有权限类型
        
        Returns:
            权限类型列表
        """
        try:
            result = self.db.query(DataPermissionRule.PERMISSION_TYPE).filter(
                and_(
                    DataPermissionRule.IS_ACTIVE == 1,
                    DataPermissionRule.is_deleted == 0
                )
            ).distinct().all()
            
            return [row.PERMISSION_TYPE for row in result]
            
        except Exception as e:
            self.logger.error(f"Get all permission types error: {str(e)}")
            return []