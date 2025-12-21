"""
系统管理模块 E2E 测试基础类
包含通用的页面对象和工具方法
"""
import pytest
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

WEB_BASE_URL = "http://localhost:5173"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

# 为E2E测试禁用asyncio模式
pytestmark = pytest.mark.asyncio(False)


class SysManagePage:
    """系统管理页面基类"""
    
    def __init__(self, page):
        self.page = page
        self.table = page.locator('.el-table, table')
        self.table_rows = page.locator('.el-table__row, tbody tr')
        self.add_btn = page.locator('button:has-text("新增用户"), button:has-text("新增"), button:has-text("添加")')
        self.search_input = page.locator('input[placeholder*="用户名"], input[placeholder*="搜索"], input[placeholder*="查询"]')
        self.search_btn = page.locator('button:has-text("查询"), button:has-text("搜索"), button .el-icon-search')
        self.reset_btn = page.locator('button:has-text("重置")')
        self.dialog = page.locator('.el-dialog, .modal')
        self.confirm_btn = page.locator('button:has-text("确定"), button:has-text("保存"), button:has-text("提交")')
        self.cancel_btn = page.locator('button:has-text("取消"), button:has-text("返回")')
        self.success_msg = page.locator('.el-message--success')
        self.error_msg = page.locator('.el-message--error')
    
    def login(self):
        """登录"""
        self.page.goto(f"{WEB_BASE_URL}/login")
        self.page.fill('input[placeholder*="用户名"]', TEST_USERNAME)
        self.page.fill('input[type="password"]', TEST_PASSWORD)
        self.page.click('button:has-text("登录")')
        try:
            self.page.wait_for_url("**/home**", timeout=10000)
        except:
            pass
    
    def goto(self, path: str):
        """导航到指定页面"""
        self.page.goto(f"{WEB_BASE_URL}{path}")
        self.page.wait_for_load_state('networkidle')
    
    def click_row_edit(self, index: int = 0):
        """点击行编辑按钮"""
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("编辑")').click()
    
    def click_row_delete(self, index: int = 0):
        """点击行删除按钮"""
        self.page.locator(f'.el-table__row:nth-child({index+1}) button:has-text("删除")').click()
    
    def get_row_count(self) -> int:
        """获取表格行数"""
        return self.table_rows.count()
    
    def wait_for_table_load(self, timeout: int = 5000):
        """等待表格加载"""
        try:
            self.table.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False
    
    def wait_for_page_load(self, timeout: int = 5000):
        """等待页面加载和表格渲染"""
        self.page.wait_for_timeout(3000)
        
        # 尝试多个可能的表格选择器
        table_selectors = [
            '.el-table',
            'table',
            '[class*="table"]',
            '.el-data-table',
            '.el-table__body-wrapper'
        ]
        
        table_found = False
        for selector in table_selectors:
            try:
                table = self.page.locator(selector)
                if table.count() > 0:
                    expect(table.first).to_be_visible(timeout=2000)
                    table_found = True
                    break
            except:
                continue
        
        # 如果没有找到表格，检查页面是否正常加载
        if not table_found:
            page_content = self.page.locator('h1, h2, .page-title, [class*="title"]')
            if page_content.count() > 0:
                print("页面已加载，但可能需要登录或权限")
            else:
                self.page.wait_for_timeout(2000)
        
        return table_found


class UserManagementPage(SysManagePage):
    """用户管理页面"""
    
    def __init__(self, page):
        super().__init__(page)
        # 表单字段选择器（适用于 BaseForm 页面）
        self.form_username = page.locator('input[placeholder*="用户名"], .el-form-item:has-text("用户名") input').first
        self.form_password = page.locator('input[type="password"]').first
        self.form_email = page.locator('input[placeholder*="邮箱"], .el-form-item:has-text("邮箱") input').first
        self.form_mobile = page.locator('input[placeholder*="手机"], input[placeholder*="联系电话"], .el-form-item:has-text("联系电话") input').first
        self.form_status = page.locator('.el-form-item:has-text("状态") .el-radio-group')
        self.assign_role_btn = page.locator('button:has-text("分配角色")')
    
    def goto_user_page(self):
        """导航到用户管理页面"""
        # 使用 History 路由格式访问用户管理页面
        print(f"📍 导航到用户管理页面: {WEB_BASE_URL}/userList")
        self.page.goto(f"{WEB_BASE_URL}/userList")
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_timeout(3000)
        
        # 检查最终URL
        final_url = self.page.url
        print(f"📍 当前URL: {final_url}")
        
        if '/login' in final_url:
            print("❌ 被重定向到登录页，可能原因：")
            print("   1. 动态路由未加载")
            print("   2. Token失效")
            print("   3. 权限不足")
            
            # 调试信息
            debug_info = self.page.evaluate("""
                ({
                    token: localStorage.getItem('token'),
                    username: localStorage.getItem('username'),
                    hasToken: !!localStorage.getItem('token')
                })
            """)
            print(f"🔍 认证状态: {debug_info}")
        else:
            print("✅ 成功访问用户管理页面")
        
        # 等待页面加载完成
        self.wait_for_page_load()
    
    def fill_user_form(self, username: str, email: str = "", mobile: str = "", password: str = "123456"):
        """填写用户表单（在 userForm 页面）"""
        self.page.wait_for_timeout(1000)
        
        # 等待表单加载
        self.page.wait_for_load_state('networkidle')
        
        # 填写用户名
        username_input = self.page.locator('.el-form-item:has-text("用户名") input').first
        if username_input.count() > 0:
            username_input.clear()
            username_input.fill(username)
        
        # 填写密码
        if password:
            password_input = self.page.locator('input[type="password"]').first
            if password_input.count() > 0:
                password_input.clear()
                password_input.fill(password)
        
        # 填写邮箱
        if email:
            email_input = self.page.locator('.el-form-item:has-text("邮箱") input').first
            if email_input.count() > 0:
                email_input.clear()
                email_input.fill(email)
        
        # 填写手机号
        if mobile:
            mobile_input = self.page.locator('.el-form-item:has-text("联系电话") input').first
            if mobile_input.count() > 0:
                mobile_input.clear()
                mobile_input.fill(mobile)
    
    def search_user(self, keyword: str):
        """搜索用户"""
        # 查找用户名输入框
        search_input = self.page.locator('.el-form-item:has-text("用户名") input').first
        if search_input.count() > 0 and not search_input.is_disabled():
            search_input.clear()
            search_input.fill(keyword)
            self.page.wait_for_timeout(300)
            
            # 点击查询按钮
            search_btn = self.page.locator('button:has-text("查询")').first
            if search_btn.count() > 0:
                search_btn.click()
                self.page.wait_for_timeout(1500)
                self.page.wait_for_load_state('networkidle')
    
    def reset_search(self):
        """重置搜索"""
        if self.reset_btn.count() > 0:
            self.reset_btn.first.click()
            self.page.wait_for_timeout(1000)
            self.page.wait_for_load_state('networkidle')
    
    def get_user_from_row(self, index: int = 0) -> dict:
        """从表格行获取用户信息"""
        row = self.page.locator(f'.el-table__row:nth-child({index+1})')
        if row.count() == 0:
            return {}
        
        cells = row.locator('td')
        user_info = {}
        
        if cells.count() >= 3:
            user_info['username'] = cells.nth(1).inner_text()
            user_info['email'] = cells.nth(2).inner_text() if cells.count() > 2 else ''
        
        return user_info


class RoleManagementPage(SysManagePage):
    """角色管理页面"""
    
    def __init__(self, page):
        super().__init__(page)
        self.form_role_name = page.locator('.el-dialog input[placeholder*="角色名称"]')
        self.form_role_key = page.locator('.el-dialog input[placeholder*="角色标识"]')
        self.form_role_sort = page.locator('.el-dialog input[placeholder*="显示顺序"]')
        self.assign_menu_btn = page.locator('button:has-text("分配权限")')
    
    def goto_role_page(self):
        self.goto("/system/role")
    
    def fill_role_form(self, role_name: str, role_key: str = ""):
        """填写角色表单"""
        if self.form_role_name.count() > 0:
            self.form_role_name.fill(role_name)
        if role_key and self.form_role_key.count() > 0:
            self.form_role_key.fill(role_key)


class MenuManagementPage(SysManagePage):
    """菜单管理页面"""
    
    def __init__(self, page):
        super().__init__(page)
        self.form_menu_name = page.locator('.el-dialog input[placeholder*="菜单名称"]')
        self.form_path = page.locator('.el-dialog input[placeholder*="路由地址"]')
        self.form_component = page.locator('.el-dialog input[placeholder*="组件路径"]')
        self.form_menu_type = page.locator('.el-dialog .el-select')
    
    def goto_menu_page(self):
        self.goto("/system/menu")
    
    def fill_menu_form(self, menu_name: str, path: str = ""):
        """填写菜单表单"""
        if self.form_menu_name.count() > 0:
            self.form_menu_name.fill(menu_name)
        if path and self.form_path.count() > 0:
            self.form_path.fill(path)


class DeptManagementPage(SysManagePage):
    """部门管理页面"""
    
    def __init__(self, page):
        super().__init__(page)
        self.form_dept_name = page.locator('.el-dialog input[placeholder*="部门名称"]')
        self.form_order_num = page.locator('.el-dialog input[placeholder*="显示顺序"]')
    
    def goto_dept_page(self):
        self.goto("/system/dept")
    
    def fill_dept_form(self, dept_name: str):
        """填写部门表单"""
        if self.form_dept_name.count() > 0:
            self.form_dept_name.fill(dept_name)
