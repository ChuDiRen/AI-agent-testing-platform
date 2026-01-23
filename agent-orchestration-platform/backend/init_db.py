#!/usr/bin/env python3
"""
数据库初始化脚本
用于在开发环境下初始化SQLite数据库
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import init_db, AsyncSessionLocal
from app.core.logger import setup_logger
from app.core.security import AuthService
from app.models.user import User
from app.schemas.user_schema import UserCreate

logger = setup_logger(name="init_db", level="INFO")


async def create_admin_user():
    """创建管理员账号"""
    async with AsyncSessionLocal() as session:
        try:
            # 检查是否已存在 admin 用户
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.info("管理员账号已存在，跳过创建")
                return
            
            # 创建 admin 用户
            admin_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=AuthService.get_password_hash("admin123456"),
                is_active=True,
                is_superuser=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            logger.info("✅ 管理员账号创建成功 (admin/admin123456)")
            print("✅ 管理员账号创建成功 (admin/admin123456)")
            
        except Exception as e:
            await session.rollback()
            raise e


async def main():
    """主函数"""
    try:
        logger.info("开始初始化数据库...")
        await init_db()
        logger.info("✅ 数据库表创建完成！")
        
        logger.info("创建管理员账号...")
        await create_admin_user()
        
        logger.info("✅ 数据库初始化完成！")
        print("✅ 数据库初始化完成！")
        print("📝 管理员账号: admin")
        print("🔑 管理员密码: admin123456")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
