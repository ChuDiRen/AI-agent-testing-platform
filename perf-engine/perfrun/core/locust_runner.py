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
        
        # Helper to colorize HTTP methods
        def method_cls(m):
            m = m.upper().split()[0] if ' ' in m else m.upper()
            if m == 'GET': return 'm-get'
            if m == 'POST': return 'm-post'
            if m == 'PUT': return 'm-put'
            if m == 'DELETE': return 'm-del'
            return ''

        rows = "".join([f"<tr><td><span class='badge {method_cls(r.get('Type','-'))}'>{r.get('Type','-')}</span></td><td>{r.get('Name','-')}</td><td>{si(r.get('Request Count'))}</td><td class='{'f' if si(r.get('Failure Count'))>0 else ''}'>{si(r.get('Failure Count'))}</td><td>{sf(r.get('Average Response Time')):.0f}</td><td>{sf(r.get('Min Response Time')):.0f}</td><td>{sf(r.get('Max Response Time')):.0f}</td><td>{sf(r.get('50%')):.0f}</td><td>{sf(r.get('90%')):.0f}</td><td>{sf(r.get('95%')):.0f}</td><td>{sf(r.get('99%')):.0f}</td><td>{sf(r.get('Requests/s')):.2f}</td></tr>" for r in reqs])
        
        frows = "".join([f"<tr><td><span class='badge {method_cls(f.get('Method','-'))}'>{f.get('Method','-')}</span></td><td>{f.get('Name','-')}</td><td>{f.get('Occurrences','-')}</td><td><code>{str(f.get('Error','-'))[:120]}</code></td></tr>" for f in fails])
        fsec = f"<div class='c'><h2>Failures</h2><div class='table-responsive'><table><tr><th>Method</th><th>Name</th><th>Count</th><th>Error</th></tr>{frows}</table></div></div>" if fails else ""
        
        return f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Locust Report</title>
<style>
:root {{ --bg: #0d1117; --card-bg: #161b22; --border: #30363d; --text: #c9d1d9; --text-muted: #8b949e; --accent: #58a6ff; --success: #238636; --danger: #da3633; --warning: #d29922; }}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;background:var(--bg);color:var(--text);padding:20px;line-height:1.5}}
.w{{max-width:1400px;margin:0 auto;animation:fadeIn 0.5s ease-out}}
@keyframes fadeIn {{ from {{opacity:0;transform:translateY(10px)}} to {{opacity:1;transform:translateY(0)}} }}
.h{{background:linear-gradient(135deg,#1f6feb,#238636);padding:32px;border-radius:12px;margin-bottom:24px;box-shadow:0 8px 24px rgba(0,0,0,0.2)}}
.h h1{{color:#fff;font-size:28px;font-weight:700;margin-bottom:8px}}
.h .m{{color:rgba(255,255,255,0.9);font-size:14px;font-family:ui-monospace,SFMono-Regular,SF Mono,Menlo,Consolas,Liberation Mono,monospace}}
.c{{background:var(--card-bg);border:1px solid var(--border);border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 4px 12px rgba(0,0,0,0.1)}}
.c h2{{font-size:18px;color:var(--accent);margin-bottom:20px;display:flex;align-items:center;gap:8px}}
.c h2::before{{content:'';display:block;width:4px;height:18px;background:var(--accent);border-radius:2px}}
.s{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px}}
.st{{background:#21262d;padding:20px;border-radius:8px;text-align:center;border:1px solid var(--border);transition:transform 0.2s}}
.st:hover{{transform:translateY(-2px);border-color:var(--accent)}}
.st .v{{font-size:32px;font-weight:700;color:var(--text);line-height:1.2}}
.st .l{{font-size:13px;color:var(--text-muted);margin-top:4px;text-transform:uppercase;letter-spacing:0.5px}}
.st.g .v{{color:#3fb950}} .st.r .v{{color:#f85149}}
table{{width:100%;border-collapse:separate;border-spacing:0;font-size:14px}}
th,td{{padding:12px 16px;text-align:left;border-bottom:1px solid var(--border)}}
th{{background:#21262d;color:var(--text-muted);font-weight:600;position:sticky;top:0}}
tr:last-child td{{border-bottom:none}}
tr:nth-child(even){{background-color:rgba(255,255,255,0.02)}}
tr:hover{{background-color:rgba(110,118,129,0.1)}}
.f{{color:#f85149;font-weight:bold}}
code{{background:rgba(110,118,129,0.2);padding:4px 8px;border-radius:4px;font-family:ui-monospace,monospace;font-size:12px;color:#e1e4e8;word-break:break-all}}
.badge{{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:600;background:#30363d;color:var(--text-muted)}}
.m-get{{background:rgba(56,139,253,0.15);color:#58a6ff}}
.m-post{{background:rgba(63,185,80,0.15);color:#3fb950}}
.m-put{{background:rgba(210,153,34,0.15);color:#d29922}}
.m-del{{background:rgba(248,81,73,0.15);color:#f85149}}
.table-responsive{{overflow-x:auto}}
</style></head>
<body><div class="w"><div class="h"><h1>Locust Performance Report</h1><div class="m">Host: {self.host} &bull; Users: {self.users} &bull; Rate: {self.spawn_rate}/s &bull; Duration: {self.run_time} &bull; {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div></div>
<div class="c"><h2>Summary</h2><div class="s"><div class="st"><div class="v">{total}</div><div class="l">Requests</div></div><div class="st {'r' if fail>0 else 'g'}"><div class="v">{fail}</div><div class="l">Failures</div></div><div class="st {'r' if rate>1 else 'g'}"><div class="v">{rate:.1f}%</div><div class="l">Fail Rate</div></div><div class="st"><div class="v">{sf(agg.get('Requests/s')):.1f}</div><div class="l">RPS</div></div><div class="st"><div class="v">{sf(agg.get('Average Response Time')):.0f}</div><div class="l">Avg(ms)</div></div><div class="st"><div class="v">{sf(agg.get('Min Response Time')):.0f}</div><div class="l">Min(ms)</div></div><div class="st"><div class="v">{sf(agg.get('Max Response Time')):.0f}</div><div class="l">Max(ms)</div></div><div class="st"><div class="v">{sf(agg.get('95%')):.0f}</div><div class="l">P95(ms)</div></div></div></div>
<div class="c"><h2>Requests Details</h2><div class="table-responsive"><table><tr><th>Type</th><th>Name</th><th>Reqs</th><th>Fails</th><th>Avg</th><th>Min</th><th>Max</th><th>P50</th><th>P90</th><th>P95</th><th>P99</th><th>RPS</th></tr>{rows}</table></div></div>{fsec}</div></body></html>'''
