# Copyright (c) 2025 左岚. All rights reserved.
"""
权限缓存配置实体
管理权限缓存的配置和状态
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Index

from app.entity.base import BaseEntity


class PermissionCache(BaseEntity):
    """
    权限缓存配置表 - t_permission_cache
    管理权限缓存的配置信息和缓存状态
    """
    __tablename__ = "permission_cache"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 使用Base类的id作为主键，没有别名
    CACHE_KEY = Column(String(200), nullable=False, unique=True, comment="缓存键名")
    CACHE_TYPE = Column(String(50), nullable=False, comment="缓存类型(USER_PERMISSION/ROLE_PERMISSION/MENU_TREE)")
    CACHE_VALUE = Column(Text, nullable=True, comment="缓存值(JSON格式)")
    EXPIRE_TIME = Column(Integer, default=3600, comment="过期时间(秒)")
    LAST_UPDATE_TIME = Column(DateTime, default=datetime.utcnow, comment="最后更新时间")
    UPDATE_COUNT = Column(Integer, default=0, comment="更新次数")
    HIT_COUNT = Column(Integer, default=0, comment="命中次数")
    MISS_COUNT = Column(Integer, default=0, comment="未命中次数")
    IS_ACTIVE = Column(Integer, default=1, comment="是否启用(0:禁用,1:启用)")
    DESCRIPTION = Column(String(500), nullable=True, comment="缓存描述")

    # 创建索引以提高查询性能
    __table_args__ = (
        Index('idx_cache_key', 'CACHE_KEY'),
        Index('idx_cache_type', 'CACHE_TYPE'),
        Index('idx_cache_active', 'IS_ACTIVE'),
        Index('idx_cache_update_time', 'LAST_UPDATE_TIME'),
        {'comment': '权限缓存配置表'}
    )

    @classmethod
    def get_primary_key_name(cls) -> str:
        """获取主键字段名"""
        return "CACHE_ID"

    def get_primary_key_value(self):
        """获取主键值"""
        return self.CACHE_ID

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'cache_id': self.CACHE_ID,
            'cache_key': self.CACHE_KEY,
            'cache_type': self.CACHE_TYPE,
            'cache_value': self.CACHE_VALUE,
            'expire_time': self.EXPIRE_TIME,
            'last_update_time': self.LAST_UPDATE_TIME.isoformat() if self.LAST_UPDATE_TIME else None,
            'update_count': self.UPDATE_COUNT,
            'hit_count': self.HIT_COUNT,
            'miss_count': self.MISS_COUNT,
            'is_active': self.IS_ACTIVE,
            'description': self.DESCRIPTION
        }

    def increment_hit(self):
        """增加命中次数"""
        self.HIT_COUNT += 1

    def increment_miss(self):
        """增加未命中次数"""
        self.MISS_COUNT += 1

    def increment_update(self):
        """增加更新次数并更新时间"""
        self.UPDATE_COUNT += 1
        self.LAST_UPDATE_TIME = datetime.utcnow()

    def get_hit_rate(self) -> float:
        """计算命中率"""
        total = self.HIT_COUNT + self.MISS_COUNT
        if total == 0:
            return 0.0
        return round(self.HIT_COUNT / total * 100, 2)

    def __repr__(self) -> str:
        return f"<PermissionCache(CACHE_ID={self.CACHE_ID}, CACHE_KEY={self.CACHE_KEY}, CACHE_TYPE={self.CACHE_TYPE})>"


class DataPermissionRule(BaseEntity):
    """
    数据权限规则表 - t_data_permission_rule
    定义基于部门和角色的数据访问控制规则
    """
    __tablename__ = "data_permission_rule"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 使用Base类的id作为主键，RULE_ID作为别名
    @property
    def RULE_ID(self):
        return self.id
    RULE_NAME = Column(String(100), nullable=False, comment="规则名称")
    RULE_CODE = Column(String(50), nullable=False, unique=True, comment="规则代码")
    RESOURCE_TYPE = Column(String(50), nullable=False, comment="资源类型(USER/ROLE/DEPT/MENU)")
    PERMISSION_TYPE = Column(String(20), nullable=False, comment="权限类型(ALL/DEPT/SELF/CUSTOM)")
    RULE_EXPRESSION = Column(Text, nullable=True, comment="规则表达式(SQL WHERE条件)")
    DEPT_IDS = Column(String(500), nullable=True, comment="部门ID列表(逗号分隔)")
    ROLE_IDS = Column(String(500), nullable=True, comment="角色ID列表(逗号分隔)")
    USER_IDS = Column(String(500), nullable=True, comment="用户ID列表(逗号分隔)")
    IS_ACTIVE = Column(Integer, default=1, comment="是否启用(0:禁用,1:启用)")
    PRIORITY = Column(Integer, default=0, comment="优先级(数字越大优先级越高)")
    DESCRIPTION = Column(String(500), nullable=True, comment="规则描述")

    # 创建索引
    __table_args__ = (
        Index('idx_rule_code', 'RULE_CODE'),
        Index('idx_rule_resource_type', 'RESOURCE_TYPE'),
        Index('idx_rule_permission_type', 'PERMISSION_TYPE'),
        Index('idx_rule_active', 'IS_ACTIVE'),
        Index('idx_rule_priority', 'PRIORITY'),
        {'comment': '数据权限规则表'}
    )

    @classmethod
    def get_primary_key_name(cls) -> str:
        """获取主键字段名"""
        return "RULE_ID"

    def get_primary_key_value(self):
        """获取主键值"""
        return self.RULE_ID

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'rule_id': self.RULE_ID,
            'rule_name': self.RULE_NAME,
            'rule_code': self.RULE_CODE,
            'resource_type': self.RESOURCE_TYPE,
            'permission_type': self.PERMISSION_TYPE,
            'rule_expression': self.RULE_EXPRESSION,
            'dept_ids': self.DEPT_IDS.split(',') if self.DEPT_IDS else [],
            'role_ids': self.ROLE_IDS.split(',') if self.ROLE_IDS else [],
            'user_ids': self.USER_IDS.split(',') if self.USER_IDS else [],
            'is_active': self.IS_ACTIVE,
            'priority': self.PRIORITY,
            'description': self.DESCRIPTION
        }

    def __repr__(self) -> str:
        return f"<DataPermissionRule(RULE_ID={self.RULE_ID}, RULE_CODE={self.RULE_CODE}, RESOURCE_TYPE={self.RESOURCE_TYPE})>"