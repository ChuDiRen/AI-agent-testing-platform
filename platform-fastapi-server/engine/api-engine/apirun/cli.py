import os
import sys
import shutil

import pytest
from allure_combine import combine_allure

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apirun.core.CasesPlugin import CasesPlugin
from apirun.plugin_config import plugin_config


def run():
    """
    命令行入口函数

    参数通过 sys.argv 传递，支持的参数：
    --type=yaml|excel  用例格式（默认：yaml）
    --cases=PATH       用例目录（默认：../examples）
    --reports=PATH     报告目录（默认：engine/reports）
    """
    # 检查是否请求帮助
    if "--help" in sys.argv or "-h" in sys.argv:
        plugin_config.print_help()
        return

    print("=" * 60)
    print(f"{plugin_config.name} v{plugin_config.version}")
    print(plugin_config.description)
    print("=" * 60)

    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 解析命令行参数（基于 plugin.yaml 定义）
    args = plugin_config.parse_args()

    # 从 sys.argv 读取参数
    case_type = args.get('type', 'yaml')
    actual_cases_dir = args.get('cases', '../examples')

    # 读取 --reports 参数（从 sys.argv）
    actual_reports_dir = None
    for arg in sys.argv:
        if arg.startswith("--reports="):
            actual_reports_dir = arg.split("=", 1)[1]
            break

    # 如果没有指定 reports，使用默认值
    if not actual_reports_dir:
        actual_reports_dir = os.path.join(project_root, "reports")

    os.makedirs(actual_reports_dir, exist_ok=True)

    # 定义报告路径
    allure_results_dir = os.path.join(actual_reports_dir, "allure-results")
    allure_report_dir = os.path.join(actual_reports_dir, "allure-report")

    # 创建 logdata 目录
    logdata_dir = os.path.join(actual_reports_dir, "logdata")
    os.makedirs(logdata_dir, exist_ok=True)
    log_file = os.path.join(logdata_dir, "log.log")

    # 获取剩余的 pytest 参数
    pytest_cmd_config = [arg for arg in sys.argv[1:] if arg.startswith("-")]
    # 2. 构建pytest参数
    pytest_args = ["-s", "-v", "--capture=tee-sys"]
    pytest_args.append(os.path.join(os.path.dirname(__file__), "core/ApiTestRunner.py"))
    pytest_args.extend(["--clean-alluredir", f"--alluredir={allure_results_dir}"])
    # 添加日志文件配置
    pytest_args.extend([
        f"--log-file={log_file}",
        "--log-file-level=INFO",
        "--log-file-format=%(asctime)s %(levelname)s %(message)s %(lineno)d",
        "--log-file-date-format=%Y-%m-%d %H:%M:%S"
    ])
    # 添加用例目录参数
    pytest_args.extend([f"--type={case_type}", f"--cases={actual_cases_dir}"])
    pytest_args.extend(pytest_cmd_config)

    print("run pytest：", pytest_args)

    # 执行pytest测试
    exit_code = pytest.main(pytest_args, plugins=[CasesPlugin()])

    # 生成报告（只保留 complete.html）
    print("\n=== 测试执行完成，正在生成Allure报告... ===")
    os.makedirs(allure_report_dir, exist_ok=True)
    os.system(f'allure generate -c -o "{allure_report_dir}" "{allure_results_dir}"')

    if not os.listdir(allure_report_dir):
        print("警告: Allure 报告生成失败")
        return exit_code

    try:
        combine_allure(allure_report_dir)
    except Exception as e:
        print(f"警告: allure-combine 失败: {e}")
        return exit_code

    complete_html = os.path.join(allure_report_dir, "complete.html")
    if not os.path.exists(complete_html):
        print("警告: complete.html 未生成")
        return exit_code

    # 将 complete.html 移动到 reports 目录
    final_report = os.path.join(actual_reports_dir, "complete.html")
    shutil.copy2(complete_html, final_report)

    # 清理临时目录（只保留 complete.html）
    try:
        shutil.rmtree(allure_results_dir, ignore_errors=True)
        shutil.rmtree(allure_report_dir, ignore_errors=True)
        shutil.rmtree(logdata_dir, ignore_errors=True)
    except Exception as e:
        print(f"警告: 清理临时文件失败: {e}")

    print(f"报告已生成: {final_report}")
    return exit_code

if __name__ == '__main__':
    # 调用run函数而不是直接执行测试代码
    run()
