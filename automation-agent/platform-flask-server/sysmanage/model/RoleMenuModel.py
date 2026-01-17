from app import database
from datetime import datetime


class RoleMenu(database.Model):
    __tablename__ = "t_role_menu"
    __table_args__ = {'extend_existing': True}

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    role_id = database.Column(database.Integer, nullable=False, comment='角色ID')
    menu_id = database.Column(database.Integer, nullable=False, comment='菜单ID')
    created_at = database.Column(database.DateTime, default=datetime.now, comment='创建时间')
