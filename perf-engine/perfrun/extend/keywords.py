"""
Perf Engine 性能测试关键字
基于 Locust 实现的性能测试专用关键字库
"""
import time
import random
from typing import Dict, Any, Optional

from ..core.globalContext import g_context
from ..utils.VarRender import refresh


class PerfKeywords:
    """
    性能测试关键字类
    
    专注于性能测试场景:
    - 场景配置: 并发用户、运行时间、阶段
    - HTTP 请求: 带性能统计的请求
    - 思考时间: 模拟用户行为
    - 响应验证: 标记成功/失败
    """
    
    def __init__(self, client=None):
        self.client = client
        self.context = {}
        self.last_response = None
    
    def set_client(self, client):
        """设置 Locust client"""
        self.client = client
    
    def set_context(self, context: Dict[str, Any]):
        """设置上下文变量（同时同步到 g_context）"""
        self.context.update(context)
        # 同步到全局上下文
        g_context().set_by_dict(context)
    
    def _render(self, value: Any) -> Any:
        """渲染变量 {{var}}（使用 VarRender.refresh）"""
        # 合并全局上下文和本地上下文
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

    
    # ==================== HTTP 请求 ====================
    
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
        """发送 HTTP 请求"""
        if not self.client:
            raise RuntimeError("Locust client 未初始化")
        
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
    
    # ==================== 思考时间 ====================
    
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
    
    # ==================== 响应验证 ====================
    
    def check_status(self, **kwargs):
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
    
    def check_response_time(self, **kwargs):
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
    
    def check_contains(self, **kwargs):
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
    
    def validate_json(self, **kwargs):
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
    
    # ==================== 事务控制 ====================
    
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
    
    # ==================== 数据操作 ====================
    
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
    
    def extract_json(self, **kwargs):
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


# 全局实例
keywords = PerfKeywords()
