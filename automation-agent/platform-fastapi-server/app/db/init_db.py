"""
数据库初始化模块
负责在应用启动时自动创建表和初始化数据
支持从JSON文件加载初始化数据
"""
import asyncio
import json
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.models import Base
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.api_resource import ApiResource
from app.models.dept import Dept
from app.models.audit_log import AuditLog
from app.models.user_role import UserRole
from app.models.role_menu import RoleMenu
from app.models.role_api import RoleApi
from app.models.dept_closure import DeptClosure
from app.core.logger import logger


# 获取初始化数据文件路径
INIT_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/init_data.json")


def load_init_data() -> dict:
    """
    从JSON文件加载初始化数据
    
    Returns:
        初始化数据字典
    """
    try:
        with open(INIT_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"✅ 成功加载初始化数据: {INIT_DATA_FILE}")
        return data
    except FileNotFoundError:
        logger.error(f"❌ 初始化数据文件不存在: {INIT_DATA_FILE}")
        return {}
    except json.JSONDecodeError as e:
        logger.error(f"❌ 初始化数据文件格式错误: {e}")
        return {}
    except Exception as e:
        logger.error(f"❌ 加载初始化数据失败: {e}")
        return {}


async def create_tables():
    """
    创建所有数据库表
    """
    from app.db.session import engine, create_database_engine

    # 确保引擎已初始化
    if engine is None:
        await create_database_engine()

    print("🔨 正在创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")


async def init_roles():
    """
    初始化角色数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal, create_database_engine

    # 确保 AsyncSessionLocal 已初始化
    if AsyncSessionLocal is None:
        await create_database_engine()

    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(Role))
        if result.scalars().first():
            print("✅ 角色数据已存在，跳过初始化")
            return
        
        print("📝 正在初始化角色数据...")
        
        # 从JSON文件加载数据
        init_data = load_init_data()
        roles_data = init_data.get("roles", [])
        
        if not roles_data:
            print("⚠️ 未找到角色初始化数据")
            return
        
        roles = [
            Role(name=role["name"], desc=role["desc"], created_at=datetime.now(), updated_at=datetime.now())
            for role in roles_data
        ]
        
        session.add_all(roles)
        await session.commit()
        print(f"✅ 角色数据初始化完成，共 {len(roles)} 条")


async def init_menus():
    """
    初始化菜单数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(Menu))
        if result.scalars().first():
            print("✅ 菜单数据已存在，跳过初始化")
            return
        
        print("📝 正在初始化菜单数据...")
        
        # 从JSON文件加载数据
        init_data = load_init_data()
        menus_data = init_data.get("menus", [])
        
        if not menus_data:
            print("⚠️ 未找到菜单初始化数据")
            return
        
        # 建立名称到ID的映射（用于parent_id解析）
        menu_id_map = {}
        menus_to_add = []
        
        # 第一遍：创建所有菜单（不处理parent_id）
        for menu_data in menus_data:
            menu = Menu(
                name=menu_data["name"],
                menu_type=menu_data.get("menu_type", "menu"),
                icon=menu_data.get("icon", ""),
                path=menu_data.get("path", ""),
                component=menu_data.get("component"),
                order=menu_data.get("order", 0),
                parent_id=0,  # 先设为0，后面再更新
                is_hidden=menu_data.get("is_hidden", False),
                keepalive=menu_data.get("keepalive", True),
                redirect=menu_data.get("redirect"),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            menus_to_add.append(menu)
        
        # 批量添加并刷新以获取ID
        session.add_all(menus_to_add)
        await session.flush()
        
        # 建立名称到ID的映射
        for menu in menus_to_add:
            menu_id_map[menu.name] = menu.id
        
        # 第二遍：更新parent_id
        for i, menu_data in enumerate(menus_data):
            parent_name = menu_data.get("parent_id")
            if parent_name and isinstance(parent_name, str) and parent_name != 0:
                parent_id = menu_id_map.get(parent_name, 0)
                menus_to_add[i].parent_id = parent_id
        
        await session.commit()
        print(f"✅ 菜单数据初始化完成，共 {len(menus_to_add)} 条")


async def init_api_resources():
    """
    初始化API资源数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(ApiResource))
        if result.scalars().first():
            print("✅ API资源数据已存在，跳过初始化")
            return
        
        print("📝 正在初始化API资源数据...")
        
        # 从JSON文件加载数据
        init_data = load_init_data()
        apis_data = init_data.get("api_resources", [])
        
        if not apis_data:
            print("⚠️ 未找到API资源初始化数据")
            return
        
        api_resources = [
            ApiResource(
                path=api["path"],
                method=api["method"],
                summary=api["summary"],
                tags=api["tags"],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for api in apis_data
        ]
        
        session.add_all(api_resources)
        await session.commit()
        print(f"✅ API资源数据初始化完成，共 {len(api_resources)} 条")


async def init_depts():
    """
    初始化部门数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(Dept))
        if result.scalars().first():
            print("✅ 部门数据已存在，跳过初始化")
            return

        print("📝 正在初始化部门数据...")

        # 从JSON文件加载数据
        init_data = load_init_data()
        depts_data = init_data.get("depts", [])

        if not depts_data:
            print("⚠️ 未找到部门初始化数据")
            return

        # 建立名称到对象的映射
        dept_map = {}
        all_depts = []

        def collect_all_depts(dept_list, parent_name=None):
            """递归收集所有部门数据"""
            for dept_data in dept_list:
                dept = Dept(
                    name=dept_data["name"],
                    desc=dept_data.get("desc", ""),
                    parent_id=0,  # 暂时设为0，后面更新
                    order=dept_data.get("order", 0),
                    is_deleted=False,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                all_depts.append(dept)
                dept_map[dept_data["name"]] = {
                    "obj": dept,
                    "parent_name": parent_name
                }

                # 递归处理子部门
                children = dept_data.get("children", [])
                if children:
                    collect_all_depts(children, dept_data["name"])

        # 收集所有部门（包括子部门）
        collect_all_depts(depts_data, None)

        # 批量添加并刷新以获取ID
        session.add_all(all_depts)
        await session.flush()

        # 更新parent_id
        for dept_name, dept_info in dept_map.items():
            dept_obj = dept_info["obj"]
            parent_name = dept_info["parent_name"]
            if parent_name and parent_name in dept_map:
                dept_obj.parent_id = dept_map[parent_name]["obj"].id

        await session.commit()

        # 初始化部门闭包表
        print("📝 正在初始化部门闭包表...")
        closures = []

        # 为每个部门插入自身记录（level=0）
        for dept in all_depts:
            closures.append(DeptClosure(ancestor=dept.id, descendant=dept.id, level=0))

        # 为每个非根部门插入父部门关系
        for dept in all_depts:
            if dept.parent_id != 0:
                # 查找所有祖先
                current_dept = dept
                level = 0
                while current_dept.parent_id != 0:
                    level += 1
                    # 查找父部门对象
                    for pd in all_depts:
                        if pd.id == current_dept.parent_id:
                            closures.append(DeptClosure(ancestor=pd.id, descendant=dept.id, level=level))
                            current_dept = pd
                            break

        session.add_all(closures)
        await session.commit()
        print(f"✅ 部门数据和闭包表初始化完成，共 {len(all_depts)} 个部门")


async def init_users():
    """
    初始化用户数据
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    from app.core.security import get_password_hash
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化（检查是否有admin用户）
        result = await session.execute(select(User).where(User.username == "admin"))
        if result.scalars().first():
            print("✅ 用户数据已存在，跳过初始化")
            return
        
        print("📝 正在初始化用户数据...")
        
        # 从JSON文件加载数据
        init_data = load_init_data()
        users_data = init_data.get("users", [])
        
        if not users_data:
            print("⚠️ 未找到用户初始化数据")
            return
        
        # 查询所有部门以建立名称映射
        dept_result = await session.execute(select(Dept))
        all_depts = {dept.name: dept.id for dept in dept_result.scalars().all()}
        
        # 默认密码: admin123
        password_hash = get_password_hash("admin123")
        
        # 创建用户
        users = []
        for user_data in users_data:
            username = user_data["username"]
            password = user_data.get("password", "admin123")
            dept_name = user_data.get("dept_name")
            
            # 获取部门ID
            dept_id = all_depts.get(dept_name)
            if not dept_id:
                # 如果找不到指定部门，使用第一个部门
                dept_result = await session.execute(select(Dept).limit(1))
                first_dept = dept_result.scalars().first()
                dept_id = first_dept.id if first_dept else None
            
            user = User(
                username=username,
                alias=user_data.get("alias", username),
                password=get_password_hash(password),
                email=user_data.get("email", f"{username}@example.com"),
                is_active=user_data.get("is_active", True),
                is_superuser=user_data.get("is_superuser", False),
                dept_id=dept_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            users.append(user)
        
        session.add_all(users)
        await session.commit()
        print(f"✅ 用户数据初始化完成，共 {len(users)} 个用户")


async def init_user_roles():
    """
    初始化用户角色关联
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(UserRole))
        if result.scalars().first():
            print("✅ 用户角色关联已存在，跳过初始化")
            return
        
        print("📝 正在初始化用户角色关联...")
        
        # 从JSON文件加载数据
        init_data = load_init_data()
        user_roles_data = init_data.get("user_roles", [])
        
        if not user_roles_data:
            print("⚠️ 未找到用户角色关联初始化数据")
            return
        
        # 建立名称到ID的映射
        user_result = await session.execute(select(User))
        user_map = {user.username: user.id for user in user_result.scalars().all()}
        
        role_result = await session.execute(select(Role))
        role_map = {role.name: role.id for role in role_result.scalars().all()}
        
        # 创建关联
        user_roles = []
        for ur_data in user_roles_data:
            username = ur_data["username"]
            role_name = ur_data["role_name"]
            
            user_id = user_map.get(username)
            role_id = role_map.get(role_name)
            
            if user_id and role_id:
                user_roles.append(
                    UserRole(user_id=user_id, role_id=role_id, created_at=datetime.now())
                )
        
        session.add_all(user_roles)
        await session.commit()
        print(f"✅ 用户角色关联初始化完成，共 {len(user_roles)} 条")


async def init_role_menus():
    """
    初始化角色菜单关联
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(RoleMenu))
        if result.scalars().first():
            print("✅ 角色菜单关联已存在，跳过初始化")
            return
        
        print("📝 正在初始化角色菜单关联...")
        
        # 从JSON文件加载数据
        init_data = load_init_data()
        role_menus_data = init_data.get("role_menus", [])
        
        if not role_menus_data:
            print("⚠️ 未找到角色菜单关联初始化数据")
            return
        
        # 建立名称到ID的映射
        role_result = await session.execute(select(Role))
        role_map = {role.name: role.id for role in role_result.scalars().all()}
        
        menu_result = await session.execute(select(Menu))
        menu_map = {menu.name: menu.id for menu in menu_result.scalars().all()}
        
        # 创建关联
        role_menus = []
        for rm_data in role_menus_data:
            role_name = rm_data["role_name"]
            role_id = role_map.get(role_name)
            
            if not role_id:
                continue
            
            all_menus_flag = rm_data.get("all_menus", False)
            
            if all_menus_flag:
                # 角色拥有所有菜单权限
                for menu_id in menu_map.values():
                    role_menus.append(
                        RoleMenu(role_id=role_id, menu_id=menu_id, created_at=datetime.now())
                    )
            else:
                # 角色拥有指定菜单
                menu_names = rm_data.get("menu_names", [])
                for menu_name in menu_names:
                    menu_id = menu_map.get(menu_name)
                    if menu_id:
                        role_menus.append(
                            RoleMenu(role_id=role_id, menu_id=menu_id, created_at=datetime.now())
                        )
        
        session.add_all(role_menus)
        await session.commit()
        print(f"✅ 角色菜单关联初始化完成，共 {len(role_menus)} 条")


async def init_role_apis():
    """
    初始化角色API关联
    """
    from sqlalchemy import select
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        result = await session.execute(select(RoleApi))
        if result.scalars().first():
            print("✅ 角色API关联已存在，跳过初始化")
            return
        
        print("📝 正在初始化角色API关联...")
        
        # 从JSON文件加载数据
        init_data = load_init_data()
        role_apis_data = init_data.get("role_apis", [])
        
        if not role_apis_data:
            print("⚠️ 未找到角色API关联初始化数据")
            return
        
        # 建立名称到ID的映射
        role_result = await session.execute(select(Role))
        role_map = {role.name: role.id for role in role_result.scalars().all()}
        
        api_result = await session.execute(select(ApiResource))
        api_map = {api.path: api.id for api in api_result.scalars().all()}
        
        # 创建关联
        role_apis = []
        for ra_data in role_apis_data:
            role_name = ra_data["role_name"]
            role_id = role_map.get(role_name)
            
            if not role_id:
                continue
            
            all_apis_flag = ra_data.get("all_apis", False)
            
            if all_apis_flag:
                # 角色拥有所有API权限
                for api_id in api_map.values():
                    role_apis.append(
                        RoleApi(role_id=role_id, api_id=api_id, created_at=datetime.now())
                    )
            else:
                # 角色拥有指定API权限
                api_filter = ra_data.get("api_filter", "")
                if api_filter:
                    for api_path, api_id in api_map.items():
                        if api_filter in api_path.lower():
                            role_apis.append(
                                RoleApi(role_id=role_id, api_id=api_id, created_at=datetime.now())
                            )
        
        session.add_all(role_apis)
        await session.commit()
        print(f"✅ 角色API关联初始化完成，共 {len(role_apis)} 条")


async def init_database():
    """
    初始化数据库（创建表和初始化数据）
    这是应用启动时调用的主函数
    """
    print("=" * 60)
    print("🚀 开始初始化数据库...")
    print("=" * 60)
    
    try:
        # 1. 创建所有表
        await create_tables()
        
        # 2. 初始化基础数据
        await init_roles()
        await init_menus()
        await init_api_resources()
        await init_depts()
        
        # 3. 初始化用户数据
        await init_users()
        
        # 4. 初始化关联数据
        await init_user_roles()
        await init_role_menus()
        await init_role_apis()
        
        print("=" * 60)
        print("✅ 数据库初始化完成！")
        print("=" * 60)
        
        # 显示登录信息
        init_data = load_init_data()
        users_data = init_data.get("users", [])
        if users_data:
            print("默认登录账号:")
            for user_data in users_data:
                password = user_data.get("password", "admin123")
                alias = user_data.get("alias", user_data["username"])
                print(f"  {alias}: {user_data['username']} / {password}")
            print("=" * 60)
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        raise


async def reset_database():
    """
    重置数据库（删除所有表并重新创建）
    警告：此操作会删除所有数据！
    """
    from sqlalchemy import text
    from app.db.session import engine, create_database_engine

    # 确保引擎已初始化
    if engine is None:
        await create_database_engine()

    print("⚠️  警告：正在重置数据库，所有数据将被删除！")

    async with engine.begin() as conn:
        # 删除所有表
        await conn.run_sync(Base.metadata.drop_all)
        print("🗑️  数据库表已删除")
        
        # 重新创建表
        await conn.run_sync(Base.metadata.create_all)
        print("🔨 数据库表已重新创建")
    
    # 重新初始化数据
    await init_database()
