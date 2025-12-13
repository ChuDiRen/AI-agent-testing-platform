"""
Perf Engine 命令行入口
基于 Locust 的性能测试引擎
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 支持直接运行和模块运行
try:
    from .parse.yaml_parser import PerfCaseParser
    from .core.locust_runner import LocustRunner
    from .core.globalContext import g_context
    from .core.exceptions import CaseNotFoundError, ParserError, LocustError
    from .plugin_config import plugin_config
except ImportError:
    from parse.yaml_parser import PerfCaseParser
    from core.locust_runner import LocustRunner
    from core.globalContext import g_context
    from core.exceptions import CaseNotFoundError, ParserError, LocustError
    from plugin_config import plugin_config



def run():
    """命令行入口函数"""
    # 检查是否请求帮助
    if "--help" in sys.argv or "-h" in sys.argv:
        plugin_config.print_help()
        return
    
    print("=" * 60)
    print(f"{plugin_config.name} v{plugin_config.version}")
    print(plugin_config.description)
    print("=" * 60)
    
    # 解析命令行参数（基于 plugin.yaml 定义）
    args = plugin_config.parse_args()
    
    # 获取参数
    cases_path = args.get("cases", "")
    host = args.get("host", "")
    users = int(args.get("users", 10))
    spawn_rate = float(args.get("spawn_rate", 1))
    run_time = args.get("run_time", "60s")
    headless = args.get("headless", True)
    html_report = args.get("html_report", True)
    case_type = args.get("type", "yaml")
    
    # 验证参数
    if not cases_path:
        raise CaseNotFoundError("请指定 --cases (YAML用例目录)")
    
    # 解析用例路径
    cases_dir = Path(cases_path)
    if not cases_dir.is_absolute():
        cases_dir = Path(os.getcwd()) / cases_dir
    
    if not cases_dir.exists():
        raise CaseNotFoundError(f"用例目录不存在: {cases_dir}")
    
    # 保存用例目录到全局上下文
    g_context().set_dict("_cases_dir", str(cases_dir.resolve()))
    
    # 获取项目根目录和报告目录
    project_root = Path(__file__).parent.parent
    reports_dir = project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"用例格式: {case_type}")
    print(f"用例目录: {cases_dir}")
    print(f"目标主机: {host or '从用例读取'}")
    print(f"并发用户: {users}")
    print(f"生成速率: {spawn_rate}/s")
    print(f"运行时长: {run_time}")
    print(f"无界面模式: {headless}")
    print("=" * 60)
    
    # 解析用例
    print("\n📂 加载测试用例...")
    try:
        parser = PerfCaseParser()
        cases = parser.load_cases(cases_dir)
        
        if not cases:
            raise CaseNotFoundError("未找到任何测试用例")
    except Exception as e:
        if isinstance(e, CaseNotFoundError):
            raise
        raise ParserError(f"用例解析失败: {e}")
    
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
        raise CaseNotFoundError("请指定 --host 或在用例中配置 host")
    
    # 合并全局上下文到 g_context
    g_context().set_by_dict(parser.context)
    for case in cases:
        case_context = case.get("context", {})
        g_context().set_by_dict(case_context)
    
    # 存储 host 到全局上下文
    g_context().set_dict("host", host)
    
    # 创建运行器
    runner = LocustRunner(
        host=host,
        users=users,
        spawn_rate=spawn_rate,
        run_time=run_time,
        headless=headless
    )
    
    # 设置测试用例和上下文（使用 g_context 的数据）
    runner.set_test_cases(cases)
    runner.set_context(g_context().show_dict())
    
    # 执行测试
    try:
        results = runner.run(output_dir=str(reports_dir))
        
        print("\n" + "=" * 60)
        print(f"Reports: {reports_dir}")
        print("=" * 60)
        
        sys.exit(results.get("exit_code", 0))
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(130)
    except LocustError as e:
        print(f"\n❌ Locust 执行错误: {e}")
        sys.exit(1)
    except CaseNotFoundError as e:
        print(f"\n❌ 用例错误: {e}")
        sys.exit(1)
    except ParserError as e:
        print(f"\n❌ 解析错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    run()
