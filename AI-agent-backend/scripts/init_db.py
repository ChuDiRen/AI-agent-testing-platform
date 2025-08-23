"""
数据库初始化脚本
创建数据库表和初始数据
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import create_tables, drop_tables
from app.core.logger import get_logger
from app.service.rbac_user_service import RBACUserService
from app.db.session import SessionLocal

logger = get_logger(__name__)


def init_database():
    """
    初始化数据库
    """
    try:
        logger.info("Starting database initialization...")
        
        # 创建数据库表
        create_tables()
        logger.info("Database tables created successfully")
        
        # 创建初始数据
        create_initial_data()
        logger.info("Initial data created successfully")
        
        logger.info("Database initialization completed")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise


def create_initial_data():
    """
    创建初始数据
    """
    db = SessionLocal()
    try:
        # 创建RBAC初始数据
        create_rbac_initial_data(db)

        # 创建超级用户
        create_superuser(db)

        db.commit()

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating initial data: {str(e)}")
        raise
    finally:
        db.close()


def create_superuser(db):
    """
    创建超级用户
    """
    try:
        service = RBACUserService(db)
        
        # 检查是否已存在超级用户
        existing_user = service.get_user_by_username("admin")
        if existing_user:
            logger.info("Superuser already exists")
            return
        
        # 创建超级用户
        user = service.create_user(
            username="admin",
            password="123456",
            email="admin@example.com",
            mobile="17788888888",
            dept_id=1,  # 假设开发部的ID为1
            ssex="0",
            avatar="default.jpg",
            description="系统管理员"
        )
        logger.info(f"Superuser created: {user.USERNAME}")
        
    except Exception as e:
        logger.error(f"Error creating superuser: {str(e)}")
        raise


def create_rbac_initial_data(db):
    """
    创建RBAC初始数据
    """
    try:
        from app.entity.department import Department
        from app.entity.role import Role
        from app.entity.menu import Menu
        from app.entity.user import User
        from app.entity.user_role import UserRole
        from app.entity.role_menu import RoleMenu
        from app.core.security import get_password_hash

        # 1. 创建部门
        dept = Department(parent_id=0, dept_name="开发部", order_num=1)
        db.add(dept)
        db.flush()  # 获取部门ID

        # 2. 创建角色
        admin_role = Role(role_name="管理员", remark="系统管理员")
        db.add(admin_role)
        db.flush()  # 获取角色ID

        # 3. 创建菜单
        # 系统管理菜单
        system_menu = Menu(
            parent_id=0,
            menu_name="系统管理",
            menu_type="0",
            path="/system",
            component="Layout",
            icon="el-icon-set-up",
            order_num=1
        )
        db.add(system_menu)
        db.flush()

        # 用户管理菜单
        user_menu = Menu(
            parent_id=system_menu.MENU_ID,
            menu_name="用户管理",
            menu_type="0",
            path="/system/user",
            component="system/user/Index",
            perms="user:view",
            order_num=1
        )
        db.add(user_menu)
        db.flush()

        # 用户管理按钮
        user_add_btn = Menu(
            parent_id=user_menu.MENU_ID,
            menu_name="新增用户",
            menu_type="1",
            perms="user:add"
        )
        db.add(user_add_btn)
        db.flush()

        user_update_btn = Menu(
            parent_id=user_menu.MENU_ID,
            menu_name="修改用户",
            menu_type="1",
            perms="user:update"
        )
        db.add(user_update_btn)
        db.flush()

        user_delete_btn = Menu(
            parent_id=user_menu.MENU_ID,
            menu_name="删除用户",
            menu_type="1",
            perms="user:delete"
        )
        db.add(user_delete_btn)
        db.flush()

        # 角色管理菜单
        role_menu = Menu(
            parent_id=system_menu.MENU_ID,
            menu_name="角色管理",
            menu_type="0",
            path="/system/role",
            component="system/role/Index",
            perms="role:view",
            order_num=2
        )
        db.add(role_menu)
        db.flush()

        # 角色管理按钮
        role_add_btn = Menu(
            parent_id=role_menu.MENU_ID,
            menu_name="新增角色",
            menu_type="1",
            perms="role:add"
        )
        db.add(role_add_btn)
        db.flush()

        role_update_btn = Menu(
            parent_id=role_menu.MENU_ID,
            menu_name="修改角色",
            menu_type="1",
            perms="role:update"
        )
        db.add(role_update_btn)
        db.flush()

        role_delete_btn = Menu(
            parent_id=role_menu.MENU_ID,
            menu_name="删除角色",
            menu_type="1",
            perms="role:delete"
        )
        db.add(role_delete_btn)
        db.flush()

        # 菜单管理菜单
        menu_menu = Menu(
            parent_id=system_menu.MENU_ID,
            menu_name="菜单管理",
            menu_type="0",
            path="/system/menu",
            component="system/menu/Index",
            perms="menu:view",
            order_num=3
        )
        db.add(menu_menu)
        db.flush()

        # 菜单管理按钮
        menu_add_btn = Menu(
            parent_id=menu_menu.MENU_ID,
            menu_name="新增菜单",
            menu_type="1",
            perms="menu:add"
        )
        db.add(menu_add_btn)
        db.flush()

        menu_update_btn = Menu(
            parent_id=menu_menu.MENU_ID,
            menu_name="修改菜单",
            menu_type="1",
            perms="menu:update"
        )
        db.add(menu_update_btn)
        db.flush()

        menu_delete_btn = Menu(
            parent_id=menu_menu.MENU_ID,
            menu_name="删除菜单",
            menu_type="1",
            perms="menu:delete"
        )
        db.add(menu_delete_btn)
        db.flush()

        # 部门管理菜单
        dept_menu = Menu(
            parent_id=system_menu.MENU_ID,
            menu_name="部门管理",
            menu_type="0",
            path="/system/department",
            component="system/department/Index",
            perms="dept:view",
            order_num=4
        )
        db.add(dept_menu)
        db.flush()

        # 部门管理按钮
        dept_add_btn = Menu(
            parent_id=dept_menu.MENU_ID,
            menu_name="新增部门",
            menu_type="1",
            perms="dept:add"
        )
        db.add(dept_add_btn)
        db.flush()

        dept_update_btn = Menu(
            parent_id=dept_menu.MENU_ID,
            menu_name="修改部门",
            menu_type="1",
            perms="dept:update"
        )
        db.add(dept_update_btn)
        db.flush()

        dept_delete_btn = Menu(
            parent_id=dept_menu.MENU_ID,
            menu_name="删除部门",
            menu_type="1",
            perms="dept:delete"
        )
        db.add(dept_delete_btn)
        db.flush()

        # 4. 创建管理员用户
        admin_user = User(
            username="admin",
            password=get_password_hash("123456"),
            email="admin@example.com",
            mobile="17788888888",
            dept_id=dept.DEPT_ID,
            ssex="0",
            avatar="default.jpg",
            description="系统管理员"
        )
        db.add(admin_user)
        db.flush()

        # 5. 分配角色给用户
        user_role = UserRole(user_id=admin_user.USER_ID, role_id=admin_role.ROLE_ID)
        db.add(user_role)

        # 6. 分配菜单权限给角色
        menu_ids = [
            system_menu.MENU_ID,
            user_menu.MENU_ID,
            user_add_btn.MENU_ID,
            user_update_btn.MENU_ID,
            user_delete_btn.MENU_ID,
            role_menu.MENU_ID,
            role_add_btn.MENU_ID,
            role_update_btn.MENU_ID,
            role_delete_btn.MENU_ID,
            menu_menu.MENU_ID,
            menu_add_btn.MENU_ID,
            menu_update_btn.MENU_ID,
            menu_delete_btn.MENU_ID,
            dept_menu.MENU_ID,
            dept_add_btn.MENU_ID,
            dept_update_btn.MENU_ID,
            dept_delete_btn.MENU_ID
        ]

        for menu_id in menu_ids:
            role_menu_rel = RoleMenu(role_id=admin_role.ROLE_ID, menu_id=menu_id)
            db.add(role_menu_rel)

        logger.info("RBAC initial data created successfully")

    except Exception as e:
        logger.error(f"Error creating RBAC initial data: {str(e)}")
        raise


def reset_database():
    """
    重置数据库（删除所有表并重新创建）
    """
    try:
        logger.warning("Resetting database...")

        # 删除所有表
        drop_tables()
        logger.info("Database tables dropped")

        # 重新初始化
        init_database()

        logger.info("Database reset completed")

    except Exception as e:
        logger.error(f"Database reset failed: {str(e)}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument("--reset", action="store_true", help="Reset database (drop and recreate)")
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database()