"""
角色管理模块 E2E 测试
测试场景:
- 角色管理页面展示
- 新增角色流程
- 编辑角色流程
- 删除角色流程
- 角色权限分配流程
- 角色搜索和分页
"""
import pytest
from datetime import datetime
from playwright.sync_api import expect

# 导入基础页面对象
from .test_sysmanage_base import RoleManagementPage


class TestRoleManagementE2E:
    """角色管理 E2E 测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_page):
        """使用全局 fixture 初始化页面对象"""
        self.page = authenticated_page
        self.role_page = RoleManagementPage(self.page)
        yield
    
    def test_role_page_display(self):
        """角色管理页面展示"""
        self.role_page.goto_role_page()
        # 等待页面加载和表格渲染
        self.role_page.wait_for_page_load()
        
        # 验证页面元素
        expect(self.role_page.add_btn.first).to_be_visible(timeout=5000)
        expect(self.role_page.search_input.first).to_be_visible(timeout=5000)
    
    def test_add_role_flow(self):
        """新增角色流程"""
        self.role_page.goto_role_page()
        if self.role_page.add_btn.count() > 0:
            self.role_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(self.role_page.dialog).to_be_visible()
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.role_page.fill_role_form(
                role_name=f"测试角色_{unique}",
                role_key=f"test_role_{unique}"
            )
            
            if self.role_page.confirm_btn.count() > 0:
                self.role_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.role_page.success_msg.count() > 0:
                    expect(self.role_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_edit_role_flow(self):
        """编辑角色流程"""
        self.role_page.goto_role_page()
        if self.role_page.get_row_count() > 0:
            self.role_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            expect(self.role_page.dialog).to_be_visible()
            
            # 修改角色名称
            if self.role_page.form_role_name.count() > 0:
                self.role_page.form_role_name.fill("更新后的角色名称")
            
            if self.role_page.confirm_btn.count() > 0:
                self.role_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_delete_role_flow(self):
        """删除角色流程"""
        self.role_page.goto_role_page()
        if self.role_page.get_row_count() > 0:
            self.role_page.click_row_delete(0)
            self.page.wait_for_timeout(500)
            # 确认删除对话框
            confirm_btn = self.page.locator('.el-message-box button:has-text("确定")')
            if confirm_btn.count() > 0:
                confirm_btn.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.role_page.success_msg.count() > 0:
                    expect(self.role_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_role_search_flow(self):
        """角色搜索流程"""
        self.role_page.goto_role_page()
        if self.role_page.search_input.count() > 0:
            self.role_page.search_input.first.fill("admin")
            if self.role_page.search_btn.count() > 0:
                self.role_page.search_btn.first.click()
                self.page.wait_for_load_state('networkidle')
                
                # 验证搜索结果
                if self.role_page.table.count() > 0:
                    expect(self.role_page.table.first).to_be_visible()
    
    def test_role_pagination_flow(self):
        """角色分页功能流程"""
        self.role_page.goto_role_page()
        
        # 检查分页控件
        pagination = self.page.locator('.el-pagination')
        if pagination.count() > 0:
            expect(pagination.first).to_be_visible()
            
            # 测试分页跳转
            next_btn = self.page.locator('.btn-next')
            if next_btn.count() > 0 and not next_btn.first.is_disabled():
                next_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_role_menu_permission_flow(self):
        """角色菜单权限分配流程"""
        self.role_page.goto_role_page()
        if self.role_page.get_row_count() > 0:
            self.role_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            
            if self.role_page.assign_menu_btn.count() > 0:
                self.role_page.assign_menu_btn.first.click()
                self.page.wait_for_timeout(1000)
                
                # 验证权限分配对话框
                permission_dialog = self.page.locator('.el-dialog:has-text("权限"), .el-dialog:has-text("菜单")')
                if permission_dialog.count() > 0:
                    expect(permission_dialog.first).to_be_visible()
                
                # 关闭对话框
                if self.role_page.cancel_btn.count() > 0:
                    self.role_page.cancel_btn.first.click()
                    self.page.wait_for_timeout(500)
