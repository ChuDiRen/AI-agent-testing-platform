# Copyright (c) 2025 左岚. All rights reserved.
"""
部门实体
严格按照博客t_dept表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, DOUBLE, DateTime
from sqlalchemy.orm import relationship

from .rbac_base import RBACBase


class Department(RBACBase):
    """
    部门实体类 - 对应t_dept表
    用于存储部门信息，主要用于数据权限控制
    """
    __tablename__ = "t_dept"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 部门ID - 主键，自增
    DEPT_ID = Column(Integer, primary_key=True, comment="部门ID")

    # 上级部门ID - 必填，0表示顶级部门
    PARENT_ID = Column(Integer, nullable=False, comment="上级部门ID")
    
    # 部门名称 - 必填，最大100个字符
    DEPT_NAME = Column(String(100), nullable=False, comment="部门名称")
    
    # 排序 - 可选，用于部门排序
    ORDER_NUM = Column(DOUBLE(20), nullable=True, comment="排序")
    
    # 创建时间 - 可选，默认当前时间
    CREATE_TIME = Column(DateTime, nullable=True, default=datetime.utcnow, comment="创建时间")
    
    # 修改时间 - 可选，更新时自动设置
    MODIFY_TIME = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

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
        self.PARENT_ID = parent_id
        self.DEPT_NAME = dept_name
        self.ORDER_NUM = order_num
        self.CREATE_TIME = datetime.utcnow()

    def is_top_level(self) -> bool:
        """
        判断是否为顶级部门
        
        Returns:
            True表示顶级部门
        """
        return self.PARENT_ID == 0

    def update_info(self, dept_name: str = None, order_num: float = None):
        """
        更新部门信息
        
        Args:
            dept_name: 部门名称
            order_num: 排序号
        """
        if dept_name is not None:
            self.DEPT_NAME = dept_name
        if order_num is not None:
            self.ORDER_NUM = order_num
        self.MODIFY_TIME = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            部门信息字典
        """
        return {
            "DEPT_ID": self.DEPT_ID,
            "PARENT_ID": self.PARENT_ID,
            "DEPT_NAME": self.DEPT_NAME,
            "ORDER_NUM": self.ORDER_NUM,
            "CREATE_TIME": self.CREATE_TIME.isoformat() if self.CREATE_TIME else None,
            "MODIFY_TIME": self.MODIFY_TIME.isoformat() if self.MODIFY_TIME else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<Department(DEPT_ID={self.DEPT_ID}, DEPT_NAME='{self.DEPT_NAME}')>"
