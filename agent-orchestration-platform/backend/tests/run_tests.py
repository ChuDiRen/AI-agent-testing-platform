#!/usr/bin/env python3
"""
测试运行脚本
提供便捷的测试运行入口
"""
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def main():
    parser = argparse.ArgumentParser(description="AI Agent编排平台后端测试运行器")
    parser.add_argument("--module", "-m", help="运行指定模块测试")
    parser.add_argument("--test_class", "-c", help="运行指定测试类")
    parser.add_argument("--function", "-f", help="运行指定测试函数")
    parser.add_argument("--coverage", action="store_true", help="生成覆盖率报告")
    parser.add_argument("--html", action="store_true", help="生成HTML报告")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--security", action="store_true", help="运行安全测试")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--p0", action="store_true", help="运行P0级别测试")
    parser.add_argument("--p1", action="store_true", help="运行P1级别测试")
    
    args = parser.parse_args()
    
    # 构建pytest命令
    cmd = "pytest tests/"
    
    if args.module:
        cmd += f"api/test_{args.module}.py"
    elif args.test_class:
        cmd += f" -k {args.test_class}"
    elif args.function:
        cmd += f" -k {args.function}"
    
    # 添加标记
    markers = []
    if args.security:
        markers.append("security")
    if args.performance:
        markers.append("performance")
    
    if markers:
        cmd += f" -m \"{' or '.join(markers)}\""
    
    # 添加选项
    if args.verbose:
        cmd += " -v -s"
    
    if args.coverage:
        cmd += " --cov=app --cov-report=html --cov-report=term-missing"
    
    if args.html:
        cmd += " --html=report.html --self-contained-html"
    
    # 默认选项
    if not any([args.coverage, args.html]):
        cmd += " --tb=short"
    
    print(f"运行命令: {cmd}")
    print("=" * 60)
    
    # 运行测试
    returncode, stdout, stderr = run_command(cmd)
    
    print(stdout)
    if stderr:
        print("错误输出:")
        print(stderr)
    
    # 生成报告摘要
    if returncode == 0:
        print("=" * 60)
        print("✅ 测试通过!")
        if args.coverage:
            print("📊 覆盖率报告已生成到 htmlcov/index.html")
        if args.html:
            print("📄 HTML报告已生成到 report.html")
    else:
        print("=" * 60)
        print("❌ 测试失败!")
        sys.exit(returncode)

if __name__ == "__main__":
    main()
