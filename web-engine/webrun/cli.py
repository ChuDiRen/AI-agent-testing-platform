import os
import sys
import pytest

# 添加父目录到Python路径，使webrun可以被导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webrun.core.CasesPlugin import CasesPlugin


def run():
    """
    命令行入口函数
    """
    # 获取 python运行参数
    # 1. 读取命令行传入的参数
    pytest_cmd_config = []
    for arg in sys.argv:
        if arg.startswith("-"):
            pytest_cmd_config.append(arg)
    
    print(os.path.join(os.path.dirname(__file__), "core/WebTestRunner.py"))
    # 2. 构建pytest参数
    pytest_args = [os.path.join(os.path.dirname(__file__), "core/WebTestRunner.py")]
    pytest_args.extend(pytest_cmd_config)
    
    print("run pytest：", pytest_args)
    
    pytest.main(pytest_args, plugins=[CasesPlugin()])


if __name__ == '__main__':
    # 测试执行入口
    print(os.path.join(os.path.dirname(__file__), 'core', "WebTestRunner.py"))
    pytest_args = [
        "-s", "-v", "--capture=tee-sys",
        os.path.join(os.path.dirname(__file__), 'core', "WebTestRunner.py"),
        "--clean-alluredir",
        "--alluredir=allure-results",
        "--type=yaml",
        r"--cases=..\examples\example-web-cases",
        "--browser=chrome",
        "--headless=false"
    ]
    print("run pytest：", pytest_args)
    pytest.main(pytest_args, plugins=[CasesPlugin()])
    
    # 集成 allure 示例
    # os.system(r"allure generate -c -o allure-report")

