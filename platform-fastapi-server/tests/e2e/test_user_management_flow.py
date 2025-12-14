"""
用户管理 E2E 端到端测试
测试场景:
- 用户列表页面展示
- 新增用户流程
- 编辑用户流程
- 删除用户流程
- 搜索用户流程
- 分页功能
"""
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

WEB_BASE_URL = "http://localhost:5173"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


class UserManagementPage:
    """Page Object: 用户管理页面"""
    
    def __init__(self, page):
        self.page = page
        # 列表页元素
        self.add_btn = page.locator('button:has-text("新增"), button:has-text("添加")')
        self.search_input = page.locator('input[placeholder*="用户名"], input[placeholder*="搜索"]')
        self.search_btn = page.locator('button:has-text("搜索"), button:has-text("查询")')
        self.reset_btn = page.locator('button:has-text("重置")')
        self.table = page.locator('.el-table, table')
        self.table_rows = page.locator('.el-table__row, tbody tr')
        self.pagination = page.locator('.el-pagination')
        
        # 弹窗元素
        self.dialog = page.locator('.el-dialog, .modal')
        self.dialog_title = page.locator('.el-dialog__title')
        self.confirm_btn = page.locator('.el-dialog button:has-text("确定"), button:has-text("保存")')
        self.cancel_btn = page.locator('.el-dialog button:has-text("取消")')
        
        # 表单元素
        self.form_username = page.locator('.el-dialog input[placeholder*="用户名"]')
        self.form_password = page.locator('.el-dialog input[type="password"]')
        self.form_email = page.locator('.el-dialog input[placeholder*="邮箱"]')
        
        # 消息提示
        self.success_msg = page.locator('.el-message--success')
        self.error_msg = page.locator('.el-message--error')
    
    def goto(self):
        self.page.goto(f"{WEB_BASE_URL}/system/user")
        self.page.wait_for_load_state('networkidle')
    
    def get_row_count(self) -> int:
        return self.table_rows.count()
    
    def click_row_edit(self, index: int = 0):
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("编辑")').click()
    
    def click_row_delete(self, index: int = 0):
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("删除")').click()


class TestUserPageDisplay:
    """用户管理页面展示测试"""
    
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
        """用户管理页面正常加载"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        expect(page_obj.table).to_be_visible()
    
    def test_table_display(self):
        """用户表格正常显示"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        expect(page_obj.table).to_be_visible()
    
    def test_add_button_visible(self):
        """新增按钮可见"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.add_btn.count() > 0:
            expect(page_obj.add_btn.first).to_be_visible()
    
    def test_pagination_display(self):
        """分页组件显示"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.pagination.count() > 0:
            expect(page_obj.pagination).to_be_visible()


class TestUserAddFlow:
    """新增用户流程测试"""
    
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
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.add_btn.count() > 0:
            page_obj.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(page_obj.dialog).to_be_visible()
    
    def test_add_form_validation(self):
        """新增表单验证"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.add_btn.count() > 0:
            page_obj.add_btn.first.click()
            self.page.wait_for_timeout(500)
            # 不填写直接提交
            if page_obj.confirm_btn.count() > 0:
                page_obj.confirm_btn.first.click()
                self.page.wait_for_timeout(500)
                # 弹窗应该还在（验证失败）
                expect(page_obj.dialog).to_be_visible()
    
    def test_add_cancel(self):
        """取消新增"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.add_btn.count() > 0:
            page_obj.add_btn.first.click()
            self.page.wait_for_timeout(500)
            if page_obj.cancel_btn.count() > 0:
                page_obj.cancel_btn.first.click()
                self.page.wait_for_timeout(500)
                expect(page_obj.dialog).not_to_be_visible()


class TestUserEditFlow:
    """编辑用户流程测试"""
    
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
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.get_row_count() > 0:
            page_obj.click_row_edit(0)
            self.page.wait_for_timeout(500)
            expect(page_obj.dialog).to_be_visible()


class TestUserDeleteFlow:
    """删除用户流程测试"""
    
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
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.get_row_count() > 0:
            page_obj.click_row_delete(0)
            self.page.wait_for_timeout(500)
            confirm = self.page.locator('.el-message-box, .el-popconfirm')
            if confirm.count() > 0:
                expect(confirm.first).to_be_visible()


class TestUserSearchFlow:
    """搜索用户流程测试"""
    
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
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.search_input.count() > 0:
            page_obj.search_input.first.fill("admin")
            if page_obj.search_btn.count() > 0:
                page_obj.search_btn.first.click()
                self.page.wait_for_load_state('networkidle')
    
    def test_search_reset(self):
        """重置搜索"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        if page_obj.search_input.count() > 0:
            page_obj.search_input.first.fill("test")
            if page_obj.reset_btn.count() > 0:
                page_obj.reset_btn.first.click()
                self.page.wait_for_load_state('networkidle')


class TestUserPaginationFlow:
    """分页功能测试"""
    
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
    
    def test_pagination_next(self):
        """下一页"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        next_btn = self.page.locator('.el-pagination .btn-next')
        if next_btn.count() > 0 and next_btn.is_enabled():
            next_btn.click()
            self.page.wait_for_load_state('networkidle')
    
    def test_pagination_size_change(self):
        """切换每页条数"""
        page_obj = UserManagementPage(self.page)
        page_obj.goto()
        size_select = self.page.locator('.el-pagination .el-select')
        if size_select.count() > 0:
            size_select.click()
            option = self.page.locator('.el-select-dropdown__item:has-text("20")')
            if option.count() > 0:
                option.click()
                self.page.wait_for_load_state('networkidle')
