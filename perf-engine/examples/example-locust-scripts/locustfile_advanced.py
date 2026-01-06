"""
Locust 高级性能测试示例
演示响应验证、事件钩子、自定义指标等高级特性
"""
import time
import random
from locust import HttpUser, task, between, events, tag


# ============ 事件钩子 ============

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时执行"""
    print("=" * 50)
    print("性能测试开始")
    print(f"目标主机: {environment.host}")
    print("=" * 50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时执行"""
    print("=" * 50)
    print("性能测试结束")
    print("=" * 50)


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """每个请求完成时执行 - 可用于自定义日志或指标收集"""
    if exception:
        print(f"[ERROR] {request_type} {name}: {exception}")
    elif response_time > 2000:  # 响应时间超过 2 秒
        print(f"[SLOW] {request_type} {name}: {response_time}ms")


# ============ 用户类 ============

class AdvancedApiUser(HttpUser):
    """高级 API 用户 - 演示响应验证和标签"""
    
    wait_time = between(1, 3)
    host = "https://httpbin.org"
    
    @tag("smoke", "critical")
    @task(3)
    def validate_response_status(self):
        """验证响应状态码"""
        with self.client.get("/status/200", catch_response=True, name="Validate Status 200") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Expected 200, got {response.status_code}")
    
    @tag("smoke")
    @task(2)
    def validate_response_content(self):
        """验证响应内容"""
        with self.client.get("/get", catch_response=True, name="Validate Content") as response:
            try:
                data = response.json()
                if "url" in data:
                    response.success()
                else:
                    response.failure("Missing 'url' in response")
            except Exception as e:
                response.failure(f"JSON parse error: {e}")
    
    @tag("regression")
    @task(1)
    def validate_headers(self):
        """验证响应头"""
        with self.client.get("/response-headers?X-Custom=test", catch_response=True, name="Validate Headers") as response:
            if response.headers.get("X-Custom") == "test":
                response.success()
            else:
                response.failure("Missing custom header")
    
    @tag("error-handling")
    @task(1)
    def handle_error_response(self):
        """处理错误响应"""
        status_codes = [200, 400, 404, 500]
        status = random.choice(status_codes)
        
        with self.client.get(f"/status/{status}", catch_response=True, name=f"Status {status}") as response:
            if status < 400:
                response.success()
            else:
                # 预期的错误状态码也标记为成功（用于测试错误处理）
                response.success()


class DataDrivenUser(HttpUser):
    """数据驱动用户 - 使用不同的测试数据"""
    
    wait_time = between(0.5, 1.5)
    host = "https://httpbin.org"
    weight = 2
    
    # 测试数据
    users = [
        {"username": "user1", "password": "pass1"},
        {"username": "user2", "password": "pass2"},
        {"username": "user3", "password": "pass3"},
        {"username": "admin", "password": "admin123"},
    ]
    
    products = [
        {"id": 1, "name": "iPhone"},
        {"id": 2, "name": "MacBook"},
        {"id": 3, "name": "iPad"},
        {"id": 4, "name": "AirPods"},
    ]
    
    @task(3)
    def login_with_random_user(self):
        """使用随机用户登录"""
        user = random.choice(self.users)
        self.client.post(
            "/post",
            json=user,
            name="POST /login (random user)"
        )
    
    @task(2)
    def get_random_product(self):
        """获取随机商品"""
        product = random.choice(self.products)
        self.client.get(
            "/get",
            params={"product_id": product["id"]},
            name="GET /product (random)"
        )
    
    @task(1)
    def batch_operation(self):
        """批量操作"""
        # 模拟批量请求
        for i in range(3):
            self.client.get(
                "/get",
                params={"batch": i},
                name="GET /batch"
            )
            time.sleep(0.1)


class ThrottledUser(HttpUser):
    """限流用户 - 模拟慢速用户"""
    
    wait_time = between(3, 5)  # 较长的等待时间
    host = "https://httpbin.org"
    weight = 1  # 较低的权重
    
    @task
    def slow_request(self):
        """慢速请求"""
        # 使用 httpbin 的 delay 端点模拟慢响应
        self.client.get("/delay/1", name="GET /delay/1s")
