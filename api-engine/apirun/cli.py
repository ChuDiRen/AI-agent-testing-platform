import os
import sys

import pytest

# 添加父目录到Python路径，使webrun可以被导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apirun.core.CasesPlugin import CasesPlugin

def run():
    # 获取 python运行参数
    # 1. 读取命令行传入的参数
    pytest_cmd_config = []
    i = 1  # 跳过脚本名称
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--"):
            # 处理长选项，如 --type=yaml 或 --cases=path
            if "=" in arg:
                pytest_cmd_config.append(arg)
            else:
                # 处理分离的参数，如 --type yaml
                if i + 1 < len(sys.argv):
                    pytest_cmd_config.append(arg)
                    pytest_cmd_config.append(sys.argv[i + 1])
                    i += 1  # 跳过下一个参数，因为它是当前选项的值
                else:
                    pytest_cmd_config.append(arg)
        elif arg.startswith("-"):
            pytest_cmd_config.append(arg)
        i += 1

    print("解析到的参数:", pytest_cmd_config)  # 调试输出
    print(os.path.join(os.path.dirname(__file__), "core/ApiTestRunner.py"))
    # 2. 构建pytest参数
    pytest_args = ["-s", "-v", "--capture=tee-sys"]
    pytest_args.append(os.path.join(os.path.dirname(__file__), "core/ApiTestRunner.py"))
    pytest_args.extend(["--clean-alluredir", "--alluredir=allure-results"])
    pytest_args.extend(pytest_cmd_config)

    print("run pytest：", pytest_args)

    # 执行pytest测试
    pytest.main(pytest_args, plugins=[CasesPlugin()])
    
    # 测试执行完成后自动生成Allure报告
    print("\n=== 测试执行完成，正在生成Allure报告... ===")
    os.system("allure generate -c -o allure-report")

if __name__ == '__main__':
    # 调用run函数而不是直接执行测试代码
    run()
