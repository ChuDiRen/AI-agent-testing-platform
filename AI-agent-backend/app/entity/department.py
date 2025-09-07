# Copyright (c) 2025 左岚. All rights reserved.
"""
部门实体
严格按照博客t_dept表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DOUBLE, DateTime, Boolean
from sqlalchemy.orm import relationship

from .base import BaseEntity


class Department(BaseEntity):
    """
    部门实体类 - 对应t_dept表
    用于存储部门信息，主要用于数据权限控制
    """
    __tablename__ = "department"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 使用Base类的id作为主键，没有别名

    # 上级部门ID - 必填，0表示顶级部门
    parent_id = Column(Integer, nullable=False, comment="上级部门ID")

    # 部门名称 - 必填，最大100个字符
    dept_name = Column(String(100), nullable=False, comment="部门名称")

    # 排序 - 可选，用于部门排序
    order_num = Column(DOUBLE(20), nullable=True, comment="排序")

    # 创建时间 - 可选，默认当前时间
    create_time = Column(DateTime, nullable=True, default=datetime.utcnow, comment="创建时间")

    # 修改时间 - 可选，更新时自动设置
    modify_time = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

    # 关联关系
    # 部门-用户关联（一个部门可以有多个用户）
    users = relationship("User", back_populates="department")

    def __init__(self, parent_id: int, dept_name: str, order_num: float = None):
        """
        初始化部门

        Args:
            parent_id: 上级部门ID，0表示顶级部门
            dept_name: 部门名称
            order_num: 排序号
        """
        self.parent_id = parent_id
        self.dept_name = dept_name
        self.order_num = order_num
        self.create_time = datetime.utcnow()

    def is_top_level(self) -> bool:
        """
        判断是否为顶级部门
        
        Returns:
            True表示顶级部门
        """
        return self.parent_id == 0

    def update_info(self, dept_name: str = None, order_num: float = None):
        """
        更新部门信息

        Args:
            dept_name: 部门名称
            order_num: 排序号
        """
        if dept_name is not None:
            self.dept_name = dept_name
        if order_num is not None:
            self.order_num = order_num
        self.modify_time = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            部门信息字典
        """
        return {
            "dept_id": self.id,
            "parent_id": self.parent_id,
            "dept_name": self.dept_name,
            "order_num": self.order_num,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "modify_time": self.modify_time.isoformat() if self.modify_time else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<Department(dept_id={self.id}, dept_name='{self.dept_name}')>"  # 修复：使用正确的属性名
