# Copyright (c) 2025 左岚. All rights reserved.
"""完整系统初始化脚本"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    """主函数"""
    print("=" * 60)
    print("AI Agent Testing Platform - 系统初始化")
    print("=" * 60)
    print()
    
    # 1. 初始化数据库
    print("步骤 1/3: 初始化数据库...")
    from app.core.database import init_db
    await init_db()
    print("✓ 数据库初始化完成")
    print()
    
    # 2. 初始化基础数据（用户、角色、菜单等）
    print("步骤 2/3: 初始化基础数据...")
    from init_data import init_data
    await init_data()
    print("✓ 基础数据初始化完成")
    print()
    
    # 3. 初始化AI模型配置
    print("步骤 3/3: 初始化AI模型配置...")
    from init_ai_models import init_ai_models
    await init_ai_models()
    print("✓ AI模型配置初始化完成")
    print()
    
    print("=" * 60)
    print("系统初始化完成！")
    print("=" * 60)
    print()
    print("快速开始:")
    print("  1. 启动服务: python run.py")
    print("  2. 访问文档: http://localhost:8000/docs")
    print("  3. 默认账号: BNTang / 1234qwer")
    print()
    print("功能模块:")
    print("  ✓ 用户管理、角色管理、菜单管理、部门管理")
    print("  ✓ 测试用例管理（API/Web/App）")
    print("  ✓ 测试报告生成与导出")
    print("  ✓ AI智能助手（聊天、用例生成）")
    print("  ✓ 消息通知、数据管理")
    print()


if __name__ == "__main__":
    asyncio.run(main())

