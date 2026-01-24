#!/usr/bin/env python3
"""
初始化数据库数据脚本
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import create_database_engine, AsyncSessionLocal
from app.db.init_menu_data import init_all_menu_data


async def main():
    print("正在初始化数据库...")
    
    # 创建数据库引擎
    engine = await create_database_engine()
    
    # 创建会话
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    # 初始化数据
    async with AsyncSessionLocal() as db:
        await init_all_menu_data(db)
    
    print("数据库初始化完成！")
    print("默认管理员账号: admin")
    print("默认管理员密码: admin123")


if __name__ == "__main__":
    asyncio.run(main())
