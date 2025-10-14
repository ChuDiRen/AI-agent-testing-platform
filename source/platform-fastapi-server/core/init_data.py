# -*- coding: utf-8 -*-
"""数据库初始化数据脚本"""

from sqlmodel import Session, select
from core.database import engine
from sysmanage.model.user import User
from sysmanage.model.role import Role
from sysmanage.model.menu import Menu
from sysmanage.model.dept import Dept
from sysmanage.model.user_role import UserRole
from sysmanage.model.role_menu import RoleMenu
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_data_exists() -> bool:
    """检查数据库中是否已有数据"""
    try:
        with Session(engine) as session:
            # 检查用户表是否有数据
            statement = select(User)
            users = session.exec(statement).all()
            return len(users) > 0
    except Exception as e:
        logger.error(f"检查数据失败: {e}")
        return False

def create_initial_depts():
    """创建初始部门数据"""
    try:
        with Session(engine) as session:
            initial_depts = [
                {"dept_id": 1, "parent_id": 0, "dept_name": "总公司", "order_num": 1},
                {"dept_id": 2, "parent_id": 1, "dept_name": "技术部", "order_num": 1},
                {"dept_id": 3, "parent_id": 1, "dept_name": "产品部", "order_num": 2},
                {"dept_id": 4, "parent_id": 1, "dept_name": "运营部", "order_num": 3},
            ]

            for dept_data in initial_depts:
                existing = session.get(Dept, dept_data["dept_id"])
                if not existing:
                    dept = Dept(**dept_data, create_time=datetime.now(), modify_time=datetime.now())
                    session.add(dept)
                    logger.info(f"创建部门: {dept_data['dept_name']}")

            session.commit()
            logger.info("初始部门数据创建完成")
    except Exception as e:
        logger.error(f"创建初始部门失败: {e}")
        raise

def create_initial_roles():
    """创建初始角色数据"""
    try:
        with Session(engine) as session:
            initial_roles = [
                {"role_id": 1, "role_name": "超级管理员", "remark": "拥有所有权限"},
                {"role_id": 2, "role_name": "管理员", "remark": "拥有部分管理权限"},
                {"role_id": 3, "role_name": "普通用户", "remark": "拥有基本权限"},
            ]

            for role_data in initial_roles:
                existing = session.get(Role, role_data["role_id"])
                if not existing:
                    role = Role(**role_data, create_time=datetime.now(), modify_time=datetime.now())
                    session.add(role)
                    logger.info(f"创建角色: {role_data['role_name']}")

            session.commit()
            logger.info("初始角色数据创建完成")
    except Exception as e:
        logger.error(f"创建初始角色失败: {e}")
        raise

def create_initial_menus():
    """创建初始菜单数据"""
    try:
        with Session(engine) as session:
            initial_menus = [
                # 系统管理
                {"menu_id": 1, "parent_id": 0, "menu_name": "系统管理", "path": "/system", "component": "Layout", "perms": "", "icon": "el-icon-setting", "type": "0", "order_num": 1},
                {"menu_id": 2, "parent_id": 1, "menu_name": "用户管理", "path": "/system/user", "component": "system/user/index", "perms": "system:user:view", "icon": "el-icon-user", "type": "0", "order_num": 1},
                {"menu_id": 3, "parent_id": 1, "menu_name": "角色管理", "path": "/system/role", "component": "system/role/index", "perms": "system:role:view", "icon": "el-icon-s-custom", "type": "0", "order_num": 2},
                {"menu_id": 4, "parent_id": 1, "menu_name": "菜单管理", "path": "/system/menu", "component": "system/menu/index", "perms": "system:menu:view", "icon": "el-icon-menu", "type": "0", "order_num": 3},
                {"menu_id": 5, "parent_id": 1, "menu_name": "部门管理", "path": "/system/dept", "component": "system/dept/index", "perms": "system:dept:view", "icon": "el-icon-office-building", "type": "0", "order_num": 4},
                
                # 用户管理按钮
                {"menu_id": 10, "parent_id": 2, "menu_name": "新增用户", "path": "", "component": "", "perms": "system:user:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 11, "parent_id": 2, "menu_name": "编辑用户", "path": "", "component": "", "perms": "system:user:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 12, "parent_id": 2, "menu_name": "删除用户", "path": "", "component": "", "perms": "system:user:delete", "icon": "", "type": "1", "order_num": 3},
                {"menu_id": 13, "parent_id": 2, "menu_name": "分配角色", "path": "", "component": "", "perms": "system:user:role", "icon": "", "type": "1", "order_num": 4},
                
                # 角色管理按钮
                {"menu_id": 20, "parent_id": 3, "menu_name": "新增角色", "path": "", "component": "", "perms": "system:role:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 21, "parent_id": 3, "menu_name": "编辑角色", "path": "", "component": "", "perms": "system:role:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 22, "parent_id": 3, "menu_name": "删除角色", "path": "", "component": "", "perms": "system:role:delete", "icon": "", "type": "1", "order_num": 3},
                {"menu_id": 23, "parent_id": 3, "menu_name": "分配权限", "path": "", "component": "", "perms": "system:role:menu", "icon": "", "type": "1", "order_num": 4},
                
                # 菜单管理按钮
                {"menu_id": 30, "parent_id": 4, "menu_name": "新增菜单", "path": "", "component": "", "perms": "system:menu:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 31, "parent_id": 4, "menu_name": "编辑菜单", "path": "", "component": "", "perms": "system:menu:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 32, "parent_id": 4, "menu_name": "删除菜单", "path": "", "component": "", "perms": "system:menu:delete", "icon": "", "type": "1", "order_num": 3},
                
                # 部门管理按钮
                {"menu_id": 40, "parent_id": 5, "menu_name": "新增部门", "path": "", "component": "", "perms": "system:dept:add", "icon": "", "type": "1", "order_num": 1},
                {"menu_id": 41, "parent_id": 5, "menu_name": "编辑部门", "path": "", "component": "", "perms": "system:dept:edit", "icon": "", "type": "1", "order_num": 2},
                {"menu_id": 42, "parent_id": 5, "menu_name": "删除部门", "path": "", "component": "", "perms": "system:dept:delete", "icon": "", "type": "1", "order_num": 3},
                
                # API测试
                {"menu_id": 100, "parent_id": 0, "menu_name": "API测试", "path": "/apitest", "component": "Layout", "perms": "", "icon": "el-icon-document", "type": "0", "order_num": 2},
                {"menu_id": 101, "parent_id": 100, "menu_name": "项目管理", "path": "/apitest/project", "component": "apitest/project/index", "perms": "apitest:project:view", "icon": "el-icon-folder", "type": "0", "order_num": 1},
                {"menu_id": 102, "parent_id": 100, "menu_name": "用例管理", "path": "/apitest/case", "component": "apitest/case/index", "perms": "apitest:case:view", "icon": "el-icon-document-copy", "type": "0", "order_num": 2},
            ]

            for menu_data in initial_menus:
                existing = session.get(Menu, menu_data["menu_id"])
                if not existing:
                    menu = Menu(**menu_data, create_time=datetime.now(), modify_time=datetime.now())
                    session.add(menu)
                    logger.info(f"创建菜单: {menu_data['menu_name']}")

            session.commit()
            logger.info("初始菜单数据创建完成")
    except Exception as e:
        logger.error(f"创建初始菜单失败: {e}")
        raise

def create_initial_users():
    """创建初始用户数据"""
    try:
        with Session(engine) as session:
            initial_users = [
                {
                    "id": 1,
                    "username": "admin",
                    "password": "admin123",
                    "dept_id": 2, # 技术部
                    "email": "admin@example.com",
                    "mobile": "13800138000",
                    "status": "1",
                    "ssex": "0",
                    "description": "超级管理员",
                    "create_time": datetime.now(),
                    "modify_time": datetime.now()
                }
            ]

            for user_data in initial_users:
                statement = select(User).where(User.username == user_data["username"])
                existing_user = session.exec(statement).first()

                if not existing_user:
                    user = User(**user_data)
                    session.add(user)
                    logger.info(f"创建用户: {user_data['username']}")
                else:
                    logger.info(f"用户已存在: {user_data['username']}")

            session.commit()
            logger.info("初始用户数据创建完成")

    except Exception as e:
        logger.error(f"创建初始用户失败: {e}")
        raise

def create_initial_user_roles():
    """创建初始用户-角色关联数据"""
    try:
        with Session(engine) as session:
            initial_user_roles = [
                {"user_id": 1, "role_id": 1}, # admin -> 超级管理员
            ]

            for ur_data in initial_user_roles:
                statement = select(UserRole).where(
                    UserRole.user_id == ur_data["user_id"],
                    UserRole.role_id == ur_data["role_id"]
                )
                existing = session.exec(statement).first()
                if not existing:
                    user_role = UserRole(**ur_data)
                    session.add(user_role)
                    logger.info(f"分配角色: 用户{ur_data['user_id']} -> 角色{ur_data['role_id']}")

            session.commit()
            logger.info("初始用户角色关联创建完成")
    except Exception as e:
        logger.error(f"创建用户角色关联失败: {e}")
        raise

def create_initial_role_menus():
    """创建初始角色-菜单关联数据"""
    try:
        with Session(engine) as session:
            # 获取所有菜单ID
            statement = select(Menu)
            all_menus = session.exec(statement).all()
            all_menu_ids = [menu.menu_id for menu in all_menus]
            
            # 超级管理员拥有所有权限
            for menu_id in all_menu_ids:
                statement = select(RoleMenu).where(
                    RoleMenu.role_id == 1,
                    RoleMenu.menu_id == menu_id
                )
                existing = session.exec(statement).first()
                if not existing:
                    role_menu = RoleMenu(role_id=1, menu_id=menu_id)
                    session.add(role_menu)
            
            logger.info("超级管理员权限分配完成")
            
            # 普通用户只有查看权限
            basic_menu_ids = [100, 101, 102] # API测试相关菜单
            for menu_id in basic_menu_ids:
                statement = select(RoleMenu).where(
                    RoleMenu.role_id == 3,
                    RoleMenu.menu_id == menu_id
                )
                existing = session.exec(statement).first()
                if not existing:
                    role_menu = RoleMenu(role_id=3, menu_id=menu_id)
                    session.add(role_menu)
            
            logger.info("普通用户权限分配完成")

            session.commit()
            logger.info("初始角色菜单关联创建完成")
    except Exception as e:
        logger.error(f"创建角色菜单关联失败: {e}")
        raise

def init_all_data():
    """初始化所有数据"""
    try:
        logger.info("开始初始化RBAC数据...")
        
        # 检查是否已有数据
        if check_data_exists():
            logger.info("数据库中已有数据，跳过初始化")
            return
        
        # 按顺序创建初始数据
        create_initial_depts() # 1. 创建部门
        create_initial_roles() # 2. 创建角色
        create_initial_menus() # 3. 创建菜单
        create_initial_users() # 4. 创建用户
        create_initial_user_roles() # 5. 分配用户角色
        create_initial_role_menus() # 6. 分配角色权限
        
        logger.info("RBAC数据初始化完成！")
        logger.info("=" * 60)
        logger.info("默认登录账号:")
        logger.info("admin / admin123 (超级管理员)")
        logger.info("")
        logger.info("RBAC功能清单:")
        logger.info("✓ 4个部门 (总公司、技术部、产品部、运营部)")
        logger.info("✓ 3个角色 (超级管理员、管理员、普通用户)")
        logger.info("✓ 完整菜单权限体系 (系统管理 + API测试)")
        logger.info("✓ 用户-角色-菜单权限关联")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"数据初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_all_data()
