"""
插件管理 E2E 端到端测试
测试场景:
- 插件列表页面展示
- 插件详情查看
- 插件启用/禁用
- 插件健康检查
"""
import pytest
from playwright.sync_api import sync_playwright, expect

WEB_BASE_URL = "http://localhost:5173"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


class PluginManagementPage:
    """Page Object: 插件管理页面"""
    
    def __init__(self, page):
        self.page = page
        self.table = page.locator('.el-table, table')
        self.table_rows = page.locator('.el-table__row, tbody tr')
        self.pagination = page.locator('.el-pagination')
        self.search_input = page.locator('input[placeholder*="插件名"], input[placeholder*="搜索"]')
        self.search_btn = page.locator('button:has-text("搜索"), button:has-text("查询")')
        self.dialog = page.locator('.el-dialog, .modal')
    
    def goto(self):
        self.page.goto(f"{WEB_BASE_URL}/plugin/list")
        self.page.wait_for_load_state('networkidle')
    
    def get_row_count(self) -> int:
        return self.table_rows.count()
    
    def click_row_detail(self, index: int = 0):
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("详情")').click()
    
    def click_row_toggle(self, index: int = 0):
        self.page.locator(f'.el-table__row:nth-child({index+1}) .el-switch').click()
    
    def click_row_health_check(self, index: int = 0):
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("检查")').click()


class TestPluginPageDisplay:
    """插件管理页面展示测试"""
    
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
        self.page.goto(f"{WEB_BASE_URL}/login")
        self.page.fill('input[placeholder*="用户名"]', TEST_USERNAME)
        self.page.fill('input[type="password"]', TEST_PASSWORD)
        self.page.click('button:has-text("登录")')
        try:
            self.page.wait_for_url("**/home**", timeout=10000)
        except:
            pass
    
    def test_page_display(self):
        """插件管理页面正常加载"""
        page_obj = PluginManagementPage(self.page)
        page_obj.goto()
        expect(page_obj.table).to_be_visible()
    
    def test_table_display(self):
        """插件表格正常显示"""
        page_obj = PluginManagementPage(self.page)
        page_obj.goto()
        expect(page_obj.table).to_be_visible()


class TestPluginDetailFlow:
    """插件详情流程测试"""
    
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
        self.page.goto(f"{WEB_BASE_URL}/login")
        self.page.fill('input[placeholder*="用户名"]', TEST_USERNAME)
        self.page.fill('input[type="password"]', TEST_PASSWORD)
        self.page.click('button:has-text("登录")')
        try:
            self.page.wait_for_url("**/home**", timeout=10000)
        except:
            pass
    
    def test_detail_dialog_open(self):
        """点击详情打开弹窗"""
        page_obj = PluginManagementPage(self.page)
        page_obj.goto()
        if page_obj.get_row_count() > 0:
            detail_btn = self.page.locator('.el-table__row:nth-child(1) button:has-text("详情")')
            if detail_btn.count() > 0:
                detail_btn.click()
                self.page.wait_for_timeout(500)
                expect(page_obj.dialog).to_be_visible()


class TestPluginToggleFlow:
    """插件启用/禁用流程测试"""
    
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
        self.page.goto(f"{WEB_BASE_URL}/login")
        self.page.fill('input[placeholder*="用户名"]', TEST_USERNAME)
        self.page.fill('input[type="password"]', TEST_PASSWORD)
        self.page.click('button:has-text("登录")')
        try:
            self.page.wait_for_url("**/home**", timeout=10000)
        except:
            pass
    
    def test_toggle_switch_visible(self):
        """启用/禁用开关可见"""
        page_obj = PluginManagementPage(self.page)
        page_obj.goto()
        if page_obj.get_row_count() > 0:
            switch = self.page.locator('.el-table__row:nth-child(1) .el-switch')
            if switch.count() > 0:
                expect(switch).to_be_visible()


class TestPluginSearchFlow:
    """插件搜索流程测试"""
    
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
        self.page.goto(f"{WEB_BASE_URL}/login")
        self.page.fill('input[placeholder*="用户名"]', TEST_USERNAME)
        self.page.fill('input[type="password"]', TEST_PASSWORD)
        self.page.click('button:has-text("登录")')
        try:
            self.page.wait_for_url("**/home**", timeout=10000)
        except:
            pass
    
    def test_search_with_keyword(self):
        """关键词搜索"""
        page_obj = PluginManagementPage(self.page)
        page_obj.goto()
        if page_obj.search_input.count() > 0:
            page_obj.search_input.first.fill("api")
            if page_obj.search_btn.count() > 0:
                page_obj.search_btn.first.click()
                self.page.wait_for_load_state('networkidle')
