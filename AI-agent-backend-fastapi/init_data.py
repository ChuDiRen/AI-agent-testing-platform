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
from app.models.notification import Notification
from app.models.testcase import TestCase

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
        # 注意: 不手动指定dept_id,让数据库自动生成
        dept = Department(
            parent_id=0,
            dept_name="开发部",
            order_num=1,
            create_time=datetime.strptime("2018-01-04 15:42:26", "%Y-%m-%d %H:%M:%S"),
            modify_time=datetime.strptime("2019-01-05 21:08:27", "%Y-%m-%d %H:%M:%S")
        )
        session.add(dept)
        await session.flush()  # flush后dept.dept_id会被自动赋值

        # 2. 创建角色（对应博客数据）
        # 注意: 不手动指定role_id,让数据库自动生成
        role = Role(
            role_name="管理员",
            remark="管理员",
            create_time=datetime.strptime("2017-12-27 16:23:11", "%Y-%m-%d %H:%M:%S"),
            modify_time=datetime.strptime("2019-01-21 08:45:02", "%Y-%m-%d %H:%M:%S")
        )
        session.add(role)
        await session.flush()  # flush后role.role_id会被自动赋值
        
        # 3. 创建菜单（对应博客数据）
        # 注意: 不手动指定menu_id,让数据库自动生成
        # 先创建父菜单
        menu_system = Menu(
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
        )
        session.add(menu_system)
        await session.flush()  # flush后menu_system.menu_id会被自动赋值

        # 创建子菜单
        menu_user = Menu(
            parent_id=menu_system.menu_id,
            menu_name="用户管理",
            path="/system/user",
            component="bntang/system/user/Index",
            perms="user:view",
            icon="",
            type="0",
            order_num=1,
            create_time=datetime.strptime("2017-12-27 16:47:13", "%Y-%m-%d %H:%M:%S"),
            modify_time=datetime.strptime("2019-01-22 06:45:55", "%Y-%m-%d %H:%M:%S")
        )
        session.add(menu_user)
        await session.flush()  # flush后menu_user.menu_id会被自动赋值

        # 创建按钮权限
        menu_buttons = [
            Menu(
                parent_id=menu_user.menu_id,
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
                parent_id=menu_user.menu_id,
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
                parent_id=menu_user.menu_id,
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
        session.add_all(menu_buttons)
        await session.flush()

        # 收集所有菜单用于后续关联
        menus = [menu_system, menu_user] + menu_buttons
        
        # 4. 创建用户（对应博客数据）
        # 密码为 1234qwer 经过 BCrypt 加密
        # 注意: 不手动指定user_id,让数据库自动生成,确保自增序列正确初始化
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
        await session.flush()  # flush后user.user_id会被自动赋值
        
        # 5. 用户角色关联（对应博客数据）
        await session.execute(
            t_user_role.insert().values(user_id=user.user_id, role_id=role.role_id)
        )
        
        # 6. 角色菜单关联（对应博客数据）
        for menu in menus:
            await session.execute(
                t_role_menu.insert().values(role_id=role.role_id, menu_id=menu.menu_id)
            )

        # 7. 创建初始通知数据
        notifications = [
            Notification(
                user_id=user.user_id,
                title="欢迎使用AI测试平台",
                content="欢迎使用AI智能测试平台!系统已为您准备好所有功能模块。",
                type="system",
                is_read=False,
                create_time=datetime.now()
            ),
            Notification(
                user_id=user.user_id,
                title="系统通知",
                content="系统将于今晚22:00进行维护,预计维护时间1小时。",
                type="system",
                is_read=False,
                create_time=datetime.now()
            ),
            Notification(
                user_id=user.user_id,
                title="测试报告生成完成",
                content="API测试报告\"用户模块测试\"已生成完成,通过率85%。",
                type="test",
                is_read=False,
                create_time=datetime.now()
            ),
            Notification(
                user_id=user.user_id,
                title="测试用例执行失败",
                content="测试用例\"登录功能测试\"执行失败,请查看详细信息。",
                type="error",
                is_read=True,
                create_time=datetime.now()
            ),
            Notification(
                user_id=user.user_id,
                title="权限变更通知",
                content="您的系统权限已更新,新增\"测试报告导出\"权限。",
                type="info",
                is_read=True,
                create_time=datetime.now()
            ),
        ]
        session.add_all(notifications)

        # 7. 创建测试用例示例数据
        print("\n📝 创建测试用例示例数据...")
        testcases = [
            TestCase(
                name="用户登录功能测试",
                test_type="API",
                module="用户管理",
                description="测试用户登录接口的各种场景",
                preconditions="用户已注册",
                test_steps="1. 发送POST请求到/api/v1/auth/login\n2. 传入用户名和密码\n3. 验证返回结果",
                expected_result="返回token和用户信息",
                priority="P0",
                status="active",
                tags="登录,认证",
                created_by=1
            ),
            TestCase(
                name="用户列表页面测试",
                test_type="WEB",
                module="用户管理",
                description="测试用户列表页面的显示和操作",
                preconditions="已登录系统",
                test_steps="1. 访问用户管理页面\n2. 检查列表数据\n3. 测试搜索功能\n4. 测试分页功能",
                expected_result="页面正常显示,功能正常",
                priority="P1",
                status="active",
                tags="用户,列表",
                created_by=1
            ),
            TestCase(
                name="移动端登录测试",
                test_type="APP",
                module="移动端",
                description="测试移动应用的登录功能",
                preconditions="应用已安装",
                test_steps="1. 打开应用\n2. 输入用户名密码\n3. 点击登录按钮\n4. 验证跳转",
                expected_result="成功登录并跳转到首页",
                priority="P1",
                status="draft",
                tags="移动端,登录",
                created_by=1
            ),
            TestCase(
                name="角色权限API测试",
                test_type="API",
                module="权限管理",
                description="测试角色权限相关接口",
                preconditions="管理员已登录",
                test_steps="1. 创建角色\n2. 分配权限\n3. 验证权限生效",
                expected_result="权限正确分配和生效",
                priority="P2",
                status="active",
                tags="权限,角色",
                created_by=1
            ),
            TestCase(
                name="数据导出功能测试",
                test_type="WEB",
                module="数据管理",
                description="测试数据导出为CSV和JSON",
                preconditions="有数据可导出",
                test_steps="1. 点击导出按钮\n2. 选择导出格式\n3. 下载文件\n4. 验证文件内容",
                expected_result="文件正确下载,数据完整",
                priority="P2",
                status="active",
                tags="导出,数据",
                created_by=1
            )
        ]

        for tc in testcases:
            session.add(tc)

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
