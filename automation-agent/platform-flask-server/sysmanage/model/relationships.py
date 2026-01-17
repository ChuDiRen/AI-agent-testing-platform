"""
定义所有多对多关联关系
在所有模型定义完成后导入执行
"""
from app import database
from login.model.UserModel import User
from sysmanage.model.RoleModel import Role
from sysmanage.model.MenuModel import Menu
from sysmanage.model.ApiModel import Api
from sysmanage.model.UserRoleModel import UserRole
from sysmanage.model.RoleMenuModel import RoleMenu
from sysmanage.model.RoleApiModel import RoleApi


def init_relationships():
    """初始化所有关联关系"""
    # User - Role 多对多 (通过 t_user_role 表)
    User.roles = database.relationship('Role',
                                        secondary=lambda: UserRole.__table__,
                                        primaryjoin=User.id == UserRole.user_id,
                                        secondaryjoin=Role.id == UserRole.role_id,
                                        backref='users',
                                        lazy='dynamic')

    # Role - Menu 多对多 (通过 t_role_menu 表)
    Role.menus = database.relationship('Menu',
                                        secondary=lambda: RoleMenu.__table__,
                                        primaryjoin=Role.id == RoleMenu.role_id,
                                        secondaryjoin=Menu.id == RoleMenu.menu_id,
                                        backref='roles',
                                        lazy='dynamic')

    # Role - Api 多对多 (通过 t_role_api 表)
    Role.apis = database.relationship('Api',
                                       secondary=lambda: RoleApi.__table__,
                                       primaryjoin=Role.id == RoleApi.role_id,
                                       secondaryjoin=Api.id == RoleApi.api_id,
                                       backref='roles',
                                       lazy='dynamic')
