"""初始化数据库和测试数据 - 完全按照博客数据结构"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.models.department import Department
from app.models.user_role import t_user_role
from app.models.role_menu import t_role_menu

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_database():
    """初始化数据库和测试数据"""
    # 创建异步引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        # 1. 创建部门（对应博客数据）
        dept = Department(
            parent_id=0,
            dept_name="开发部",
            order_num=1,
            create_time=datetime.strptime("2018-01-04 15:42:26", "%Y-%m-%d %H:%M:%S"),
            modify_time=datetime.strptime("2019-01-05 21:08:27", "%Y-%m-%d %H:%M:%S")
        )
        session.add(dept)
        await session.flush()
        
        # 2. 创建角色（对应博客数据）
        role = Role(
            role_name="管理员",
            remark="管理员",
            create_time=datetime.strptime("2017-12-27 16:23:11", "%Y-%m-%d %H:%M:%S"),
            modify_time=datetime.strptime("2019-01-21 08:45:02", "%Y-%m-%d %H:%M:%S")
        )
        session.add(role)
        await session.flush()
        
        # 3. 创建菜单（对应博客数据）
        menus = [
            Menu(
                parent_id=0,
                menu_name="系统管理",
                path="/system",
                component="Layout",
                perms=None,
                icon="el-icon-set-up",
                type="0",
                order_num=1,
                create_time=datetime.strptime("2017-12-27 16:39:07", "%Y-%m-%d %H:%M:%S"),
                modify_time=datetime.strptime("2019-07-20 16:19:04", "%Y-%m-%d %H:%M:%S")
            ),
            Menu(
                parent_id=1,
                menu_name="用户管理",
                path="/system/user",
                component="bntang/system/user/Index",
                perms="user:view",
                icon="",
                type="0",
                order_num=1,
                create_time=datetime.strptime("2017-12-27 16:47:13", "%Y-%m-%d %H:%M:%S"),
                modify_time=datetime.strptime("2019-01-22 06:45:55", "%Y-%m-%d %H:%M:%S")
            ),
            Menu(
                parent_id=2,
                menu_name="新增用户",
                path="",
                component="",
                perms="user:add",
                icon=None,
                type="1",
                order_num=None,
                create_time=datetime.strptime("2017-12-27 17:02:58", "%Y-%m-%d %H:%M:%S"),
                modify_time=None
            ),
            Menu(
                parent_id=2,
                menu_name="修改用户",
                path="",
                component="",
                perms="user:update",
                icon=None,
                type="1",
                order_num=None,
                create_time=datetime.strptime("2017-12-27 17:04:07", "%Y-%m-%d %H:%M:%S"),
                modify_time=None
            ),
            Menu(
                parent_id=2,
                menu_name="删除用户",
                path="",
                component="",
                perms="user:delete",
                icon=None,
                type="1",
                order_num=None,
                create_time=datetime.strptime("2017-12-27 17:04:58", "%Y-%m-%d %H:%M:%S"),
                modify_time=None
            ),
        ]
        session.add_all(menus)
        await session.flush()
        
        # 4. 创建用户（对应博客数据）
        # 密码为 1234qwer 经过 BCrypt 加密
        user = User(
            username="BNTang",
            password="$2a$10$gzhiUb1ldc1Rf3lka4k/WOoFKKGPepHSzJxzcPSN5/65SzkMdc.SK",
            dept_id=1,
            email="303158131@qq.com",
            mobile="17788888888",
            status="1",
            create_time=datetime.strptime("2019-06-14 20:39:22", "%Y-%m-%d %H:%M:%S"),
            modify_time=datetime.strptime("2019-07-19 10:18:36", "%Y-%m-%d %H:%M:%S"),
            last_login_time=datetime.strptime("2019-08-02 15:57:00", "%Y-%m-%d %H:%M:%S"),
            ssex="0",
            avatar="default.jpg",
            description="我是帅比作者。"
        )
        session.add(user)
        await session.flush()
        
        # 5. 用户角色关联（对应博客数据）
        await session.execute(
            t_user_role.insert().values(user_id=user.user_id, role_id=role.role_id)
        )
        
        # 6. 角色菜单关联（对应博客数据）
        for menu in menus:
            await session.execute(
                t_role_menu.insert().values(role_id=role.role_id, menu_id=menu.menu_id)
            )
        
        await session.commit()
    
    print("✅ 数据库初始化完成！")
    print("\n初始化的数据（完全对应博客）:")
    print("="*60)
    print("📁 部门 (t_dept):")
    print("  - dept_id=1, dept_name='开发部', parent_id=0")
    print("\n🎭 角色 (t_role):")
    print("  - role_id=1, role_name='管理员'")
    print("\n📋 菜单 (t_menu):")
    print("  - menu_id=1, menu_name='系统管理', type='0' (菜单)")
    print("  - menu_id=2, menu_name='用户管理', type='0' (菜单)")
    print("  - menu_id=3, menu_name='新增用户', type='1' (按钮), perms='user:add'")
    print("  - menu_id=4, menu_name='修改用户', type='1' (按钮), perms='user:update'")
    print("  - menu_id=5, menu_name='删除用户', type='1' (按钮), perms='user:delete'")
    print("\n👤 用户 (t_user):")
    print("  - user_id=1, username='BNTang', password='1234qwer' (已加密)")
    print("  - email='303158131@qq.com', mobile='17788888888'")
    print("  - status='1' (有效), ssex='0' (男)")
    print("\n🔗 关联关系:")
    print("  - t_user_role: user_id=1 ↔ role_id=1 (BNTang是管理员)")
    print("  - t_role_menu: role_id=1 拥有所有5个菜单/按钮权限")
    print("="*60)
    print("\n📚 数据库表结构完全对应博客:")
    print("  https://www.cnblogs.com/BNTang/articles/17024549.html")
    print("\n🚀 启动服务: python run.py")
    print("📖 API文档: http://localhost:8000/docs")
    print("\n🔑 登录凭证:")
    print("  用户名: BNTang")
    print("  密码: 1234qwer")


if __name__ == "__main__":
    asyncio.run(init_database())
