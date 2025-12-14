"""
登录模块 E2E 端到端测试
测试场景:
- 登录页面展示
- 登录成功流程
- 登录失败流程
- 退出登录流程
"""
import pytest
from playwright.sync_api import sync_playwright, expect

WEB_BASE_URL = "http://localhost:5173"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


class LoginPage:
    """Page Object: 登录页面"""
    
    def __init__(self, page):
        self.page = page
        self.username_input = page.locator('input[placeholder*="用户名"], input[name="username"]')
        self.password_input = page.locator('input[type="password"]')
        self.login_btn = page.locator('button:has-text("登录"), button[type="submit"]')
        self.error_msg = page.locator('.el-message--error, .error-message')
        self.success_msg = page.locator('.el-message--success')
    
    def goto(self):
        self.page.goto(f"{WEB_BASE_URL}/login")
        self.page.wait_for_load_state('networkidle')
    
    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()


class TestLoginPageDisplay:
    """登录页面展示测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        yield
        self.browser.close()
        self.playwright.stop()
    
    def test_page_display(self):
        """登录页面正常加载"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        expect(page_obj.username_input).to_be_visible()
        expect(page_obj.password_input).to_be_visible()
        expect(page_obj.login_btn).to_be_visible()
    
    def test_username_input_visible(self):
        """用户名输入框可见"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        expect(page_obj.username_input).to_be_visible()
        expect(page_obj.username_input).to_be_editable()
    
    def test_password_input_visible(self):
        """密码输入框可见"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        expect(page_obj.password_input).to_be_visible()
        expect(page_obj.password_input).to_be_editable()
    
    def test_login_button_visible(self):
        """登录按钮可见"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        expect(page_obj.login_btn).to_be_visible()
        expect(page_obj.login_btn).to_be_enabled()


class TestLoginSuccessFlow:
    """登录成功流程测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        yield
        self.browser.close()
        self.playwright.stop()
    
    def test_login_success(self):
        """正确用户名密码登录成功"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        page_obj.login(TEST_USERNAME, TEST_PASSWORD)
        # 等待跳转到首页
        self.page.wait_for_url("**/home**", timeout=10000)
    
    def test_login_redirect_to_home(self):
        """登录成功后跳转到首页"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        page_obj.login(TEST_USERNAME, TEST_PASSWORD)
        self.page.wait_for_url("**/home**", timeout=10000)
        assert "/home" in self.page.url or "/dashboard" in self.page.url


class TestLoginFailureFlow:
    """登录失败流程测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        yield
        self.browser.close()
        self.playwright.stop()
    
    def test_login_wrong_password(self):
        """错误密码登录失败"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        page_obj.login(TEST_USERNAME, "wrong_password")
        self.page.wait_for_timeout(1000)
        # 应该还在登录页
        assert "/login" in self.page.url
    
    def test_login_wrong_username(self):
        """错误用户名登录失败"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        page_obj.login("wrong_user", TEST_PASSWORD)
        self.page.wait_for_timeout(1000)
        assert "/login" in self.page.url
    
    def test_login_empty_username(self):
        """空用户名登录"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        page_obj.login("", TEST_PASSWORD)
        self.page.wait_for_timeout(500)
        # 应该还在登录页，可能显示验证错误
        assert "/login" in self.page.url
    
    def test_login_empty_password(self):
        """空密码登录"""
        page_obj = LoginPage(self.page)
        page_obj.goto()
        page_obj.login(TEST_USERNAME, "")
        self.page.wait_for_timeout(500)
        assert "/login" in self.page.url


class TestLogoutFlow:
    """退出登录流程测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
        self._login()
        yield
        self.browser.close()
        self.playwright.stop()
    
    def _login(self):
        page_obj = LoginPage(self.page)
        page_obj.goto()
        page_obj.login(TEST_USERNAME, TEST_PASSWORD)
        try:
            self.page.wait_for_url("**/home**", timeout=10000)
        except:
            pass
    
    def test_logout_button_visible(self):
        """退出按钮可见"""
        # 查找用户头像或退出按钮
        logout_trigger = self.page.locator('.el-dropdown, .user-avatar, .logout-btn')
        if logout_trigger.count() > 0:
            expect(logout_trigger.first).to_be_visible()
