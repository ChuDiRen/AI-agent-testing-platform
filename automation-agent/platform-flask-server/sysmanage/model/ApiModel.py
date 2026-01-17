from app import database
from datetime import datetime


class Api(database.Model):
    __tablename__ = "t_api"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    path = database.Column(database.String(100), nullable=False, comment='API路径')
    method = database.Column(database.String(10), nullable=False, comment='请求方法')
    summary = database.Column(database.String(500), comment='请求简介')
    tags = database.Column(database.String(100), comment='API标签')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
