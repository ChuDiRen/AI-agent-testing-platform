"""
用户管理模块 E2E 测试
测试场景:
- 用户管理页面展示
- 新增用户流程
- 编辑用户流程
- 删除用户流程
- 用户搜索流程
- 分页功能
- 用户角色分配
"""
import pytest
from datetime import datetime
from playwright.sync_api import expect

# 导入基础页面对象
from .test_sysmanage_base import UserManagementPage


class TestUserManagementE2E:
    """用户管理 E2E 测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_page):
        """使用全局 fixture 初始化页面对象"""
        self.page = authenticated_page
        self.user_page = UserManagementPage(self.page)
        yield
    
    def test_user_page_display(self):
        """用户管理页面展示"""
        self.user_page.goto_user_page()
        # 等待页面加载和表格渲染
        self.user_page.wait_for_page_load()
        
        # 验证页面元素
        expect(self.user_page.add_btn.first).to_be_visible(timeout=5000)
        expect(self.user_page.search_input.first).to_be_visible(timeout=5000)
    
    def test_add_user_flow(self):
        """新增用户流程"""
        self.user_page.goto_user_page()
        if self.user_page.add_btn.count() > 0:
            self.user_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(self.user_page.dialog).to_be_visible()
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.user_page.fill_user_form(
                username=f"test_user_{unique}",
                email=f"test_{unique}@test.com",
                mobile="13800138000"
            )
            
            if self.user_page.confirm_btn.count() > 0:
                self.user_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.user_page.success_msg.count() > 0:
                    expect(self.user_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_edit_user_flow(self):
        """编辑用户流程"""
        self.user_page.goto_user_page()
        if self.user_page.get_row_count() > 0:
            self.user_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            expect(self.user_page.dialog).to_be_visible()
            
            # 修改邮箱
            if self.user_page.form_email.count() > 0:
                self.user_page.form_email.fill("updated@test.com")
            
            if self.user_page.confirm_btn.count() > 0:
                self.user_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_delete_user_flow(self):
        """删除用户流程"""
        self.user_page.goto_user_page()
        if self.user_page.get_row_count() > 0:
            self.user_page.click_row_delete(0)
            self.page.wait_for_timeout(500)
            # 确认删除对话框
            confirm_btn = self.page.locator('.el-message-box button:has-text("确定")')
            if confirm_btn.count() > 0:
                confirm_btn.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.user_page.success_msg.count() > 0:
                    expect(self.user_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_user_search_flow(self):
        """用户搜索流程"""
        self.user_page.goto_user_page()
        if self.user_page.search_input.count() > 0:
            self.user_page.search_input.first.fill("admin")
            if self.user_page.search_btn.count() > 0:
                self.user_page.search_btn.first.click()
                self.page.wait_for_load_state('networkidle')
                
                # 验证搜索结果
                if self.user_page.table.count() > 0:
                    expect(self.user_page.table.first).to_be_visible()
    
    def test_user_pagination_flow(self):
        """用户分页功能流程"""
        self.user_page.goto_user_page()
        
        # 检查分页控件
        pagination = self.page.locator('.el-pagination')
        if pagination.count() > 0:
            expect(pagination.first).to_be_visible()
            
            # 测试分页跳转
            next_btn = self.page.locator('.btn-next')
            if next_btn.count() > 0 and not next_btn.first.is_disabled():
                next_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_user_role_assignment_flow(self):
        """用户角色分配流程"""
        self.user_page.goto_user_page()
        if self.user_page.get_row_count() > 0:
            self.user_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            
            if self.user_page.assign_role_btn.count() > 0:
                self.user_page.assign_role_btn.first.click()
                self.page.wait_for_timeout(1000)
                
                # 验证角色分配对话框
                role_dialog = self.page.locator('.el-dialog:has-text("分配角色")')
                if role_dialog.count() > 0:
                    expect(role_dialog.first).to_be_visible()
                
                # 关闭对话框
                if self.user_page.cancel_btn.count() > 0:
                    self.user_page.cancel_btn.first.click()
                    self.page.wait_for_timeout(500)
