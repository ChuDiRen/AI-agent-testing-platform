"""
数据权限Service
提供数据权限规则的业务逻辑处理
"""

from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.entity.permission_cache import DataPermissionRule
from app.repository.data_permission_repository import DataPermissionRepository
from app.service.base import BaseService
from app.service.user_service import RBACUserService

logger = get_logger(__name__)


class DataPermissionService(BaseService):
    """
    数据权限Service
    提供数据权限规则的业务逻辑处理
    """

    def __init__(self, db: Session):
        self.db = db  # 添加db属性
        self.data_permission_repo = DataPermissionRepository(db)
        super().__init__(self.data_permission_repo)  # 传递repository给BaseService
        self.user_service = RBACUserService(db)
        self.logger = get_logger(self.__class__.__name__)
    
    def _create_entity_from_data(self, data: Dict[str, Any]) -> DataPermissionRule:
        """
        从数据字典创建数据权限规则实体
        
        Args:
            data: 数据字典
            
        Returns:
            数据权限规则实体
        """
        return DataPermissionRule(**data)

    def create_data_permission_rule(
        self, rule_name: str, rule_code: str, resource_type: str,
        permission_type: str, rule_expression: Optional[str] = None,
        dept_ids: Optional[List[int]] = None, role_ids: Optional[List[int]] = None,
        user_ids: Optional[List[int]] = None, priority: int = 0,
        description: Optional[str] = None
    ) -> Optional[DataPermissionRule]:
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
            # 验证规则代码唯一性
            existing_rule = self.data_permission_repo.get_rule_by_code(rule_code)
            if existing_rule:
                raise ValueError(f"规则代码 {rule_code} 已存在")
            
            # 验证权限类型
            valid_permission_types = ["ALL", "DEPT", "SELF", "CUSTOM"]
            if permission_type not in valid_permission_types:
                raise ValueError(f"无效的权限类型: {permission_type}")
            
            # 转换ID列表为字符串
            dept_ids_str = ",".join(map(str, dept_ids)) if dept_ids else None
            role_ids_str = ",".join(map(str, role_ids)) if role_ids else None
            user_ids_str = ",".join(map(str, user_ids)) if user_ids else None
            
            rule = self.data_permission_repo.create_data_permission_rule(
                rule_name=rule_name,
                rule_code=rule_code,
                resource_type=resource_type,
                permission_type=permission_type,
                rule_expression=rule_expression,
                dept_ids=dept_ids_str,
                role_ids=role_ids_str,
                user_ids=user_ids_str,
                priority=priority,
                description=description
            )
            
            self.logger.info(f"Created data permission rule: {rule_code}")
            return rule
            
        except Exception as e:
            self.logger.error(f"Create data permission rule error: {str(e)}")
            raise

    def update_data_permission_rule(
        self, rule_id: int, rule_name: Optional[str] = None,
        rule_expression: Optional[str] = None, dept_ids: Optional[List[int]] = None,
        role_ids: Optional[List[int]] = None, user_ids: Optional[List[int]] = None,
        priority: Optional[int] = None, description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[DataPermissionRule]:
        """
        更新数据权限规则
        
        Args:
            rule_id: 规则ID
            rule_name: 规则名称
            rule_expression: 规则表达式
            dept_ids: 部门ID列表
            role_ids: 角色ID列表
            user_ids: 用户ID列表
            priority: 优先级
            description: 描述
            is_active: 是否激活
            
        Returns:
            更新后的数据权限规则对象
        """
        try:
            rule = self.data_permission_repo.get_by_id(rule_id)
            if not rule:
                raise ValueError(f"数据权限规则不存在: {rule_id}")
            
            # 更新字段
            if rule_name is not None:
                rule.RULE_NAME = rule_name
            
            if rule_expression is not None:
                rule.RULE_EXPRESSION = rule_expression
            
            if dept_ids is not None:
                rule.DEPT_IDS = ",".join(map(str, dept_ids)) if dept_ids else None
            
            if role_ids is not None:
                rule.ROLE_IDS = ",".join(map(str, role_ids)) if role_ids else None
            
            if user_ids is not None:
                rule.USER_IDS = ",".join(map(str, user_ids)) if user_ids else None
            
            if priority is not None:
                rule.PRIORITY = priority
            
            if description is not None:
                rule.description = description
            
            if is_active is not None:
                rule.IS_ACTIVE = 1 if is_active else 0
            
            updated_rule = self.data_permission_repo.update(rule)
            
            self.logger.info(f"Updated data permission rule: {rule.RULE_CODE}")
            return updated_rule
            
        except Exception as e:
            self.logger.error(f"Update data permission rule error: {str(e)}")
            raise

    def delete_data_permission_rule(self, rule_id: int) -> bool:
        """
        删除数据权限规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            是否删除成功
        """
        try:
            rule = self.data_permission_repo.get_by_id(rule_id)
            if not rule:
                return False
            
            self.data_permission_repo.delete(rule_id)
            
            self.logger.info(f"Deleted data permission rule: {rule.RULE_CODE}")
            return True
            
        except Exception as e:
            self.logger.error(f"Delete data permission rule error: {str(e)}")
            return False

    def get_user_data_permission_rules(
        self, user_id: int, resource_type: str
    ) -> List[DataPermissionRule]:
        """
        获取用户适用的数据权限规则
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            
        Returns:
            数据权限规则列表
        """
        try:
            # 获取用户信息
            user = self.user_service.get_user_by_id(user_id)
            if not user:
                return []
            
            # 获取用户角色
            user_roles = self.user_service.get_user_roles(user_id)
            role_ids = [role.role_id for role in user_roles]
            
            # 获取适用的规则
            rules = self.data_permission_repo.get_user_applicable_rules(
                user_id=user_id,
                role_ids=role_ids,
                dept_id=user.dept_id,
                resource_type=resource_type
            )
            
            return rules
            
        except Exception as e:
            self.logger.error(f"Get user data permission rules error: {str(e)}")
            return []

    def check_user_data_permission(
        self, user_id: int, resource_type: str, resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        检查用户数据权限
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            
        Returns:
            权限检查结果
        """
        try:
            rules = self.get_user_data_permission_rules(user_id, resource_type)
            
            if not rules:
                return {
                    'has_permission': False,
                    'permission_type': 'NONE',
                    'message': '无数据权限规则'
                }
            
            # 按优先级排序，取最高优先级的规则
            sorted_rules = sorted(rules, key=lambda x: x.PRIORITY, reverse=True)
            highest_rule = sorted_rules[0]
            
            result = {
                'has_permission': True,
                'permission_type': highest_rule.PERMISSION_TYPE,
                'rule_code': highest_rule.RULE_CODE,
                'rule_name': highest_rule.RULE_NAME,
                'message': f'适用规则: {highest_rule.RULE_NAME}'
            }
            
            # 根据权限类型添加额外信息
            if highest_rule.PERMISSION_TYPE == "ALL":
                result['scope'] = 'all_data'
                result['message'] = '拥有全部数据权限'
            elif highest_rule.PERMISSION_TYPE == "DEPT":
                result['scope'] = 'department_data'
                result['dept_ids'] = highest_rule.DEPT_IDS.split(',') if highest_rule.DEPT_IDS else []
                result['message'] = '拥有部门数据权限'
            elif highest_rule.PERMISSION_TYPE == "SELF":
                result['scope'] = 'self_data'
                result['message'] = '仅拥有个人数据权限'
            elif highest_rule.PERMISSION_TYPE == "CUSTOM":
                result['scope'] = 'custom_data'
                result['rule_expression'] = highest_rule.RULE_EXPRESSION
                result['message'] = '拥有自定义数据权限'
            
            return result
            
        except Exception as e:
            self.logger.error(f"Check user data permission error: {str(e)}")
            return {
                'has_permission': False,
                'permission_type': 'ERROR',
                'message': f'权限检查失败: {str(e)}'
            }

    def get_data_filter_conditions(
        self, user_id: int, resource_type: str
    ) -> Dict[str, Any]:
        """
        获取数据过滤条件
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            
        Returns:
            过滤条件字典
        """
        try:
            rules = self.get_user_data_permission_rules(user_id, resource_type)
            
            if not rules:
                return {'type': 'NONE', 'conditions': []}
            
            # 按优先级排序
            sorted_rules = sorted(rules, key=lambda x: x.PRIORITY, reverse=True)
            
            filter_conditions = []
            
            for rule in sorted_rules:
                if rule.PERMISSION_TYPE == "ALL":
                    # 全部数据权限，不需要过滤条件
                    return {'type': 'ALL', 'conditions': []}
                
                elif rule.PERMISSION_TYPE == "DEPT":
                    # 部门数据权限
                    if rule.DEPT_IDS:
                        dept_ids = [int(id.strip()) for id in rule.DEPT_IDS.split(',') if id.strip()]
                        filter_conditions.append({
                            'type': 'DEPT',
                            'field': 'DEPT_ID',
                            'operator': 'IN',
                            'values': dept_ids
                        })
                
                elif rule.PERMISSION_TYPE == "SELF":
                    # 个人数据权限
                    filter_conditions.append({
                        'type': 'SELF',
                        'field': 'USER_ID',
                        'operator': 'EQ',
                        'values': [user_id]
                    })
                
                elif rule.PERMISSION_TYPE == "CUSTOM":
                    # 自定义权限表达式
                    if rule.RULE_EXPRESSION:
                        filter_conditions.append({
                            'type': 'CUSTOM',
                            'expression': rule.RULE_EXPRESSION
                        })
            
            return {
                'type': 'FILTERED',
                'conditions': filter_conditions,
                'logic': 'OR'  # 多个条件之间使用OR逻辑
            }
            
        except Exception as e:
            self.logger.error(f"Get data filter conditions error: {str(e)}")
            return {'type': 'ERROR', 'conditions': []}

    def search_data_permission_rules(
        self, filters: Dict[str, Any], page: int = 1, size: int = 20
    ) -> tuple[List[Dict], int]:
        """
        搜索数据权限规则
        
        Args:
            filters: 搜索条件
            page: 页码
            size: 每页大小
            
        Returns:
            规则列表和总数
        """
        try:
            rules, total = self.data_permission_repo.search_rules(filters, page, size)
            
            rule_dicts = []
            for rule in rules:
                rule_dict = rule.to_dict()
                rule_dicts.append(rule_dict)
            
            return rule_dicts, total
            
        except Exception as e:
            self.logger.error(f"Search data permission rules error: {str(e)}")
            return [], 0

    def get_resource_types(self) -> List[str]:
        """
        获取所有资源类型
        
        Returns:
            资源类型列表
        """
        try:
            return self.data_permission_repo.get_all_resource_types()
            
        except Exception as e:
            self.logger.error(f"Get resource types error: {str(e)}")
            return []

    def get_permission_types(self) -> List[str]:
        """
        获取所有权限类型
        
        Returns:
            权限类型列表
        """
        try:
            return self.data_permission_repo.get_all_permission_types()
            
        except Exception as e:
            self.logger.error(f"Get permission types error: {str(e)}")
            return []

    def validate_rule_expression(self, expression: str, resource_type: str) -> Dict[str, Any]:
        """
        验证规则表达式
        
        Args:
            expression: 规则表达式
            resource_type: 资源类型
            
        Returns:
            验证结果
        """
        try:
            # 基本的SQL注入检查
            dangerous_keywords = [
                'DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER',
                'EXEC', 'EXECUTE', 'UNION', 'SCRIPT', '--', '/*', '*/'
            ]
            
            expression_upper = expression.upper()
            for keyword in dangerous_keywords:
                if keyword in expression_upper:
                    return {
                        'valid': False,
                        'message': f'表达式包含危险关键词: {keyword}'
                    }
            
            # 检查表达式格式
            if not expression.strip():
                return {
                    'valid': False,
                    'message': '表达式不能为空'
                }
            
            # 简单的语法检查
            if expression.count('(') != expression.count(')'):
                return {
                    'valid': False,
                    'message': '括号不匹配'
                }
            
            return {
                'valid': True,
                'message': '表达式验证通过'
            }
            
        except Exception as e:
            self.logger.error(f"Validate rule expression error: {str(e)}")
            return {
                'valid': False,
                'message': f'表达式验证失败: {str(e)}'
            }

    def get_rule_statistics(self) -> Dict[str, Any]:
        """
        获取规则统计信息
        
        Returns:
            统计信息
        """
        try:
            # 获取所有规则
            all_rules, _ = self.data_permission_repo.search_rules({}, page=1, size=1000)
            
            # 按资源类型统计
            resource_type_stats = {}
            permission_type_stats = {}
            active_count = 0
            inactive_count = 0
            
            for rule in all_rules:
                # 资源类型统计
                resource_type = rule.RESOURCE_TYPE
                resource_type_stats[resource_type] = resource_type_stats.get(resource_type, 0) + 1
                
                # 权限类型统计
                permission_type = rule.PERMISSION_TYPE
                permission_type_stats[permission_type] = permission_type_stats.get(permission_type, 0) + 1
                
                # 状态统计
                if rule.IS_ACTIVE == 1:
                    active_count += 1
                else:
                    inactive_count += 1
            
            return {
                'total_rules': len(all_rules),
                'active_rules': active_count,
                'inactive_rules': inactive_count,
                'resource_type_stats': [
                    {'type': k, 'count': v} for k, v in resource_type_stats.items()
                ],
                'permission_type_stats': [
                    {'type': k, 'count': v} for k, v in permission_type_stats.items()
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Get rule statistics error: {str(e)}")
            return {}

    def batch_update_rule_status(self, rule_ids: List[int], is_active: bool) -> int:
        """
        批量更新规则状态
        
        Args:
            rule_ids: 规则ID列表
            is_active: 是否激活
            
        Returns:
            更新成功的数量
        """
        try:
            success_count = 0
            
            for rule_id in rule_ids:
                if self.data_permission_repo.update_rule_status(rule_id, 1 if is_active else 0):
                    success_count += 1
            
            self.logger.info(f"Batch updated {success_count} rules status to {is_active}")
            return success_count
            
        except Exception as e:
            self.logger.error(f"Batch update rule status error: {str(e)}")
            return 0
