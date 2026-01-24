"""
初始化菜单数据
参考vue-fastapi-admin的菜单结构
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models.menu import Menu
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_menu import RoleMenu


async def init_menu_data(db: AsyncSession):
    """初始化菜单数据"""
    
    # 检查是否已有菜单数据
    result = await db.execute(text("SELECT COUNT(*) FROM t_menu"))
    count = result.scalar()
    if count > 0:
        print(f"菜单数据已存在，跳过初始化（当前有 {count} 条记录）")
        return
    
    # 创建菜单数据
    menus_data = [
        # 系统管理
        {
            "name": "系统管理",
            "menu_type": "catalog",
            "icon": "system",
            "path": "/system",
            "component": "Layout",
            "order": 1,
            "parent_id": 0,
            "is_hidden": False,
            "keepalive": True,
            "redirect": "/system/users"
        },
        # 用户管理
        {
            "name": "用户管理",
            "menu_type": "menu",
            "icon": "user",
            "path": "/system/users",
            "component": "users/userList",
            "order": 1,
            "parent_id": 1,  # 系统管理的子菜单
            "is_hidden": False,
            "keepalive": True
        },
        # 角色管理
        {
            "name": "角色管理",
            "menu_type": "menu",
            "icon": "role",
            "path": "/system/roles",
            "component": "roles/roleList",
            "order": 2,
            "parent_id": 1,
            "is_hidden": False,
            "keepalive": True
        },
        # 菜单管理
        {
            "name": "菜单管理",
            "menu_type": "menu",
            "icon": "menu",
            "path": "/system/menus",
            "component": "menus/menuList",
            "order": 3,
            "parent_id": 1,
            "is_hidden": False,
            "keepalive": True
        },
        # 部门管理
        {
            "name": "部门管理",
            "menu_type": "menu",
            "icon": "dept",
            "path": "/system/depts",
            "component": "depts/deptList",
            "order": 4,
            "parent_id": 1,
            "is_hidden": False,
            "keepalive": True
        },
        # API测试
        {
            "name": "API测试",
            "menu_type": "catalog",
            "icon": "api",
            "path": "/apitest",
            "component": "Layout",
            "order": 2,
            "parent_id": 0,
            "is_hidden": False,
            "keepalive": True,
            "redirect": "/apitest/projects"
        },
        # 项目管理
        {
            "name": "项目管理",
            "menu_type": "menu",
            "icon": "project",
            "path": "/apitest/projects",
            "component": "apitest/project/ApiProjectList",
            "order": 1,
            "parent_id": 6,  # API测试的子菜单
            "is_hidden": False,
            "keepalive": True
        },
        # 接口信息
        {
            "name": "接口信息",
            "menu_type": "menu",
            "icon": "api-info",
            "path": "/apitest/apiinfo",
            "component": "apitest/apiinfo/ApiInfoList",
            "order": 2,
            "parent_id": 6,
            "is_hidden": False,
            "keepalive": True
        },
        # 用例管理
        {
            "name": "用例管理",
            "menu_type": "menu",
            "icon": "testcase",
            "path": "/apitest/testcases",
            "component": "apitest/apiinfocase/ApiInfoCaseList",
            "order": 3,
            "parent_id": 6,
            "is_hidden": False,
            "keepalive": True
        },
        # 数据统计
        {
            "name": "数据统计",
            "menu_type": "catalog",
            "icon": "chart",
            "path": "/statistics",
            "component": "Layout",
            "order": 3,
            "parent_id": 0,
            "is_hidden": False,
            "keepalive": True,
            "redirect": "/statistics/overview"
        },
        # 统计概览
        {
            "name": "统计概览",
            "menu_type": "menu",
            "icon": "overview",
            "path": "/statistics/overview",
            "component": "statistics/statistics",
            "order": 1,
            "parent_id": 10,  # 数据统计的子菜单
            "is_hidden": False,
            "keepalive": True
        }
    ]
    
    # 创建菜单记录
    created_menus = []
    for menu_data in menus_data:
        menu = Menu(**menu_data)
        db.add(menu)
        created_menus.append(menu)
    
    await db.commit()
    
    # 刷新以获取ID
    for menu in created_menus:
        await db.refresh(menu)
    
    print(f"成功创建 {len(created_menus)} 条菜单记录")
    
    # 为管理员角色分配所有菜单权限
    result = await db.execute(text("SELECT id FROM t_role WHERE name = 'admin'"))
    admin_role = result.scalar_one_or_none()
    
    if admin_role:
        # 清除现有的菜单权限
        await db.execute(text("DELETE FROM t_role_menu WHERE role_id = :role_id"), {"role_id": admin_role})
        
        # 为管理员角色分配所有菜单
        for menu in created_menus:
            role_menu = RoleMenu(role_id=admin_role, menu_id=menu.id)
            db.add(role_menu)
        
        await db.commit()
        print(f"为管理员角色分配了 {len(created_menus)} 个菜单权限")
    else:
        print("警告：未找到管理员角色，请先创建角色数据")


async def create_admin_role_if_not_exists(db: AsyncSession):
    """创建管理员角色（如果不存在）"""
    result = await db.execute(text("SELECT COUNT(*) FROM t_role WHERE name = 'admin'"))
    count = result.scalar()
    
    if count == 0:
        admin_role = Role(
            name="admin",
            desc="系统管理员，拥有所有权限"
        )
        db.add(admin_role)
        await db.commit()
        await db.refresh(admin_role)
        print(f"创建管理员角色，ID: {admin_role.id}")
        return admin_role
    else:
        result = await db.execute(text("SELECT id FROM t_role WHERE name = 'admin'"))
        admin_role_id = result.scalar()
        print(f"管理员角色已存在，ID: {admin_role_id}")
        return admin_role_id


async def create_admin_user_if_not_exists(db: AsyncSession):
    """创建管理员用户（如果不存在）"""
    result = await db.execute(text("SELECT COUNT(*) FROM t_user WHERE username = 'admin'"))
    count = result.scalar()
    
    if count == 0:
        # 获取管理员角色
        admin_role = await create_admin_role_if_not_exists(db)
        
        # 创建管理员用户
        admin_user = User(
            username="admin",
            alias="系统管理员",
            email="admin@example.com",
            is_active=True,
            is_superuser=True
        )
        admin_user.set_password("admin123")  # 设置默认密码
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        # 分配角色
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role)
        db.add(user_role)
        await db.commit()
        
        print(f"创建管理员用户，ID: {admin_user.id}，默认密码: admin123")
        return admin_user
    else:
        result = await db.execute(text("SELECT id FROM t_user WHERE username = 'admin'"))
        admin_user_id = result.scalar()
        print(f"管理员用户已存在，ID: {admin_user_id}")
        return admin_user_id


async def init_all_menu_data(db: AsyncSession):
    """初始化所有菜单相关数据"""
    print("开始初始化菜单数据...")
    
    # 创建管理员用户和角色
    await create_admin_user_if_not_exists(db)
    
    # 初始化菜单数据
    await init_menu_data(db)
    
    print("菜单数据初始化完成！")
