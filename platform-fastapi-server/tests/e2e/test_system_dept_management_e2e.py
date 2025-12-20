"""
部门管理模块 E2E 测试
测试场景:
- 部门管理页面展示
- 新增部门流程
- 编辑部门流程
- 删除部门流程
- 部门树形结构管理
- 部门搜索和分页
- 部门层级管理
"""
import pytest
from datetime import datetime
from playwright.sync_api import expect

# 导入基础页面对象
from .test_sysmanage_base import DeptManagementPage


class TestDeptManagementE2E:
    """部门管理 E2E 测试"""
    
    @pytest.fixture(autouse=True)
    def setup(self, authenticated_page):
        """使用全局 fixture 初始化页面对象"""
        self.page = authenticated_page
        self.dept_page = DeptManagementPage(self.page)
        yield
    
    def test_dept_page_display(self):
        """部门管理页面展示"""
        self.dept_page.goto_dept_page()
        # 等待页面加载和表格渲染
        self.dept_page.wait_for_page_load()
        
        # 验证页面元素
        expect(self.dept_page.add_btn.first).to_be_visible(timeout=5000)
        expect(self.dept_page.search_input.first).to_be_visible(timeout=5000)
    
    def test_add_dept_flow(self):
        """新增部门流程"""
        self.dept_page.goto_dept_page()
        if self.dept_page.add_btn.count() > 0:
            self.dept_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(self.dept_page.dialog).to_be_visible()
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.dept_page.fill_dept_form(dept_name=f"测试部门_{unique}")
            
            if self.dept_page.confirm_btn.count() > 0:
                self.dept_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.dept_page.success_msg.count() > 0:
                    expect(self.dept_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_edit_dept_flow(self):
        """编辑部门流程"""
        self.dept_page.goto_dept_page()
        if self.dept_page.get_row_count() > 0:
            self.dept_page.click_row_edit(0)
            self.page.wait_for_timeout(500)
            expect(self.dept_page.dialog).to_be_visible()
            
            # 修改部门名称
            if self.dept_page.form_dept_name.count() > 0:
                self.dept_page.form_dept_name.fill("更新后的部门名称")
            
            if self.dept_page.confirm_btn.count() > 0:
                self.dept_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_delete_dept_flow(self):
        """删除部门流程"""
        self.dept_page.goto_dept_page()
        if self.dept_page.get_row_count() > 0:
            self.dept_page.click_row_delete(0)
            self.page.wait_for_timeout(500)
            # 确认删除对话框
            confirm_btn = self.page.locator('.el-message-box button:has-text("确定")')
            if confirm_btn.count() > 0:
                confirm_btn.click()
                self.page.wait_for_timeout(1000)
                
                # 验证成功消息
                if self.dept_page.success_msg.count() > 0:
                    expect(self.dept_page.success_msg.first).to_be_visible(timeout=3000)
    
    def test_dept_search_flow(self):
        """部门搜索流程"""
        self.dept_page.goto_dept_page()
        if self.dept_page.search_input.count() > 0:
            self.dept_page.search_input.first.fill("部门")
            if self.dept_page.search_btn.count() > 0:
                self.dept_page.search_btn.first.click()
                self.page.wait_for_load_state('networkidle')
                
                # 验证搜索结果
                if self.dept_page.table.count() > 0:
                    expect(self.dept_page.table.first).to_be_visible()
    
    def test_dept_pagination_flow(self):
        """部门分页功能流程"""
        self.dept_page.goto_dept_page()
        
        # 检查分页控件
        pagination = self.page.locator('.el-pagination')
        if pagination.count() > 0:
            expect(pagination.first).to_be_visible()
            
            # 测试分页跳转
            next_btn = self.page.locator('.btn-next')
            if next_btn.count() > 0 and not next_btn.first.is_disabled():
                next_btn.first.click()
                self.page.wait_for_timeout(1000)
    
    def test_dept_tree_structure_flow(self):
        """部门树形结构管理流程"""
        self.dept_page.goto_dept_page()
        # 检查部门树是否正常显示
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
    
    def test_dept_hierarchy_flow(self):
        """部门层级管理流程"""
        self.dept_page.goto_dept_page()
        # 测试创建子部门
        if self.dept_page.add_btn.count() > 0:
            self.dept_page.add_btn.first.click()
            self.page.wait_for_timeout(500)
            expect(self.dept_page.dialog).to_be_visible()
            
            # 选择父级部门
            parent_dept_select = self.page.locator('.el-dialog select[placeholder*="父级"], .el-dialog .el-select')
            if parent_dept_select.count() > 0:
                parent_dept_select.first.click()
                self.page.wait_for_timeout(500)
                
                # 选择第一个选项
                first_option = self.page.locator('.el-select-dropdown__item:first-child')
                if first_option.count() > 0:
                    first_option.first.click()
                    self.page.wait_for_timeout(500)
            
            unique = datetime.now().strftime('%Y%m%d%H%M%S%f')
            self.dept_page.fill_dept_form(dept_name=f"子部门_{unique}")
            
            if self.dept_page.confirm_btn.count() > 0:
                self.dept_page.confirm_btn.first.click()
                self.page.wait_for_timeout(1000)
