"""用户数据库模型 - 完全按照博客 t_user 表结构设计"""
from sqlalchemy import Column, String, CHAR, DateTime, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """用户表模型 - 对应博客 t_user 表"""
    __tablename__ = "t_user"

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment="用户ID")  # SQLite使用INTEGER支持自增
    username = Column(String(50), nullable=False, comment="用户名")
    password = Column(String(128), nullable=False, comment="密码")
    dept_id = Column(Integer, nullable=True, comment="部门ID")  # SQLite使用INTEGER支持自增
    email = Column(String(128), nullable=True, comment="邮箱")
    mobile = Column(String(20), nullable=True, comment="联系电话")
    status = Column(CHAR(1), nullable=False, comment="状态 0锁定 1有效")
    create_time = Column(DateTime, nullable=False, comment="创建时间")
    modify_time = Column(DateTime, nullable=True, comment="修改时间")
    last_login_time = Column(DateTime, nullable=True, comment="最近访问时间")
    ssex = Column(CHAR(1), nullable=True, comment="性别 0男 1女 2保密")
    avatar = Column(String(100), nullable=True, comment="头像")
    description = Column(String(100), nullable=True, comment="描述")
    
    # 关联关系
    roles = relationship("Role", secondary="t_user_role", back_populates="users")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")  # 用户的通知列表

    @property
    def is_active(self) -> bool:
        """用户是否激活（基于status字段）"""
        return self.status == "1"

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"

