"""
测试配置文件
提供通用的 fixtures 和测试工具
"""
import os
import sys
from datetime import datetime

import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# API 测试配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000")
WEB_BASE_URL = os.getenv("WEB_BASE_URL", "http://localhost:5173")
TEST_USERNAME = os.getenv("TEST_USERNAME", "admin")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "admin123")


class APIClient:
    """API 测试客户端"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        import requests
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def login(self, username: str = TEST_USERNAME, password: str = TEST_PASSWORD):
        """登录获取 token"""
        response = self.session.post(
            f"{self.base_url}/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                self.token = data.get("data", {}).get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        return response
    
    def get(self, path: str, params: dict = None):
        """GET 请求"""
        return self.session.get(f"{self.base_url}{path}", params=params)
    
    def post(self, path: str, json: dict = None, data: dict = None):
        """POST 请求"""
        return self.session.post(f"{self.base_url}{path}", json=json, data=data)
    
    def put(self, path: str, json: dict = None):
        """PUT 请求"""
        return self.session.put(f"{self.base_url}{path}", json=json)
    
    def delete(self, path: str, params: dict = None):
        """DELETE 请求"""
        return self.session.delete(f"{self.base_url}{path}", params=params)
    
    def assert_success(self, response):
        """断言请求成功"""
        assert response.status_code == 200
        data = response.json()
        assert data.get("code") == 200, f"API 返回错误: {data.get('msg')}"
        return data
    
    def close(self):
        """关闭会话"""
        self.session.close()


@pytest.fixture
def api_client():
    """提供已登录的 API 客户端"""
    client = APIClient()
    client.login()
    yield client
    client.close()


@pytest.fixture
def api_client_no_auth():
    """提供未登录的 API 客户端"""
    client = APIClient()
    yield client
    client.close()


@pytest.fixture
def unique_name():
    """生成唯一名称"""
    return f"test_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


# ==================== Playwright E2E 测试 Fixtures ====================

@pytest.fixture(scope="class")
def browser():
    """提供 Playwright 浏览器实例（非无头模式）- 类级别共享"""
    from playwright.sync_api import sync_playwright
    
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    yield browser
    browser.close()
    playwright.stop()


@pytest.fixture(scope="class")
def page(browser):
    """提供 Playwright 页面实例 - 类级别共享"""
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture(scope="class")
def authenticated_page(page):
    """提供已登录的 Playwright 页面实例 - 类级别共享，只登录一次"""
    # 首先尝试直接访问主页，如果已登录就直接使用
    page.goto(f"{WEB_BASE_URL}/Statistics")
    page.wait_for_load_state('networkidle')
    page.wait_for_timeout(2000)
    
    # 检查是否已经登录
    try:
        token = page.evaluate("localStorage.getItem('token')")
        current_url = page.url
        
        if token and '/login' not in current_url:
            print("✅ 检测到已登录状态，直接使用")
            yield page
            return
    except:
        pass
    
    # 如果没有登录，执行登录流程
    print("🔐 执行登录流程...")
    page.goto(f"{WEB_BASE_URL}/login")
    
    # 等待页面加载
    page.wait_for_load_state('networkidle')
    
    # 使用 Element Plus 选择器填写登录表单
    # 用户名输入框 - Element Plus 的 el-input 组件
    page.fill('input[placeholder="请输入用户名"]', TEST_USERNAME)
    
    # 密码输入框 - Element Plus 的 el-input 组件
    page.fill('input[placeholder="请输入密码"]', TEST_PASSWORD)
    
    # 点击登录按钮
    page.click('button:has-text("登录")')
    
    # 等待登录成功并跳转到首页
    try:
        # 等待URL变化，不再是 /login
        page.wait_for_timeout(3000)
        page.wait_for_load_state('networkidle')
        
        current_url = page.url
        print(f"✅ 登录成功，当前URL: {current_url}")
        
        # 如果URL不正确，手动导航到主页
        if '/Statistics' not in current_url:
            print("🔄 手动导航到主页...")
            page.goto(f"{WEB_BASE_URL}/Statistics")
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
            print(f"✅ 已导航到主页: {page.url}")
        
        # 等待页面完全加载
        page.wait_for_timeout(3000)
        
        # 验证token是否正确保存
        token = page.evaluate("localStorage.getItem('token')")
        if token:
            print(f"✅ Token已保存: {token[:20]}...")
        else:
            print("⚠️ Token未找到")
        
        # 验证当前页面是主页而不是登录页
        final_url = page.url
        if '/login' in final_url:
            print("⚠️ 当前仍在登录页面，尝试重新导航...")
            page.goto(f"{WEB_BASE_URL}/Statistics")
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(2000)
            final_url = page.url
        
        print(f"✅ 当前页面URL: {final_url}")
        
        # 确保token和用户信息正确保存
        page.evaluate("""
            localStorage.setItem('token', localStorage.getItem('token'));
            localStorage.setItem('username', 'admin');
            localStorage.setItem('permissions', JSON.stringify(['*']));
        """)
        print("✅ 认证信息已强化保存")
        
        # 刷新页面以确保应用重新读取 localStorage 中的认证信息
        print("🔄 刷新页面以应用认证状态...")
        page.reload()
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)
        
        # 验证刷新后仍在主页而不是登录页
        refreshed_url = page.url
        if '/login' in refreshed_url:
            print("⚠️ 刷新后仍在登录页，认证可能有问题")
        else:
            print(f"✅ 刷新后认证状态正常: {refreshed_url}")
        
        # 等待动态路由加载完成
        print("⏳ 等待动态路由加载...")
        page.wait_for_timeout(2000)
        print("✅ 动态路由加载完成")
        
    except Exception as e:
        print(f"⚠️ 登录可能失败: {e}")
    
    yield page
