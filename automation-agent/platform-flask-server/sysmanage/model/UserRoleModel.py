from app import database
from datetime import datetime


class UserRole(database.Model):
    __tablename__ = "t_user_role"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_id = database.Column(database.Integer, nullable=False, comment='用户ID')
    role_id = database.Column(database.Integer, nullable=False, comment='角色ID')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
