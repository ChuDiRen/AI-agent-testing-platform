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
from app.service.user_service import RBACUserService
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
            icon="User",
            order_num=1
        )
        db.add(user_menu)
        db.flush()

        # 用户管理按钮
        user_add_btn = Menu(
            parent_id=user_menu.id,
            menu_name="新增用户",
            menu_type="1",
            perms="user:add"
        )
        db.add(user_add_btn)
        db.flush()

        user_update_btn = Menu(
            parent_id=user_menu.id,
            menu_name="修改用户",
            menu_type="1",
            perms="user:update"
        )
        db.add(user_update_btn)
        db.flush()

        user_delete_btn = Menu(
            parent_id=user_menu.id,
            menu_name="删除用户",
            menu_type="1",
            perms="user:delete"
        )
        db.add(user_delete_btn)
        db.flush()

        # 角色管理菜单
        role_menu = Menu(
            parent_id=system_menu.id,
            menu_name="角色管理",
            menu_type="0",
            path="/system/role",
            component="system/role/Index",
            perms="role:view",
            icon="UserFilled",
            order_num=2
        )
        db.add(role_menu)
        db.flush()

        # 角色管理按钮
        role_add_btn = Menu(
            parent_id=role_menu.id,
            menu_name="新增角色",
            menu_type="1",
            perms="role:add"
        )
        db.add(role_add_btn)
        db.flush()

        role_update_btn = Menu(
            parent_id=role_menu.id,
            menu_name="修改角色",
            menu_type="1",
            perms="role:update"
        )
        db.add(role_update_btn)
        db.flush()

        role_delete_btn = Menu(
            parent_id=role_menu.id,
            menu_name="删除角色",
            menu_type="1",
            perms="role:delete"
        )
        db.add(role_delete_btn)
        db.flush()

        # 菜单管理菜单
        menu_menu = Menu(
            parent_id=system_menu.id,
            menu_name="菜单管理",
            menu_type="0",
            path="/system/menu",
            component="system/menu/Index",
            perms="menu:view",
            icon="Menu",
            order_num=3
        )
        db.add(menu_menu)
        db.flush()

        # 菜单管理按钮
        menu_add_btn = Menu(
            parent_id=menu_menu.id,
            menu_name="新增菜单",
            menu_type="1",
            perms="menu:add"
        )
        db.add(menu_add_btn)
        db.flush()

        menu_update_btn = Menu(
            parent_id=menu_menu.id,
            menu_name="修改菜单",
            menu_type="1",
            perms="menu:update"
        )
        db.add(menu_update_btn)
        db.flush()

        menu_delete_btn = Menu(
            parent_id=menu_menu.id,
            menu_name="删除菜单",
            menu_type="1",
            perms="menu:delete"
        )
        db.add(menu_delete_btn)
        db.flush()

        # 部门管理菜单
        dept_menu = Menu(
            parent_id=system_menu.id,
            menu_name="部门管理",
            menu_type="0",
            path="/system/department",
            component="system/department/Index",
            perms="dept:view",
            icon="OfficeBuilding",
            order_num=4
        )
        db.add(dept_menu)
        db.flush()

        # 部门管理按钮
        dept_add_btn = Menu(
            parent_id=dept_menu.id,
            menu_name="新增部门",
            menu_type="1",
            perms="dept:add"
        )
        db.add(dept_add_btn)
        db.flush()

        dept_update_btn = Menu(
            parent_id=dept_menu.id,
            menu_name="修改部门",
            menu_type="1",
            perms="dept:update"
        )
        db.add(dept_update_btn)
        db.flush()

        dept_delete_btn = Menu(
            parent_id=dept_menu.id,
            menu_name="删除部门",
            menu_type="1",
            perms="dept:delete"
        )
        db.add(dept_delete_btn)
        db.flush()

        # 权限缓存管理相关菜单和按钮
        cache_stats_btn = Menu(
            parent_id=system_menu.id,
            menu_name="缓存统计查看",
            menu_type="1",
            perms="cache:stats:view"
        )
        db.add(cache_stats_btn)
        db.flush()

        cache_refresh_btn = Menu(
            parent_id=system_menu.id,
            menu_name="缓存刷新",
            menu_type="1",
            perms="cache:refresh"
        )
        db.add(cache_refresh_btn)
        db.flush()

        cache_config_btn = Menu(
            parent_id=system_menu.id,
            menu_name="缓存配置更新",
            menu_type="1",
            perms="cache:config:update"
        )
        db.add(cache_config_btn)
        db.flush()

        user_permission_view_btn = Menu(
            parent_id=system_menu.id,
            menu_name="用户权限查看",
            menu_type="1",
            perms="user:permission:view"
        )
        db.add(user_permission_view_btn)
        db.flush()

        user_menu_view_btn = Menu(
            parent_id=system_menu.id,
            menu_name="用户菜单查看",
            menu_type="1",
            perms="user:menu:view"
        )
        db.add(user_menu_view_btn)
        db.flush()

        role_permission_view_btn = Menu(
            parent_id=system_menu.id,
            menu_name="角色权限查看",
            menu_type="1",
            perms="role:permission:view"
        )
        db.add(role_permission_view_btn)
        db.flush()

        user_role_assign_btn = Menu(
            parent_id=system_menu.id,
            menu_name="用户角色分配",
            menu_type="1",
            perms="user:role:assign"
        )
        db.add(user_role_assign_btn)
        db.flush()

        role_menu_assign_btn = Menu(
            parent_id=system_menu.id,
            menu_name="角色菜单分配",
            menu_type="1",
            perms="role:menu:assign"
        )
        db.add(role_menu_assign_btn)
        db.flush()

        data_permission_create_btn = Menu(
            parent_id=system_menu.id,
            menu_name="数据权限创建",
            menu_type="1",
            perms="data:permission:create"
        )
        db.add(data_permission_create_btn)
        db.flush()

        # 日志管理菜单
        log_menu = Menu(
            parent_id=system_menu.id,
            menu_name="日志管理",
            menu_type="0",
            path="/system/logs",
            component="system/logs/Index",
            perms="log:view",
            icon="el-icon-document",
            order_num=5
        )
        db.add(log_menu)
        db.flush()

        # 日志管理按钮
        log_view_btn = Menu(
            parent_id=log_menu.id,
            menu_name="查看日志",
            menu_type="1",
            perms="log:view"
        )
        db.add(log_view_btn)
        db.flush()

        log_delete_btn = Menu(
            parent_id=log_menu.id,
            menu_name="清空日志",
            menu_type="1",
            perms="log:delete"
        )
        db.add(log_delete_btn)
        db.flush()

        log_export_btn = Menu(
            parent_id=log_menu.id,
            menu_name="导出日志",
            menu_type="1",
            perms="log:export"
        )
        db.add(log_export_btn)
        db.flush()

        # 仪表板菜单
        dashboard_menu = Menu(
            parent_id=0,
            menu_name="仪表板",
            menu_type="0",
            path="/dashboard",
            component="dashboard/Index",
            icon="el-icon-data-line",
            order_num=0
        )
        db.add(dashboard_menu)
        db.flush()

        # 系统信息查看权限
        system_info_btn = Menu(
            parent_id=dashboard_menu.id,
            menu_name="系统信息",
            menu_type="1",
            perms="system:info:view"
        )
        db.add(system_info_btn)
        db.flush()

        # 测试管理菜单
        test_menu = Menu(
            parent_id=0,
            menu_name="测试管理",
            menu_type="0",
            path="/test",
            component="Layout",
            icon="DataAnalysis",
            order_num=2
        )
        db.add(test_menu)
        db.flush()

        # 测试用例菜单
        test_cases_menu = Menu(
            parent_id=test_menu.id,
            menu_name="测试用例",
            menu_type="0",
            path="/test/cases",
            component="test/cases/Index",
            perms="test:cases:view",
            icon="Document",
            order_num=1
        )
        db.add(test_cases_menu)
        db.flush()

        # 测试用例按钮
        test_cases_add_btn = Menu(
            parent_id=test_cases_menu.id,
            menu_name="新增用例",
            menu_type="1",
            perms="test:cases:add"
        )
        db.add(test_cases_add_btn)
        db.flush()

        test_cases_update_btn = Menu(
            parent_id=test_cases_menu.id,
            menu_name="修改用例",
            menu_type="1",
            perms="test:cases:update"
        )
        db.add(test_cases_update_btn)
        db.flush()

        test_cases_delete_btn = Menu(
            parent_id=test_cases_menu.id,
            menu_name="删除用例",
            menu_type="1",
            perms="test:cases:delete"
        )
        db.add(test_cases_delete_btn)
        db.flush()

        test_cases_run_btn = Menu(
            parent_id=test_cases_menu.id,
            menu_name="执行用例",
            menu_type="1",
            perms="test:cases:run"
        )
        db.add(test_cases_run_btn)
        db.flush()

        # 测试报告菜单
        test_reports_menu = Menu(
            parent_id=test_menu.id,
            menu_name="测试报告",
            menu_type="0",
            path="/test/reports",
            component="test/reports/Index",
            perms="test:reports:view",
            icon="PieChart",
            order_num=2
        )
        db.add(test_reports_menu)
        db.flush()

        # 测试报告按钮
        test_reports_export_btn = Menu(
            parent_id=test_reports_menu.id,
            menu_name="导出报告",
            menu_type="1",
            perms="test:reports:export"
        )
        db.add(test_reports_export_btn)
        db.flush()

        test_reports_delete_btn = Menu(
            parent_id=test_reports_menu.id,
            menu_name="删除报告",
            menu_type="1",
            perms="test:reports:delete"
        )
        db.add(test_reports_delete_btn)
        db.flush()

        # AI代理管理菜单
        agent_menu = Menu(
            parent_id=0,
            menu_name="AI代理管理",
            menu_type="0",
            path="/agent",
            component="Layout",
            icon="Cpu",
            order_num=3
        )
        db.add(agent_menu)
        db.flush()

        # 代理列表菜单
        agent_list_menu = Menu(
            parent_id=agent_menu.id,
            menu_name="代理列表",
            menu_type="0",
            path="/agent/list",
            component="agent/list/Index",
            perms="agent:list:view",
            icon="List",
            order_num=1
        )
        db.add(agent_list_menu)
        db.flush()

        # 代理列表按钮
        agent_list_add_btn = Menu(
            parent_id=agent_list_menu.id,
            menu_name="新增代理",
            menu_type="1",
            perms="agent:list:add"
        )
        db.add(agent_list_add_btn)
        db.flush()

        agent_list_update_btn = Menu(
            parent_id=agent_list_menu.id,
            menu_name="修改代理",
            menu_type="1",
            perms="agent:list:update"
        )
        db.add(agent_list_update_btn)
        db.flush()

        agent_list_delete_btn = Menu(
            parent_id=agent_list_menu.id,
            menu_name="删除代理",
            menu_type="1",
            perms="agent:list:delete"
        )
        db.add(agent_list_delete_btn)
        db.flush()

        agent_list_start_btn = Menu(
            parent_id=agent_list_menu.id,
            menu_name="启动代理",
            menu_type="1",
            perms="agent:list:start"
        )
        db.add(agent_list_start_btn)
        db.flush()

        agent_list_stop_btn = Menu(
            parent_id=agent_list_menu.id,
            menu_name="停止代理",
            menu_type="1",
            perms="agent:list:stop"
        )
        db.add(agent_list_stop_btn)
        db.flush()

        # 代理配置菜单
        agent_config_menu = Menu(
            parent_id=agent_menu.id,
            menu_name="代理配置",
            menu_type="0",
            path="/agent/config",
            component="agent/config/Index",
            perms="agent:config:view",
            icon="Tools",
            order_num=2
        )
        db.add(agent_config_menu)
        db.flush()

        # 代理配置按钮
        agent_config_update_btn = Menu(
            parent_id=agent_config_menu.id,
            menu_name="修改配置",
            menu_type="1",
            perms="agent:config:update"
        )
        db.add(agent_config_update_btn)
        db.flush()

        agent_config_reset_btn = Menu(
            parent_id=agent_config_menu.id,
            menu_name="重置配置",
            menu_type="1",
            perms="agent:config:reset"
        )
        db.add(agent_config_reset_btn)
        db.flush()

        # 4. 创建用户
        # 管理员用户
        admin_user = User(
            username="admin",
            password=get_password_hash("123456"),
            email="admin@example.com",
            mobile="17788888888",
            dept_id=tech_dept.id,
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
            dept_id=tech_dept.id,
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
            dept_id=dev_team.id,
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
            dept_id=dev_team.id,
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
            dept_id=test_team.id,
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
            dept_id=hr_dept.id,
            ssex="0",
            avatar="default.jpg",
            description="普通用户"
        )
        db.add(normal_user)
        db.flush()

        # 5. 分配角色给用户
        # 管理员角色
        admin_user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        db.add(admin_user_role)

        # 技术部经理角色
        tech_manager_user_role = UserRole(user_id=tech_manager.id, role_id=manager_role.id)
        db.add(tech_manager_user_role)

        # 开发人员角色
        dev1_user_role = UserRole(user_id=developer1.id, role_id=developer_role.id)
        db.add(dev1_user_role)

        dev2_user_role = UserRole(user_id=developer2.id, role_id=developer_role.id)
        db.add(dev2_user_role)

        # 测试人员角色
        tester_user_role = UserRole(user_id=tester.id, role_id=user_role.id)
        db.add(tester_user_role)

        # 普通用户角色
        normal_user_role = UserRole(user_id=normal_user.id, role_id=user_role.id)
        db.add(normal_user_role)

        # 6. 分配菜单权限给角色
        # 管理员角色 - 拥有所有权限
        admin_menu_ids = [
            dashboard_menu.id,
            system_info_btn.id,
            system_menu.id,
            user_menu.id,
            user_add_btn.id,
            user_update_btn.id,
            user_delete_btn.id,
            role_menu.id,
            role_add_btn.id,
            role_update_btn.id,
            role_delete_btn.id,
            menu_menu.id,
            menu_add_btn.id,
            menu_update_btn.id,
            menu_delete_btn.id,
            dept_menu.id,
            dept_add_btn.id,
            dept_update_btn.id,
            dept_delete_btn.id,
            cache_stats_btn.id,
            cache_refresh_btn.id,
            cache_config_btn.id,
            user_permission_view_btn.id,
            user_menu_view_btn.id,
            role_permission_view_btn.id,
            user_role_assign_btn.id,
            role_menu_assign_btn.id,
            data_permission_create_btn.id,
            log_menu.id,
            log_view_btn.id,
            log_delete_btn.id,
            log_export_btn.id,
            # 测试管理权限
            test_menu.id,
            test_cases_menu.id,
            test_cases_add_btn.id,
            test_cases_update_btn.id,
            test_cases_delete_btn.id,
            test_cases_run_btn.id,
            test_reports_menu.id,
            test_reports_export_btn.id,
            test_reports_delete_btn.id,
            # AI代理管理权限
            agent_menu.id,
            agent_list_menu.id,
            agent_list_add_btn.id,
            agent_list_update_btn.id,
            agent_list_delete_btn.id,
            agent_list_start_btn.id,
            agent_list_stop_btn.id,
            agent_config_menu.id,
            agent_config_update_btn.id,
            agent_config_reset_btn.id
        ]

        for menu_id in admin_menu_ids:
            role_menu_rel = RoleMenu(role_id=admin_role.id, menu_id=menu_id)
            db.add(role_menu_rel)

        # 部门经理角色 - 有用户管理权限
        manager_menu_ids = [
            dashboard_menu.id,
            system_info_btn.id,
            system_menu.id,
            user_menu.id,
            user_add_btn.id,
            user_update_btn.id,
            dept_menu.id,
            user_permission_view_btn.id,
            user_menu_view_btn.id
        ]

        for menu_id in manager_menu_ids:
            role_menu_rel = RoleMenu(role_id=manager_role.id, menu_id=menu_id)
            db.add(role_menu_rel)

        # 开发人员角色 - 有基本查看权限
        developer_menu_ids = [
            dashboard_menu.id,
            system_info_btn.id,
            system_menu.id,
            user_menu.id,
            dept_menu.id,
            user_permission_view_btn.id,
            user_menu_view_btn.id
        ]

        for menu_id in developer_menu_ids:
            role_menu_rel = RoleMenu(role_id=developer_role.id, menu_id=menu_id)
            db.add(role_menu_rel)

        # 普通用户角色 - 只有基本查看权限
        user_menu_ids = [
            dashboard_menu.id,
            system_info_btn.id,
            user_menu.id,
            user_permission_view_btn.id,
            user_menu_view_btn.id
        ]

        for menu_id in user_menu_ids:
            role_menu_rel = RoleMenu(role_id=user_role.id, menu_id=menu_id)
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