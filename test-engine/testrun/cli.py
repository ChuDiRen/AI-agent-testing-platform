"""
统一的测试引擎命令行入口
支持 API 测试和 Web 测试，通过 --engine-type 参数或配置文件指定测试类型
参数定义从 plugin.yaml 读取
"""
import os
import sys
from pathlib import Path
from typing import Optional

import pytest
import yaml
from allure_combine import combine_allure

from .plugin_config import plugin_config


import shutil


def generate_report(allure_results_dir: Path, allure_report_dir: Path) -> Optional[Path]:
    """
    生成 Allure 报告并只保留 complete.html
    
    :param allure_results_dir: allure-results 目录
    :param allure_report_dir: allure-report 目录
    :return: complete.html 文件路径，失败返回 None
    """
    print("\n=== 测试执行完成，正在生成Allure报告... ===")
    
    # 1. 生成 Allure 报告
    os.system(f'allure generate -c -o "{allure_report_dir}" "{allure_results_dir}"')
    
    # 2. 使用 allure-combine 生成单文件报告
    try:
        combine_allure(str(allure_report_dir))
    except Exception as e:
        print(f"警告: allure-combine 失败: {e}")
        return None
    
    complete_html = allure_report_dir / "complete.html"
    if not complete_html.exists():
        print("警告: complete.html 未生成")
        return None
    
    # 3. 将 complete.html 移动到 reports 目录
    reports_dir = allure_report_dir.parent
    final_report = reports_dir / "complete.html"
    shutil.copy2(complete_html, final_report)
    
    # 4. 清理临时目录（只保留 complete.html）
    try:
        shutil.rmtree(allure_results_dir, ignore_errors=True)
        shutil.rmtree(allure_report_dir, ignore_errors=True)
        # 清理 logdata 目录
        logdata_dir = reports_dir / "logdata"
        if logdata_dir.exists():
            shutil.rmtree(logdata_dir, ignore_errors=True)
        # 清理空的 screenshots 目录
        screenshots_dir = reports_dir / "screenshots"
        if screenshots_dir.exists() and not any(screenshots_dir.iterdir()):
            shutil.rmtree(screenshots_dir, ignore_errors=True)
    except Exception as e:
        print(f"警告: 清理临时文件失败: {e}")
    
    print(f"报告已生成: {final_report}")
    return final_report


def get_engine_type_from_config(cases_dir: str) -> Optional[str]:
    """从 context.yaml 配置文件中读取 ENGINE_TYPE"""
    if not cases_dir:
        return None

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
    
    # 生成报告（只保留 complete.html）
    generate_report(allure_results_dir, allure_report_dir)
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
    
    # 生成报告（只保留 complete.html）
    generate_report(allure_results_dir, allure_report_dir)
    return exit_code


def run_api_engine() -> int:
    """运行 API 测试引擎"""
    try:
        project_root = Path(__file__).parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # 从 plugin_config 获取参数
        case_type = plugin_config.get_arg("type", "yaml")
        cases_dir = plugin_config.get_arg("cases") or "examples/api-cases_yaml"
        
        if case_type == 'pytest':
            print(f"检测到 pytest 模式，直接运行测试脚本")
            return run_pytest_tests('api', project_root, reports_dir, cases_dir)
        else:
            from testengine_api.core.CasesPlugin import CasesPlugin
            print(f"检测到 {case_type} 模式，使用 CasesPlugin 运行")
            api_runner_path = project_root / "testengine_api" / "core" / "ApiTestRunner.py"
            return run_with_plugin('api', project_root, reports_dir, api_runner_path, CasesPlugin)

    except ImportError as e:
        print(f"错误: 无法导入 API 引擎模块: {e}")
        sys.exit(1)


def run_web_engine() -> int:
    """运行 Web 测试引擎"""
    try:
        project_root = Path(__file__).parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # 从 plugin_config 获取参数
        case_type = plugin_config.get_arg("type", "yaml")
        cases_dir = plugin_config.get_arg("cases") or "examples/web-cases_yaml"
        
        if case_type == 'pytest':
            print(f"检测到 pytest 模式，直接运行测试脚本")
            return run_pytest_tests('web', project_root, reports_dir, cases_dir)
        else:
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
    1. 检查是否请求帮助
    2. 从 plugin.yaml 解析命令行参数
    3. 验证参数并运行对应引擎
    """
    # 检查是否请求帮助
    if "--help" in sys.argv or "-h" in sys.argv:
        plugin_config.print_help()
        sys.exit(0)
    
    print("=" * 60)
    print(f"{plugin_config.name} v{plugin_config.version}")
    print(plugin_config.description)
    print("=" * 60)
    
    # 解析命令行参数（基于 plugin.yaml 定义）
    args = plugin_config.parse_args()
    
    # 1. 获取 engine_type
    engine_type = args.get("engine_type")
    
    # 2. 如果未指定，尝试从 context.yaml 读取
    if not engine_type:
        cases_dir = args.get("cases")
        if cases_dir:
            engine_type = get_engine_type_from_config(cases_dir)
            if engine_type:
                print(f"从配置文件读取 ENGINE_TYPE: {engine_type}")
    
    # 3. 验证参数
    if not engine_type:
        print("\n错误: 未指定测试引擎类型!")
        plugin_config.print_help()
        sys.exit(1)
    
    # 验证当前引擎类型的参数
    errors = plugin_config.validate_args(engine_type)
    if errors:
        print("\n参数验证失败:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    
    print(f"\n测试引擎类型: {engine_type.upper()}")
    print(f"用例格式: {args.get('type', 'yaml')}")
    print(f"用例目录: {args.get('cases', '默认')}")
    if engine_type == 'web':
        print(f"浏览器: {args.get('browser', 'chrome')}")
        print(f"无头模式: {args.get('headless', False)}")
    print("=" * 60)
    print()

    # 4. 运行对应引擎
    engine_runners = {
        'api': run_api_engine,
        'web': run_web_engine
    }
    
    if runner := engine_runners.get(engine_type):
        runner()


if __name__ == '__main__':
    run()

