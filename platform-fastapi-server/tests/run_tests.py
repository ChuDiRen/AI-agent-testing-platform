#!/usr/bin/env python
"""
测试运行脚本
提供便捷的测试执行命令
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_all_tests():
    """运行所有测试"""
    print("=" * 80)
    print("运行所有单元测试")
    print("=" * 80)
    
    cmd = ["pytest", "tests/", "-v"]
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
  python run_tests.py --help             # 显示此帮助信息

示例:
  python run_tests.py
  python run_tests.py --coverage
  python run_tests.py --file test_api_project_controller.py
  python run_tests.py --mark unit

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
    
    elif args[0] in ["--help", "-h"]:
        show_help()
        return 0
    
    else:
        print(f"未知命令: {args[0]}")
        print("使用 --help 查看帮助信息")
        return 1


if __name__ == "__main__":
    sys.exit(main())
