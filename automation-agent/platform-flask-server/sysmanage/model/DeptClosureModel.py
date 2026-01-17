from app import database
from datetime import datetime


class DeptClosure(database.Model):
    __tablename__ = "t_dept_closure"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    ancestor = database.Column(database.Integer, nullable=False, comment='父代')
    descendant = database.Column(database.Integer, nullable=False, comment='子代')
    level = database.Column(database.Integer, default=0, comment='深度')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
