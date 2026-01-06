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
"""
import time
import random
import re
import csv
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

from ..core.globalContext import g_context
from ..utils.VarRender import refresh


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
    """
    
    def __init__(self, client=None):
        self.client = client
        self.context = {}
        self.last_response = None
        self._catch_response_ctx = None  # catch_response 上下文
        self._transaction_stack = []     # 事务栈
        self._data_iterators = {}        # 数据迭代器
        self._user_weight = 1            # 用户权重
        self._wait_time_config = None    # 等待时间配置
    
    def set_client(self, client):
        """设置 Locust client"""
        self.client = client
    
    def set_context(self, context: Dict[str, Any]):
        """设置上下文变量"""
        self.context.update(context)
        g_context().set_by_dict(context)
    
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
        
        参数:
        - wait_time: 等待时间策略 "between(1,3)" | "constant(2)"
        - weight: 用户权重
        - host: 目标主机
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
        """
        GET 请求
        对应 Locust: self.client.get()
        """
        return self._request("GET", **self._pop_keyword(kwargs))
    
    def post(self, **kwargs) -> Optional[Any]:
        """
        POST 请求
        对应 Locust: self.client.post()
        """
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
        
        # 构建请求参数
        req_kwargs = {}
        if name:
            req_kwargs["name"] = name
        if catch_response:
            req_kwargs["catch_response"] = True
        
        for key in ["headers", "params", "data", "json", "files"]:
            if key in kwargs:
                req_kwargs[key] = self._render(kwargs[key])
        
        # 发送请求
        func = getattr(self.client, method.lower())
        
        if catch_response:
            # catch_response 模式：返回上下文管理器
            self._catch_response_ctx = func(url, **req_kwargs)
            self.last_response = self._catch_response_ctx.__enter__()
        else:
            self.last_response = func(url, **req_kwargs)
        
        return self.last_response

    # ==================== 等待时间 ====================
    
    def wait(self, **kwargs):
        """
        等待时间
        对应 Locust: wait_time = between(min, max) 或 constant(seconds)
        
        参数:
        - seconds: 固定等待秒数
        - min/max: 随机等待范围
        """
        self._pop_keyword(kwargs)
        
        seconds = kwargs.get("seconds")
        if seconds is not None:
            time.sleep(float(seconds))
        else:
            min_s = float(kwargs.get("min", 1))
            max_s = float(kwargs.get("max", min_s))
            time.sleep(random.uniform(min_s, max_s))
    
    # 兼容旧版本
    think_time = wait
    
    def constant_pacing(self, **kwargs):
        """
        固定节奏等待
        对应 Locust: wait_time = constant_pacing(seconds)
        确保任务以固定间隔执行
        """
        self._pop_keyword(kwargs)
        seconds = float(kwargs.get("seconds", 1))
        time.sleep(seconds)

    # ==================== 响应验证 (catch_response 模式) ====================
    
    def assert_status(self, **kwargs):
        """
        断言状态码
        对应 Locust: response.success() / response.failure()
        
        参数:
        - expected: 期望状态码 (默认 200)
        - fail_on_error: 失败时标记请求失败 (默认 True)
        """
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
    
    # 兼容旧版本
    check_status = assert_status
    
    def assert_response_time(self, **kwargs):
        """
        断言响应时间
        
        参数:
        - max_ms: 最大响应时间 (毫秒)
        - fail_on_error: 超时标记失败 (默认 True)
        """
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
    
    # 兼容旧版本
    check_response_time = assert_response_time
    
    def assert_contains(self, **kwargs):
        """
        断言响应包含文本
        
        参数:
        - text: 期望包含的文本
        - fail_on_error: 不包含时标记失败 (默认 True)
        """
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
    
    # 兼容旧版本
    check_contains = assert_contains
    
    def assert_json(self, **kwargs):
        """
        断言 JSON 响应
        
        参数:
        - path: JSONPath 表达式
        - expected: 期望值
        - operator: 比较操作符 (eq, ne, gt, lt, gte, lte, contains)
        - fail_on_error: 验证失败标记失败 (默认 True)
        """
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
            
            # 比较操作
            passed = self._compare(actual, expected, operator)
            
            if not passed and fail_on_error:
                self._mark_failure(f"JSON assert failed: {actual} {operator} {expected}")
            
            return passed
        except Exception as e:
            if kwargs.get("fail_on_error", True):
                self._mark_failure(f"JSON parse error: {e}")
            return False
    
    # 兼容旧版本
    validate_json = assert_json
    
    def assert_header(self, **kwargs):
        """
        断言响应头
        
        参数:
        - name: 响应头名称
        - expected: 期望值
        - fail_on_error: 验证失败标记失败 (默认 True)
        """
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
        """
        标记请求成功
        对应 Locust: response.success()
        """
        self._pop_keyword(kwargs)
        message = kwargs.get("message", "")
        self._mark_success(message)
    
    def mark_failure(self, **kwargs):
        """
        标记请求失败
        对应 Locust: response.failure()
        """
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
        """
        事务块 - 包含多个步骤的事务
        
        参数:
        - name: 事务名称
        - steps: 事务内的步骤列表
        """
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
        """
        开始事务
        
        参数:
        - name: 事务名称
        """
        self._pop_keyword(kwargs)
        name = kwargs.get("name", "transaction")
        self._transaction_stack.append({
            "name": name,
            "start_time": time.time()
        })
    
    def end_transaction(self, **kwargs):
        """
        结束事务
        
        参数:
        - success: 是否成功 (默认 True)
        """
        self._pop_keyword(kwargs)
        success = kwargs.get("success", True)
        
        if self._transaction_stack:
            tx = self._transaction_stack.pop()
            duration = (time.time() - tx["start_time"]) * 1000
            status = "✓" if success else "✗"
            print(f"[TX] {status} {tx['name']}: {duration:.0f}ms")

    # ==================== 顺序任务集 ====================
    
    def sequential_tasks(self, **kwargs):
        """
        顺序任务集
        对应 Locust: SequentialTaskSet
        
        参数:
        - name: 任务集名称
        - steps: 顺序执行的步骤列表
        - loop: 循环次数 (默认 1)
        """
        self._pop_keyword(kwargs)
        name = kwargs.get("name", "sequential")
        steps = kwargs.get("steps", [])
        loop_count = int(kwargs.get("loop", 1))
        
        for i in range(loop_count):
            for step in steps:
                self._execute_step(step)
    
    def interrupt(self, **kwargs):
        """
        中断任务集
        对应 Locust: self.interrupt()
        """
        self._pop_keyword(kwargs)
        message = kwargs.get("message", "Task interrupted")
        print(f"[INTERRUPT] {message}")
        raise StopIteration(message)

    # ==================== 任务权重 ====================
    
    def task(self, **kwargs):
        """
        定义带权重的任务
        对应 Locust: @task(weight)
        
        参数:
        - name: 任务名称
        - weight: 任务权重 (默认 1)
        - steps: 任务步骤列表
        - tags: 任务标签列表
        """
        self._pop_keyword(kwargs)
        name = kwargs.get("name", "task")
        weight = int(kwargs.get("weight", 1))
        steps = kwargs.get("steps", [])
        tags = kwargs.get("tags", [])
        
        # 存储任务定义 (供 runner 使用)
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
        """
        从响应提取 JSON 数据
        
        参数:
        - path: JSONPath 表达式
        - var: 存储的变量名
        - index: 结果索引 (默认 0)
        """
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
        """
        从响应提取正则匹配
        
        参数:
        - pattern: 正则表达式
        - var: 存储的变量名
        - group: 捕获组索引 (默认 1)
        """
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
        """
        从响应提取响应头
        
        参数:
        - name: 响应头名称
        - var: 存储的变量名
        """
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
        """
        随机数据
        
        参数:
        - source: 数据源 (list | file | csv)
        - data: 数据列表 (source=list)
        - file: 文件路径 (source=file/csv)
        - var: 存储的变量名
        """
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
        """
        循环数据 (轮询)
        
        参数:
        - source: 数据源 (list | file | csv)
        - data: 数据列表
        - file: 文件路径
        - var: 存储的变量名
        """
        self._pop_keyword(kwargs)
        
        source = kwargs.get("source", "list")
        var = kwargs.get("var", "cycle_item")
        
        # 获取或创建迭代器
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
        """
        条件控制
        
        参数:
        - condition: 条件表达式
        - then: 条件为真时执行的步骤
        - else: 条件为假时执行的步骤 (可选)
        """
        self._pop_keyword(kwargs)
        
        condition = self._render(kwargs.get("condition", ""))
        then_steps = kwargs.get("then", [])
        else_steps = kwargs.get("else", [])
        
        # 简单条件求值
        try:
            result = eval(condition, {"__builtins__": {}}, self.context)
        except:
            result = False
        
        steps = then_steps if result else else_steps
        for step in steps:
            self._execute_step(step)

    # ==================== 循环 ====================
    
    def loop(self, **kwargs):
        """
        循环执行
        
        参数:
        - count: 循环次数
        - steps: 循环执行的步骤
        - delay: 每次循环后延迟 (秒)
        """
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
        """
        遍历执行
        
        参数:
        - items: 遍历的列表或变量名
        - var: 当前项变量名
        - steps: 每项执行的步骤
        """
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
        """
        打印日志
        
        参数:
        - message: 日志消息
        - level: 日志级别 (info, debug, warning, error)
        """
        self._pop_keyword(kwargs)
        message = self._render(kwargs.get("message", ""))
        level = kwargs.get("level", "info").upper()
        print(f"[{level}] {message}")
    
    def print_response(self, **kwargs):
        """
        打印响应内容
        
        参数:
        - format: 输出格式 (json, text, headers, all)
        """
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
    
    def on_start(self, **kwargs):
        """
        用户启动时执行
        对应 Locust: def on_start(self)
        
        参数:
        - steps: 启动时执行的步骤
        """
        self._pop_keyword(kwargs)
        steps = kwargs.get("steps", [])
        for step in steps:
            self._execute_step(step)
    
    def on_stop(self, **kwargs):
        """
        用户停止时执行
        对应 Locust: def on_stop(self)
        
        参数:
        - steps: 停止时执行的步骤
        """
        self._pop_keyword(kwargs)
        steps = kwargs.get("steps", [])
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


# 全局实例
keywords = PerfKeywords()
