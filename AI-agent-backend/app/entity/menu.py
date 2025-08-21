# Copyright (c) 2025 左岚. All rights reserved.
"""
菜单实体
严格按照博客t_menu表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, CHAR, DOUBLE, DateTime
from sqlalchemy.orm import relationship

from .rbac_base import RBACBase


class Menu(RBACBase):
    """
    菜单实体类 - 对应t_menu表
    用于存储菜单、按钮及其对应的权限标识
    """
    __tablename__ = "t_menu"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 菜单/按钮ID - 主键，自增
    MENU_ID = Column(Integer, primary_key=True, comment="菜单/按钮ID")

    # 上级菜单ID - 必填，0表示顶级菜单
    PARENT_ID = Column(Integer, nullable=False, comment="上级菜单ID")
    
    # 菜单/按钮名称 - 必填，最大50个字符
    MENU_NAME = Column(String(50), nullable=False, comment="菜单/按钮名称")
    
    # 对应路由path - 可选，最大255个字符
    PATH = Column(String(255), nullable=True, comment="对应路由path")
    
    # 对应路由组件component - 可选，最大255个字符
    COMPONENT = Column(String(255), nullable=True, comment="对应路由组件component")
    
    # 权限标识 - 可选，最大50个字符，如：user:view, user:add
    PERMS = Column(String(50), nullable=True, comment="权限标识")
    
    # 图标 - 可选，最大50个字符
    ICON = Column(String(50), nullable=True, comment="图标")
    
    # 类型 - 必填，2个字符，0菜单 1按钮
    TYPE = Column(CHAR(2), nullable=False, comment="类型 0菜单 1按钮")
    
    # 排序 - 可选，用于菜单排序
    ORDER_NUM = Column(DOUBLE(20), nullable=True, comment="排序")
    
    # 创建时间 - 必填，默认当前时间
    CREATE_TIME = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")
    
    # 修改时间 - 可选，更新时自动设置
    MODIFY_TIME = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

    # 关联关系
    # 菜单-角色关联（一个菜单可以分配给多个角色）
    role_menus = relationship("RoleMenu", back_populates="menu")

    def __init__(self, parent_id: int, menu_name: str, menu_type: str, 
                 path: str = None, component: str = None, perms: str = None, 
                 icon: str = None, order_num: float = None):
        """
        初始化菜单
        
        Args:
            parent_id: 上级菜单ID，0表示顶级菜单
            menu_name: 菜单/按钮名称
            menu_type: 类型，'0'菜单 '1'按钮
            path: 路由路径
            component: 路由组件
            perms: 权限标识
            icon: 图标
            order_num: 排序号
        """
        self.PARENT_ID = parent_id
        self.MENU_NAME = menu_name
        self.TYPE = menu_type
        self.PATH = path
        self.COMPONENT = component
        self.PERMS = perms
        self.ICON = icon
        self.ORDER_NUM = order_num
        self.CREATE_TIME = datetime.utcnow()

    def is_menu(self) -> bool:
        """
        判断是否为菜单
        
        Returns:
            True表示菜单，False表示按钮
        """
        return self.TYPE == '0'

    def is_button(self) -> bool:
        """
        判断是否为按钮
        
        Returns:
            True表示按钮，False表示菜单
        """
        return self.TYPE == '1'

    def is_top_level(self) -> bool:
        """
        判断是否为顶级菜单
        
        Returns:
            True表示顶级菜单
        """
        return self.PARENT_ID == 0

    def update_info(self, menu_name: str = None, path: str = None, 
                   component: str = None, perms: str = None, 
                   icon: str = None, order_num: float = None):
        """
        更新菜单信息
        
        Args:
            menu_name: 菜单名称
            path: 路由路径
            component: 路由组件
            perms: 权限标识
            icon: 图标
            order_num: 排序号
        """
        if menu_name is not None:
            self.MENU_NAME = menu_name
        if path is not None:
            self.PATH = path
        if component is not None:
            self.COMPONENT = component
        if perms is not None:
            self.PERMS = perms
        if icon is not None:
            self.ICON = icon
        if order_num is not None:
            self.ORDER_NUM = order_num
        self.MODIFY_TIME = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式
        
        Returns:
            菜单信息字典
        """
        return {
            "MENU_ID": self.MENU_ID,
            "PARENT_ID": self.PARENT_ID,
            "MENU_NAME": self.MENU_NAME,
            "PATH": self.PATH,
            "COMPONENT": self.COMPONENT,
            "PERMS": self.PERMS,
            "ICON": self.ICON,
            "TYPE": self.TYPE,
            "ORDER_NUM": self.ORDER_NUM,
            "CREATE_TIME": self.CREATE_TIME.isoformat() if self.CREATE_TIME else None,
            "MODIFY_TIME": self.MODIFY_TIME.isoformat() if self.MODIFY_TIME else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<Menu(MENU_ID={self.MENU_ID}, MENU_NAME='{self.MENU_NAME}', TYPE='{self.TYPE}')>"
