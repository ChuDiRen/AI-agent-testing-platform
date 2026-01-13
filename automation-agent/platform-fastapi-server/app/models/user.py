"""
用户模型
从 Flask-SQLAlchemy 迁移到 SQLAlchemy 2.0
"""
from sqlalchemy import Column, String
from app.db.base import Base
import bcrypt


class User(Base):
    """用户表"""
    __tablename__ = "t_user"
    
    username = Column(String(255), unique=True, comment='用户名')
    password = Column(String(255), comment='密码')
    create_time = Column(String(255), comment='创建时间')
    
    def set_password(self, password: str):
        """设置密码（加密）"""
        self.password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password.encode("utf-8")
        )
