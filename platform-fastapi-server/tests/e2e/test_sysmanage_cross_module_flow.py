"""
系统管理模块跨模块业务流程 E2E 测试
测试场景:
- 用户角色分配流程
- 角色菜单权限分配流程
- 用户部门分配流程
- 完整的用户权限管理流程
"""
import pytest
from datetime import datetime
from playwright.sync_api import expect

# 导入基础页面对象
from .test_sysmanage_base import (
    UserManagementPage, 
    RoleManagementPage, 
    MenuManagementPage, 
    DeptManagementPage
)


class TestSysManageCrossModuleE2E:
    """系统管理跨模块业务流程 E2E 测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_page):
        """使用全局 fixture 初始化页面对象"""
        self.page = authenticated_page
        
        # 初始化各个页面对象
        self.user_page = UserManagementPage(self.page)
        self.role_page = RoleManagementPage(self.page)
        self.menu_page = MenuManagementPage(self.page)
        self.dept_page = DeptManagementPage(self.page)
        yield
    
    def test_user_role_assignment_flow(self):
        """用户角色分配流程"""
        # 1. 创建角色
        self.role_page.goto_role_page()
        if self.role_page.add_btn.count() > 0:
            self.role_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.role_page.fill_role_form(
                role_name=f"测试角色_{unique}",
                role_key=f"test_role_{unique}"
            )
            
            if self.role_page.confirm_btn.count() > 0:
                self.role_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 2. 创建用户
        self.user_page.goto_user_page()
        if self.user_page.add_btn.count() > 0:
            self.user_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            
            self.user_page.fill_user_form(
                username=f"test_user_{unique}",
                email=f"test_{unique}@test.com"
            )
            
            if self.user_page.confirm_btn.count() > 0:
                self.user_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 3. 为用户分配角色
        if self.user_page.get_row_count() > 0:
            self.user_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            
            if self.user_page.assign_role_btn.count() > 0:
                self.user_page.assign_role_btn.first.click()
                self.page.wait_for_timeout(1000)
                # 关闭对话框
                if self.user_page.cancel_btn.count() > 0:
                    self.user_page.cancel_btn.first.click()
                    self.page.wait_for_timeout(500)
    
    def test_role_menu_permission_flow(self):
        """角色菜单权限分配流程"""
        # 1. 创建菜单
        self.menu_page.goto_menu_page()
        if self.menu_page.add_btn.count() > 0:
            self.menu_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.menu_page.fill_menu_form(
                menu_name=f"测试菜单_{unique}",
                path=f"/test_{unique}"
            )
            
            if self.menu_page.confirm_btn.count() > 0:
                self.menu_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 2. 创建角色
        self.role_page.goto_role_page()
        if self.role_page.add_btn.count() > 0:
            self.role_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            
            self.role_page.fill_role_form(
                role_name=f"测试角色_{unique}",
                role_key=f"test_role_{unique}"
            )
            
            if self.role_page.confirm_btn.count() > 0:
                self.role_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 3. 为角色分配菜单权限
        if self.role_page.get_row_count() > 0:
            self.role_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            
            if self.role_page.assign_menu_btn.count() > 0:
                self.role_page.assign_menu_btn.first.click()
                self.page.wait_for_timeout(1000)
                # 关闭对话框
                if self.role_page.cancel_btn.count() > 0:
                    self.role_page.cancel_btn.first.click()
                    self.page.wait_for_timeout(500)
    
    def test_user_dept_assignment_flow(self):
        """用户部门分配流程"""
        # 1. 创建部门
        self.dept_page.goto_dept_page()
        if self.dept_page.add_btn.count() > 0:
            self.dept_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.dept_page.fill_dept_form(dept_name=f"测试部门_{unique}")
            
            if self.dept_page.confirm_btn.count() > 0:
                self.dept_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 2. 创建用户并关联部门
        self.user_page.goto_user_page()
        if self.user_page.add_btn.count() > 0:
            self.user_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            
            self.user_page.fill_user_form(
                username=f"test_user_{unique}",
                email=f"test_{unique}@test.com"
            )
            
            if self.user_page.confirm_btn.count() > 0:
                self.user_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_complete_user_permission_flow(self):
        """完整的用户权限管理流程"""
        unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
        
        # 1. 创建部门
        self.dept_page.goto_dept_page()
        if self.dept_page.add_btn.count() > 0:
            self.dept_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            self.dept_page.fill_dept_form(dept_name=f"测试部门_{unique}")
            if self.dept_page.confirm_btn.count() > 0:
                self.dept_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 2. 创建菜单
        self.menu_page.goto_menu_page()
        if self.menu_page.add_btn.count() > 0:
            self.menu_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            self.menu_page.fill_menu_form(
                menu_name=f"测试菜单_{unique}",
                path=f"/test_{unique}"
            )
            if self.menu_page.confirm_btn.count() > 0:
                self.menu_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 3. 创建角色
        self.role_page.goto_role_page()
        if self.role_page.add_btn.count() > 0:
            self.role_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            self.role_page.fill_role_form(
                role_name=f"测试角色_{unique}",
                role_key=f"test_role_{unique}"
            )
            if self.role_page.confirm_btn.count() > 0:
                self.role_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 4. 创建用户
        self.user_page.goto_user_page()
        if self.user_page.add_btn.count() > 0:
            self.user_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            self.user_page.fill_user_form(
                username=f"test_user_{unique}",
                email=f"test_{unique}@test.com"
            )
            if self.user_page.confirm_btn.count() > 0:
                self.user_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
        
        # 5. 为角色分配菜单权限
        if self.role_page.get_row_count() > 0:
            self.role_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            if self.role_page.assign_menu_btn.count() > 0:
                self.role_page.assign_menu_btn.first.click()
                self.page.wait_for_timeout(1000)
                if self.role_page.cancel_btn.count() > 0:
                    self.role_page.cancel_btn.first.click()
                    self.page.wait_for_timeout(500)
        
        # 6. 为用户分配角色
        if self.user_page.get_row_count() > 0:
            self.user_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            if self.user_page.assign_role_btn.count() > 0:
                self.user_page.assign_role_btn.first.click()
                self.page.wait_for_timeout(1000)
                if self.user_page.cancel_btn.count() > 0:
                    self.user_page.cancel_btn.first.click()
                    self.page.wait_for_timeout(500)
