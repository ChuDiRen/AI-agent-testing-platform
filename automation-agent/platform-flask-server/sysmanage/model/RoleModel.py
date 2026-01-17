from app import database
from datetime import datetime


class Role(database.Model):
    __tablename__ = "t_role"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(20), unique=True, nullable=False, comment='角色名称')
    desc = database.Column(database.String(500), comment='角色描述')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
