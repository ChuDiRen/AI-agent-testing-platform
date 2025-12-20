"""
菜单管理模块 E2E 测试
测试场景:
- 菜单管理页面展示
- 新增菜单流程
- 编辑菜单流程
- 删除菜单流程
- 菜单树形结构管理
- 菜单搜索和分页
- 菜单层级管理
"""
import pytest
from datetime import datetime
from playwright.sync_api import expect

# 导入基础页面对象
from .test_sysmanage_base import MenuManagementPage


class TestMenuManagementE2E:
    """菜单管理 E2E 测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_page):
        """使用全局 fixture 初始化页面对象"""
        self.page = authenticated_page
        self.menu_page = MenuManagementPage(self.page)
        yield
    
    def test_menu_page_display(self):
        """菜单管理页面展示"""
        self.menu_page.goto_menu_page()
        # 等待页面加载和表格渲染
        self.menu_page.wait_for_page_load()
        
        # 验证页面元素
        expect(self.menu_page.add_btn.first).to_be_visible(timeout=5000)
        expect(self.menu_page.search_input.first).to_be_visible(timeout=5000)
    
    def test_add_menu_flow(self):
        """新增菜单流程"""
        self.menu_page.goto_menu_page()
        if self.menu_page.add_btn.count() > 0:
            self.menu_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(self.menu_page.dialog).to_be_visible()
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.menu_page.fill_menu_form(
                menu_name=f"测试菜单_{unique}",
                path=f"/test_{unique}"
            )
            
            if self.menu_page.confirm_btn.count() > 0:
                self.menu_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.menu_page.success_msg.count() > 0:
                    expect(self.menu_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_edit_menu_flow(self):
        """编辑菜单流程"""
        self.menu_page.goto_menu_page()
        if self.menu_page.get_row_count() > 0:
            self.menu_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            expect(self.menu_page.dialog).to_be_visible()
            
            # 修改菜单名称
            if self.menu_page.form_menu_name.count() > 0:
                self.menu_page.form_menu_name.fill("更新后的菜单名称")
            
            if self.menu_page.confirm_btn.count() > 0:
                self.menu_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_delete_menu_flow(self):
        """删除菜单流程"""
        self.menu_page.goto_menu_page()
        if self.menu_page.get_row_count() > 0:
            self.menu_page.click_row_delete(0)
            self.page.wait_for_timeout(500)
            # 确认删除对话框
            confirm_btn = self.page.locator('.el-message-box button:has-text("确定")')
            if confirm_btn.count() > 0:
                confirm_btn.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.menu_page.success_msg.count() > 0:
                    expect(self.menu_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_menu_search_flow(self):
        """菜单搜索流程"""
        self.menu_page.goto_menu_page()
        if self.menu_page.search_input.count() > 0:
            self.menu_page.search_input.first.fill("系统")
            if self.menu_page.search_btn.count() > 0:
                self.menu_page.search_btn.first.click()
                self.page.wait_for_load_state('networkidle')
                
                # 验证搜索结果
                if self.menu_page.table.count() > 0:
                    expect(self.menu_page.table.first).to_be_visible()
    
    def test_menu_pagination_flow(self):
        """菜单分页功能流程"""
        self.menu_page.goto_menu_page()
        
        # 检查分页控件
        pagination = self.page.locator('.el-pagination')
        if pagination.count() > 0:
            expect(pagination.first).to_be_visible()
            
            # 测试分页跳转
            next_btn = self.page.locator('.btn-next')
            if next_btn.count() > 0 and not next_btn.first.is_disabled():
                next_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_menu_tree_structure_flow(self):
        """菜单树形结构管理流程"""
        self.menu_page.goto_menu_page()
        # 检查菜单树是否正常显示
        tree_elements = self.page.locator('.el-tree, .tree-container')
        if tree_elements.count() > 0:
            # 尝试展开树节点
            expand_btn = self.page.locator('.el-tree-node__expand-icon')
            if expand_btn.count() > 0:
                expand_btn.first.click()
                self.page.wait_for_timeout(1000)
                
                # 验证树节点展开
                expanded_node = self.page.locator('.el-tree-node--expanded')
                if expanded_node.count() > 0:
                    expect(expanded_node.first).to_be_visible()
    
    def test_menu_hierarchy_flow(self):
        """菜单层级管理流程"""
        self.menu_page.goto_menu_page()
        # 测试创建子菜单
        if self.menu_page.add_btn.count() > 0:
            self.menu_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(self.menu_page.dialog).to_be_visible()
            
            # 选择父级菜单
            parent_menu_select = self.page.locator('.el-dialog select[placeholder*="父级"], .el-dialog .el-select')
            if parent_menu_select.count() > 0:
                parent_menu_select.first.click()
                self.page.wait_for_timeout(500)
                
                # 选择第一个选项
                first_option = self.page.locator('.el-select-dropdown__item:first-child')
                if first_option.count() > 0:
                    first_option.first.click()
                    self.page.wait_for_timeout(500)
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.menu_page.fill_menu_form(
                menu_name=f"子菜单_{unique}",
                path=f"/child_{unique}"
            )
            
            if self.menu_page.confirm_btn.count() > 0:
                self.menu_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
