# Copyright (c) 2025 左岚. All rights reserved.
"""系统统一初始化脚本 - 整合所有初始化功能"""
import asyncio
import sys
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from passlib.context import CryptContext

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
from app.models.ai_chat import AIModel, ChatSession, ChatMessage
from app.models.knowledge import KnowledgeBase, Document, DocumentChunk, SearchHistory

# 导入插件模型
from app.plugins.api_engine.models import ApiEngineSuite, ApiEngineCase, ApiEngineExecution, ApiEngineKeyword
from app.plugins.api_engine.init_db import init_api_engine_plugin_db

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def init_database():
    """初始化数据库和所有数据"""
    print("=" * 80)
    print("AI Agent Testing Platform - 系统初始化")
    print("=" * 80)
    print()
    
    # 创建异步引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # 创建所有表
    print("📦 步骤 1/4: 创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")
    print()
    
    # 创建会话
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as session:
        # ==================== 步骤 2: 初始化基础数据 ====================
        print("📦 步骤 2/4: 初始化基础数据（用户、角色、菜单、部门）...")
        
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
        
        print("✅ 基础数据初始化完成")
        print()
        
        # ==================== 步骤 3: 初始化AI模型配置 ====================
        print("📦 步骤 3/4: 初始化AI模型配置...")
        
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
        
        print("✅ AI模型配置初始化完成")
        print()
        
        # ==================== 步骤 4: 初始化插件数据 ====================
        print("📦 步骤 4/5: 初始化API引擎插件数据...")
        try:
            await init_api_engine_plugin_db(session)
            print("✅ API引擎插件数据初始化完成")
        except Exception as e:
            print(f"⚠️  API引擎插件初始化失败: {e}")
        print()
        
        # ==================== 步骤 5: 提交所有更改 ====================
        print("📦 步骤 5/5: 提交数据到数据库...")
        await session.commit()
        print("✅ 数据提交完成")
        print()

    await engine.dispose()
    
    # ==================== 打印初始化总结 ====================
    print("=" * 80)
    print("✅ 系统初始化完成!")
    print("=" * 80)
    print()
    print("📊 初始化统计:")
    print("  ✓ 部门: 1个")
    print("  ✓ 角色: 1个")
    print("  ✓ 菜单: 5个 (2个菜单 + 3个按钮)")
    print("  ✓ 用户: 1个")
    print("  ✓ 通知: 3条")
    print("  ✓ 测试用例: 3个")
    print("  ✓ AI模型: 6个")
    print("  ✓ API引擎插件: 1个套件 + 2个示例用例")
    print()
    print("🔑 登录凭证:")
    print("  用户名: BNTang")
    print("  密码: 1234qwer")
    print()
    print("🚀 快速开始:")
    print("  1. 启动Redis: redis-server")
    print("  2. 启动Celery Worker: python start_celery_worker.py")
    print("  3. 启动FastAPI服务: python run.py")
    print("  4. 访问API文档: http://localhost:8000/docs")
    print()
    print("📚 功能模块:")
    print("  ✓ 用户管理、角色管理、菜单管理、部门管理")
    print("  ✓ 测试用例管理（API/Web/App）")
    print("  ✓ AI智能助手（多模型对话、流式响应）")
    print("  ✓ RAG知识库（文档上传、语义搜索）")
    print("  ✓ 任务队列（异步处理大文件）")
    print("  ✓ 消息通知、数据管理")
    print("  ✓ API引擎插件（接口自动化测试）")
    print()
    print("⚙️  配置AI模型:")
    print("  1. 访问: http://localhost:8000/docs")
    print("  2. 使用 PUT /api/v1/ai/models/{id} 配置API Key")
    print("  3. OpenAI Key: https://platform.openai.com/api-keys")
    print("  4. Claude Key: https://console.anthropic.com/settings/keys")
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(init_database())

