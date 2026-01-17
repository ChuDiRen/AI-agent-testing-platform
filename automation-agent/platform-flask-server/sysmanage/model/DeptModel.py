from app import database
from datetime import datetime


class Dept(database.Model):
    __tablename__ = "t_dept"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(20), unique=True, nullable=False, comment='部门名称')
    desc = database.Column(database.String(500), comment='备注')
    is_deleted = database.Column(database.Boolean, default=False, comment='软删除标记')
    order = database.Column(database.Integer, default=0, comment='排序')
    parent_id = database.Column(database.Integer, default=0, comment='父部门ID')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
