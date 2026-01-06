"""
Perf Engine 性能测试关键字
基于 Locust 语法设计的关键字驱动库

核心特性:
- 完整支持 Locust HttpUser 行为模拟
- catch_response 模式的响应验证
- 事务控制与统计
- 顺序任务集 (SequentialTaskSet)
- 数据驱动测试
- 生命周期钩子
- Pytest 模式支持
"""
import time
import random
import re
import csv
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field

from ..core.globalContext import g_context
from ..utils.VarRender import refresh

# Locust 相关导入
try:
    from locust import HttpUser, task, between, events
    from locust.env import Environment
    from locust.stats import RequestStats
    import gevent
    from gevent import monkey
    if not monkey.is_module_patched('socket'):
        monkey.patch_all()
    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False


# ==================== 数据模型 ====================

@dataclass
class PerfTestConfig:
    """性能测试配置"""
    host: str = "http://localhost"
    users: int = 10
    spawn_rate: int = 1
    run_time: int = 60
    wait_time_min: float = 1.0
    wait_time_max: float = 3.0


@dataclass
class PerfTestResult:
    """性能测试结果"""
    total_requests: int = 0
    failures: int = 0
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    median_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    requests_per_second: float = 0.0
    failure_rate: float = 0.0
    request_stats: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)


# ==================== 统一关键字类 ====================

class PerfKeywords:
    """
    性能测试关键字类
    
    基于 Locust 语法设计，支持:
    - HTTP 请求 (get/post/put/delete/patch)
    - 等待时间 (wait/constant_pacing)
    - 响应验证 (assert_status/assert_json/assert_contains)
    - 事务控制 (transaction/start_transaction/end_transaction)
    - 顺序任务 (sequential_tasks)
    - 数据驱动 (random_data/cycle_data)
    - 条件控制 (if_condition)
    - 循环 (loop/foreach)
    - 生命周期钩子 (on_start/on_stop)
    """
    
    def __init__(self, client=None):
        self.client = client
        self.context = {}
        self.last_response = None
        self._catch_response_ctx = None
        self._transaction_stack = []
        self._data_iterators = {}
        self._user_weight = 1
        self._wait_time_config = None
        
        # Pytest 模式
        self._tasks: List[Dict] = []
        self._on_start_func: Optional[Callable] = None
        self._on_stop_func: Optional[Callable] = None
        self._config: Optional[PerfTestConfig] = None
        self._result: Optional[PerfTestResult] = None
    
    def set_client(self, client):
        """设置 Locust client"""
        self.client = client
    
    def set_context(self, context: Dict[str, Any] = None, **kwargs):
        """设置上下文变量"""
        if context:
            self.context.update(context)
        if kwargs:
            self.context.update(kwargs)
        g_context().set_by_dict(self.context)
    
    def _render(self, value: Any) -> Any:
        """渲染变量 {{var}}"""
        merged_context = g_context().show_dict().copy()
        merged_context.update(self.context)
        
        if isinstance(value, str):
            result = refresh(value, merged_context)
            return result if result is not None else value
        elif isinstance(value, dict):
            return {k: self._render(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._render(i) for i in value]
        return value
    
    def _pop_keyword(self, kwargs: dict) -> dict:
        """移除关键字标识"""
        kwargs.pop("关键字", None)
        kwargs.pop("keyword", None)
        return kwargs

    # ==================== 用户行为配置 ====================
    
    def user_config(self, **kwargs):
        """
        用户行为配置
        对应 Locust: HttpUser 类属性
        """
        self._pop_keyword(kwargs)
        if "wait_time" in kwargs:
            self._wait_time_config = kwargs["wait_time"]
        if "weight" in kwargs:
            self._user_weight = int(kwargs["weight"])
        if "host" in kwargs:
            self.context["_host"] = self._render(kwargs["host"])

    # ==================== HTTP 请求 ====================
    
    def get(self, **kwargs) -> Optional[Any]:
        """GET 请求"""
        return self._request("GET", **self._pop_keyword(kwargs))
    
    def post(self, **kwargs) -> Optional[Any]:
        """POST 请求"""
        return self._request("POST", **self._pop_keyword(kwargs))
    
    def put(self, **kwargs) -> Optional[Any]:
        """PUT 请求"""
        return self._request("PUT", **self._pop_keyword(kwargs))
    
    def delete(self, **kwargs) -> Optional[Any]:
        """DELETE 请求"""
        return self._request("DELETE", **self._pop_keyword(kwargs))
    
    def patch(self, **kwargs) -> Optional[Any]:
        """PATCH 请求"""
        return self._request("PATCH", **self._pop_keyword(kwargs))
    
    def _request(self, method: str, **kwargs) -> Optional[Any]:
        """发送 HTTP 请求"""
        if not self.client:
            raise RuntimeError("Locust client 未初始化")
        
        url = self._render(kwargs.pop("url", "/"))
        name = kwargs.pop("name", None)
        catch_response = kwargs.pop("catch_response", False)
        
        req_kwargs = {}
        if name:
            req_kwargs["name"] = name
        if catch_response:
            req_kwargs["catch_response"] = True
        
        for key in ["headers", "params", "data", "json", "files"]:
            if key in kwargs:
                req_kwargs[key] = self._render(kwargs[key])
        
        func = getattr(self.client, method.lower())
        
        if catch_response:
            self._catch_response_ctx = func(url, **req_kwargs)
            self.last_response = self._catch_response_ctx.__enter__()
        else:
            self.last_response = func(url, **req_kwargs)
        
        return self.last_response

    # ==================== 等待时间 ====================
    
    def wait(self, **kwargs):
        """等待时间"""
        self._pop_keyword(kwargs)
        seconds = kwargs.get("seconds")
        if seconds is not None:
            time.sleep(float(seconds))
        else:
            min_s = float(kwargs.get("min", 1))
            max_s = float(kwargs.get("max", min_s))
            time.sleep(random.uniform(min_s, max_s))
    
    think_time = wait
    
    def constant_pacing(self, **kwargs):
        """固定节奏等待"""
        self._pop_keyword(kwargs)
        seconds = float(kwargs.get("seconds", 1))
        time.sleep(seconds)

    # ==================== 响应验证 (catch_response 模式) ====================
    
    def assert_status(self, **kwargs):
        """断言状态码"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return False
        
        expected = int(kwargs.get("expected", 200))
        fail_on_error = kwargs.get("fail_on_error", True)
        actual = self.last_response.status_code
        
        if actual == expected:
            self._mark_success()
            return True
        else:
            if fail_on_error:
                self._mark_failure(f"Expected status {expected}, got {actual}")
            return False
    
    check_status = assert_status
    
    def assert_response_time(self, **kwargs):
        """断言响应时间"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return False
        
        max_ms = float(kwargs.get("max_ms", 1000))
        fail_on_error = kwargs.get("fail_on_error", True)
        actual_ms = self.last_response.elapsed.total_seconds() * 1000
        
        if actual_ms <= max_ms:
            return True
        else:
            if fail_on_error:
                self._mark_failure(f"Response time {actual_ms:.0f}ms > {max_ms}ms")
            return False
    
    check_response_time = assert_response_time
    
    def assert_contains(self, **kwargs):
        """断言响应包含文本"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return False
        
        text = self._render(kwargs.get("text", ""))
        fail_on_error = kwargs.get("fail_on_error", True)
        
        if text in self.last_response.text:
            return True
        else:
            if fail_on_error:
                self._mark_failure(f"Response does not contain: {text}")
            return False
    
    check_contains = assert_contains
    
    def assert_json(self, **kwargs):
        """断言 JSON 响应"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return False
        
        try:
            import jsonpath
            data = self.last_response.json()
            path = kwargs.get("path", "$")
            expected = self._render(kwargs.get("expected"))
            operator = kwargs.get("operator", "eq")
            fail_on_error = kwargs.get("fail_on_error", True)
            
            result = jsonpath.jsonpath(data, path)
            if not result:
                if fail_on_error:
                    self._mark_failure(f"JSONPath {path} not found")
                return False
            
            actual = result[0] if isinstance(result, list) else result
            passed = self._compare(actual, expected, operator)
            
            if not passed and fail_on_error:
                self._mark_failure(f"JSON assert failed: {actual} {operator} {expected}")
            
            return passed
        except Exception as e:
            if kwargs.get("fail_on_error", True):
                self._mark_failure(f"JSON parse error: {e}")
            return False
    
    validate_json = assert_json
    
    def assert_header(self, **kwargs):
        """断言响应头"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return False
        
        header_name = kwargs.get("name", "")
        expected = self._render(kwargs.get("expected", ""))
        fail_on_error = kwargs.get("fail_on_error", True)
        
        actual = self.last_response.headers.get(header_name, "")
        
        if str(actual) == str(expected):
            return True
        else:
            if fail_on_error:
                self._mark_failure(f"Header {header_name}: expected {expected}, got {actual}")
            return False
    
    def _compare(self, actual, expected, operator: str) -> bool:
        """比较操作"""
        try:
            if operator == "eq":
                return str(actual) == str(expected)
            elif operator == "ne":
                return str(actual) != str(expected)
            elif operator == "gt":
                return float(actual) > float(expected)
            elif operator == "lt":
                return float(actual) < float(expected)
            elif operator == "gte":
                return float(actual) >= float(expected)
            elif operator == "lte":
                return float(actual) <= float(expected)
            elif operator == "contains":
                return str(expected) in str(actual)
            else:
                return str(actual) == str(expected)
        except:
            return False
    
    def mark_success(self, **kwargs):
        """标记请求成功"""
        self._pop_keyword(kwargs)
        message = kwargs.get("message", "")
        self._mark_success(message)
    
    def mark_failure(self, **kwargs):
        """标记请求失败"""
        self._pop_keyword(kwargs)
        message = kwargs.get("message", "Unknown error")
        self._mark_failure(message)
    
    def _mark_success(self, message: str = ""):
        """内部：标记成功"""
        if self._catch_response_ctx and self.last_response:
            self.last_response.success()
    
    def _mark_failure(self, message: str):
        """内部：标记失败"""
        if self._catch_response_ctx and self.last_response:
            self.last_response.failure(message)
        else:
            print(f"[FAIL] {message}")
    
    def _close_catch_response(self):
        """关闭 catch_response 上下文"""
        if self._catch_response_ctx:
            try:
                self._catch_response_ctx.__exit__(None, None, None)
            except:
                pass
            self._catch_response_ctx = None

    # ==================== 事务控制 ====================
    
    def transaction(self, **kwargs):
        """事务块"""
        self._pop_keyword(kwargs)
        name = kwargs.get("name", "transaction")
        steps = kwargs.get("steps", [])
        
        self.start_transaction(name=name)
        try:
            for step in steps:
                self._execute_step(step)
            self.end_transaction(success=True)
        except Exception as e:
            self.end_transaction(success=False)
            raise
    
    def start_transaction(self, **kwargs):
        """开始事务"""
        self._pop_keyword(kwargs)
        name = kwargs.get("name", "transaction")
        self._transaction_stack.append({
            "name": name,
            "start_time": time.time()
        })
    
    def end_transaction(self, **kwargs):
        """结束事务"""
        self._pop_keyword(kwargs)
        success = kwargs.get("success", True)
        
        if self._transaction_stack:
            tx = self._transaction_stack.pop()
            duration = (time.time() - tx["start_time"]) * 1000
            status = "✓" if success else "✗"
            print(f"[TX] {status} {tx['name']}: {duration:.0f}ms")

    # ==================== 顺序任务集 ====================
    
    def sequential_tasks(self, **kwargs):
        """顺序任务集"""
        self._pop_keyword(kwargs)
        name = kwargs.get("name", "sequential")
        steps = kwargs.get("steps", [])
        loop_count = int(kwargs.get("loop", 1))
        
        for i in range(loop_count):
            for step in steps:
                self._execute_step(step)
    
    def interrupt(self, **kwargs):
        """中断任务集"""
        self._pop_keyword(kwargs)
        message = kwargs.get("message", "Task interrupted")
        print(f"[INTERRUPT] {message}")
        raise StopIteration(message)

    # ==================== 任务权重 ====================
    
    def task_def(self, **kwargs):
        """定义带权重的任务"""
        self._pop_keyword(kwargs)
        name = kwargs.get("name", "task")
        weight = int(kwargs.get("weight", 1))
        steps = kwargs.get("steps", [])
        tags = kwargs.get("tags", [])
        
        self.context.setdefault("_tasks", []).append({
            "name": name,
            "weight": weight,
            "steps": steps,
            "tags": tags
        })

    # ==================== 数据操作 ====================
    
    def set_var(self, **kwargs):
        """设置变量"""
        self._pop_keyword(kwargs)
        name = kwargs.get("name")
        value = kwargs.get("value")
        if name:
            self.context[name] = self._render(value)
            g_context().set_dict(name, self.context[name])
    
    def extract_json(self, **kwargs):
        """从响应提取 JSON 数据"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return None
        
        try:
            import jsonpath
            data = self.last_response.json()
            path = kwargs.get("path", "$")
            var = kwargs.get("var", "extracted")
            index = int(kwargs.get("index", 0))
            
            result = jsonpath.jsonpath(data, path)
            if result:
                value = result[index] if isinstance(result, list) and len(result) > index else result
                self.context[var] = value
                g_context().set_dict(var, value)
                return value
        except Exception as e:
            print(f"[EXTRACT] JSON error: {e}")
        return None
    
    def extract_regex(self, **kwargs):
        """从响应提取正则匹配"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return None
        
        try:
            pattern = kwargs.get("pattern", "")
            var = kwargs.get("var", "extracted")
            group = int(kwargs.get("group", 1))
            
            match = re.search(pattern, self.last_response.text)
            if match:
                value = match.group(group)
                self.context[var] = value
                g_context().set_dict(var, value)
                return value
        except Exception as e:
            print(f"[EXTRACT] Regex error: {e}")
        return None
    
    def extract_header(self, **kwargs):
        """从响应提取响应头"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            return None
        
        header_name = kwargs.get("name", "")
        var = kwargs.get("var", "extracted")
        
        value = self.last_response.headers.get(header_name, "")
        self.context[var] = value
        g_context().set_dict(var, value)
        return value

    # ==================== 数据驱动 ====================
    
    def random_data(self, **kwargs):
        """随机数据"""
        self._pop_keyword(kwargs)
        source = kwargs.get("source", "list")
        var = kwargs.get("var", "random_item")
        
        data_list = self._get_data_list(source, kwargs)
        if data_list:
            value = random.choice(data_list)
            self.context[var] = value
            g_context().set_dict(var, value)
            return value
        return None
    
    def cycle_data(self, **kwargs):
        """循环数据（轮询）"""
        self._pop_keyword(kwargs)
        source = kwargs.get("source", "list")
        var = kwargs.get("var", "cycle_item")
        
        key = f"_cycle_{var}"
        if key not in self._data_iterators:
            data_list = self._get_data_list(source, kwargs)
            self._data_iterators[key] = {"data": data_list, "index": 0}
        
        iterator = self._data_iterators[key]
        if iterator["data"]:
            value = iterator["data"][iterator["index"] % len(iterator["data"])]
            iterator["index"] += 1
            self.context[var] = value
            g_context().set_dict(var, value)
            return value
        return None
    
    def _get_data_list(self, source: str, kwargs: dict) -> List:
        """获取数据列表"""
        if source == "list":
            return kwargs.get("data", [])
        elif source in ("file", "csv"):
            file_path = kwargs.get("file", "")
            if file_path and Path(file_path).exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    if source == "csv":
                        return list(csv.DictReader(f))
                    else:
                        return json.load(f)
        return []

    # ==================== 条件控制 ====================
    
    def if_condition(self, **kwargs):
        """条件控制"""
        self._pop_keyword(kwargs)
        condition = self._render(kwargs.get("condition", ""))
        then_steps = kwargs.get("then", [])
        else_steps = kwargs.get("else", [])
        
        try:
            result = eval(condition, {"__builtins__": {}}, self.context)
        except:
            result = False
        
        steps = then_steps if result else else_steps
        for step in steps:
            self._execute_step(step)

    # ==================== 循环 ====================
    
    def loop(self, **kwargs):
        """循环执行"""
        self._pop_keyword(kwargs)
        count = int(kwargs.get("count", 1))
        steps = kwargs.get("steps", [])
        delay = float(kwargs.get("delay", 0))
        
        for i in range(count):
            self.context["_loop_index"] = i
            for step in steps:
                self._execute_step(step)
            if delay > 0:
                time.sleep(delay)
    
    def foreach(self, **kwargs):
        """遍历执行"""
        self._pop_keyword(kwargs)
        items = kwargs.get("items", [])
        if isinstance(items, str):
            items = self.context.get(items, [])
        items = self._render(items)
        
        var = kwargs.get("var", "item")
        steps = kwargs.get("steps", [])
        
        for i, item in enumerate(items):
            self.context[var] = item
            self.context["_foreach_index"] = i
            for step in steps:
                self._execute_step(step)
    
    def _execute_step(self, step: dict):
        """执行单个步骤"""
        if isinstance(step, dict):
            for name, data in step.items():
                if isinstance(data, dict):
                    keyword = data.get("关键字") or data.get("keyword", "")
                    if keyword and hasattr(self, keyword):
                        try:
                            getattr(self, keyword)(**data)
                        except StopIteration:
                            raise
                        except Exception as e:
                            print(f"[ERROR] Step '{name}': {e}")

    # ==================== 日志与调试 ====================
    
    def log(self, **kwargs):
        """打印日志"""
        self._pop_keyword(kwargs)
        message = self._render(kwargs.get("message", ""))
        level = kwargs.get("level", "info").upper()
        print(f"[{level}] {message}")
    
    def print_response(self, **kwargs):
        """打印响应内容"""
        self._pop_keyword(kwargs)
        if not self.last_response:
            print("[RESPONSE] No response")
            return
        
        fmt = kwargs.get("format", "json")
        
        if fmt == "json":
            try:
                print(json.dumps(self.last_response.json(), indent=2, ensure_ascii=False))
            except:
                print(self.last_response.text)
        elif fmt == "text":
            print(self.last_response.text)
        elif fmt == "headers":
            print(dict(self.last_response.headers))
        elif fmt == "all":
            print(f"Status: {self.last_response.status_code}")
            print(f"Headers: {dict(self.last_response.headers)}")
            print(f"Body: {self.last_response.text[:500]}")

    # ==================== 生命周期钩子 ====================
    
    def on_start(self, func_or_kwargs=None, **kwargs):
        """用户启动时执行"""
        # 装饰器模式
        if callable(func_or_kwargs):
            self._on_start_func = func_or_kwargs
            return func_or_kwargs
        
        # YAML 关键字模式
        if func_or_kwargs is None:
            func_or_kwargs = kwargs
        self._pop_keyword(func_or_kwargs)
        steps = func_or_kwargs.get("steps", [])
        for step in steps:
            self._execute_step(step)
    
    def on_stop(self, func_or_kwargs=None, **kwargs):
        """用户停止时执行"""
        # 装饰器模式
        if callable(func_or_kwargs):
            self._on_stop_func = func_or_kwargs
            return func_or_kwargs
        
        # YAML 关键字模式
        if func_or_kwargs is None:
            func_or_kwargs = kwargs
        self._pop_keyword(func_or_kwargs)
        steps = func_or_kwargs.get("steps", [])
        for step in steps:
            self._execute_step(step)

    # ==================== Python 脚本执行 ====================

    def run_script(self, **kwargs):
        """执行 Python 脚本文件"""
        from .script.run_script import exec_script_file
        
        script_path = kwargs.pop("script_path", None)
        function_name = kwargs.pop("function_name", None)
        variable_name = kwargs.pop("variable_name", None)
        self._pop_keyword(kwargs)
        
        if not script_path:
            raise ValueError("必须指定 script_path 参数")
        
        context = {**g_context().show_dict(), **self.context}
        
        result = exec_script_file(
            script_path=script_path,
            context=context,
            caseinfo=None,
            function_name=function_name,
            **kwargs
        )
        
        if variable_name and result is not None:
            self.context[variable_name] = result
            g_context().set_dict(variable_name, result)
        
        return result

    def run_code(self, **kwargs):
        """执行 Python 代码片段"""
        from .script.run_script import exec_script
        
        code = kwargs.get("code", "")
        variable_name = kwargs.get("variable_name")
        
        if not code:
            raise ValueError("必须指定 code 参数")
        
        context = {**g_context().show_dict(), **self.context}
        result = exec_script(code, context)
        
        if variable_name and result is not None:
            self.context[variable_name] = result
            g_context().set_dict(variable_name, result)
        
        return result

    # ==================== Pytest 模式 API ====================
    
    def task(self, weight: int = 1):
        """装饰器：定义用户任务 (Pytest 模式)"""
        if not LOCUST_AVAILABLE:
            raise ImportError("Locust 未安装，请执行: pip install locust")
        
        def decorator(func: Callable):
            self._tasks.append({
                "func": func,
                "weight": weight,
                "name": func.__name__
            })
            return func
        return decorator
    
    def run_test(
        self,
        host: str,
        users: int = 10,
        spawn_rate: int = 1,
        run_time: int = 60,
        wait_time_min: float = 1.0,
        wait_time_max: float = 3.0
    ) -> PerfTestResult:
        """运行性能测试 (Pytest 模式)"""
        if not LOCUST_AVAILABLE:
            raise ImportError("Locust 未安装，请执行: pip install locust")
        
        if not self._tasks:
            raise ValueError("没有定义任何任务，请使用 @perf.task() 装饰器定义任务")
        
        self._config = PerfTestConfig(
            host=host,
            users=users,
            spawn_rate=spawn_rate,
            run_time=run_time,
            wait_time_min=wait_time_min,
            wait_time_max=wait_time_max
        )
        
        user_class = self._create_user_class()
        env = Environment(user_classes=[user_class])
        runner = env.create_local_runner()
        
        print(f"\n{'='*60}")
        print(f"Locust Performance Test")
        print(f"{'='*60}")
        print(f"Host: {host}")
        print(f"Users: {users}, Spawn Rate: {spawn_rate}/s")
        print(f"Duration: {run_time}s")
        print(f"Tasks: {[t['name'] for t in self._tasks]}")
        print(f"{'='*60}\n")
        
        runner.start(user_count=users, spawn_rate=spawn_rate)
        gevent.sleep(run_time)
        runner.quit()
        
        self._result = self._collect_results(env.stats)
        return self._result
    
    def _create_user_class(self) -> type:
        """动态创建 Locust User 类"""
        tasks = self._tasks
        on_start_func = self._on_start_func
        on_stop_func = self._on_stop_func
        context = self.context
        config = self._config
        
        class DynamicUser(HttpUser):
            host = config.host
            wait_time = between(config.wait_time_min, config.wait_time_max)
            
            def on_start(self):
                self.kw = PerfKeywords(client=self.client)
                self.kw.context = context.copy()
                if on_start_func:
                    on_start_func(self.kw)
            
            def on_stop(self):
                if on_stop_func:
                    on_stop_func(self.kw)
        
        for task_info in tasks:
            func = task_info["func"]
            weight = task_info["weight"]
            
            def make_task(f):
                def task_method(user_self):
                    f(user_self.kw)
                return task_method
            
            task_method = make_task(func)
            task_method.__name__ = func.__name__
            
            decorated = task(weight)(task_method)
            setattr(DynamicUser, func.__name__, decorated)
        
        return DynamicUser
    
    def _collect_results(self, stats: RequestStats) -> PerfTestResult:
        """收集性能测试结果"""
        total = stats.total
        
        result = PerfTestResult(
            total_requests=total.num_requests,
            failures=total.num_failures,
            avg_response_time=total.avg_response_time,
            min_response_time=total.min_response_time or 0,
            max_response_time=total.max_response_time or 0,
            median_response_time=total.median_response_time or 0,
            p95_response_time=total.get_response_time_percentile(0.95) or 0,
            p99_response_time=total.get_response_time_percentile(0.99) or 0,
            requests_per_second=total.total_rps,
            failure_rate=total.fail_ratio
        )
        
        for entry in stats.entries.values():
            result.request_stats.append({
                "name": entry.name,
                "method": entry.method,
                "num_requests": entry.num_requests,
                "num_failures": entry.num_failures,
                "avg_response_time": entry.avg_response_time,
                "min_response_time": entry.min_response_time,
                "max_response_time": entry.max_response_time,
                "p95": entry.get_response_time_percentile(0.95),
                "p99": entry.get_response_time_percentile(0.99),
                "rps": entry.total_rps
            })
        
        for error in stats.errors.values():
            result.errors.append({
                "method": error.method,
                "name": error.name,
                "error": error.error,
                "occurrences": error.occurrences
            })
        
        return result
    
    def clear(self):
        """清除所有任务和配置"""
        self._tasks.clear()
        self._on_start_func = None
        self._on_stop_func = None
        self.context.clear()
        self._config = None
        self._result = None


# ==================== 便捷函数 ====================

def create_perf_test() -> PerfKeywords:
    """创建性能测试实例"""
    return PerfKeywords()


# 全局实例
keywords = PerfKeywords()
