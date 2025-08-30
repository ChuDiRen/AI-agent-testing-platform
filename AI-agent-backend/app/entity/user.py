# Copyright (c) 2025 左岚. All rights reserved.
"""
用户实体
严格按照博客t_user表结构设计
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, CHAR, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseEntity


class User(BaseEntity):
    """
    用户实体类 - 对应t_user表
    定义用户的基本信息和行为
    """
    __tablename__ = "user"
    __allow_unmapped__ = True  # 允许未映射的注解

    # 使用Base类的id作为主键，没有别名

    # 用户名 - 必填，最大50个字符，唯一
    username = Column(String(50), nullable=False, unique=True, index=True, comment="用户名")

    # 密码 - 必填，最大128个字符，加密存储
    password = Column(String(128), nullable=False, comment="密码")

    # 部门ID - 可选，关联部门表
    dept_id = Column(Integer, ForeignKey('department.id'), nullable=True, comment="部门ID")

    # 邮箱 - 可选，最大128个字符
    email = Column(String(128), nullable=True, comment="邮箱")

    # 联系电话 - 可选，最大20个字符
    mobile = Column(String(20), nullable=True, comment="联系电话")

    # 状态 - 必填，1个字符，1启用 0禁用
    status = Column(CHAR(1), nullable=False, default='1', comment="状态 1启用 0禁用")

    # 创建时间 - 必填，默认当前时间
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow, comment="创建时间")

    # 修改时间 - 可选，更新时自动设置
    modify_time = Column(DateTime, nullable=True, onupdate=datetime.utcnow, comment="修改时间")

    # 最近访问时间 - 可选
    last_login_time = Column(DateTime, nullable=True, comment="最近访问时间")

    # 性别 - 可选，1个字符，0男 1女 2保密
    ssex = Column(CHAR(1), nullable=True, comment="性别 0男 1女 2保密")

    # 头像 - 可选，最大100个字符
    avatar = Column(String(100), nullable=True, comment="头像")

    # 描述 - 可选，最大100个字符
    description = Column(String(100), nullable=True, comment="描述")

    # 关联关系
    # 用户-角色关联（一个用户可以有多个角色）
    user_roles = relationship("UserRole", back_populates="user")

    # 用户-部门关联（一个用户属于一个部门）
    department = relationship("Department", back_populates="users")

    @property
    def user_id(self) -> int:
        """用户ID属性，返回主键id的值"""
        return self.id

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
        self.username = username
        self.password = password
        self.email = email
        self.mobile = mobile
        self.dept_id = dept_id
        self.ssex = ssex
        self.avatar = avatar
        self.description = description
        self.status = '1'  # 默认有效状态
        self.create_time = datetime.utcnow()

    def is_active(self) -> bool:
        """
        判断用户是否有效

        Returns:
            True表示有效，False表示锁定
        """
        return self.status == '1'

    def is_locked(self) -> bool:
        """
        判断用户是否被锁定

        Returns:
            True表示锁定，False表示有效
        """
        return self.status == '0'

    def lock_user(self):
        """
        锁定用户
        """
        self.status = '0'
        self.modify_time = datetime.utcnow()

    def unlock_user(self):
        """
        解锁用户
        """
        self.status = '1'
        self.modify_time = datetime.utcnow()

    def update_last_login(self):
        """
        更新最后登录时间
        """
        self.last_login_time = datetime.utcnow()

    def change_password(self, new_password: str):
        """
        修改密码

        Args:
            new_password: 新的加密密码
        """
        self.password = new_password
        self.modify_time = datetime.utcnow()

    def update_info(self, username: str = None, email: str = None, mobile: str = None,
                   dept_id: int = None, status: str = None, ssex: str = None, avatar: str = None, description: str = None):
        """
        更新用户信息

        Args:
            username: 用户名
            email: 邮箱
            mobile: 手机号
            dept_id: 部门ID
            status: 状态
            ssex: 性别
            avatar: 头像
            description: 描述
        """
        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        if mobile is not None:
            self.mobile = mobile
        if dept_id is not None:
            self.dept_id = dept_id
        if status is not None:
            self.status = status
        if ssex is not None:
            self.ssex = ssex
        if avatar is not None:
            self.avatar = avatar
        if description is not None:
            self.description = description
        self.modify_time = datetime.utcnow()

    def get_gender_display(self) -> str:
        """
        获取性别显示文本

        Returns:
            性别显示文本
        """
        gender_map = {'0': '男', '1': '女', '2': '保密'}
        return gender_map.get(self.ssex, '未知')

    def to_dict(self) -> dict:
        """
        转换为字典格式

        Returns:
            用户信息字典
        """
        return {
            "user_id": self.id,
            "username": self.username,
            "dept_id": self.dept_id,
            "email": self.email,
            "mobile": self.mobile,
            "status": self.status,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "modify_time": self.modify_time.isoformat() if self.modify_time else None,
            "last_login_time": self.last_login_time.isoformat() if self.last_login_time else None,
            "ssex": self.ssex,
            "avatar": self.avatar,
            "description": self.description
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
        return f"<User(user_id={self.id}, username='{self.username}', status='{self.status}')>"
