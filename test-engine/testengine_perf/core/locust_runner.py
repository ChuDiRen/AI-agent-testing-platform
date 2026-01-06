"""
Locust Runner - 基于关键字驱动的性能测试执行器

支持特性:
- 完整 Locust 语法映射
- catch_response 响应验证
- 事务统计
- 顺序任务集
- 数据驱动
- 多用户类型
- HTML 报告生成
"""
import os
import sys
import subprocess
import tempfile
import json
import csv
import re
from pathlib import Path
from datetime import datetime


# Locust 脚本模板 - 支持完整关键字驱动
LOCUSTFILE_TEMPLATE = '''
"""Auto-generated Locust script from YAML test cases"""
import json
import time
import random
import re
from locust import HttpUser, task, between, constant, events, SequentialTaskSet

# 测试用例和上下文
CASES = __CASES__
CTX = __CTX__
CONFIG = __CONFIG__


class Keywords:
    """关键字驱动执行器"""
    
    def __init__(self, client):
        self.client = client
        self.ctx = {}
        self.response = None
        self._catch_ctx = None
        self._tx_stack = []
    
    def _render(self, value):
        """渲染变量 {{var}}"""
        if isinstance(value, str):
            return re.sub(r"\\{\\{(\\w+)\\}\\}", lambda m: str(self.ctx.get(m.group(1), m.group(0))), value)
        if isinstance(value, dict):
            return {k: self._render(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._render(i) for i in value]
        return value
    
    def _pop_kw(self, kw):
        kw.pop("关键字", None)
        kw.pop("keyword", None)
        return kw
    
    # ========== HTTP 请求 ==========
    
    def get(self, **kw):
        return self._request("get", **self._pop_kw(kw))
    
    def post(self, **kw):
        return self._request("post", **self._pop_kw(kw))
    
    def put(self, **kw):
        return self._request("put", **self._pop_kw(kw))
    
    def delete(self, **kw):
        return self._request("delete", **self._pop_kw(kw))
    
    def patch(self, **kw):
        return self._request("patch", **self._pop_kw(kw))
    
    def _request(self, method, **kw):
        url = self._render(kw.pop("url", "/"))
        name = kw.pop("name", None)
        catch = kw.pop("catch_response", False)
        
        req_kw = {}
        if name:
            req_kw["name"] = name
        if catch:
            req_kw["catch_response"] = True
        
        for key in ["headers", "params", "data", "json", "files"]:
            if key in kw:
                req_kw[key] = self._render(kw[key])
        
        func = getattr(self.client, method)
        
        if catch:
            self._catch_ctx = func(url, **req_kw)
            self.response = self._catch_ctx.__enter__()
        else:
            self.response = func(url, **req_kw)
        
        return self.response
    
    # ========== 等待时间 ==========
    
    def wait(self, **kw):
        self._pop_kw(kw)
        sec = kw.get("seconds")
        if sec:
            time.sleep(float(sec))
        else:
            time.sleep(random.uniform(float(kw.get("min", 1)), float(kw.get("max", 1))))
    
    think_time = wait
    
    def constant_pacing(self, **kw):
        self._pop_kw(kw)
        time.sleep(float(kw.get("seconds", 1)))
    
    # ========== 响应验证 ==========
    
    def assert_status(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return False
        expected = int(kw.get("expected", 200))
        actual = self.response.status_code
        if actual == expected:
            self._mark_success()
            return True
        if kw.get("fail_on_error", True):
            self._mark_failure(f"Expected {expected}, got {actual}")
        return False
    
    check_status = assert_status
    
    def assert_response_time(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return False
        max_ms = float(kw.get("max_ms", 1000))
        actual = self.response.elapsed.total_seconds() * 1000
        if actual <= max_ms:
            return True
        if kw.get("fail_on_error", True):
            self._mark_failure(f"Response time {actual:.0f}ms > {max_ms}ms")
        return False
    
    check_response_time = assert_response_time
    
    def assert_contains(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return False
        text = self._render(kw.get("text", ""))
        if text in self.response.text:
            return True
        if kw.get("fail_on_error", True):
            self._mark_failure(f"Response does not contain: {text}")
        return False
    
    check_contains = assert_contains
    
    def assert_json(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return False
        try:
            import jsonpath
            data = self.response.json()
            path = kw.get("path", "$")
            expected = self._render(kw.get("expected"))
            op = kw.get("operator", "eq")
            
            result = jsonpath.jsonpath(data, path)
            if not result:
                if kw.get("fail_on_error", True):
                    self._mark_failure(f"JSONPath {path} not found")
                return False
            
            actual = result[0] if isinstance(result, list) else result
            passed = self._compare(actual, expected, op)
            
            if not passed and kw.get("fail_on_error", True):
                self._mark_failure(f"JSON: {actual} {op} {expected} failed")
            return passed
        except Exception as e:
            if kw.get("fail_on_error", True):
                self._mark_failure(f"JSON error: {e}")
            return False
    
    validate_json = assert_json
    
    def assert_header(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return False
        name = kw.get("name", "")
        expected = self._render(kw.get("expected", ""))
        actual = self.response.headers.get(name, "")
        if str(actual) == str(expected):
            return True
        if kw.get("fail_on_error", True):
            self._mark_failure(f"Header {name}: expected {expected}, got {actual}")
        return False
    
    def _compare(self, actual, expected, op):
        try:
            if op == "eq": return str(actual) == str(expected)
            if op == "ne": return str(actual) != str(expected)
            if op == "gt": return float(actual) > float(expected)
            if op == "lt": return float(actual) < float(expected)
            if op == "gte": return float(actual) >= float(expected)
            if op == "lte": return float(actual) <= float(expected)
            if op == "contains": return str(expected) in str(actual)
            return str(actual) == str(expected)
        except:
            return False
    
    def mark_success(self, **kw):
        self._pop_kw(kw)
        self._mark_success(kw.get("message", ""))
    
    def mark_failure(self, **kw):
        self._pop_kw(kw)
        self._mark_failure(kw.get("message", "Unknown error"))
    
    def _mark_success(self, msg=""):
        if self._catch_ctx and self.response:
            self.response.success()
    
    def _mark_failure(self, msg):
        if self._catch_ctx and self.response:
            self.response.failure(msg)
        else:
            print(f"[FAIL] {msg}")
    
    # ========== 事务控制 ==========
    
    def start_transaction(self, **kw):
        self._pop_kw(kw)
        name = kw.get("name", "tx")
        self._tx_stack.append({"name": name, "start": time.time()})
    
    def end_transaction(self, **kw):
        self._pop_kw(kw)
        success = kw.get("success", True)
        if self._tx_stack:
            tx = self._tx_stack.pop()
            ms = (time.time() - tx["start"]) * 1000
            s = "✓" if success else "✗"
            print(f"[TX] {s} {tx['name']}: {ms:.0f}ms")
    
    def transaction(self, **kw):
        self._pop_kw(kw)
        name = kw.get("name", "tx")
        steps = kw.get("steps", [])
        self.start_transaction(name=name)
        try:
            for step in steps:
                self._exec_step(step)
            self.end_transaction(success=True)
        except:
            self.end_transaction(success=False)
            raise
    
    # ========== 顺序任务 ==========
    
    def sequential_tasks(self, **kw):
        self._pop_kw(kw)
        steps = kw.get("steps", [])
        loop = int(kw.get("loop", 1))
        for _ in range(loop):
            for step in steps:
                self._exec_step(step)
    
    def interrupt(self, **kw):
        self._pop_kw(kw)
        raise StopIteration(kw.get("message", "Interrupted"))
    
    # ========== 数据操作 ==========
    
    def set_var(self, **kw):
        self._pop_kw(kw)
        name = kw.get("name")
        if name:
            self.ctx[name] = self._render(kw.get("value"))
    
    def extract_json(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return None
        try:
            import jsonpath
            data = self.response.json()
            path = kw.get("path", "$")
            var = kw.get("var", "extracted")
            idx = int(kw.get("index", 0))
            result = jsonpath.jsonpath(data, path)
            if result:
                val = result[idx] if isinstance(result, list) and len(result) > idx else result
                self.ctx[var] = val
                return val
        except Exception as e:
            print(f"[EXTRACT] {e}")
        return None
    
    def extract_regex(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return None
        try:
            pattern = kw.get("pattern", "")
            var = kw.get("var", "extracted")
            group = int(kw.get("group", 1))
            match = re.search(pattern, self.response.text)
            if match:
                val = match.group(group)
                self.ctx[var] = val
                return val
        except Exception as e:
            print(f"[EXTRACT] {e}")
        return None
    
    def extract_header(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            return None
        name = kw.get("name", "")
        var = kw.get("var", "extracted")
        val = self.response.headers.get(name, "")
        self.ctx[var] = val
        return val
    
    # ========== 数据驱动 ==========
    
    def random_data(self, **kw):
        self._pop_kw(kw)
        data = kw.get("data", [])
        var = kw.get("var", "random_item")
        if data:
            self.ctx[var] = random.choice(data)
            return self.ctx[var]
        return None
    
    def cycle_data(self, **kw):
        self._pop_kw(kw)
        data = kw.get("data", [])
        var = kw.get("var", "cycle_item")
        key = f"_idx_{var}"
        if data:
            idx = self.ctx.get(key, 0)
            self.ctx[var] = data[idx % len(data)]
            self.ctx[key] = idx + 1
            return self.ctx[var]
        return None
    
    # ========== 条件与循环 ==========
    
    def if_condition(self, **kw):
        self._pop_kw(kw)
        cond = self._render(kw.get("condition", ""))
        then_steps = kw.get("then", [])
        else_steps = kw.get("else", [])
        try:
            result = eval(cond, {"__builtins__": {}}, self.ctx)
        except:
            result = False
        for step in (then_steps if result else else_steps):
            self._exec_step(step)
    
    def loop(self, **kw):
        self._pop_kw(kw)
        count = int(kw.get("count", 1))
        steps = kw.get("steps", [])
        delay = float(kw.get("delay", 0))
        for i in range(count):
            self.ctx["_loop_index"] = i
            for step in steps:
                self._exec_step(step)
            if delay > 0:
                time.sleep(delay)
    
    def foreach(self, **kw):
        self._pop_kw(kw)
        items = kw.get("items", [])
        if isinstance(items, str):
            items = self.ctx.get(items, [])
        items = self._render(items)
        var = kw.get("var", "item")
        steps = kw.get("steps", [])
        for i, item in enumerate(items):
            self.ctx[var] = item
            self.ctx["_foreach_index"] = i
            for step in steps:
                self._exec_step(step)
    
    # ========== 日志 ==========
    
    def log(self, **kw):
        self._pop_kw(kw)
        msg = self._render(kw.get("message", ""))
        level = kw.get("level", "info").upper()
        print(f"[{level}] {msg}")
    
    def print_response(self, **kw):
        self._pop_kw(kw)
        if not self.response:
            print("[RESPONSE] No response")
            return
        fmt = kw.get("format", "json")
        if fmt == "json":
            try:
                print(json.dumps(self.response.json(), indent=2, ensure_ascii=False))
            except:
                print(self.response.text)
        elif fmt == "text":
            print(self.response.text)
        elif fmt == "headers":
            print(dict(self.response.headers))
    
    # ========== 步骤执行 ==========
    
    def _exec_step(self, step):
        if isinstance(step, dict):
            for name, data in step.items():
                if isinstance(data, dict):
                    kw = data.get("关键字") or data.get("keyword", "")
                    if kw and hasattr(self, kw):
                        try:
                            getattr(self, kw)(**data)
                        except StopIteration:
                            raise
                        except Exception as e:
                            print(f"[ERROR] {name}: {e}")


# 事件钩子
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("=" * 60)
    print("Performance Test Started")
    print(f"Host: {environment.host}")
    print("=" * 60)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("=" * 60)
    print("Performance Test Completed")
    print("=" * 60)


# 用户类
class YamlUser(HttpUser):
    wait_time = between(
        CONFIG.get("wait_min", 1),
        CONFIG.get("wait_max", 3)
    )
    
    def on_start(self):
        self.kw = Keywords(self.client)
        self.kw.ctx.update(CTX)
        
        # 执行 on_start 步骤
        for case in CASES:
            on_start = case.get("on_start", [])
            for step in on_start:
                self.kw._exec_step(step)
    
    def on_stop(self):
        # 执行 on_stop 步骤
        for case in CASES:
            on_stop = case.get("on_stop", [])
            for step in on_stop:
                self.kw._exec_step(step)
    
    @task
    def run_cases(self):
        for case in CASES:
            steps = case.get("steps", [])
            for step in steps:
                self.kw._exec_step(step)
'''


class LocustRunner:
    """Locust 性能测试执行器"""
    
    def __init__(self, host, users=10, spawn_rate=1, run_time="60s", headless=True):
        self.host = host
        self.users = users
        self.spawn_rate = spawn_rate
        self.run_time = run_time
        self.headless = headless
        self.test_cases = []
        self.context = {}
        self.config = {
            "wait_min": 1,
            "wait_max": 3
        }
    
    def set_test_cases(self, cases):
        """设置测试用例"""
        self.test_cases = cases
    
    def set_context(self, context):
        """设置上下文变量"""
        self.context = context
    
    def set_config(self, config):
        """设置运行配置"""
        self.config.update(config)
    
    def run(self, output_dir=None):
        """运行性能测试"""
        locustfile = self._generate_locustfile()
        
        cmd = [
            sys.executable, "-m", "locust",
            "-f", locustfile,
            "-H", self.host,
            "-u", str(self.users),
            "-r", str(self.spawn_rate),
            "-t", self.run_time
        ]
        
        if self.headless:
            cmd.append("--headless")
        
        csv_prefix = None
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            csv_prefix = str(Path(output_dir) / "locust")
            cmd.extend(["--csv", csv_prefix])
        
        print(f"\n{'='*60}")
        print("Locust Performance Test")
        print(f"{'='*60}")
        print(f"Host: {self.host}")
        print(f"Users: {self.users}")
        print(f"Spawn Rate: {self.spawn_rate}/s")
        print(f"Duration: {self.run_time}")
        print(f"{'='*60}\n")
        
        try:
            result = subprocess.run(cmd)
            if output_dir and csv_prefix:
                self._generate_html_from_csv(output_dir, csv_prefix)
            return {"exit_code": result.returncode}
        finally:
            try:
                os.unlink(locustfile)
            except:
                pass
    
    def _generate_locustfile(self):
        """生成 Locust 脚本文件"""
        cases_json = repr(self.test_cases)
        ctx_json = repr(self.context)
        config_json = repr(self.config)
        
        code = LOCUSTFILE_TEMPLATE
        code = code.replace('__CASES__', cases_json)
        code = code.replace('__CTX__', ctx_json)
        code = code.replace('__CONFIG__', config_json)
        
        fd, fp = tempfile.mkstemp(suffix=".py", prefix="locust_")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(code)
        return fp
    
    def _generate_html_from_csv(self, output_dir, csv_prefix):
        """从 CSV 生成 HTML 报告"""
        stats_file = f"{csv_prefix}_stats.csv"
        failures_file = f"{csv_prefix}_failures.csv"
        
        if not os.path.exists(stats_file):
            return
        
        stats, failures = [], []
        
        with open(stats_file, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                stats.append(row)
        
        if os.path.exists(failures_file):
            with open(failures_file, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    failures.append(row)
        
        agg = next((s for s in stats if s.get('Name') == 'Aggregated'), stats[-1] if stats else {})
        reqs = [s for s in stats if s.get('Name') != 'Aggregated']
        
        html = self._build_html(agg, reqs, failures)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        html_path = Path(output_dir) / f"perf-report-{timestamp}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\nHTML Report: {html_path}")
    
    def _build_html(self, agg, reqs, fails):
        """构建 HTML 报告"""
        def sf(v, d=0):
            try:
                return float(v) if v else d
            except:
                return d
        
        def si(v, d=0):
            try:
                return int(float(v)) if v else d
            except:
                return d
        
        total = si(agg.get('Request Count'))
        fail = si(agg.get('Failure Count'))
        success_rate = ((total - fail) / total * 100) if total > 0 else 0
        
        def method_cls(m):
            m = m.upper().split()[0] if ' ' in m else m.upper()
            return f"method-{m.lower()}" if m in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'] else 'method-other'
        
        rows = "".join([f"""
        <tr>
            <td><span class='badge {method_cls(r.get('Type', '-'))}'>{r.get('Type', '-')}</span></td>
            <td class='name-cell' title='{r.get('Name', '-')}'>{r.get('Name', '-')}</td>
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
            <td><span class='badge {method_cls(f.get('Method', '-'))}'>{f.get('Method', '-')}</span></td>
            <td class='name-cell'>{f.get('Name', '-')}</td>
            <td class='text-right'>{f.get('Occurrences', '-')}</td>
            <td class='error-cell'>{str(f.get('Error', '-'))[:120]}</td>
        </tr>""" for f in fails])
        
        fsec = f"""
        <div class='section-card danger-border'>
            <div class='card-header'>
                <h2>❌ Failures</h2>
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
    <title>Performance Test Report</title>
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
            --shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg-body);
            color: var(--text-primary);
            padding: 40px 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
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
        .brand h1 {{ font-size: 24px; font-weight: 700; }}
        .brand .subtitle {{ font-size: 14px; color: var(--text-secondary); margin-top: 4px; }}
        .meta-grid {{ display: flex; gap: 40px; }}
        .meta-item label {{ display: block; font-size: 12px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; }}
        .meta-item value {{ display: block; font-size: 15px; font-weight: 500; margin-top: 2px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; margin-bottom: 24px; }}
        .stat-card {{ background: var(--bg-card); padding: 24px; border-radius: 16px; box-shadow: var(--shadow); }}
        .stat-label {{ font-size: 14px; color: var(--text-secondary); }}
        .stat-value {{ font-size: 32px; font-weight: 700; margin: 8px 0; }}
        .stat-desc {{ font-size: 13px; color: var(--success); }}
        .stat-desc.bad {{ color: var(--danger); }}
        .section-card {{ background: var(--bg-card); border-radius: 16px; box-shadow: var(--shadow); margin-bottom: 24px; overflow: hidden; }}
        .danger-border {{ border-left: 4px solid var(--danger); }}
        .card-header {{ padding: 20px 24px; border-bottom: 1px solid var(--border-color); background: #f9fafb; }}
        .card-header h2 {{ font-size: 18px; font-weight: 600; }}
        .table-container {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th {{ background: #f9fafb; padding: 12px 24px; font-weight: 600; color: var(--text-secondary); border-bottom: 1px solid var(--border-color); white-space: nowrap; text-align: left; }}
        td {{ padding: 16px 24px; border-bottom: 1px solid var(--border-color); }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover td {{ background: #f9fafb; }}
        .text-right {{ text-align: right; }}
        .font-medium {{ font-weight: 600; }}
        .name-cell {{ font-weight: 500; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        .error-cell {{ color: var(--danger); font-family: monospace; font-size: 13px; }}
        .badge {{ padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; }}
        .method-get {{ background: #eff6ff; color: #3b82f6; }}
        .method-post {{ background: #ecfdf5; color: #10b981; }}
        .method-put {{ background: #fffbeb; color: #f59e0b; }}
        .method-delete {{ background: #fef2f2; color: #ef4444; }}
        .method-patch {{ background: #f3e8ff; color: #9333ea; }}
        .method-other {{ background: #f3f4f6; color: #6b7280; }}
        .progress-bar {{ height: 6px; background: #e5e7eb; border-radius: 3px; overflow: hidden; margin-top: 6px; }}
        .fill {{ height: 100%; border-radius: 3px; }}
        .bg-success {{ background: var(--success); }}
        .bg-danger {{ background: var(--danger); }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="brand">
                <h1>🚀 Performance Test Report</h1>
                <div class="subtitle">Generated by Test-Engine (Locust)</div>
            </div>
            <div class="meta-grid">
                <div class="meta-item"><label>Target Host</label><value>{self.host}</value></div>
                <div class="meta-item"><label>Concurrency</label><value>{self.users} Users</value></div>
                <div class="meta-item"><label>Duration</label><value>{self.run_time}</value></div>
                <div class="meta-item"><label>Date</label><value>{datetime.now().strftime('%Y-%m-%d %H:%M')}</value></div>
            </div>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Requests</div>
                <div class="stat-value">{total:,}</div>
                <div class="stat-desc">Samples collected</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{success_rate:.1f}%</div>
                <div class="stat-desc {'bad' if success_rate < 99 else ''}">{fail} failures</div>
                <div class="progress-bar"><div class="fill {'bg-success' if success_rate >= 99 else 'bg-danger'}" style="width: {success_rate}%"></div></div>
            </div>
            <div class="stat-card">
                <div class="stat-label">RPS (Throughput)</div>
                <div class="stat-value">{sf(agg.get('Requests/s')):.1f}</div>
                <div class="stat-desc">Requests per second</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Response Time (P95)</div>
                <div class="stat-value">{sf(agg.get('95%')):.0f} ms</div>
                <div class="stat-desc">Avg: {sf(agg.get('Average Response Time')):.0f}ms / Max: {sf(agg.get('Max Response Time')):.0f}ms</div>
            </div>
        </div>
        
        <div class="section-card">
            <div class="card-header"><h2>📊 Request Statistics</h2></div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th width="80">Method</th>
                            <th>Name</th>
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
                    <tbody>{rows}</tbody>
                </table>
            </div>
        </div>
        
        {fsec}
    </div>
</body>
</html>'''
