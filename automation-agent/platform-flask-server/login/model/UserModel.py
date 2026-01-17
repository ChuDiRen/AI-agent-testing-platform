from app import database
import bcrypt
from datetime import datetime


class User(database.Model):
    __tablename__ = "t_user"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    username = database.Column(database.String(20), unique=True, nullable=False, comment='用户名称')
    alias = database.Column(database.String(30), comment='姓名')
    email = database.Column(database.String(255), unique=True, nullable=False, comment='邮箱')
    phone = database.Column(database.String(20), comment='电话')
    password = database.Column(database.String(128), comment='密码')
    is_active = database.Column(database.Boolean, default=True, comment='是否激活')
    is_superuser = database.Column(database.Boolean, default=False, comment='是否为超级管理员')
    last_login = database.Column(database.DateTime, comment='最后登录时间')
    dept_id = database.Column(database.Integer, comment='部门ID')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def set_password(self, password):
        """加密密码：使用bcrypt生成哈希值"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        """验证密码：比对输入密码的哈希值与存储的哈希值"""
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))