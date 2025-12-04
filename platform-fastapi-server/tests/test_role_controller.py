"""
RoleController 角色管理模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestRoleController:
    """角色控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询角色"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="测试角色_page",
            remark="分页测试",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        
        response = client.post("/role/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤的分页查询"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="特殊角色名称",
            remark="过滤测试",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        
        response = client.post("/role/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "role_name": "特殊"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询角色"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="ID查询角色",
            remark="ID查询测试",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        session.refresh(role)
        
        response = client.get(f"/role/queryById?id={role.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["role_name"] == "ID查询角色"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的角色"""
        response = client.get("/role/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_insert_role(self, client: TestClient):
        """测试新增角色"""
        response = client.post("/role/insert", json={
            "role_name": "新增测试角色",
            "remark": "这是一个测试角色"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_insert_duplicate_role(self, client: TestClient, session: Session):
        """测试新增重复角色名"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="重复角色名",
            remark="测试",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        
        response = client.post("/role/insert", json={
            "role_name": "重复角色名",
            "remark": "尝试重复"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "已存在" in data["msg"]
    
    def test_update_role(self, client: TestClient, session: Session):
        """测试更新角色"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="待更新角色",
            remark="原始备注",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        session.refresh(role)
        
        response = client.put("/role/update", json={
            "id": role.id,
            "remark": "更新后的备注"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_role_not_found(self, client: TestClient):
        """测试更新不存在的角色"""
        response = client.put("/role/update", json={
            "id": 99999,
            "remark": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_role(self, client: TestClient, session: Session):
        """测试删除角色"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="待删除角色",
            remark="删除测试",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        session.refresh(role)
        
        response = client.delete(f"/role/delete?id={role.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_role_not_found(self, client: TestClient):
        """测试删除不存在的角色"""
        response = client.delete("/role/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_assign_menus(self, client: TestClient, session: Session):
        """测试为角色分配菜单"""
        from sysmanage.model.role import Role
        from sysmanage.model.menu import Menu
        
        role = Role(
            role_name="菜单分配角色",
            remark="测试",
            create_time=datetime.now()
        )
        session.add(role)
        
        menu = Menu(
            menu_name="测试菜单",
            parent_id=0,
            menu_type="C",
            create_time=datetime.now()
        )
        session.add(menu)
        session.commit()
        session.refresh(role)
        session.refresh(menu)
        
        response = client.post("/role/assignMenus", json={
            "id": role.id,
            "menu_ids": [menu.id]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_get_role_menus(self, client: TestClient, session: Session):
        """测试获取角色菜单"""
        from sysmanage.model.role import Role
        
        role = Role(
            role_name="获取菜单角色",
            remark="测试",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        session.refresh(role)
        
        response = client.get(f"/role/menus/{role.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
