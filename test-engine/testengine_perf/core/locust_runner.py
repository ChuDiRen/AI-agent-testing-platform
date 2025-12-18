"""Locust Runner - CLI based with CSV output and HTML report generation"""
import os
import sys
import subprocess
import tempfile
import json
import csv
from pathlib import Path
from datetime import datetime

LOCUSTFILE_TEMPLATE = '''
import json, time, random, re
from locust import HttpUser, task, between

CASES = __CASES__
CTX = __CTX__

class KW:
    def __init__(s, c): s.c, s.ctx, s.r = c, {}, None
    def _rv(s, v):
        if isinstance(v, str): return re.sub(r"\\{\\{(\\w+)\\}\\}", lambda m: str(s.ctx.get(m.group(1), m.group(0))), v)
        if isinstance(v, dict): return {k: s._rv(x) for k,x in v.items()}
        if isinstance(v, list): return [s._rv(x) for x in v]
        return v
    def get(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        u, n = s._rv(k.pop("url","/")), k.pop("name",None)
        rk = {"name":n} if n else {}
        if "params" in k: rk["params"] = s._rv(k["params"])
        if "headers" in k: rk["headers"] = s._rv(k["headers"])
        s.r = s.c.get(u, **rk)
    def post(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        u, n = s._rv(k.pop("url","/")), k.pop("name",None)
        rk = {"name":n} if n else {}
        if "json" in k: rk["json"] = s._rv(k["json"])
        if "data" in k: rk["data"] = s._rv(k["data"])
        if "headers" in k: rk["headers"] = s._rv(k["headers"])
        s.r = s.c.post(u, **rk)
    def put(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        u, n = s._rv(k.pop("url","/")), k.pop("name",None)
        rk = {"name":n} if n else {}
        if "json" in k: rk["json"] = s._rv(k["json"])
        s.r = s.c.put(u, **rk)
    def delete(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        u, n = s._rv(k.pop("url","/")), k.pop("name",None)
        s.r = s.c.delete(u, name=n) if n else s.c.delete(u)
    def think_time(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        sec = k.get("seconds")
        if sec: time.sleep(float(sec))
        else: time.sleep(random.uniform(float(k.get("min",1)), float(k.get("max",1))))
    def check_status(s, **k): k.pop("\\u5173\\u952e\\u5b57", None)
    def check_response_time(s, **k): k.pop("\\u5173\\u952e\\u5b57", None)
    def check_contains(s, **k): k.pop("\\u5173\\u952e\\u5b57", None)
    def start_transaction(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        s.ctx["_ts"], s.ctx["_tn"] = time.time(), k.get("name","tx")
    def end_transaction(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        if "_ts" in s.ctx: print("TX [%s]: %.0fms" % (s.ctx["_tn"], (time.time()-s.ctx["_ts"])*1000))
    def set_var(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        if k.get("name"): s.ctx[k["name"]] = s._rv(k.get("value"))
    def log(s, **k):
        k.pop("\\u5173\\u952e\\u5b57", None)
        print("[LOG] %s" % s._rv(k.get("message","")))

class U(HttpUser):
    wait_time = between(1, 3)
    def on_start(s): s.kw = KW(s.client); s.kw.ctx.update(CTX)
    @task
    def t(s):
        for c in CASES:
            for st in c.get("steps", []):
                if isinstance(st, dict):
                    for nm, dt in st.items():
                        if isinstance(dt, dict):
                            kw = dt.get("\\u5173\\u952e\\u5b57") or dt.get("keyword","")
                            if kw and hasattr(s.kw, kw):
                                try: getattr(s.kw, kw)(**dt)
                                except Exception as e: print("Err [%s]: %s" % (nm, e))
'''


class LocustRunner:
    def __init__(self, host, users=10, spawn_rate=1, run_time="60s", headless=True):
        self.host = host
        self.users = users
        self.spawn_rate = spawn_rate
        self.run_time = run_time
        self.headless = headless
        self.test_cases = []
        self.context = {}
    
    def set_test_cases(self, cases):
        self.test_cases = cases
    
    def set_context(self, context):
        self.context = context
    
    def run(self, output_dir=None):
        locustfile = self._generate_locustfile()
        
        cmd = [sys.executable, "-m", "locust", "-f", locustfile, "-H", self.host,
               "-u", str(self.users), "-r", str(self.spawn_rate), "-t", self.run_time, "--headless"]
        
        csv_prefix = None
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            csv_prefix = str(Path(output_dir) / "locust")
            cmd.extend(["--csv", csv_prefix])
        
        print(f"\n{'='*60}\nLocust Performance Test\n{'='*60}")
        print(f"Host: {self.host}, Users: {self.users}, Duration: {self.run_time}\n{'='*60}\n")
        
        try:
            result = subprocess.run(cmd)
            if output_dir and csv_prefix:
                self._generate_html_from_csv(output_dir, csv_prefix)
            return {"exit_code": result.returncode}
        finally:
            try: os.unlink(locustfile)
            except: pass
    
    def _generate_locustfile(self):
        cases_json = repr(self.test_cases)
        ctx_json = repr(self.context)
        code = LOCUSTFILE_TEMPLATE.replace('__CASES__', cases_json).replace('__CTX__', ctx_json)
        fd, fp = tempfile.mkstemp(suffix=".py", prefix="lf_")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(code)
        return fp
    
    def _generate_html_from_csv(self, output_dir, csv_prefix):
        stats_file = f"{csv_prefix}_stats.csv"
        failures_file = f"{csv_prefix}_failures.csv"
        if not os.path.exists(stats_file): return
        
        stats, failures = [], []
        with open(stats_file, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f): stats.append(row)
        if os.path.exists(failures_file):
            with open(failures_file, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f): failures.append(row)
        
        agg = next((s for s in stats if s.get('Name') == 'Aggregated'), stats[-1] if stats else {})
        reqs = [s for s in stats if s.get('Name') != 'Aggregated']
        
        html = self._build_html(agg, reqs, failures)
        
        # 使用时间戳命名报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_path = Path(output_dir) / f"report_{timestamp}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f: f.write(html)
        print(f"HTML Report: {html_path}")
    
    def _build_html(self, agg, reqs, fails):
        def sf(v, d=0):
            try: return float(v) if v else d
            except: return d
        def si(v, d=0):
            try: return int(float(v)) if v else d
            except: return d
        
        total, fail = si(agg.get('Request Count')), si(agg.get('Failure Count'))
        rate = (fail/total*100) if total > 0 else 0
        success_rate = 100 - rate

        # Helper to colorize HTTP methods
        def method_cls(m):
            m = m.upper().split()[0] if ' ' in m else m.upper()
            return f"method-{m.lower()}" if m in ['GET','POST','PUT','DELETE'] else 'method-other'

        def p_bar(percent, color_class):
            return f'<div class="progress-bar"><div class="fill {color_class}" style="width: {percent}%"></div></div>'

        rows = "".join([f"""
        <tr>
            <td><span class='badge {method_cls(r.get('Type','-'))}'>{r.get('Type','-')}</span></td>
            <td class='name-cell' title='{r.get('Name','-')}'>{r.get('Name','-')}</td>
            <td class='text-right'>{si(r.get('Request Count'))}</td>
            <td class='text-right'>{si(r.get('Failure Count'))}</td>
            <td class='text-right'>{sf(r.get('Average Response Time')):.0f}</td>
            <td class='text-right'>{sf(r.get('Min Response Time')):.0f}</td>
            <td class='text-right'>{sf(r.get('Max Response Time')):.0f}</td>
            <td class='text-right font-medium'>{sf(r.get('95%')):.0f}</td>
            <td class='text-right font-medium'>{sf(r.get('99%')):.0f}</td>
            <td class='text-right'>{sf(r.get('Requests/s')):.2f}</td>
        </tr>""" for r in reqs])
        
        frows = "".join([f"""
        <tr>
            <td><span class='badge {method_cls(f.get('Method','-'))}'>{f.get('Method','-')}</span></td>
            <td class='name-cell'>{f.get('Name','-')}</td>
            <td class='text-right'>{f.get('Occurrences','-')}</td>
            <td class='error-cell'>{str(f.get('Error','-'))[:120]}</td>
        </tr>""" for f in fails])
        
        fsec = f"""
        <div class='section-card danger-border'>
            <div class='card-header'>
                <div class='card-icon icon-danger'>!</div>
                <h2>Failures Details</h2>
            </div>
            <div class='table-container'>
                <table>
                    <thead><tr><th width="80">Method</th><th>Name</th><th width="100" class='text-right'>Count</th><th>Error</th></tr></thead>
                    <tbody>{frows}</tbody>
                </table>
            </div>
        </div>""" if fails else ""
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-body: #f4f6f8;
            --bg-card: #ffffff;
            --text-primary: #111827;
            --text-secondary: #6b7280;
            --border-color: #e5e7eb;
            --primary: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 40px 20px;
        }}

        .container {{ max-width: 1400px; margin: 0 auto; }}

        /* Header */
        .header {{
            background: var(--bg-card);
            padding: 30px;
            border-radius: 16px;
            box-shadow: var(--shadow);
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .brand h1 {{ font-size: 24px; font-weight: 700; color: var(--text-primary); }}
        .brand .subtitle {{ font-size: 14px; color: var(--text-secondary); margin-top: 4px; }}
        
        .meta-grid {{ display: flex; gap: 40px; }}
        .meta-item label {{ display: block; font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }}
        .meta-item value {{ display: block; font-size: 15px; font-weight: 500; color: var(--text-primary); margin-top: 2px; }}

        /* Stats Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 24px;
            margin-bottom: 24px;
        }}

        .stat-card {{
            background: var(--bg-card);
            padding: 24px;
            border-radius: 16px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
        }}

        .stat-label {{ font-size: 14px; color: var(--text-secondary); font-weight: 500; }}
        .stat-value {{ font-size: 32px; font-weight: 700; color: var(--text-primary); margin: 8px 0; letter-spacing: -0.02em; }}
        .stat-desc {{ font-size: 13px; color: var(--success); font-weight: 500; display: flex; align-items: center; gap: 4px; }}
        .stat-desc.bad {{ color: var(--danger); }}

        /* Main Content */
        .section-card {{
            background: var(--bg-card);
            border-radius: 16px;
            box-shadow: var(--shadow);
            border: 1px solid var(--border-color);
            margin-bottom: 24px;
            overflow: hidden;
        }}
        
        .danger-border {{ border-left: 4px solid var(--danger); }}

        .card-header {{
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 12px;
            background: #f9fafb;
        }}

        .card-header h2 {{ font-size: 18px; font-weight: 600; color: var(--text-primary); }}
        
        .table-container {{ overflow-x: auto; }}
        
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; text-align: left; }}
        
        th {{
            background: #f9fafb;
            padding: 12px 24px;
            font-weight: 600;
            color: var(--text-secondary);
            border-bottom: 1px solid var(--border-color);
            white-space: nowrap;
        }}
        
        td {{
            padding: 16px 24px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
        }}
        
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #f9fafb; }}

        /* Utils */
        .text-right {{ text-align: right; }}
        .font-medium {{ font-weight: 600; color: var(--text-primary); }}
        .name-cell {{ font-weight: 500; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .error-cell {{ color: var(--danger); font-family: monospace; font-size: 13px; }}
        
        /* Badges & Progress */
        .badge {{
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .method-get {{ background: #eff6ff; color: #3b82f6; }}
        .method-post {{ background: #ecfdf5; color: #10b981; }}
        .method-put {{ background: #fffbeb; color: #f59e0b; }}
        .method-delete {{ background: #fef2f2; color: #ef4444; }}
        .method-other {{ background: #f3f4f6; color: #6b7280; }}

        .progress-bar {{
            height: 6px;
            background: #e5e7eb;
            border-radius: 3px;
            overflow: hidden;
            margin-top: 6px;
        }}
        
        .fill {{ height: 100%; border-radius: 3px; }}
        .bg-success {{ background: var(--success); }}
        .bg-danger {{ background: var(--danger); }}

    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div class="brand">
                <h1>Performance Test Report</h1>
                <div class="subtitle">Generated by Perf-Engine</div>
            </div>
            <div class="meta-grid">
                <div class="meta-item"><label>Target Host</label><value>{self.host}</value></div>
                <div class="meta-item"><label>Concurrency</label><value>{self.users} Users</value></div>
                <div class="meta-item"><label>Duration</label><value>{self.run_time}</value></div>
                <div class="meta-item"><label>Date</label><value>{datetime.now().strftime('%Y-%m-%d %H:%M')}</value></div>
            </div>
        </header>

        <!-- Stats Overview -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Requests</div>
                <div class="stat-value">{total:,}</div>
                <div class="stat-desc">Samples collected</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{success_rate:.1f}%</div>
                <div class="stat-desc {'bad' if success_rate < 99 else ''}">
                    {fail} failures recorded
                </div>
                {p_bar(success_rate, 'bg-success' if success_rate >= 99 else 'bg-danger')}
            </div>
            
            <div class="stat-card">
                <div class="stat-label">RPS (Throughput)</div>
                <div class="stat-value">{sf(agg.get('Requests/s')):.1f}</div>
                <div class="stat-desc">Requests per second</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">Response Time (P95)</div>
                <div class="stat-value">{sf(agg.get('95%')):.0f} ms</div>
                <div class="stat-desc">Avg: {sf(agg.get('Average Response Time')):.0f} ms / Max: {sf(agg.get('Max Response Time')):.0f} ms</div>
            </div>
        </div>

        <!-- Main Table -->
        <div class="section-card">
            <div class="card-header">
                <h2>Request Statistics</h2>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th width="80">Method</th>
                            <th>Info / Name</th>
                            <th class="text-right">Requests</th>
                            <th class="text-right">Fails</th>
                            <th class="text-right">Avg (ms)</th>
                            <th class="text-right">Min (ms)</th>
                            <th class="text-right">Max (ms)</th>
                            <th class="text-right">P95 (ms)</th>
                            <th class="text-right">P99 (ms)</th>
                            <th class="text-right">RPS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Failures -->
        {fsec}
    </div>
</body>
</html>'''
