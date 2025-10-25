"""
统一的测试引擎命令行入口
支持 API 测试和 Web 测试，通过 --engine-type 参数或配置文件指定测试类型
"""
import os
import sys
from pathlib import Path
from typing import Optional

import pytest
import yaml


def get_engine_type_from_args() -> Optional[str]:
    """
    从命令行参数中获取 engine-type
    返回: 'api', 'web' 或 None
    """
    engine_arg = next((arg for arg in sys.argv if arg.startswith("--engine-type=")), None)
    if engine_arg:
        engine_type = engine_arg.split("=")[1].lower()
        if engine_type in ['api', 'web']:
            # 从 sys.argv 中移除这个参数，避免传递给子引擎
            sys.argv.remove(engine_arg)
            return engine_type
        else:
            print(f"错误: 不支持的 engine-type: {engine_type}")
            print("支持的类型: api, web")
            sys.exit(1)
    return None


def get_engine_type_from_config(cases_dir: str) -> Optional[str]:
    """
    从 context.yaml 配置文件中读取 ENGINE_TYPE
    返回: 'api', 'web' 或 None
    """
    if not cases_dir:
        return None

    # 查找 context.yaml 文件
    context_file = Path(cases_dir) / "context.yaml"
    if not context_file.exists():
        return None

    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config and (engine_type := config.get('ENGINE_TYPE')):
                engine_type = engine_type.lower()
                if engine_type in ['api', 'web']:
                    return engine_type
    except Exception as e:
        print(f"警告: 读取配置文件失败: {e}")

    return None


def get_cases_dir_from_args() -> Optional[str]:
    """
    从命令行参数中获取 cases 目录
    """
    cases_arg = next((arg for arg in sys.argv if arg.startswith("--cases=")), None)
    return cases_arg.split("=")[1] if cases_arg else None


def get_case_type_from_args() -> str:
    """
    从命令行参数中获取用例类型
    
    :return: 'yaml', 'excel', 'pytest'，默认为 'yaml'
    """
    type_arg = next((arg for arg in sys.argv if arg.startswith("--type=")), None)
    if type_arg:
        case_type = type_arg.split("=")[1].lower()
        if case_type in ['yaml', 'excel', 'pytest']:
            return case_type
    return 'yaml'  # 默认值


def run_pytest_tests(
    engine: str, 
    project_root: Path, 
    reports_dir: Path,
    cases_dir: str
) -> int:
    """
    直接运行 pytest 测试脚本（不使用 CasesPlugin）
    
    :param engine: 引擎类型 ('api' 或 'web')
    :param project_root: 项目根目录
    :param reports_dir: 报告目录
    :param cases_dir: 测试用例目录
    :return: pytest 退出代码
    """
    # 配置报告路径
    allure_results_dir = reports_dir / "allure-results"
    allure_report_dir = reports_dir / "allure-report"
    logdata_dir = reports_dir / "logdata"
    logdata_dir.mkdir(exist_ok=True)
    log_file = logdata_dir / "log.log"
    
    # 如果是 web 测试，还需要创建 screenshots 目录
    if engine == 'web':
        screenshots_dir = reports_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
    
    # 构建 pytest 参数
    pytest_args = [
        "-s", "-v", "--capture=tee-sys",
        str(cases_dir),  # 直接指定测试目录
        "--clean-alluredir", f"--alluredir={allure_results_dir}",
        f"--log-file={log_file}",
        "--log-file-level=INFO",
        "--log-file-format=%(asctime)s %(levelname)s %(message)s %(lineno)d",
        "--log-file-date-format=%Y-%m-%d %H:%M:%S"
    ]
    
    # 添加其他命令行参数（过滤掉特定参数）
    other_args = [
        arg for arg in sys.argv 
        if arg.startswith("-") and 
        not arg.startswith("--type=") and
        not arg.startswith("--engine-type=") and
        not arg.startswith("--cases=")
    ]
    pytest_args.extend(other_args)
    
    print(f"运行 {engine.upper()} Pytest 测试:", pytest_args)
    exit_code = pytest.main(pytest_args)  # 不传 plugins 参数
    
    # 生成 Allure 报告
    print("\n=== 测试执行完成，正在生成Allure报告... ===")
    print(f"报告目录: {allure_report_dir}")
    os.system(f'allure generate -c -o "{allure_report_dir}" "{allure_results_dir}"')
    
    return exit_code


def run_with_plugin(
    engine: str,
    project_root: Path,
    reports_dir: Path,
    runner_path: Path,
    plugin_class
) -> int:
    """
    使用 CasesPlugin 运行 yaml/excel 用例
    
    :param engine: 引擎类型 ('api' 或 'web')
    :param project_root: 项目根目录
    :param reports_dir: 报告目录
    :param runner_path: TestRunner.py 文件路径
    :param plugin_class: CasesPlugin 类
    :return: pytest 退出代码
    """
    # 配置报告路径
    allure_results_dir = reports_dir / "allure-results"
    allure_report_dir = reports_dir / "allure-report"
    
    # 创建 logdata 目录
    logdata_dir = reports_dir / "logdata"
    logdata_dir.mkdir(exist_ok=True)
    log_file = logdata_dir / "log.log"
    
    # 如果是 web 测试，还需要创建 screenshots 目录
    if engine == 'web':
        screenshots_dir = reports_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
    
    # 获取 python 运行参数（使用列表推导式）
    pytest_cmd_config = [arg for arg in sys.argv if arg.startswith("-")]
    
    # 构建 pytest 参数
    pytest_args = [
        "-s", "-v", "--capture=tee-sys",
        str(runner_path),
        "--clean-alluredir", f"--alluredir={allure_results_dir}",
        f"--log-file={log_file}",
        "--log-file-level=INFO",
        "--log-file-format=%(asctime)s %(levelname)s %(message)s %(lineno)d",
        "--log-file-date-format=%Y-%m-%d %H:%M:%S",
        *pytest_cmd_config
    ]
    
    print(f"运行 {engine.upper()} 测试引擎:", pytest_args)
    exit_code = pytest.main(pytest_args, plugins=[plugin_class()])
    
    # 测试执行完成后自动生成Allure报告
    print("\n=== 测试执行完成，正在生成Allure报告... ===")
    print(f"报告目录: {allure_report_dir}")
    os.system(f'allure generate -c -o "{allure_report_dir}" "{allure_results_dir}"')
    
    return exit_code


def run_api_engine() -> int:
    """
    运行 API 测试引擎
    支持 yaml、excel、pytest 三种用例类型
    """
    try:
        # 获取项目根目录（test-engine目录）
        project_root = Path(__file__).parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # 获取用例类型和用例目录
        case_type = get_case_type_from_args()
        cases_dir = get_cases_dir_from_args() or "examples/api-cases"
        
        # 根据用例类型选择运行方式
        if case_type == 'pytest':
            # 直接运行 pytest 脚本（不使用 CasesPlugin）
            print(f"检测到 pytest 模式，直接运行测试脚本")
            return run_pytest_tests('api', project_root, reports_dir, cases_dir)
        else:
            # 使用 CasesPlugin 运行 yaml/excel 用例
            from testengine_api.core.CasesPlugin import CasesPlugin
            print(f"检测到 {case_type} 模式，使用 CasesPlugin 运行")
            api_runner_path = project_root / "testengine_api" / "core" / "ApiTestRunner.py"
            return run_with_plugin('api', project_root, reports_dir, api_runner_path, CasesPlugin)

    except ImportError as e:
        print(f"错误: 无法导入 API 引擎模块: {e}")
        sys.exit(1)


def run_web_engine() -> int:
    """
    运行 Web 测试引擎
    支持 yaml、excel、pytest 三种用例类型
    """
    try:
        # 获取项目根目录（test-engine目录）
        project_root = Path(__file__).parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # 获取用例类型和用例目录
        case_type = get_case_type_from_args()
        cases_dir = get_cases_dir_from_args() or "examples/web-cases"
        
        # 根据用例类型选择运行方式
        if case_type == 'pytest':
            # 直接运行 pytest 脚本（不使用 CasesPlugin）
            print(f"检测到 pytest 模式，直接运行测试脚本")
            return run_pytest_tests('web', project_root, reports_dir, cases_dir)
        else:
            # 使用 CasesPlugin 运行 yaml/excel 用例
            from testengine_web.core.CasesPlugin import CasesPlugin
            print(f"检测到 {case_type} 模式，使用 CasesPlugin 运行")
            web_runner_path = project_root / "testengine_web" / "core" / "WebTestRunner.py"
            return run_with_plugin('web', project_root, reports_dir, web_runner_path, CasesPlugin)

    except ImportError as e:
        print(f"错误: 无法导入 Web 引擎模块: {e}")
        sys.exit(1)


def run() -> None:
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
        if cases_dir := get_cases_dir_from_args():
            if engine_type := get_engine_type_from_config(cases_dir):
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

    # 4. 根据类型运行对应的引擎（使用字典映射）
    engine_runners = {
        'api': run_api_engine,
        'web': run_web_engine
    }
    
    if runner := engine_runners.get(engine_type):
        runner()


if __name__ == '__main__':
    run()

