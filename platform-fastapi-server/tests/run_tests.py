#!/usr/bin/env python
"""
测试运行脚本
提供便捷的测试执行命令

使用方法:
  python run_tests.py                    # 运行所有测试
  python run_tests.py --coverage         # 运行测试并生成覆盖率报告
  python run_tests.py --file <文件名>    # 运行特定测试文件
  python run_tests.py --mark <标记>      # 运行带特定标记的测试
  python run_tests.py --module <模块>    # 运行特定模块的测试
  python run_tests.py --help             # 显示帮助信息
"""
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("运行所有单元测试")
    print("=" * 80)
    
    cmd = ["pytest", "tests/", "-v", "--tb=short"]
    return subprocess.call(cmd, cwd=BASE_DIR)


def run_module_tests(module: str):
    """运行特定模块的测试"""
    print("=" * 80)
    print(f"运行模块测试: {module}")
    print("=" * 80)
    
    # 模块映射
    module_map = {
        "core": "test_core_utils.py",
        "login": "test_login_controller.py",
        "user": "test_user_controller.py",
        "role": "test_role_controller.py",
        "menu": "test_menu_controller.py",
        "dept": "test_dept_controller.py",
        "plugin": "test_plugin_controller.py",
        "task": "test_task_controller.py",
        "robot": "test_robot_config_controller.py test_robot_msg_config_controller.py",
        "ai": "test_ai_model_controller.py test_ai_conversation_controller.py test_prompt_template_controller.py test_test_case_controller.py",
        "generator": "test_generator_controller.py",
        "apitest": "test_api_*.py",
        "models": "test_models.py",
        "schemas": "test_schemas.py",
        "integration": "test_integration.py"
    }
    
    if module not in module_map:
        print(f"未知模块: {module}")
        print(f"可用模块: {', '.join(module_map.keys())}")
        return 1
    
    test_files = module_map[module]
    cmd = ["pytest", f"tests/{test_files}", "-v", "--tb=short"]
    return subprocess.call(cmd, cwd=BASE_DIR)


def run_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("=" * 80)
    print("运行测试并生成覆盖率报告")
    print("=" * 80)
    
    cmd = ["pytest", "tests/", "-v", "--cov=.", "--cov-report=html", "--cov-report=term"]
    return subprocess.call(cmd, cwd=BASE_DIR)


def run_specific_test(test_file: str):
    """运行特定测试文件"""
    print("=" * 80)
    print(f"运行测试: {test_file}")
    print("=" * 80)
    
    cmd = ["pytest", f"tests/{test_file}", "-v"]
    return subprocess.call(cmd, cwd=BASE_DIR)


def run_marked_tests(marker: str):
    """运行带特定标记的测试"""
    print("=" * 80)
    print(f"运行标记为 '{marker}' 的测试")
    print("=" * 80)
    
    cmd = ["pytest", "tests/", "-v", "-m", marker]
    return subprocess.call(cmd, cwd=BASE_DIR)


def show_help():
    """显示帮助信息"""
    print("""
测试运行脚本使用说明
==================

命令:
  python run_tests.py                    # 运行所有测试
  python run_tests.py --coverage         # 运行测试并生成覆盖率报告
  python run_tests.py --file <文件名>    # 运行特定测试文件
  python run_tests.py --mark <标记>      # 运行带特定标记的测试
  python run_tests.py --module <模块>    # 运行特定模块的测试
  python run_tests.py --help             # 显示此帮助信息

示例:
  python run_tests.py
  python run_tests.py --coverage
  python run_tests.py --file test_api_project_controller.py
  python run_tests.py --mark unit
  python run_tests.py --module core

模块:
  core         - 核心工具模块 (JwtUtil, time_utils, resp_model等)
  login        - 登录模块
  user         - 用户管理模块
  role         - 角色管理模块
  menu         - 菜单管理模块
  dept         - 部门管理模块
  plugin       - 插件管理模块
  task         - 任务调度模块
  robot        - 机器人配置模块
  ai           - AI助手模块
  generator    - 代码生成器模块
  apitest      - API测试模块
  models       - 数据模型测试
  schemas      - Schema验证测试
  integration  - 集成测试

标记:
  unit         - 单元测试
  integration  - 集成测试
  api          - API测试
  database     - 数据库测试
  slow         - 慢速测试
    """)


def main():
    """主函数"""
    args = sys.argv[1:]
    
    if not args or args[0] == "--all":
        return run_all_tests()
    
    elif args[0] == "--coverage":
        return run_with_coverage()
    
    elif args[0] == "--file" and len(args) > 1:
        return run_specific_test(args[1])
    
    elif args[0] == "--mark" and len(args) > 1:
        return run_marked_tests(args[1])
    
    elif args[0] == "--module" and len(args) > 1:
        return run_module_tests(args[1])
    
    elif args[0] in ["--help", "-h"]:
        show_help()
        return 0
    
    else:
        print(f"未知命令: {args[0]}")
        print("使用 --help 查看帮助信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
