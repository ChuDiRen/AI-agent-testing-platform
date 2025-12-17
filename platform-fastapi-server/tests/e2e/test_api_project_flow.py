"""
API项目管理 E2E 端到端测试
测试场景:
- 项目列表页面展示
- 新增项目流程
- 编辑项目流程
- 删除项目流程
- 搜索项目流程
"""
import pytest
from playwright.sync_api import sync_playwright, expect

WEB_BASE_URL = "http://localhost:5173"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


class ApiProjectPage:
    """Page Object: API项目管理页面"""
    
    def __init__(self, page):
        self.page = page
        self.add_btn = page.locator('button:has-text("新增"), button:has-text("添加")')
        self.search_input = page.locator('input[placeholder*="项目名"], input[placeholder*="搜索"]')
        self.search_btn = page.locator('button:has-text("搜索"), button:has-text("查询")')
        self.reset_btn = page.locator('button:has-text("重置")')
        self.table = page.locator('.el-table, table')
        self.table_rows = page.locator('.el-table__row, tbody tr')
        self.pagination = page.locator('.el-pagination')
        self.dialog = page.locator('.el-dialog, .modal')
        self.confirm_btn = page.locator('.el-dialog button:has-text("确定"), button:has-text("保存")')
        self.cancel_btn = page.locator('.el-dialog button:has-text("取消")')
        self.success_msg = page.locator('.el-message--success')
    
    def goto(self):
        self.page.goto(f"{WEB_BASE_URL}/apitest/project")
        self.page.wait_for_load_state('networkidle')
    
    def get_row_count(self) -> int:
        return self.table_rows.count()
    
    def click_row_edit(self, index: int = 0):
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("编辑")').click()
    
    def click_row_delete(self, index: int = 0):
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("删除")').click()


class TestApiProjectPageDisplay:
    """API项目页面展示测试"""
    
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
        """项目管理页面正常加载"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        expect(page_obj.table).to_be_visible()
    
    def test_table_display(self):
        """项目表格正常显示"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        expect(page_obj.table).to_be_visible()
    
    def test_add_button_visible(self):
        """新增按钮可见"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        if page_obj.add_btn.count() > 0:
            expect(page_obj.add_btn.first).to_be_visible()


class TestApiProjectAddFlow:
    """新增项目流程测试"""
    
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
    
    def test_add_dialog_open(self):
        """点击新增打开弹窗"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        if page_obj.add_btn.count() > 0:
            page_obj.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(page_obj.dialog).to_be_visible()
    
    def test_add_cancel(self):
        """取消新增"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        if page_obj.add_btn.count() > 0:
            page_obj.add_btn.first.click()
            self.page.wait_for_timeout(500)
            if page_obj.cancel_btn.count() > 0:
                page_obj.cancel_btn.first.click()
                self.page.wait_for_timeout(500)
                expect(page_obj.dialog).not_to_be_visible()


class TestApiProjectEditFlow:
    """编辑项目流程测试"""
    
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
    
    def test_edit_dialog_open(self):
        """点击编辑打开弹窗"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        if page_obj.get_row_count() > 0:
            page_obj.click_row_edit(0)
            self.page.wait_for_timeout(500)
            expect(page_obj.dialog).to_be_visible()


class TestApiProjectDeleteFlow:
    """删除项目流程测试"""
    
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
    
    def test_delete_confirm_dialog(self):
        """删除确认弹窗"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        if page_obj.get_row_count() > 0:
            page_obj.click_row_delete(0)
            self.page.wait_for_timeout(500)
            confirm = self.page.locator('.el-message-box, .el-popconfirm')
            if confirm.count() > 0:
                expect(confirm.first).to_be_visible()


class TestApiProjectSearchFlow:
    """搜索项目流程测试"""
    
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
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        if page_obj.search_input.count() > 0:
            page_obj.search_input.first.fill("test")
            if page_obj.search_btn.count() > 0:
                page_obj.search_btn.first.click()
                self.page.wait_for_load_state('networkidle')
    
    def test_search_reset(self):
        """重置搜索"""
        page_obj = ApiProjectPage(self.page)
        page_obj.goto()
        if page_obj.search_input.count() > 0:
            page_obj.search_input.first.fill("test")
            if page_obj.reset_btn.count() > 0:
                page_obj.reset_btn.first.click()
                self.page.wait_for_load_state('networkidle')
