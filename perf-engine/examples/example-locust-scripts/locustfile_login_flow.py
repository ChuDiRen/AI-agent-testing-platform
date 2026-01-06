"""
Locust 登录流程性能测试
演示完整的用户登录场景
"""
from locust import HttpUser, task, between, SequentialTaskSet


class LoginTaskSet(SequentialTaskSet):
    """登录任务集 - 按顺序执行任务"""
    
    @task
    def login(self):
        """步骤1: 登录"""
        response = self.client.post(
            "/post",
            json={
                "username": "testuser",
                "password": "password123"
            },
            name="POST /login"
        )
        # 模拟从响应中提取 token
        if response.status_code == 200:
            self.user.token = "mock_token_12345"
    
    @task
    def get_profile(self):
        """步骤2: 获取用户信息"""
        headers = {"Authorization": f"Bearer {getattr(self.user, 'token', '')}"}
        self.client.get(
            "/get",
            headers=headers,
            name="GET /profile"
        )
    
    @task
    def browse_products(self):
        """步骤3: 浏览商品列表"""
        for page in range(1, 4):
            self.client.get(
                "/get",
                params={"page": page, "category": "electronics"},
                name="GET /products"
            )
    
    @task
    def logout(self):
        """步骤4: 登出"""
        self.client.post("/post", json={"action": "logout"}, name="POST /logout")
        self.interrupt()  # 结束任务集，重新开始


class LoginFlowUser(HttpUser):
    """登录流程用户"""
    
    wait_time = between(1, 2)
    host = "https://httpbin.org"
    tasks = [LoginTaskSet]
    
    def on_start(self):
        """初始化用户属性"""
        self.token = None


class QuickBrowseUser(HttpUser):
    """快速浏览用户 - 不登录直接浏览"""
    
    wait_time = between(0.5, 1.5)
    host = "https://httpbin.org"
    weight = 2  # 权重为 LoginFlowUser 的 2 倍
    
    @task(5)
    def browse_home(self):
        """浏览首页"""
        self.client.get("/get", params={"page": "home"}, name="GET /home")
    
    @task(3)
    def browse_category(self):
        """浏览分类"""
        categories = ["electronics", "clothing", "books", "food"]
        import random
        category = random.choice(categories)
        self.client.get(
            "/get",
            params={"category": category},
            name="GET /category"
        )
    
    @task(1)
    def search(self):
        """搜索商品"""
        keywords = ["phone", "laptop", "headphones", "camera"]
        import random
        keyword = random.choice(keywords)
        self.client.get(
            "/get",
            params={"q": keyword},
            name="GET /search"
        )
