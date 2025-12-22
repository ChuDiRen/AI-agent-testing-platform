"""
统一的测试引擎命令行入口
支持 API 测试和 Web 测试，通过 --engine-type 参数或配置文件指定测试类型
参数定义从 plugin.yaml 读取
"""
import os
import subprocess
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
    
    # 1. 生成 Allure 报告（使用 subprocess 替代 os.system）
    try:
        subprocess.run(
            ['allure', 'generate', '-c', '-o', str(allure_report_dir), str(allure_results_dir)],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"警告: Allure 报告生成失败: {e.stderr}")
    except FileNotFoundError:
        print("警告: 未找到 allure 命令，请确保已安装 Allure CLI")
        return None
    
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
                if engine_type in ['api', 'web', 'mobile', 'perf']:
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
    
    :param engine: 引擎类型 ('api'、'web'、'mobile'、'perf')
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
    
    # 如果是 perf 测试，创建性能测试报告目录
    if engine == 'perf':
        perf_reports_dir = reports_dir / "perf-reports"
        perf_reports_dir.mkdir(exist_ok=True)
    
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


def run_mobile_engine() -> int:
    """运行 Mobile 测试引擎"""
    try:
        project_root = Path(__file__).parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # 创建 screenshots 目录
        screenshots_dir = reports_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        # 从 plugin_config 获取参数
        case_type = plugin_config.get_arg("type", "yaml")
        cases_dir = plugin_config.get_arg("cases") or "examples/mobile-cases_yaml"
        
        if case_type == 'pytest':
            print(f"检测到 pytest 模式，直接运行测试脚本")
            return run_pytest_tests('mobile', project_root, reports_dir, cases_dir)
        else:
            from testengine_mobile.core.CasesPlugin import CasesPlugin
            print(f"检测到 {case_type} 模式，使用 CasesPlugin 运行")
            mobile_runner_path = project_root / "testengine_mobile" / "core" / "MobileTestRunner.py"
            return run_with_plugin('mobile', project_root, reports_dir, mobile_runner_path, CasesPlugin)

    except ImportError as e:
        print(f"错误: 无法导入 Mobile 引擎模块: {e}")
        sys.exit(1)


def run_perf_engine() -> int:
    """运行性能测试引擎"""
    try:
        project_root = Path(__file__).parent.parent
        reports_dir = project_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        # 从 plugin_config 获取参数
        case_type = plugin_config.get_arg("type", "yaml")
        cases_dir = plugin_config.get_arg("cases") or "examples/perf-cases_yaml"
        
        # pytest 模式：直接运行 pytest 测试脚本
        if case_type == 'pytest':
            print(f"检测到 pytest 模式，直接运行测试脚本")
            return run_pytest_tests('perf', project_root, reports_dir, cases_dir)
        
        # yaml 模式：使用 Locust 运行器
        host = plugin_config.get_arg("host", "")
        users = int(plugin_config.get_arg("users", 10))
        spawn_rate = float(plugin_config.get_arg("spawn_rate", 1))
        run_time = plugin_config.get_arg("run_time", "60s")
        headless = plugin_config.get_arg("headless", True)
        
        # 解析用例路径
        cases_path = Path(cases_dir)
        if not cases_path.is_absolute():
            cases_path = project_root / cases_dir
        
        if not cases_path.exists():
            print(f"错误: 用例目录不存在: {cases_path}")
            sys.exit(1)
        
        # 导入性能测试模块
        from testengine_perf.parse.yaml_parser import PerfCaseParser
        from testengine_perf.core.locust_runner import LocustRunner
        from testengine_perf.core.globalContext import g_context
        
        # 保存用例目录到全局上下文
        g_context().set_dict("_cases_dir", str(cases_path.resolve()))
        
        print(f"用例目录: {cases_path}")
        print(f"目标主机: {host or '从用例读取'}")
        print(f"并发用户: {users}")
        print(f"生成速率: {spawn_rate}/s")
        print(f"运行时长: {run_time}")
        print(f"无界面模式: {headless}")
        print("=" * 60)
        
        # 解析用例
        print("\n📂 加载测试用例...")
        parser = PerfCaseParser()
        cases = parser.load_cases(cases_path)
        
        if not cases:
            print("错误: 未找到任何测试用例")
            sys.exit(1)
        
        print(f"✅ 加载了 {len(cases)} 个测试用例")
        
        # 从用例中获取 host（如果未指定）
        if not host:
            for case in cases:
                case_host = case.get("host") or case.get("context", {}).get("host")
                if case_host:
                    host = case_host
                    print(f"📌 从用例获取目标主机: {host}")
                    break
        
        if not host:
            print("错误: 请指定 --host 或在用例中配置 host")
            sys.exit(1)
        
        # 合并全局上下文
        g_context().set_by_dict(parser.context)
        for case in cases:
            case_context = case.get("context", {})
            g_context().set_by_dict(case_context)
        
        g_context().set_dict("host", host)
        
        # 创建运行器
        runner = LocustRunner(
            host=host,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            headless=headless
        )
        
        runner.set_test_cases(cases)
        runner.set_context(g_context().show_dict())
        
        # 执行测试
        results = runner.run(output_dir=str(reports_dir))
        
        print("\n" + "=" * 60)
        print(f"Reports: {reports_dir}")
        print("=" * 60)
        
        return results.get("exit_code", 0)
        
    except ImportError as e:
        print(f"错误: 无法导入性能测试引擎模块: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 性能测试执行失败: {e}")
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
    
    # 打印 Mobile 专属参数
    if engine_type == 'mobile':
        print(f"平台: {args.get('platform', 'android')}")
        print(f"Appium Server: {args.get('server', 'http://127.0.0.1:4723')}")
    
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
        'web': run_web_engine,
        'mobile': run_mobile_engine,
        'perf': run_perf_engine
    }
    
    if runner := engine_runners.get(engine_type):
        runner()


if __name__ == '__main__':
    run()

