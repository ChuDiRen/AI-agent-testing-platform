# Copyright (c) 2025 左岚. All rights reserved.
"""
完整数据初始化脚本
统一管理所有初始化数据的创建和清除
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.logger import get_logger
from app.db.session import create_tables, drop_tables

logger = get_logger(__name__)


def init_complete_database():
    """
    完整的数据库初始化
    包括表结构创建和所有示例数据
    """
    try:
        logger.info("开始完整数据库初始化...")
        
        # 1. 创建数据库表结构
        logger.info("创建数据库表结构...")
        create_tables()
        
        # 2. 创建基础RBAC数据
        logger.info("创建基础RBAC数据...")
        from init_db import create_initial_data
        create_initial_data()
        
        # 3. 创建演示数据（可选）
        logger.info("创建演示数据...")
        from seed_data import create_demo_data
        create_demo_data()
        
        logger.info("完整数据库初始化成功！")
        print_initialization_summary()
        
    except Exception as e:
        logger.error(f"完整数据库初始化失败: {str(e)}")
        raise


def init_ai_data_only():
    """
    仅初始化AI相关数据
    适用于已有基础数据的情况
    """
    try:
        logger.info("开始AI数据初始化...")
        
        # 创建AI模型配置
        logger.info("创建AI模型配置...")
        from init_ai_models import create_ai_model_configs
        create_ai_model_configs()
        
        # 创建AI代理示例
        logger.info("创建AI代理示例...")
        from init_agents import create_agent_examples
        create_agent_examples()
        
        # 创建测试用例模板
        logger.info("创建测试用例模板...")
        from init_test_cases import create_test_case_templates
        create_test_case_templates()
        
        # 创建测试报告示例
        logger.info("创建测试报告示例...")
        from init_test_reports import create_test_report_examples
        create_test_report_examples()
        
        # 创建生成历史数据
        logger.info("创建生成历史数据...")
        from init_generation_history import create_generation_history_examples
        create_generation_history_examples()
        
        logger.info("AI数据初始化成功！")
        print_ai_data_summary()
        
    except Exception as e:
        logger.error(f"AI数据初始化失败: {str(e)}")
        raise


def clear_all_data():
    """
    清除所有示例数据
    保留基础的RBAC结构
    """
    try:
        logger.info("开始清除所有示例数据...")
        
        # 清除生成历史数据
        logger.info("清除生成历史数据...")
        from init_generation_history import clear_generation_history_examples
        clear_generation_history_examples()
        
        # 清除测试报告数据
        logger.info("清除测试报告数据...")
        from init_test_reports import clear_test_report_examples
        clear_test_report_examples()
        
        # 清除测试用例数据
        logger.info("清除测试用例数据...")
        from init_test_cases import clear_test_case_templates
        clear_test_case_templates()
        
        # 清除AI代理数据
        logger.info("清除AI代理数据...")
        from init_agents import clear_agent_examples
        clear_agent_examples()
        
        # 清除AI模型配置
        logger.info("清除AI模型配置...")
        from init_ai_models import clear_ai_model_configs
        clear_ai_model_configs()
        
        # 清除演示数据
        logger.info("清除演示数据...")
        from seed_data import clear_demo_data
        clear_demo_data()
        
        logger.info("所有示例数据清除成功！")
        
    except Exception as e:
        logger.error(f"清除示例数据失败: {str(e)}")
        raise


def reset_complete_database():
    """
    完全重置数据库
    删除所有表并重新创建
    """
    try:
        logger.warning("开始完全重置数据库...")
        
        # 删除所有表
        drop_tables()
        logger.info("数据库表已删除")
        
        # 重新初始化
        init_complete_database()
        
        logger.info("数据库完全重置成功！")
        
    except Exception as e:
        logger.error(f"数据库重置失败: {str(e)}")
        raise


def print_initialization_summary():
    """
    打印初始化摘要信息
    """
    print("\n" + "="*60)
    print("🎉 AI代理测试平台初始化完成！")
    print("="*60)
    print("📊 已创建的数据：")
    print("   • 用户管理：管理员、开发人员、测试人员等用户")
    print("   • 权限系统：角色、菜单、权限完整配置")
    print("   • AI模型：5个主流AI模型配置")
    print("   • AI代理：8个不同类型的示例代理")
    print("   • 测试用例：15个基础测试用例模板")
    print("   • 测试报告：5个示例测试报告")
    print("   • 生成历史：6个测试用例生成历史记录")
    print("\n🔑 默认登录信息：")
    print("   • 管理员：admin / 123456")
    print("   • 测试员：tester / 123456")
    print("   • 开发员：developer1 / 123456")
    print("\n🌐 访问地址：")
    print("   • 前端：http://localhost:3000")
    print("   • 后端：http://localhost:8000")
    print("   • API文档：http://localhost:8000/docs")
    print("="*60)


def print_ai_data_summary():
    """
    打印AI数据初始化摘要
    """
    print("\n" + "="*50)
    print("🤖 AI数据初始化完成！")
    print("="*50)
    print("📊 已创建的AI数据：")
    print("   • AI模型配置：5个")
    print("   • AI代理示例：8个")
    print("   • 测试用例模板：15个")
    print("   • 测试报告示例：5个")
    print("   • 生成历史记录：6个")
    print("="*50)


def check_dependencies():
    """
    检查依赖项是否满足
    """
    try:
        # 检查数据库连接
        from app.db.session import SessionLocal
        db = SessionLocal()
        db.close()
        logger.info("数据库连接正常")
        
        # 检查必要的模块
        required_modules = [
            'init_ai_models',
            'init_agents', 
            'init_test_cases',
            'init_test_reports',
            'init_generation_history',
            'seed_data'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                logger.info(f"模块 {module} 导入成功")
            except ImportError as e:
                logger.error(f"模块 {module} 导入失败: {str(e)}")
                raise
        
        logger.info("所有依赖项检查通过")
        return True
        
    except Exception as e:
        logger.error(f"依赖项检查失败: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI代理测试平台数据初始化脚本")
    parser.add_argument("--init", action="store_true", help="完整初始化数据库和所有数据")
    parser.add_argument("--init-ai", action="store_true", help="仅初始化AI相关数据")
    parser.add_argument("--clear", action="store_true", help="清除所有示例数据")
    parser.add_argument("--reset", action="store_true", help="完全重置数据库")
    parser.add_argument("--check", action="store_true", help="检查依赖项")
    
    args = parser.parse_args()
    
    if args.check:
        if check_dependencies():
            print("✅ 所有依赖项检查通过，可以进行初始化")
        else:
            print("❌ 依赖项检查失败，请检查配置")
    elif args.init:
        if check_dependencies():
            init_complete_database()
        else:
            print("❌ 依赖项检查失败，无法进行初始化")
    elif args.init_ai:
        if check_dependencies():
            init_ai_data_only()
        else:
            print("❌ 依赖项检查失败，无法进行初始化")
    elif args.clear:
        clear_all_data()
    elif args.reset:
        if check_dependencies():
            reset_complete_database()
        else:
            print("❌ 依赖项检查失败，无法进行重置")
    else:
        print("请指定操作:")
        print("  --init     完整初始化数据库和所有数据")
        print("  --init-ai  仅初始化AI相关数据")
        print("  --clear    清除所有示例数据")
        print("  --reset    完全重置数据库")
        print("  --check    检查依赖项")
