import os
import sys
import pytest

# 添加父目录到Python路径,使webrun可以被导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webrun.core.CasesPlugin import CasesPlugin  # 绝对导入: cli.py作为入口文件


def run():
    """
    命令行入口函数
    """
    # 获取 python运行参数
    # 1. 读取命令行传入的参数
    pytest_cmd_config = []
    for arg in sys.argv[1:]:  # 跳过脚本名称
        if arg.startswith("-"):
            pytest_cmd_config.append(arg)

    # 2. 构建pytest参数
    runner_path = os.path.join(os.path.dirname(__file__), "core", "WebTestRunner.py")
    print(f"测试运行器路径: {runner_path}")

    # 基础 pytest 参数
    pytest_args = [
        "-s", "-v", "--capture=tee-sys",
        runner_path,
        "--clean-alluredir",
        "--alluredir=allure-results"
    ]

    # 添加命令行传入的参数
    pytest_args.extend(pytest_cmd_config)

    print(f"run pytest: {pytest_args}")

    # 执行测试
    pytest.main(pytest_args, plugins=[CasesPlugin()])

    # 测试执行完成后自动生成Allure报告
    print("\n=== 测试执行完成，正在生成Allure报告... ===")
    os.system("allure generate -c -o allure-report")


if __name__ == '__main__':
    # 直接调用 run() 函数，使用命令行参数
    run()

    # 集成 allure 示例（可选）
    # os.system(r"allure generate -c -o allure-report")

