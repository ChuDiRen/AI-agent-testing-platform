import os
import sys
import shutil

import pytest
from allure_combine import combine_allure

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mobilerun.core.CasesPlugin import CasesPlugin
from mobilerun.plugin_config import plugin_config


def _parse_cli_args() -> dict:
    defaults = {
        "type": "yaml",
        "cases": "../examples",
        "platform": "android",
        "server": "http://127.0.0.1:4723",
        "deviceName": "",
        "udid": "",
        "app": "",
        "bundleId": "",
        "noReset": "true",
    }

    args = defaults.copy()
    argv = sys.argv[1:]
    i = 0

    while i < len(argv):
        arg = argv[i]
        if arg.startswith("--"):
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                args[key] = value
            elif i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                key = arg[2:]
                args[key] = argv[i + 1]
                i += 1
        i += 1

    return args


def run():
    if "--help" in sys.argv or "-h" in sys.argv:
        plugin_config.print_help()
        return

    print("=" * 60)
    print(f"{plugin_config.name} v{plugin_config.version}")
    print(plugin_config.description)
    print("=" * 60)

    args = _parse_cli_args()

    print(f"用例格式: {args['type']}")
    print(f"用例目录: {args['cases']}")
    print(f"平台: {args['platform']}")
    print(f"Appium Server: {args['server']}")
    print("=" * 60)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(project_root, "reports")
    os.makedirs(reports_dir, exist_ok=True)

    allure_results_dir = os.path.join(reports_dir, "allure-results")
    allure_report_dir = os.path.join(reports_dir, "allure-report")

    logdata_dir = os.path.join(reports_dir, "logdata")
    os.makedirs(logdata_dir, exist_ok=True)
    log_file = os.path.join(logdata_dir, "log.log")

    pytest_args = ["-s", "-v", "--capture=tee-sys"]
    pytest_args.append(os.path.join(os.path.dirname(__file__), "core/MobileTestRunner.py"))
    pytest_args.extend(["--clean-alluredir", f"--alluredir={allure_results_dir}"])
    pytest_args.extend(
        [
            f"--log-file={log_file}",
            "--log-file-level=INFO",
            "--log-file-format=%(asctime)s %(levelname)s %(message)s %(lineno)d",
            "--log-file-date-format=%Y-%m-%d %H:%M:%S",
        ]
    )

    pytest_args.extend(
        [
            f"--type={args['type']}",
            f"--cases={args['cases']}",
            f"--platform={args['platform']}",
            f"--server={args['server']}",
            f"--deviceName={args['deviceName']}",
            f"--udid={args['udid']}",
            f"--app={args['app']}",
            f"--bundleId={args['bundleId']}",
            f"--noReset={args['noReset']}",
        ]
    )

    print("run pytest：", pytest_args)

    pytest.main(pytest_args, plugins=[CasesPlugin()])

    print("\n=== 测试执行完成，正在生成Allure报告... ===")
    os.system(f'allure generate -c -o "{allure_report_dir}" "{allure_results_dir}"')

    try:
        combine_allure(allure_report_dir)
    except Exception as e:
        print(f"警告: allure-combine 失败: {e}")
        return

    complete_html = os.path.join(allure_report_dir, "complete.html")
    if not os.path.exists(complete_html):
        print("警告: complete.html 未生成")
        return

    final_report = os.path.join(reports_dir, "complete.html")
    shutil.copy2(complete_html, final_report)

    try:
        shutil.rmtree(allure_results_dir, ignore_errors=True)
        shutil.rmtree(allure_report_dir, ignore_errors=True)
        shutil.rmtree(logdata_dir, ignore_errors=True)
    except Exception as e:
        print(f"警告: 清理临时文件失败: {e}")

    print(f"报告已生成: {final_report}")


if __name__ == "__main__":
    run()
