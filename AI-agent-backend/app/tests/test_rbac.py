# Copyright (c) 2025 左岚. All rights reserved.
"""
RBAC功能测试用例
测试角色、菜单、部门、用户等RBAC相关功能
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.service.department_service import DepartmentService
from app.service.menu_service import MenuService
from app.service.rbac_user_service import RBACUserService
from app.service.role_service import RoleService


class TestRoleService:
    """角色服务测试"""

    def test_create_role(self, db_session: Session):
        """测试创建角色"""
        role_service = RoleService(db_session)
        
        # 创建角色
        role = role_service.create_role("测试角色", "这是一个测试角色")
        
        assert role is not None
        assert role.ROLE_NAME == "测试角色"
        assert role.REMARK == "这是一个测试角色"
        assert role.ROLE_ID is not None

    def test_create_duplicate_role(self, db_session: Session):
        """测试创建重复角色名称"""
        role_service = RoleService(db_session)
        
        # 创建第一个角色
        role_service.create_role("重复角色", "第一个角色")
        
        # 尝试创建同名角色，应该抛出异常
        with pytest.raises(ValueError, match="角色名称 '重复角色' 已存在"):
            role_service.create_role("重复角色", "第二个角色")

    def test_get_role_by_id(self, db_session: Session):
        """测试根据ID获取角色"""
        role_service = RoleService(db_session)
        
        # 创建角色
        created_role = role_service.create_role("查询角色", "用于查询测试")
        
        # 根据ID查询
        found_role = role_service.get_role_by_id(created_role.ROLE_ID)
        
        assert found_role is not None
        assert found_role.ROLE_ID == created_role.ROLE_ID
        assert found_role.ROLE_NAME == "查询角色"

    def test_update_role(self, db_session: Session):
        """测试更新角色"""
        role_service = RoleService(db_session)
        
        # 创建角色
        role = role_service.create_role("原始角色", "原始描述")
        
        # 更新角色
        updated_role = role_service.update_role(
            role.ROLE_ID, 
            role_name="更新角色", 
            remark="更新描述"
        )
        
        assert updated_role is not None
        assert updated_role.ROLE_NAME == "更新角色"
        assert updated_role.REMARK == "更新描述"

    def test_delete_role(self, db_session: Session):
        """测试删除角色"""
        role_service = RoleService(db_session)
        
        # 创建角色
        role = role_service.create_role("待删除角色", "将被删除")
        
        # 删除角色
        success = role_service.delete_role(role.ROLE_ID)
        
        assert success is True
        
        # 验证角色已被删除
        deleted_role = role_service.get_role_by_id(role.ROLE_ID)
        assert deleted_role is None


class TestMenuService:
    """菜单服务测试"""

    def test_create_menu(self, db_session: Session):
        """测试创建菜单"""
        menu_service = MenuService(db_session)
        
        # 创建顶级菜单
        menu = menu_service.create_menu(
            parent_id=0,
            menu_name="系统管理",
            menu_type="0",
            path="/system",
            component="Layout",
            icon="el-icon-set-up",
            order_num=1
        )
        
        assert menu is not None
        assert menu.MENU_NAME == "系统管理"
        assert menu.TYPE == "0"
        assert menu.is_menu() is True
        assert menu.is_top_level() is True

    def test_create_button(self, db_session: Session):
        """测试创建按钮"""
        menu_service = MenuService(db_session)
        
        # 先创建父菜单
        parent_menu = menu_service.create_menu(
            parent_id=0,
            menu_name="用户管理",
            menu_type="0",
            path="/user",
            component="user/Index"
        )
        
        # 创建按钮
        button = menu_service.create_menu(
            parent_id=parent_menu.MENU_ID,
            menu_name="新增用户",
            menu_type="1",
            perms="user:add"
        )
        
        assert button is not None
        assert button.MENU_NAME == "新增用户"
        assert button.TYPE == "1"
        assert button.is_button() is True
        assert button.PERMS == "user:add"

    def test_get_menu_tree(self, db_session: Session):
        """测试获取菜单树"""
        menu_service = MenuService(db_session)
        
        # 创建菜单层级结构
        system_menu = menu_service.create_menu(0, "系统管理", "0", "/system", order_num=1)
        user_menu = menu_service.create_menu(system_menu.MENU_ID, "用户管理", "0", "/system/user", order_num=1)
        add_button = menu_service.create_menu(user_menu.MENU_ID, "新增用户", "1", perms="user:add")
        
        # 获取菜单树
        tree = menu_service.get_menu_tree()
        
        assert len(tree) >= 1
        # 验证树形结构
        system_node = next((node for node in tree if node["menu_name"] == "系统管理"), None)
        assert system_node is not None
        assert len(system_node["children"]) >= 1


class TestDepartmentService:
    """部门服务测试"""

    def test_create_department(self, db_session: Session):
        """测试创建部门"""
        dept_service = DepartmentService(db_session)
        
        # 创建顶级部门
        dept = dept_service.create_department(
            parent_id=0,
            dept_name="技术部",
            order_num=1
        )
        
        assert dept is not None
        assert dept.DEPT_NAME == "技术部"
        assert dept.is_top_level() is True

    def test_create_sub_department(self, db_session: Session):
        """测试创建子部门"""
        dept_service = DepartmentService(db_session)
        
        # 创建父部门
        parent_dept = dept_service.create_department(0, "技术部", 1)
        
        # 创建子部门
        sub_dept = dept_service.create_department(
            parent_id=parent_dept.DEPT_ID,
            dept_name="开发组",
            order_num=1
        )
        
        assert sub_dept is not None
        assert sub_dept.DEPT_NAME == "开发组"
        assert sub_dept.PARENT_ID == parent_dept.DEPT_ID
        assert sub_dept.is_top_level() is False

    def test_get_department_tree(self, db_session: Session):
        """测试获取部门树"""
        dept_service = DepartmentService(db_session)
        
        # 创建部门层级结构
        tech_dept = dept_service.create_department(0, "技术部", 1)
        dev_group = dept_service.create_department(tech_dept.DEPT_ID, "开发组", 1)
        test_group = dept_service.create_department(tech_dept.DEPT_ID, "测试组", 2)
        
        # 获取部门树
        tree = dept_service.get_department_tree()
        
        assert len(tree) >= 1
        # 验证树形结构
        tech_node = next((node for node in tree if node["dept_name"] == "技术部"), None)
        assert tech_node is not None
        assert len(tech_node["children"]) >= 2


class TestRBACUserService:
    """RBAC用户服务测试"""

    def test_create_user(self, db_session: Session):
        """测试创建用户"""
        user_service = RBACUserService(db_session)
        
        # 创建用户
        user = user_service.create_user(
            username="testuser",
            password="123456",
            email="test@example.com",
            mobile="13800138000",
            ssex="0",
            description="测试用户"
        )
        
        assert user is not None
        assert user.USERNAME == "testuser"
        assert user.EMAIL == "test@example.com"
        assert user.is_active() is True

    def test_authenticate_user(self, db_session: Session):
        """测试用户认证"""
        user_service = RBACUserService(db_session)
        
        # 创建用户
        user_service.create_user("authuser", "password123", "auth@example.com")
        
        # 正确认证
        authenticated_user = user_service.authenticate_user("authuser", "password123")
        assert authenticated_user is not None
        assert authenticated_user.USERNAME == "authuser"
        
        # 错误密码
        failed_auth = user_service.authenticate_user("authuser", "wrongpassword")
        assert failed_auth is None

    def test_assign_roles_to_user(self, db_session: Session):
        """测试为用户分配角色"""
        user_service = RBACUserService(db_session)
        role_service = RoleService(db_session)
        
        # 创建用户和角色
        user = user_service.create_user("roleuser", "123456")
        role1 = role_service.create_role("角色1", "第一个角色")
        role2 = role_service.create_role("角色2", "第二个角色")
        
        # 分配角色
        success = user_service.assign_roles_to_user(user.USER_ID, [role1.ROLE_ID, role2.ROLE_ID])
        assert success is True
        
        # 验证角色分配
        user_roles = user_service.get_user_roles(user.USER_ID)
        assert len(user_roles) == 2
        role_names = [role.ROLE_NAME for role in user_roles]
        assert "角色1" in role_names
        assert "角色2" in role_names


class TestRBACIntegration:
    """RBAC集成测试"""

    def test_complete_rbac_flow(self, db_session: Session):
        """测试完整的RBAC流程"""
        # 初始化服务
        user_service = RBACUserService(db_session)
        role_service = RoleService(db_session)
        menu_service = MenuService(db_session)
        dept_service = DepartmentService(db_session)
        
        # 1. 创建部门
        dept = dept_service.create_department(0, "测试部门", 1)
        
        # 2. 创建角色
        role = role_service.create_role("测试角色", "用于集成测试")
        
        # 3. 创建菜单和权限
        system_menu = menu_service.create_menu(0, "系统管理", "0", "/system")
        user_menu = menu_service.create_menu(system_menu.MENU_ID, "用户管理", "0", "/system/user", perms="user:view")
        add_button = menu_service.create_menu(user_menu.MENU_ID, "新增用户", "1", perms="user:add")
        
        # 4. 为角色分配菜单权限
        menu_ids = [system_menu.MENU_ID, user_menu.MENU_ID, add_button.MENU_ID]
        role_service.assign_menus_to_role(role.ROLE_ID, menu_ids)
        
        # 5. 创建用户
        user = user_service.create_user(
            username="integrationuser",
            password="123456",
            email="integration@example.com",
            dept_id=dept.DEPT_ID
        )
        
        # 6. 为用户分配角色
        user_service.assign_roles_to_user(user.USER_ID, [role.ROLE_ID])
        
        # 7. 验证用户权限
        permissions = user_service.get_user_permissions(user.USER_ID)
        assert "user:view" in permissions
        assert "user:add" in permissions
        
        # 8. 验证权限检查
        assert user_service.has_permission(user.USER_ID, "user:view") is True
        assert user_service.has_permission(user.USER_ID, "user:add") is True
        assert user_service.has_permission(user.USER_ID, "user:delete") is False
        
        # 9. 验证用户菜单
        user_menus = menu_service.get_user_menus(user.USER_ID)
        assert len(user_menus) == 3
        menu_names = [menu.MENU_NAME for menu in user_menus]
        assert "系统管理" in menu_names
        assert "用户管理" in menu_names
        assert "新增用户" in menu_names
