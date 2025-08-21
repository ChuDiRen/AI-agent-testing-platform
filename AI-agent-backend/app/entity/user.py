# Copyright (c) 2025 左岚. All rights reserved.
"""
用户实体
严格按照博客t_user表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, CHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .rbac_base import RBACBase


class User(RBACBase):
    """
    用户实体类 - 对应t_user表
    定义用户的基本信息和行为
    """
    __tablename__ = "users"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 用户ID - 主键，自增
    USER_ID = Column(Integer, primary_key=True, comment="用户ID")

    # 用户名 - 必填，最大50个字符，唯一
    USERNAME = Column(String(50), nullable=False, unique=True, index=True, comment="用户名")

    # 密码 - 必填，最大128个字符，加密存储
    PASSWORD = Column(String(128), nullable=False, comment="密码")

    # 部门ID - 可选，关联部门表
    DEPT_ID = Column(Integer, ForeignKey('t_dept.DEPT_ID'), nullable=True, comment="部门ID")

    # 邮箱 - 可选，最大128个字符
    EMAIL = Column(String(128), nullable=True, comment="邮箱")

    # 联系电话 - 可选，最大20个字符
    MOBILE = Column(String(20), nullable=True, comment="联系电话")

    # 状态 - 必填，1个字符，0锁定 1有效
    STATUS = Column(CHAR(1), nullable=False, default='1', comment="状态 0锁定 1有效")

    # 创建时间 - 必填，默认当前时间
    CREATE_TIME = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")

    # 修改时间 - 可选，更新时自动设置
    MODIFY_TIME = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

    # 最近访问时间 - 可选
    LAST_LOGIN_TIME = Column(DateTime, nullable=True, comment="最近访问时间")

    # 性别 - 可选，1个字符，0男 1女 2保密
    SSEX = Column(CHAR(1), nullable=True, comment="性别 0男 1女 2保密")

    # 头像 - 可选，最大100个字符
    AVATAR = Column(String(100), nullable=True, comment="头像")

    # 描述 - 可选，最大100个字符
    DESCRIPTION = Column(String(100), nullable=True, comment="描述")

    # 关联关系
    # 用户-角色关联（一个用户可以有多个角色）
    user_roles = relationship("UserRole", back_populates="user")

    # 用户-部门关联（一个用户属于一个部门）
    department = relationship("Department", back_populates="users")

    def __init__(self, username: str, password: str, email: str = None,
                 mobile: str = None, dept_id: int = None, ssex: str = None,
                 avatar: str = None, description: str = None):
        """
        初始化用户

        Args:
            username: 用户名
            password: 加密后的密码
            email: 邮箱
            mobile: 手机号
            dept_id: 部门ID
            ssex: 性别，'0'男 '1'女 '2'保密
            avatar: 头像
            description: 描述
        """
        self.USERNAME = username
        self.PASSWORD = password
        self.EMAIL = email
        self.MOBILE = mobile
        self.DEPT_ID = dept_id
        self.SSEX = ssex
        self.AVATAR = avatar
        self.DESCRIPTION = description
        self.STATUS = '1'  # 默认有效状态
        self.CREATE_TIME = datetime.utcnow()

    def is_active(self) -> bool:
        """
        判断用户是否有效

        Returns:
            True表示有效，False表示锁定
        """
        return self.STATUS == '1'

    def is_locked(self) -> bool:
        """
        判断用户是否被锁定

        Returns:
            True表示锁定，False表示有效
        """
        return self.STATUS == '0'

    def lock_user(self):
        """
        锁定用户
        """
        self.STATUS = '0'
        self.MODIFY_TIME = datetime.utcnow()

    def unlock_user(self):
        """
        解锁用户
        """
        self.STATUS = '1'
        self.MODIFY_TIME = datetime.utcnow()

    def update_last_login(self):
        """
        更新最后登录时间
        """
        self.LAST_LOGIN_TIME = datetime.utcnow()

    def change_password(self, new_password: str):
        """
        修改密码

        Args:
            new_password: 新的加密密码
        """
        self.PASSWORD = new_password
        self.MODIFY_TIME = datetime.utcnow()

    def update_info(self, email: str = None, mobile: str = None,
                   ssex: str = None, avatar: str = None, description: str = None):
        """
        更新用户信息

        Args:
            email: 邮箱
            mobile: 手机号
            ssex: 性别
            avatar: 头像
            description: 描述
        """
        if email is not None:
            self.EMAIL = email
        if mobile is not None:
            self.MOBILE = mobile
        if ssex is not None:
            self.SSEX = ssex
        if avatar is not None:
            self.AVATAR = avatar
        if description is not None:
            self.DESCRIPTION = description
        self.MODIFY_TIME = datetime.utcnow()

    def get_gender_display(self) -> str:
        """
        获取性别显示文本

        Returns:
            性别显示文本
        """
        gender_map = {'0': '男', '1': '女', '2': '保密'}
        return gender_map.get(self.SSEX, '未知')

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            用户信息字典
        """
        return {
            "USER_ID": self.USER_ID,
            "USERNAME": self.USERNAME,
            "DEPT_ID": self.DEPT_ID,
            "EMAIL": self.EMAIL,
            "MOBILE": self.MOBILE,
            "STATUS": self.STATUS,
            "CREATE_TIME": self.CREATE_TIME.isoformat() if self.CREATE_TIME else None,
            "MODIFY_TIME": self.MODIFY_TIME.isoformat() if self.MODIFY_TIME else None,
            "LAST_LOGIN_TIME": self.LAST_LOGIN_TIME.isoformat() if self.LAST_LOGIN_TIME else None,
            "SSEX": self.SSEX,
            "AVATAR": self.AVATAR,
            "DESCRIPTION": self.DESCRIPTION
        }

    def to_dict_safe(self) -> dict:
        """
        安全的字典转换（不包含密码）

        Returns:
            不包含密码的用户信息字典
        """
        data = self.to_dict()
        # 不包含密码字段
        return data

    def __repr__(self):
        """
        字符串表示
        """
        return f"<User(USER_ID={self.USER_ID}, USERNAME='{self.USERNAME}', STATUS='{self.STATUS}')>"
