# Copyright (c) 2025 左岚. All rights reserved.
"""数据库连接配置 - 增强版"""
import logging
from typing import AsyncGenerator
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import select
from app.core.config import settings

logger = logging.getLogger(__name__)

# 数据库引擎配置
engine_kwargs = {
    "echo": settings.DB_ECHO,
    "future": True,
}

# 根据数据库类型配置连接池
if "sqlite" in settings.DATABASE_URL:
    # SQLite 不支持连接池
    engine_kwargs["poolclass"] = NullPool
else:
    # 其他数据库使用连接池
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,  # 检测连接有效性
        "poolclass": QueuePool
    })

# 创建异步引擎
engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """SQLAlchemy基础模型"""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    
    Yields:
        AsyncSession: 数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"数据库会话异常: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库表结构"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def check_db_health() -> bool:
    """
    检查数据库健康状态
    
    Returns:
        bool: 数据库是否健康
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return False


async def close_db():
    """关闭数据库连接"""
    try:
        await engine.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭数据库连接失败: {e}")


async def check_db_empty() -> bool:
    """检查数据库是否为空（通过检查User表）"""
    try:
        from app.models.user import User  # 延迟导入避免循环依赖
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            return user is None  # 如果没有用户，说明数据库为空
    except Exception as e:
        logger.warning(f"检查数据库状态失败: {e}")
        return True  # 出错时假设为空，触发初始化


async def init_data():
    """初始化数据库数据（仅在数据库为空时执行）"""
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.menu import Menu
        from app.models.department import Department
        from app.models.user_role import t_user_role
        from app.models.role_menu import t_role_menu
        from app.models.notification import Notification
        from app.models.testcase import TestCase
        from app.models.ai_chat import AIModel

        logger.info("📦 开始初始化数据库数据...")

        async with AsyncSessionLocal() as session:
            # 1. 创建部门
            dept = Department(
                parent_id=0, dept_name="开发部", order_num=1,
                create_time=datetime.strptime("2018-01-04 15:42:26", "%Y-%m-%d %H:%M:%S"),
                modify_time=datetime.strptime("2019-01-05 21:08:27", "%Y-%m-%d %H:%M:%S")
            )
            session.add(dept)
            await session.flush()

            # 2. 创建角色
            role = Role(
                role_name="管理员", remark="管理员",
                create_time=datetime.strptime("2017-12-27 16:23:11", "%Y-%m-%d %H:%M:%S"),
                modify_time=datetime.strptime("2019-01-21 08:45:02", "%Y-%m-%d %H:%M:%S")
            )
            session.add(role)
            await session.flush()

            # 3. 创建菜单
            menu_system = Menu(
                parent_id=0, menu_name="系统管理", path="/system", component="Layout",
                perms=None, icon="el-icon-set-up", type="0", order_num=1,
                create_time=datetime.strptime("2017-12-27 16:39:07", "%Y-%m-%d %H:%M:%S"),
                modify_time=datetime.strptime("2019-07-20 16:19:04", "%Y-%m-%d %H:%M:%S")
            )
            session.add(menu_system)
            await session.flush()

            menu_user = Menu(
                parent_id=menu_system.menu_id, menu_name="用户管理",
                path="/system/user", component="bntang/system/user/Index",
                perms="user:view", icon="", type="0", order_num=1,
                create_time=datetime.strptime("2017-12-27 16:47:13", "%Y-%m-%d %H:%M:%S"),
                modify_time=datetime.strptime("2019-01-22 06:45:55", "%Y-%m-%d %H:%M:%S")
            )
            session.add(menu_user)
            await session.flush()

            menu_buttons = [
                Menu(parent_id=menu_user.menu_id, menu_name="新增用户", path="", component="",
                     perms="user:add", icon=None, type="1", order_num=None,
                     create_time=datetime.strptime("2017-12-27 17:02:58", "%Y-%m-%d %H:%M:%S"), modify_time=None),
                Menu(parent_id=menu_user.menu_id, menu_name="修改用户", path="", component="",
                     perms="user:update", icon=None, type="1", order_num=None,
                     create_time=datetime.strptime("2017-12-27 17:04:07", "%Y-%m-%d %H:%M:%S"), modify_time=None),
                Menu(parent_id=menu_user.menu_id, menu_name="删除用户", path="", component="",
                     perms="user:delete", icon=None, type="1", order_num=None,
                     create_time=datetime.strptime("2017-12-27 17:04:58", "%Y-%m-%d %H:%M:%S"), modify_time=None),
            ]
            session.add_all(menu_buttons)
            await session.flush()

            menus = [menu_system, menu_user] + menu_buttons

            # 4. 创建用户
            user = User(
                username="BNTang",
                password="$2a$10$gzhiUb1ldc1Rf3lka4k/WOoFKKGPepHSzJxzcPSN5/65SzkMdc.SK",  # 1234qwer
                dept_id=1, email="303158131@qq.com", mobile="17788888888", status="1",
                create_time=datetime.strptime("2019-06-14 20:39:22", "%Y-%m-%d %H:%M:%S"),
                modify_time=datetime.strptime("2019-07-19 10:18:36", "%Y-%m-%d %H:%M:%S"),
                last_login_time=datetime.strptime("2019-08-02 15:57:00", "%Y-%m-%d %H:%M:%S"),
                ssex="0", avatar="default.jpg", description="我是帅比作者。"
            )
            session.add(user)
            await session.flush()

            # 5. 用户角色关联
            await session.execute(t_user_role.insert().values(user_id=user.user_id, role_id=role.role_id))

            # 6. 角色菜单关联
            for menu in menus:
                await session.execute(t_role_menu.insert().values(role_id=role.role_id, menu_id=menu.menu_id))

            # 7. 创建通知数据
            notifications = [
                Notification(user_id=user.user_id, title="欢迎使用AI测试平台",
                            content="欢迎使用AI智能测试平台!系统已为您准备好所有功能模块。",
                            type="system", is_read=False, create_time=datetime.now()),
                Notification(user_id=user.user_id, title="系统通知",
                            content="系统将于今晚22:00进行维护,预计维护时间1小时。",
                            type="system", is_read=False, create_time=datetime.now()),
                Notification(user_id=user.user_id, title="测试报告生成完成",
                            content="API测试报告\"用户模块测试\"已生成完成,通过率85%。",
                            type="test", is_read=False, create_time=datetime.now()),
            ]
            session.add_all(notifications)

            # 8. 创建测试用例
            testcases = [
                TestCase(name="用户登录功能测试", test_type="API", module="用户管理",
                        description="测试用户登录接口的各种场景", preconditions="用户已注册",
                        test_steps="1. 发送POST请求到/api/v1/auth/login\n2. 传入用户名和密码\n3. 验证返回结果",
                        expected_result="返回token和用户信息", priority="P0", status="active",
                        tags="登录,认证", created_by=1),
                TestCase(name="用户列表页面测试", test_type="WEB", module="用户管理",
                        description="测试用户列表页面的显示和操作", preconditions="已登录系统",
                        test_steps="1. 访问用户管理页面\n2. 检查列表数据\n3. 测试搜索功能\n4. 测试分页功能",
                        expected_result="页面正常显示,功能正常", priority="P1", status="active",
                        tags="用户,列表", created_by=1),
                TestCase(name="移动端登录测试", test_type="APP", module="移动端",
                        description="测试移动应用的登录功能", preconditions="应用已安装",
                        test_steps="1. 打开应用\n2. 输入用户名密码\n3. 点击登录按钮\n4. 验证跳转",
                        expected_result="成功登录并跳转到首页", priority="P1", status="draft",
                        tags="移动端,登录", created_by=1),
            ]
            session.add_all(testcases)

            # 9. 创建AI模型配置
            models = [
                AIModel(name="GPT-3.5 Turbo", provider="openai", model_key="gpt-3.5-turbo",
                       api_base="https://api.openai.com/v1", max_tokens=4096, temperature="0.7",
                       is_enabled=False, description="OpenAI GPT-3.5 Turbo模型，适合日常对话和测试用例生成"),
                AIModel(name="GPT-4", provider="openai", model_key="gpt-4",
                       api_base="https://api.openai.com/v1", max_tokens=8192, temperature="0.7",
                       is_enabled=False, description="OpenAI GPT-4模型，更强大的推理能力"),
                AIModel(name="GPT-4 Turbo", provider="openai", model_key="gpt-4-turbo-preview",
                       api_base="https://api.openai.com/v1", max_tokens=128000, temperature="0.7",
                       is_enabled=False, description="OpenAI GPT-4 Turbo模型，支持更长上下文"),
                AIModel(name="Claude 3 Sonnet", provider="claude", model_key="claude-3-sonnet-20240229",
                       api_base="https://api.anthropic.com/v1", max_tokens=4096, temperature="0.7",
                       is_enabled=False, description="Anthropic Claude 3 Sonnet模型，平衡性能和成本"),
                AIModel(name="Claude 3 Opus", provider="claude", model_key="claude-3-opus-20240229",
                       api_base="https://api.anthropic.com/v1", max_tokens=4096, temperature="0.7",
                       is_enabled=False, description="Anthropic Claude 3 Opus模型，最强推理能力"),
                AIModel(name="Claude 3.5 Sonnet", provider="claude", model_key="claude-3-5-sonnet-20241022",
                       api_base="https://api.anthropic.com/v1", max_tokens=8192, temperature="0.7",
                       is_enabled=False, description="Anthropic Claude 3.5 Sonnet模型，最新版本")
            ]
            session.add_all(models)

            # 10. 初始化API引擎插件数据
            logger.info("📦 初始化API引擎插件数据...")
            try:
                from app.plugins.api_engine.init_db import init_api_engine_plugin_db
                await init_api_engine_plugin_db(session)
                logger.info("✅ API引擎插件数据初始化完成")
            except Exception as e:
                logger.warning(f"⚠️  API引擎插件数据初始化失败: {e}")

            # 提交所有更改
            await session.commit()

        logger.info("✅ 数据库数据初始化完成")
        logger.info("🔑 默认用户: BNTang / 1234qwer")

    except Exception as e:
        logger.error(f"❌ 数据库数据初始化失败: {e}")
        raise

