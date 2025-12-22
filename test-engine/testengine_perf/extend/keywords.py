"""
Perf Engine 性能测试关键字
基于 Locust 实现的统一关键字库

使用方式:
1. YAML 模式: 在 Locust User 类中使用，需要设置 client
2. Pytest 模式: 使用 @perf.task() 装饰器定义任务，调用 run_test() 运行

两种模式使用同一套关键字 API (get/post/check_status 等)
"""
import time
import random
from typing import Dict, Any, Optional, List, Callable
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
    # 确保 gevent monkey patch
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
    run_time: int = 60  # 秒
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
    
    # 详细数据
    request_stats: List[Dict] = field(default_factory=list)
    errors: List[Dict] = field(default_factory=list)


# ==================== 统一关键字类 ====================

class PerfKeywords:
    """
    性能测试统一关键字类
    
    两种模式使用同一套关键字 API:
    
    1. YAML 模式 (在 Locust User 中使用):
    ```python
    class MyUser(HttpUser):
        def on_start(self):
            self.kw = PerfKeywords(client=self.client)
        
        @task
        def my_task(self):
            self.kw.get(url="/users")
            self.kw.check_status(expected=200)
    ```
    
    2. Pytest 模式 (装饰器方式):
    ```python
    perf = PerfKeywords()
    
    @perf.task(weight=3)
    def get_users(kw):  # kw 是 PerfKeywords 实例
        kw.get(url="/users")
        kw.check_status(expected=200)
    
    result = perf.run_test(host="https://api.example.com", users=50)
    ```
    """
    
    def __init__(self, client=None):
        """
        初始化关键字
        
        Args:
            client: Locust HttpSession (YAML 模式需要传入)
        """
        self.client = client
        self.context = {}
        self.last_response = None
        
        # Pytest 模式的任务列表
        self._tasks: List[Dict] = []
        self._on_start_func: Optional[Callable] = None
        self._on_stop_func: Optional[Callable] = None
        self._config: Optional[PerfTestConfig] = None
        self._result: Optional[PerfTestResult] = None
    
    # ==================== 客户端管理 ====================
    
    def set_client(self, client):
        """设置 Locust client (YAML 模式)"""
        self.client = client
    
    def set_context(self, context: Dict[str, Any] = None, **kwargs):
        """
        设置上下文变量
        
        Args:
            context: 上下文字典
            **kwargs: 关键字参数
        """
        if context:
            self.context.update(context)
        if kwargs:
            self.context.update(kwargs)
        # 同步到全局上下文
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
    
    # ==================== HTTP 请求关键字 (YAML 模式) ====================
    
    def get(self, **kwargs) -> Optional[Any]:
        """
        GET 请求
        
        参数:
        - url: 请求路径
        - name: 请求名称 (报告分组)
        - params: URL 参数
        - headers: 请求头
        """
        kwargs.pop("关键字", None)
        return self._request("GET", **kwargs)
    
    def post(self, **kwargs) -> Optional[Any]:
        """
        POST 请求
        
        参数:
        - url: 请求路径
        - name: 请求名称
        - json: JSON 数据
        - data: 表单数据
        - headers: 请求头
        """
        kwargs.pop("关键字", None)
        return self._request("POST", **kwargs)
    
    def put(self, **kwargs) -> Optional[Any]:
        """PUT 请求"""
        kwargs.pop("关键字", None)
        return self._request("PUT", **kwargs)
    
    def delete(self, **kwargs) -> Optional[Any]:
        """DELETE 请求"""
        kwargs.pop("关键字", None)
        return self._request("DELETE", **kwargs)
    
    def _request(self, method: str, **kwargs) -> Optional[Any]:
        """发送 HTTP 请求 (YAML 模式)"""
        if not self.client:
            raise RuntimeError("Locust client 未初始化，请先调用 set_client() 或使用 Pytest 模式")
        
        url = self._render(kwargs.pop("url", "/"))
        name = kwargs.pop("name", None)
        
        # 渲染参数
        req_kwargs = {}
        if name:
            req_kwargs["name"] = name
        for key in ["headers", "params", "data", "json"]:
            if key in kwargs:
                req_kwargs[key] = self._render(kwargs[key])
        
        # 发送请求
        func = getattr(self.client, method.lower())
        self.last_response = func(url, **req_kwargs)
        return self.last_response
    
    # ==================== 思考时间关键字 ====================
    
    def think_time(self, **kwargs):
        """
        思考时间 - 模拟用户操作间隔
        
        参数:
        - seconds: 固定等待秒数
        - min: 最小秒数 (随机)
        - max: 最大秒数 (随机)
        """
        kwargs.pop("关键字", None)
        
        seconds = kwargs.get("seconds")
        if seconds is not None:
            time.sleep(float(seconds))
        else:
            min_s = float(kwargs.get("min", 1))
            max_s = float(kwargs.get("max", min_s))
            time.sleep(random.uniform(min_s, max_s))
    
    def constant_pacing(self, **kwargs):
        """
        固定节奏 - 确保任务以固定间隔执行
        
        参数:
        - seconds: 间隔秒数
        """
        kwargs.pop("关键字", None)
        seconds = float(kwargs.get("seconds", 1))
        time.sleep(seconds)
    
    # ==================== 响应验证关键字 ====================
    
    def check_status(self, **kwargs) -> bool:
        """
        检查状态码
        
        参数:
        - expected: 期望状态码 (默认 200)
        """
        kwargs.pop("关键字", None)
        
        if not self.last_response:
            return False
        
        expected = int(kwargs.get("expected", 200))
        return self.last_response.status_code == expected
    
    def check_response_time(self, **kwargs) -> bool:
        """
        检查响应时间
        
        参数:
        - max_ms: 最大响应时间 (毫秒)
        """
        kwargs.pop("关键字", None)
        
        if not self.last_response:
            return False
        
        max_ms = float(kwargs.get("max_ms", 1000))
        actual_ms = self.last_response.elapsed.total_seconds() * 1000
        return actual_ms <= max_ms
    
    def check_contains(self, **kwargs) -> bool:
        """
        检查响应包含文本
        
        参数:
        - text: 期望包含的文本
        """
        kwargs.pop("关键字", None)
        
        if not self.last_response:
            return False
        
        text = kwargs.get("text", "")
        return text in self.last_response.text
    
    def validate_json(self, **kwargs) -> bool:
        """
        验证 JSON 响应
        
        参数:
        - path: JSONPath 表达式
        - expected: 期望值
        """
        kwargs.pop("关键字", None)
        
        if not self.last_response:
            return False
        
        try:
            import jsonpath
            data = self.last_response.json()
            path = kwargs.get("path", "$")
            expected = kwargs.get("expected")
            
            result = jsonpath.jsonpath(data, path)
            if result and expected is not None:
                actual = result[0] if isinstance(result, list) else result
                return str(actual) == str(expected)
            return result is not False
        except:
            return False
    
    # ==================== 事务控制关键字 ====================
    
    def start_transaction(self, **kwargs):
        """
        开始事务 - 用于分组统计
        
        参数:
        - name: 事务名称
        """
        kwargs.pop("关键字", None)
        name = kwargs.get("name", "transaction")
        self.context["_transaction_start"] = time.time()
        self.context["_transaction_name"] = name
    
    def end_transaction(self, **kwargs):
        """
        结束事务
        
        参数:
        - success: 是否成功 (默认 True)
        """
        kwargs.pop("关键字", None)
        
        start = self.context.get("_transaction_start")
        name = self.context.get("_transaction_name", "transaction")
        success = kwargs.get("success", True)
        
        if start:
            duration = (time.time() - start) * 1000  # ms
            print(f"事务 [{name}]: {duration:.2f}ms - {'成功' if success else '失败'}")
    
    # ==================== 数据操作关键字 ====================
    
    def set_var(self, **kwargs):
        """
        设置变量
        
        参数:
        - name: 变量名
        - value: 变量值
        """
        kwargs.pop("关键字", None)
        name = kwargs.get("name")
        value = kwargs.get("value")
        if name:
            self.context[name] = self._render(value)
    
    def extract_json(self, **kwargs) -> Optional[Any]:
        """
        从响应提取 JSON 数据
        
        参数:
        - path: JSONPath 表达式
        - var: 存储的变量名
        """
        kwargs.pop("关键字", None)
        
        if not self.last_response:
            return None
        
        try:
            import jsonpath
            data = self.last_response.json()
            path = kwargs.get("path", "$")
            var = kwargs.get("var", "extracted")
            
            result = jsonpath.jsonpath(data, path)
            if result:
                value = result[0] if isinstance(result, list) else result
                self.context[var] = value
                return value
        except:
            pass
        return None
    
    def log(self, **kwargs):
        """
        打印日志
        
        参数:
        - message: 日志消息
        """
        kwargs.pop("关键字", None)
        message = self._render(kwargs.get("message", ""))
        print(f"[PERF] {message}")
    
    # ==================== Pytest 模式 API ====================
    
    def task(self, weight: int = 1):
        """
        装饰器：定义用户任务 (Pytest 模式)
        
        参数:
            weight: 任务权重，数值越大执行频率越高
        
        示例:
        ```python
        perf = PerfKeywords()
        
        @perf.task(weight=3)
        def get_users(kw):  # kw 是 PerfKeywords 实例，已设置好 client
            kw.get(url="/users")
            kw.check_status(expected=200)
        ```
        """
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
    
    def on_start(self, func: Callable):
        """
        装饰器：用户启动时执行 (Pytest 模式)
        
        示例:
        ```python
        @perf.on_start
        def login(kw):  # kw 是 PerfKeywords 实例
            kw.post(url="/login", json={"user": "test", "pass": "123"})
        ```
        """
        self._on_start_func = func
        return func
    
    def on_stop(self, func: Callable):
        """
        装饰器：用户停止时执行 (Pytest 模式)
        """
        self._on_stop_func = func
        return func
    
    def run_test(
        self,
        host: str,
        users: int = 10,
        spawn_rate: int = 1,
        run_time: int = 60,
        wait_time_min: float = 1.0,
        wait_time_max: float = 3.0
    ) -> PerfTestResult:
        """
        运行性能测试 (Pytest 模式)
        
        参数:
            host: 目标主机 URL
            users: 并发用户数
            spawn_rate: 用户生成速率 (用户/秒)
            run_time: 运行时间 (秒)
            wait_time_min: 最小等待时间 (秒)
            wait_time_max: 最大等待时间 (秒)
        
        返回:
            PerfTestResult: 性能测试结果
        """
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
        
        # 动态创建 User 类
        user_class = self._create_user_class()
        
        # 创建 Locust 环境
        env = Environment(user_classes=[user_class])
        
        # 创建本地 runner
        runner = env.create_local_runner()
        
        # 启动测试
        print(f"\n{'='*60}")
        print(f"Locust Performance Test")
        print(f"{'='*60}")
        print(f"Host: {host}")
        print(f"Users: {users}, Spawn Rate: {spawn_rate}/s")
        print(f"Duration: {run_time}s")
        print(f"Tasks: {[t['name'] for t in self._tasks]}")
        print(f"{'='*60}\n")
        
        runner.start(user_count=users, spawn_rate=spawn_rate)
        
        # 运行指定时间
        gevent.sleep(run_time)
        
        # 停止测试
        runner.quit()
        
        # 收集结果
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
                # 创建 PerfKeywords 实例并设置 client
                self.kw = PerfKeywords(client=self.client)
                self.kw.context = context.copy()
                if on_start_func:
                    on_start_func(self.kw)
            
            def on_stop(self):
                if on_stop_func:
                    on_stop_func(self.kw)
        
        # 动态添加任务
        for task_info in tasks:
            func = task_info["func"]
            weight = task_info["weight"]
            
            # 创建任务方法，传入 PerfKeywords 实例
            def make_task(f):
                def task_method(user_self):
                    f(user_self.kw)
                return task_method
            
            task_method = make_task(func)
            task_method.__name__ = func.__name__
            
            # 添加 @task 装饰器
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
        
        # 收集各请求的详细统计
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
        
        # 收集错误信息
        for error in stats.errors.values():
            result.errors.append({
                "method": error.method,
                "name": error.name,
                "error": error.error,
                "occurrences": error.occurrences
            })
        
        return result
    
    def clear(self):
        """清除所有任务和配置 (Pytest 模式)"""
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


# 全局实例 (YAML 模式使用)
keywords = PerfKeywords()
