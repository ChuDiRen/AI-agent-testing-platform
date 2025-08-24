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
        
        # 获取技术部ID（如果不存在则创建）
        from app.entity.department import Department
        tech_dept = db.query(Department).filter(Department.dept_name == "技术部").first()
        if not tech_dept:
            tech_dept = Department(parent_id=0, dept_name="技术部", order_num=1.0)
            db.add(tech_dept)
            db.flush()

        # 创建超级用户
        user = service.create_user(
            username="admin",
            password="123456",
            email="admin@example.com",
            mobile="17788888888",
            dept_id=tech_dept.id,
            ssex="0",
            avatar="default.jpg",
            description="系统管理员"
        )
        logger.info(f"Superuser created: {user.username}")
        
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

        # 1. 创建部门层级结构
        # 顶级部门
        tech_dept = Department(parent_id=0, dept_name="技术部", order_num=1.0)
        db.add(tech_dept)
        db.flush()

        hr_dept = Department(parent_id=0, dept_name="人事部", order_num=2.0)
        db.add(hr_dept)
        db.flush()

        finance_dept = Department(parent_id=0, dept_name="财务部", order_num=3.0)
        db.add(finance_dept)
        db.flush()

        # 技术部子部门
        dev_team = Department(parent_id=tech_dept.id, dept_name="开发组", order_num=1.1)
        db.add(dev_team)
        db.flush()

        test_team = Department(parent_id=tech_dept.id, dept_name="测试组", order_num=1.2)
        db.add(test_team)
        db.flush()

        ops_team = Department(parent_id=tech_dept.id, dept_name="运维组", order_num=1.3)
        db.add(ops_team)
        db.flush()

        # 2. 创建角色体系
        # 管理员角色
        admin_role = Role(role_name="管理员", remark="系统管理员，拥有所有权限")
        db.add(admin_role)
        db.flush()

        # 普通用户角色
        user_role = Role(role_name="普通用户", remark="普通用户，只有基本查看权限")
        db.add(user_role)
        db.flush()

        # 部门经理角色
        manager_role = Role(role_name="部门经理", remark="部门经理，管理本部门用户")
        db.add(manager_role)
        db.flush()

        # 开发人员角色
        developer_role = Role(role_name="开发人员", remark="开发人员，有开发相关权限")
        db.add(developer_role)
        db.flush()

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
            parent_id=system_menu.id,
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
            parent_id=user_menu.menu_id,
            menu_name="新增用户",
            menu_type="1",
            perms="user:add"
        )
        db.add(user_add_btn)
        db.flush()

        user_update_btn = Menu(
            parent_id=user_menu.menu_id,
            menu_name="修改用户",
            menu_type="1",
            perms="user:update"
        )
        db.add(user_update_btn)
        db.flush()

        user_delete_btn = Menu(
            parent_id=user_menu.menu_id,
            menu_name="删除用户",
            menu_type="1",
            perms="user:delete"
        )
        db.add(user_delete_btn)
        db.flush()

        # 角色管理菜单
        role_menu = Menu(
            parent_id=system_menu.menu_id,
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
            parent_id=role_menu.menu_id,
            menu_name="新增角色",
            menu_type="1",
            perms="role:add"
        )
        db.add(role_add_btn)
        db.flush()

        role_update_btn = Menu(
            parent_id=role_menu.menu_id,
            menu_name="修改角色",
            menu_type="1",
            perms="role:update"
        )
        db.add(role_update_btn)
        db.flush()

        role_delete_btn = Menu(
            parent_id=role_menu.menu_id,
            menu_name="删除角色",
            menu_type="1",
            perms="role:delete"
        )
        db.add(role_delete_btn)
        db.flush()

        # 菜单管理菜单
        menu_menu = Menu(
            parent_id=system_menu.menu_id,
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
            parent_id=menu_menu.menu_id,
            menu_name="新增菜单",
            menu_type="1",
            perms="menu:add"
        )
        db.add(menu_add_btn)
        db.flush()

        menu_update_btn = Menu(
            parent_id=menu_menu.menu_id,
            menu_name="修改菜单",
            menu_type="1",
            perms="menu:update"
        )
        db.add(menu_update_btn)
        db.flush()

        menu_delete_btn = Menu(
            parent_id=menu_menu.menu_id,
            menu_name="删除菜单",
            menu_type="1",
            perms="menu:delete"
        )
        db.add(menu_delete_btn)
        db.flush()

        # 部门管理菜单
        dept_menu = Menu(
            parent_id=system_menu.menu_id,
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
            parent_id=dept_menu.menu_id,
            menu_name="新增部门",
            menu_type="1",
            perms="dept:add"
        )
        db.add(dept_add_btn)
        db.flush()

        dept_update_btn = Menu(
            parent_id=dept_menu.menu_id,
            menu_name="修改部门",
            menu_type="1",
            perms="dept:update"
        )
        db.add(dept_update_btn)
        db.flush()

        dept_delete_btn = Menu(
            parent_id=dept_menu.menu_id,
            menu_name="删除部门",
            menu_type="1",
            perms="dept:delete"
        )
        db.add(dept_delete_btn)
        db.flush()

        # 权限缓存管理相关菜单和按钮
        cache_stats_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="缓存统计查看",
            menu_type="1",
            perms="cache:stats:view"
        )
        db.add(cache_stats_btn)
        db.flush()

        cache_refresh_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="缓存刷新",
            menu_type="1",
            perms="cache:refresh"
        )
        db.add(cache_refresh_btn)
        db.flush()

        cache_config_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="缓存配置更新",
            menu_type="1",
            perms="cache:config:update"
        )
        db.add(cache_config_btn)
        db.flush()

        user_permission_view_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="用户权限查看",
            menu_type="1",
            perms="user:permission:view"
        )
        db.add(user_permission_view_btn)
        db.flush()

        user_menu_view_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="用户菜单查看",
            menu_type="1",
            perms="user:menu:view"
        )
        db.add(user_menu_view_btn)
        db.flush()

        role_permission_view_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="角色权限查看",
            menu_type="1",
            perms="role:permission:view"
        )
        db.add(role_permission_view_btn)
        db.flush()

        user_role_assign_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="用户角色分配",
            menu_type="1",
            perms="user:role:assign"
        )
        db.add(user_role_assign_btn)
        db.flush()

        role_menu_assign_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="角色菜单分配",
            menu_type="1",
            perms="role:menu:assign"
        )
        db.add(role_menu_assign_btn)
        db.flush()

        data_permission_create_btn = Menu(
            parent_id=system_menu.menu_id,
            menu_name="数据权限创建",
            menu_type="1",
            perms="data:permission:create"
        )
        db.add(data_permission_create_btn)
        db.flush()

        # 4. 创建用户
        # 管理员用户
        admin_user = User(
            username="admin",
            password=get_password_hash("123456"),
            email="admin@example.com",
            mobile="17788888888",
            dept_id=tech_dept.dept_id,
            ssex="0",
            avatar="default.jpg",
            description="系统管理员"
        )
        db.add(admin_user)
        db.flush()

        # 技术部经理
        tech_manager = User(
            username="tech_manager",
            password=get_password_hash("123456"),
            email="tech.manager@example.com",
            mobile="17788888889",
            dept_id=tech_dept.dept_id,
            ssex="1",
            avatar="default.jpg",
            description="技术部经理"
        )
        db.add(tech_manager)
        db.flush()

        # 开发人员
        developer1 = User(
            username="developer1",
            password=get_password_hash("123456"),
            email="dev1@example.com",
            mobile="17788888890",
            dept_id=dev_team.dept_id,
            ssex="0",
            avatar="default.jpg",
            description="前端开发工程师"
        )
        db.add(developer1)
        db.flush()

        developer2 = User(
            username="developer2",
            password=get_password_hash("123456"),
            email="dev2@example.com",
            mobile="17788888891",
            dept_id=dev_team.dept_id,
            ssex="1",
            avatar="default.jpg",
            description="后端开发工程师"
        )
        db.add(developer2)
        db.flush()

        # 测试人员
        tester = User(
            username="tester",
            password=get_password_hash("123456"),
            email="tester@example.com",
            mobile="17788888892",
            dept_id=test_team.dept_id,
            ssex="1",
            avatar="default.jpg",
            description="测试工程师"
        )
        db.add(tester)
        db.flush()

        # 普通用户
        normal_user = User(
            username="user",
            password=get_password_hash("123456"),
            email="user@example.com",
            mobile="17788888893",
            dept_id=hr_dept.dept_id,
            ssex="0",
            avatar="default.jpg",
            description="普通用户"
        )
        db.add(normal_user)
        db.flush()

        # 5. 分配角色给用户
        # 管理员角色
        admin_user_role = UserRole(user_id=admin_user.user_id, role_id=admin_role.role_id)
        db.add(admin_user_role)

        # 技术部经理角色
        tech_manager_user_role = UserRole(user_id=tech_manager.user_id, role_id=manager_role.role_id)
        db.add(tech_manager_user_role)

        # 开发人员角色
        dev1_user_role = UserRole(user_id=developer1.user_id, role_id=developer_role.role_id)
        db.add(dev1_user_role)

        dev2_user_role = UserRole(user_id=developer2.user_id, role_id=developer_role.role_id)
        db.add(dev2_user_role)

        # 测试人员角色
        tester_user_role = UserRole(user_id=tester.user_id, role_id=user_role.role_id)
        db.add(tester_user_role)

        # 普通用户角色
        normal_user_role = UserRole(user_id=normal_user.user_id, role_id=user_role.role_id)
        db.add(normal_user_role)

        # 6. 分配菜单权限给角色
        # 管理员角色 - 拥有所有权限
        admin_menu_ids = [
            system_menu.menu_id,
            user_menu.menu_id,
            user_add_btn.menu_id,
            user_update_btn.menu_id,
            user_delete_btn.menu_id,
            role_menu.menu_id,
            role_add_btn.menu_id,
            role_update_btn.menu_id,
            role_delete_btn.menu_id,
            menu_menu.menu_id,
            menu_add_btn.menu_id,
            menu_update_btn.menu_id,
            menu_delete_btn.menu_id,
            dept_menu.menu_id,
            dept_add_btn.menu_id,
            dept_update_btn.menu_id,
            dept_delete_btn.menu_id,
            cache_stats_btn.menu_id,
            cache_refresh_btn.menu_id,
            cache_config_btn.menu_id,
            user_permission_view_btn.menu_id,
            user_menu_view_btn.menu_id,
            role_permission_view_btn.menu_id,
            user_role_assign_btn.menu_id,
            role_menu_assign_btn.menu_id,
            data_permission_create_btn.menu_id
        ]

        for menu_id in admin_menu_ids:
            role_menu_rel = RoleMenu(role_id=admin_role.role_id, menu_id=menu_id)
            db.add(role_menu_rel)

        # 部门经理角色 - 有用户管理权限
        manager_menu_ids = [
            system_menu.menu_id,
            user_menu.menu_id,
            user_add_btn.menu_id,
            user_update_btn.menu_id,
            dept_menu.menu_id,
            user_permission_view_btn.menu_id,
            user_menu_view_btn.menu_id
        ]

        for menu_id in manager_menu_ids:
            role_menu_rel = RoleMenu(role_id=manager_role.role_id, menu_id=menu_id)
            db.add(role_menu_rel)

        # 开发人员角色 - 有基本查看权限
        developer_menu_ids = [
            system_menu.menu_id,
            user_menu.menu_id,
            dept_menu.menu_id,
            user_permission_view_btn.menu_id,
            user_menu_view_btn.menu_id
        ]

        for menu_id in developer_menu_ids:
            role_menu_rel = RoleMenu(role_id=developer_role.role_id, menu_id=menu_id)
            db.add(role_menu_rel)

        # 普通用户角色 - 只有基本查看权限
        user_menu_ids = [
            user_menu.menu_id,
            user_permission_view_btn.menu_id,
            user_menu_view_btn.menu_id
        ]

        for menu_id in user_menu_ids:
            role_menu_rel = RoleMenu(role_id=user_role.role_id, menu_id=menu_id)
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