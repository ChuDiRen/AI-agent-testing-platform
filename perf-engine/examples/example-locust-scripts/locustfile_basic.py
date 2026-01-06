"""
Locust 基础性能测试示例
演示标准的 Locust 脚本写法
"""
from locust import HttpUser, task, between, constant


class BasicApiUser(HttpUser):
    """基础 API 用户 - 模拟普通用户行为"""
    
    # 任务间等待时间：1-3 秒
    wait_time = between(1, 3)
    
    # 目标主机（可通过命令行 --host 覆盖）
    host = "https://httpbin.org"
    
    @task(3)
    def get_request(self):
        """GET 请求 - 权重 3"""
        self.client.get("/get", name="GET /get")
    
    @task(2)
    def post_request(self):
        """POST 请求 - 权重 2"""
        self.client.post(
            "/post",
            json={"username": "test", "action": "login"},
            name="POST /post"
        )
    
    @task(1)
    def get_with_params(self):
        """带参数的 GET 请求 - 权重 1"""
        self.client.get(
            "/get",
            params={"page": 1, "size": 10},
            name="GET /get?params"
        )
    
    def on_start(self):
        """用户启动时执行 - 可用于登录等初始化操作"""
        pass
    
    def on_stop(self):
        """用户停止时执行 - 可用于清理操作"""
        pass


class HealthCheckUser(HttpUser):
    """健康检查用户 - 低频率检查服务状态"""
    
    # 固定等待时间：5 秒
    wait_time = constant(5)
    
    # 用户权重（相对于其他 User 类）
    weight = 1
    
    host = "https://httpbin.org"
    
    @task
    def health_check(self):
        """健康检查"""
        with self.client.get("/status/200", catch_response=True, name="Health Check") as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
