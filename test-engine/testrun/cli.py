"""
统一的测试引擎命令行入口
支持 API 测试和 Web 测试，通过 --engine-type 参数或配置文件指定测试类型
"""
import os
import sys
import yaml
import pytest


def get_engine_type_from_args():
    """
    从命令行参数中获取 engine-type
    返回: 'api', 'web' 或 None
    """
    for arg in sys.argv:
        if arg.startswith("--engine-type="):
            engine_type = arg.split("=")[1].lower()
            if engine_type in ['api', 'web']:
                # 从 sys.argv 中移除这个参数，避免传递给子引擎
                sys.argv.remove(arg)
                return engine_type
            else:
                print(f"错误: 不支持的 engine-type: {engine_type}")
                print("支持的类型: api, web")
                sys.exit(1)
    return None


def get_engine_type_from_config(cases_dir):
    """
    从 context.yaml 配置文件中读取 ENGINE_TYPE
    返回: 'api', 'web' 或 None
    """
    if not cases_dir:
        return None

    # 查找 context.yaml 文件
    context_file = os.path.join(cases_dir, "context.yaml")
    if not os.path.exists(context_file):
        return None

    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config and 'ENGINE_TYPE' in config:
                engine_type = config['ENGINE_TYPE'].lower()
                if engine_type in ['api', 'web']:
                    return engine_type
    except Exception as e:
        print(f"警告: 读取配置文件失败: {e}")

    return None


def get_cases_dir_from_args():
    """
    从命令行参数中获取 cases 目录
    """
    for arg in sys.argv:
        if arg.startswith("--cases="):
            return arg.split("=")[1]
    return None


def run_api_engine():
    """
    运行 API 测试引擎
    """
    try:
        from testengine_api.core.CasesPlugin import CasesPlugin  # 绝对导入: 跨包导入

        # 获取 python 运行参数
        pytest_cmd_config = []
        for arg in sys.argv:
            if arg.startswith("-"):
                pytest_cmd_config.append(arg)

        # 构建 pytest 参数
        api_runner_path = os.path.join(os.path.dirname(__file__), "..", "testengine_api", "core", "ApiTestRunner.py")
        pytest_args = [api_runner_path]
        pytest_args.extend(pytest_cmd_config)

        print("运行 API 测试引擎:", pytest_args)
        pytest.main(pytest_args, plugins=[CasesPlugin()])

    except ImportError as e:
        print(f"错误: 无法导入 API 引擎模块: {e}")
        sys.exit(1)


def run_web_engine():
    """
    运行 Web 测试引擎
    """
    try:
        from testengine_web.core.CasesPlugin import CasesPlugin  # 绝对导入: 跨包导入

        # 获取 python 运行参数
        pytest_cmd_config = []
        for arg in sys.argv:
            if arg.startswith("-"):
                pytest_cmd_config.append(arg)

        # 构建 pytest 参数
        web_runner_path = os.path.join(os.path.dirname(__file__), "..", "testengine_web", "core", "WebTestRunner.py")
        pytest_args = [web_runner_path]
        pytest_args.extend(pytest_cmd_config)

        print("运行 Web 测试引擎:", pytest_args)
        pytest.main(pytest_args, plugins=[CasesPlugin()])

    except ImportError as e:
        print(f"错误: 无法导入 Web 引擎模块: {e}")
        sys.exit(1)


def run():
    """
    统一入口函数
    1. 从命令行参数获取 engine-type（优先级高）
    2. 如果未指定，从 context.yaml 读取 ENGINE_TYPE
    3. 根据类型运行对应的引擎
    """
    print("=" * 60)
    print("Test Engine - 统一自动化测试引擎")
    print("=" * 60)

    # 1. 从命令行参数获取 engine-type
    engine_type = get_engine_type_from_args()

    # 2. 如果未指定，尝试从配置文件读取
    if not engine_type:
        cases_dir = get_cases_dir_from_args()
        if cases_dir:
            engine_type = get_engine_type_from_config(cases_dir)
            if engine_type:
                print(f"从配置文件读取 ENGINE_TYPE: {engine_type}")

    # 3. 如果还是没有，提示用户
    if not engine_type:
        print("\n错误: 未指定测试引擎类型!")
        print("\n请使用以下方式之一指定测试类型:")
        print("  1. 命令行参数: --engine-type=api 或 --engine-type=web")
        print("  2. 在 context.yaml 中配置: ENGINE_TYPE: api 或 ENGINE_TYPE: web")
        print("\n示例:")
        print("  testrun --engine-type=api --type=yaml --cases=examples/api-cases")
        print("  testrun --engine-type=web --type=yaml --cases=examples/web-cases --browser=chrome")
        sys.exit(1)

    print(f"测试引擎类型: {engine_type.upper()}")
    print("=" * 60)
    print()

    # 4. 根据类型运行对应的引擎
    if engine_type == 'api':
        run_api_engine()
    elif engine_type == 'web':
        run_web_engine()


if __name__ == '__main__':
    run()

