"""
菜单实体
严格按照博客t_menu表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, CHAR, DOUBLE, DateTime, Boolean
from sqlalchemy.orm import relationship

from .base import BaseEntity


class Menu(BaseEntity):
    """
    菜单实体类 - 对应t_menu表
    用于存储菜单、按钮及其对应的权限标识
    """
    __tablename__ = "menu"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 使用Base类的id作为主键，对应博客中的menu_id

    # 上级菜单ID - 必填，0表示顶级菜单
    parent_id = Column(Integer, nullable=False, comment="上级菜单ID")

    # 菜单/按钮名称 - 必填，最大50个字符
    menu_name = Column(String(50), nullable=False, comment="菜单/按钮名称")

    # 对应路由path - 可选，最大255个字符
    path = Column(String(255), nullable=True, comment="对应路由path")

    # 对应路由组件component - 可选，最大255个字符
    component = Column(String(255), nullable=True, comment="对应路由组件component")

    # 权限标识 - 可选，最大50个字符，如：user:view, user:add
    perms = Column(String(50), nullable=True, comment="权限标识")

    # 图标 - 可选，最大50个字符
    icon = Column(String(50), nullable=True, comment="图标")

    # 类型 - 必填，2个字符，0菜单 1按钮
    menu_type = Column(CHAR(2), nullable=False, comment="类型 0菜单 1按钮")

    # 排序 - 可选，用于菜单排序
    order_num = Column(DOUBLE(20), nullable=True, comment="排序")

    # 是否启用 - 必填，默认启用
    is_active = Column(Boolean, nullable=False, default=True, comment="是否启用")

    # 创建时间 - 必填，默认当前时间
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")

    # 修改时间 - 可选，更新时自动设置
    modify_time = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

    # 关联关系
    # 菜单-角色关联（一个菜单可以分配给多个角色）
    role_menus = relationship("RoleMenu", back_populates="menu")

    def __init__(self, parent_id: int, menu_name: str, menu_type: str,
                 path: str = None, component: str = None, perms: str = None,
                 icon: str = None, order_num: float = None, is_active: bool = True):
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
            is_active: 是否启用
        """
        self.parent_id = parent_id
        self.menu_name = menu_name
        self.menu_type = menu_type
        self.path = path
        self.component = component
        self.perms = perms
        self.icon = icon
        self.order_num = order_num
        self.is_active = is_active
        self.create_time = datetime.utcnow()

    def is_menu(self) -> bool:
        """
        判断是否为菜单

        Returns:
            True表示菜单，False表示按钮
        """
        return self.menu_type == '0'

    def is_button(self) -> bool:
        """
        判断是否为按钮

        Returns:
            True表示按钮，False表示菜单
        """
        return self.menu_type == '1'

    def is_top_level(self) -> bool:
        """
        判断是否为顶级菜单

        Returns:
            True表示顶级菜单
        """
        return self.parent_id == 0

    def update_info(self, menu_name: str = None, path: str = None,
                   component: str = None, perms: str = None,
                   icon: str = None, order_num: float = None, is_active: bool = None):
        """
        更新菜单信息

        Args:
            menu_name: 菜单名称
            path: 路由路径
            component: 路由组件
            perms: 权限标识
            icon: 图标
            order_num: 排序号
            is_active: 是否启用
        """
        if menu_name is not None:
            self.menu_name = menu_name
        if path is not None:
            self.path = path
        if component is not None:
            self.component = component
        if perms is not None:
            self.perms = perms
        if icon is not None:
            self.icon = icon
        if order_num is not None:
            self.order_num = order_num
        if is_active is not None:
            self.is_active = is_active
        self.modify_time = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            菜单信息字典
        """
        return {
            "menu_id": self.id,  # 对应博客中的menu_id主键
            "parent_id": self.parent_id,
            "menu_name": self.menu_name,
            "path": self.path,
            "component": self.component,
            "perms": self.perms,
            "icon": self.icon,
            "menu_type": self.menu_type,
            "order_num": self.order_num,
            "is_active": self.is_active,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "modify_time": self.modify_time.isoformat() if self.modify_time else None
        }

    def __repr__(self):
        """
        字符串表示
        """
        return f"<Menu(menu_id={self.id}, menu_name='{self.menu_name}', menu_type='{self.menu_type}')>"
