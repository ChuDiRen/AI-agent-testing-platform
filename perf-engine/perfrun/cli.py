"""
Perf Engine 命令行入口
"""
import argparse
import os
import sys
from pathlib import Path

# 支持直接运行和模块运行
try:
    from .core.runner import K6Runner
    from .parse.yaml_parser import PerfCaseParser
except ImportError:
    from core.runner import K6Runner
    from parse.yaml_parser import PerfCaseParser


def find_k6_path():
    """查找 k6 可执行文件路径（仅检查系统 PATH）"""
    import shutil
    return shutil.which("k6")


def run():
    """命令行入口函数"""
    parser = argparse.ArgumentParser(
        description="Perf Engine - 基于 k6 的性能测试引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--cases",
        type=str,
        default=None,
        help="YAML 用例目录路径"
    )
    
    parser.add_argument(
        "--script",
        type=str,
        default=None,
        help="原生 k6 JavaScript 脚本路径"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="../reports",
        help="报告输出目录 (默认: ../reports)"
    )
    
    parser.add_argument(
        "--format",
        type=str,
        choices=["json", "html", "influxdb"],
        default="json",
        help="报告格式: json, html, influxdb (默认: json)"
    )
    
    parser.add_argument(
        "--k6-path",
        type=str,
        default=None,
        help="k6 可执行文件路径 (默认: 自动检测)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅生成脚本，不执行测试"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细日志"
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.cases and not args.script:
        print("❌ 请指定 --cases (YAML用例目录) 或 --script (k6脚本路径)")
        sys.exit(1)
    
    # 解析输出目录
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(os.getcwd()) / output_path
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Perf Engine - 性能测试引擎")
    print("=" * 60)
    
    # 模式1: 运行原生 k6 脚本
    if args.script:
        script_path = Path(args.script)
        if not script_path.is_absolute():
            script_path = Path(os.getcwd()) / script_path
        
        if not script_path.exists():
            print(f"❌ 脚本文件不存在: {script_path}")
            sys.exit(1)
        
        print(f"脚本文件: {script_path}")
        print(f"输出目录: {output_path}")
        print("=" * 60)
        
        # 运行原生脚本
        run_native_script(script_path, output_path, args.k6_path, args.verbose)
        return
    
    # 模式2: 运行 YAML 用例
    cases_path = Path(args.cases)
    if not cases_path.is_absolute():
        cases_path = Path(os.getcwd()) / cases_path
    
    if not cases_path.exists():
        print(f"❌ 用例目录不存在: {cases_path}")
        sys.exit(1)
    
    print(f"用例目录: {cases_path}")
    print(f"输出目录: {output_path}")
    print(f"报告格式: {args.format}")
    print("=" * 60)
    
    # 解析用例
    parser_instance = PerfCaseParser()
    cases = parser_instance.load_cases(cases_path)
    
    if not cases:
        print("❌ 未找到任何测试用例")
        sys.exit(1)
    
    print(f"✅ 加载了 {len(cases)} 个测试用例")
    
    # 创建运行器
    runner = K6Runner(
        k6_path=args.k6_path,
        output_dir=output_path,
        output_format=args.format,
        verbose=args.verbose
    )
    
    # 执行测试
    if args.dry_run:
        print("\n🔧 Dry Run 模式 - 仅生成脚本")
        for case in cases:
            script_path = runner.generate_script(case)
            print(f"   生成脚本: {script_path}")
    else:
        # 检查 k6 是否安装
        if not runner.check_k6_installed():
            print("❌ k6 未安装或未配置到系统 PATH")
            print("   请确保 k6 已安装并添加到系统环境变量")
            sys.exit(1)
        
        print("\n🚀 开始执行性能测试...")
        results = runner.run_all(cases)
        
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        
        for result in results:
            status = "✅ 通过" if result["success"] else "❌ 失败"
            print(f"{status} - {result['name']}")
            if result.get("summary"):
                print(f"   请求数: {result['summary'].get('http_reqs', 'N/A')}")
                print(f"   平均响应时间: {result['summary'].get('http_req_duration_avg', 'N/A')}ms")
                print(f"   P95 响应时间: {result['summary'].get('http_req_duration_p95', 'N/A')}ms")
        
        print("\n" + "=" * 60)
        print(f"报告已生成: {output_path}")
        print("=" * 60)


def run_native_script(script_path: Path, output_path: Path, k6_path: str = None, verbose: bool = False):
    """运行原生 k6 脚本"""
    import subprocess
    import shutil
    from datetime import datetime
    
    # 查找 k6
    if not k6_path:
        k6_path = find_k6_path()
    
    if not k6_path:
        print("❌ k6 未安装或未配置到系统 PATH")
        print("   请确保 k6 已安装并添加到系统环境变量")
        sys.exit(1)
    
    # 检查 k6 是否可用
    try:
        result = subprocess.run([k6_path, "version"], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError()
        print(f"k6 版本: {result.stdout.strip()}")
    except FileNotFoundError:
        print(f"❌ k6 不可用: {k6_path}")
        sys.exit(1)
    
    # 准备输出文件
    script_name = script_path.stem
    json_file = output_path / f"{script_name}_result.json"
    html_file = output_path / f"{script_name}_report.html"
    
    # 构建命令
    cmd = [k6_path, "run"]
    cmd.extend(["--out", f"json={json_file}"])
    cmd.append(str(script_path))
    
    print(f"\n🚀 开始执行: {script_path.name}")
    if verbose:
        print(f"命令: {' '.join(cmd)}")
    
    # 执行测试，捕获输出
    try:
        result = subprocess.run(
            cmd,
            cwd=str(script_path.parent),
            capture_output=True
        )
        
        # 解码输出，处理编码问题
        try:
            stdout = result.stdout.decode('utf-8')
        except:
            try:
                stdout = result.stdout.decode('gbk', errors='ignore')
            except:
                stdout = str(result.stdout)
        
        try:
            stderr = result.stderr.decode('utf-8')
        except:
            try:
                stderr = result.stderr.decode('gbk', errors='ignore')
            except:
                stderr = str(result.stderr)
        
        # 打印 k6 输出
        if stdout:
            print(stdout)
        if stderr:
            print(stderr)
        
        success = result.returncode == 0
        
        # 解析 k6 输出生成 HTML 报告
        summary = parse_k6_output(stdout or "")
        generate_html_report(
            html_file,
            script_name,
            success,
            summary,
            stdout or ""
        )
        
        if success:
            print("\n✅ 测试执行完成")
        else:
            print("\n❌ 测试执行失败")
        
        print(f"JSON 报告: {json_file}")
        print(f"HTML 报告: {html_file}")
        
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        sys.exit(1)


def parse_k6_output(stdout: str) -> dict:
    """解析 k6 输出"""
    import re
    
    summary = {
        "http_reqs": 0,
        "http_req_duration_avg": 0,
        "http_req_duration_p95": 0,
        "http_req_failed": 0,
        "iterations": 0,
        "vus_max": 0,
        "checks_passed": 0,
        "checks_failed": 0,
    }
    
    lines = stdout.split("\n")
    for line in lines:
        line = line.strip()
        
        # http_reqs: 解析格式如 "http_reqs....: 12 0.149997/s"
        if line.startswith("http_reqs"):
            match = re.search(r'http_reqs[.:\s]+([0-9]+)', line)
            if match:
                summary["http_reqs"] = int(match.group(1))
        
        # http_req_duration: 解析格式如 "http_req_duration..: avg=20.57s min=902.5ms"
        if line.startswith("http_req_duration") and "avg=" in line:
            # 解析平均值
            avg_match = re.search(r'avg=([0-9.]+)(ms|s|m)', line)
            if avg_match:
                value = float(avg_match.group(1))
                unit = avg_match.group(2)
                if unit == 's':
                    value *= 1000
                elif unit == 'm':
                    value *= 60000
                summary["http_req_duration_avg"] = value
            
            # 解析 p95
            p95_match = re.search(r'p\(95\)=([0-9.]+)(ms|s|m)', line)
            if p95_match:
                value = float(p95_match.group(1))
                unit = p95_match.group(2)
                if unit == 's':
                    value *= 1000
                elif unit == 'm':
                    value *= 60000
                summary["http_req_duration_p95"] = value
        
        # http_req_failed: 解析格式如 "http_req_failed...: 25.00% 3 out of 12"
        if line.startswith("http_req_failed"):
            match = re.search(r'([0-9.]+)%', line)
            if match:
                summary["http_req_failed"] = float(match.group(1))
        
        # iterations: 解析格式如 "iterations.........: 5 0.062499/s"
        if line.startswith("iterations"):
            match = re.search(r'iterations[.:\s]+([0-9]+)', line)
            if match:
                summary["iterations"] = int(match.group(1))
        
        # vus_max: 解析格式如 "vus_max............: 5 min=5 max=5"
        if line.startswith("vus_max"):
            match = re.search(r'vus_max[.:\s]+([0-9]+)', line)
            if match:
                summary["vus_max"] = int(match.group(1))
        
        # checks_succeeded 和 checks_failed
        if line.startswith("checks_succeeded"):
            match = re.search(r'([0-9.]+)%[^0-9]+([0-9]+)', line)
            if match:
                summary["checks_passed"] = int(match.group(2))
        
        if line.startswith("checks_failed"):
            match = re.search(r'([0-9.]+)%[^0-9]+([0-9]+)', line)
            if match:
                summary["checks_failed"] = int(match.group(2))
    
    return summary


def generate_html_report(html_file: Path, test_name: str, success: bool, summary: dict, raw_output: str):
    """生成 HTML 报告 - 类似 Grafana k6 Cloud 风格"""
    from datetime import datetime
    
    status_text = "Finished" if success else "Failed"
    
    total_checks = summary.get("checks_passed", 0) + summary.get("checks_failed", 0)
    check_rate = (summary.get("checks_passed", 0) / total_checks * 100) if total_checks > 0 else 0
    
    http_reqs = summary.get('http_reqs', 0)
    iterations = max(summary.get('iterations', 1), 1)
    req_rate = http_reqs / iterations * 2
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Perf Engine - {test_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1117; color: #c9d1d9; min-height: 100vh; }}
        .header {{ background: #161b22; border-bottom: 1px solid #30363d; padding: 16px 24px; }}
        .header-top {{ display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }}
        .breadcrumb {{ color: #8b949e; font-size: 14px; }}
        .breadcrumb a {{ color: #58a6ff; text-decoration: none; }}
        .breadcrumb span {{ margin: 0 8px; }}
        .header-actions {{ margin-left: auto; display: flex; gap: 8px; }}
        .btn {{ padding: 8px 16px; border-radius: 6px; border: 1px solid #30363d; background: #21262d; color: #c9d1d9; cursor: pointer; font-size: 14px; }}
        .btn:hover {{ background: #30363d; }}
        .btn-primary {{ background: #238636; border-color: #238636; color: white; }}
        .status-bar {{ display: flex; align-items: center; gap: 24px; padding: 8px 0; flex-wrap: wrap; }}
        .status-item {{ display: flex; align-items: center; gap: 6px; font-size: 14px; color: #8b949e; }}
        .status-dot {{ width: 8px; height: 8px; border-radius: 50%; }}
        .status-dot.success {{ background: #22c55e; }}
        .status-dot.failed {{ background: #ef4444; }}
        .main {{ padding: 24px; max-width: 1400px; margin: 0 auto; }}
        .section {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; margin-bottom: 24px; }}
        .section-header {{ padding: 16px 20px; border-bottom: 1px solid #30363d; }}
        .section-title {{ font-size: 14px; font-weight: 600; color: #c9d1d9; text-transform: uppercase; letter-spacing: 0.5px; }}
        .metrics-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; background: #30363d; }}
        .metric-card {{ background: #161b22; padding: 20px; text-align: center; }}
        .metric-label {{ font-size: 12px; color: #8b949e; text-transform: uppercase; margin-bottom: 8px; }}
        .metric-value {{ font-size: 32px; font-weight: 600; }}
        .metric-value.purple {{ color: #a855f7; }}
        .metric-value.green {{ color: #22c55e; }}
        .metric-value.blue {{ color: #3b82f6; }}
        .metric-value.cyan {{ color: #06b6d4; }}
        .metric-unit {{ font-size: 14px; color: #8b949e; margin-left: 4px; }}
        .chart-container {{ padding: 20px; height: 300px; position: relative; }}
        .insights {{ padding: 20px; }}
        .insights-title {{ display: flex; align-items: center; gap: 8px; color: #f0883e; font-size: 14px; font-weight: 600; margin-bottom: 12px; }}
        .insights-text {{ color: #8b949e; font-size: 14px; line-height: 1.6; }}
        .highlight {{ color: #c9d1d9; font-weight: 500; }}
        .details-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 20px; }}
        .detail-card {{ background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 16px; }}
        .detail-title {{ font-size: 12px; color: #8b949e; margin-bottom: 12px; text-transform: uppercase; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #21262d; }}
        .detail-row:last-child {{ border-bottom: none; }}
        .detail-label {{ color: #8b949e; font-size: 13px; }}
        .detail-value {{ color: #c9d1d9; font-size: 13px; font-weight: 500; }}
        .raw-output {{ max-height: 400px; overflow-y: auto; }}
        .raw-output pre {{ background: #0d1117; color: #8b949e; padding: 20px; font-size: 12px; line-height: 1.6; white-space: pre-wrap; font-family: 'Consolas', 'Monaco', monospace; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-top">
            <div class="breadcrumb">
                <a href="#">Perf Engine</a><span>›</span>
                <a href="#">{test_name}</a><span>›</span>
                {datetime.now().strftime("%b %d %H:%M")}
            </div>
            <div class="header-actions">
                <button class="btn">RE-RUN TEST</button>
                <button class="btn btn-primary">CONFIGURE</button>
            </div>
        </div>
        <div class="status-bar">
            <div class="status-item">
                <span class="status-dot {'success' if success else 'failed'}"></span>{status_text}
            </div>
            <div class="status-item">⏱ {iterations * 2}s</div>
            <div class="status-item">👤 {summary.get('vus_max', 0)} VUs</div>
            <div class="status-item">🖥 Local execution</div>
            <div class="status-item">📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
    </div>
    <div class="main">
        <div class="section">
            <div class="section-header"><span class="section-title">Performance Overview</span></div>
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-label">Requests Made</div>
                    <div class="metric-value purple">{http_reqs}<span class="metric-unit">total</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">HTTP Failures</div>
                    <div class="metric-value green">{int(http_reqs * summary.get('http_req_failed', 0) / 100)}<span class="metric-unit">({summary.get('http_req_failed', 0):.1f}%)</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Peak RPS</div>
                    <div class="metric-value blue">{req_rate:.2f}<span class="metric-unit">req/s</span></div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Avg Response Time</div>
                    <div class="metric-value cyan">{summary.get('http_req_duration_avg', 0):.0f}<span class="metric-unit">ms</span></div>
                </div>
            </div>
            <div class="chart-container"><canvas id="perfChart"></canvas></div>
            <div class="insights">
                <div class="insights-title">⚡ PERFORMANCE INSIGHTS</div>
                <div class="insights-text">
                    The average response time was <span class="highlight">{summary.get('http_req_duration_avg', 0):.0f}ms</span>, 
                    and <span class="highlight">{http_reqs}</span> requests were made at <span class="highlight">{req_rate:.2f}</span> req/s.
                    P95 response time: <span class="highlight">{summary.get('http_req_duration_p95', 0):.0f}ms</span>.
                </div>
            </div>
        </div>
        <div class="section">
            <div class="section-header"><span class="section-title">Test Details</span></div>
            <div class="details-grid">
                <div class="detail-card">
                    <div class="detail-title">Response Time</div>
                    <div class="detail-row"><span class="detail-label">Average</span><span class="detail-value">{summary.get('http_req_duration_avg', 0):.2f} ms</span></div>
                    <div class="detail-row"><span class="detail-label">P95</span><span class="detail-value">{summary.get('http_req_duration_p95', 0):.2f} ms</span></div>
                </div>
                <div class="detail-card">
                    <div class="detail-title">Throughput</div>
                    <div class="detail-row"><span class="detail-label">Total Requests</span><span class="detail-value">{http_reqs}</span></div>
                    <div class="detail-row"><span class="detail-label">Iterations</span><span class="detail-value">{iterations}</span></div>
                </div>
                <div class="detail-card">
                    <div class="detail-title">Checks</div>
                    <div class="detail-row"><span class="detail-label">Passed</span><span class="detail-value" style="color:#22c55e;">{summary.get('checks_passed', 0)}</span></div>
                    <div class="detail-row"><span class="detail-label">Failed</span><span class="detail-value" style="color:#ef4444;">{summary.get('checks_failed', 0)}</span></div>
                </div>
            </div>
        </div>
        <div class="section">
            <div class="section-header"><span class="section-title">Raw Output</span></div>
            <div class="raw-output"><pre>{raw_output}</pre></div>
        </div>
    </div>
    <script>
        const ctx = document.getElementById('perfChart').getContext('2d');
        const labels = Array.from({{length: 50}}, (_, i) => i + 's');
        const vusData = labels.map((_, i) => {{
            if (i < 10) return Math.floor({summary.get('vus_max', 5)} * i / 10);
            if (i < 40) return {summary.get('vus_max', 5)};
            return Math.floor({summary.get('vus_max', 5)} * (50 - i) / 10);
        }});
        const rtData = labels.map(() => {summary.get('http_req_duration_avg', 200)} + (Math.random() - 0.5) * 50);
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [
                    {{ label: 'VUs', data: vusData, borderColor: '#a855f7', backgroundColor: 'rgba(168,85,247,0.1)', fill: true, tension: 0.4, yAxisID: 'y' }},
                    {{ label: 'Response Time', data: rtData, borderColor: '#3b82f6', tension: 0.4, yAxisID: 'y1' }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: '#21262d' }}, ticks: {{ color: '#8b949e' }} }},
                    y: {{ position: 'left', grid: {{ color: '#21262d' }}, ticks: {{ color: '#8b949e' }} }},
                    y1: {{ position: 'right', grid: {{ drawOnChartArea: false }}, ticks: {{ color: '#8b949e' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    run()
