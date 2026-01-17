from app import database
from datetime import datetime


class Menu(database.Model):
    __tablename__ = "t_menu"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    name = database.Column(database.String(20), nullable=False, comment='菜单名称')
    remark = database.Column(database.JSON, comment='保留字段')
    menu_type = database.Column(database.String(20), comment='菜单类型: catalog/menu')
    icon = database.Column(database.String(100), comment='菜单图标')
    path = database.Column(database.String(100), nullable=False, comment='菜单路径')
    order = database.Column(database.Integer, default=0, comment='排序')
    parent_id = database.Column(database.Integer, default=0, comment='父菜单ID')
    is_hidden = database.Column(database.Boolean, default=False, comment='是否隐藏')
    component = database.Column(database.String(100), nullable=False, comment='组件')
    keepalive = database.Column(database.Boolean, default=True, comment='存活')
    redirect = database.Column(database.String(100), comment='重定向')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
    updated_at = database.Column(database.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
