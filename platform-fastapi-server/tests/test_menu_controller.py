"""
MenuController 菜单管理模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestMenuController:
    """菜单控制器测试类"""
    
    def test_get_tree(self, client: TestClient, session: Session):
        """测试获取菜单树"""
        from sysmanage.model.menu import Menu
        
        # 创建父菜单
        parent_menu = Menu(
            menu_name="父菜单",
            parent_id=0,
            menu_type="M",
            order_num=1,
            create_time=datetime.now()
        )
        session.add(parent_menu)
        session.commit()
        session.refresh(parent_menu)
        
        # 创建子菜单
        child_menu = Menu(
            menu_name="子菜单",
            parent_id=parent_menu.id,
            menu_type="C",
            order_num=1,
            create_time=datetime.now()
        )
        session.add(child_menu)
        session.commit()
        
        response = client.get("/menu/tree")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "data" in data
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询菜单"""
        from sysmanage.model.menu import Menu
        
        menu = Menu(
            menu_name="ID查询菜单",
            parent_id=0,
            menu_type="C",
            path="/test",
            create_time=datetime.now()
        )
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        response = client.get(f"/menu/queryById?id={menu.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["menu_name"] == "ID查询菜单"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的菜单"""
        response = client.get("/menu/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_insert_menu(self, client: TestClient):
        """测试新增菜单"""
        response = client.post("/menu/insert", json={
            "menu_name": "新增测试菜单",
            "parent_id": 0,
            "menu_type": "C",
            "path": "/new-menu",
            "component": "NewMenu",
            "order_num": 1
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_menu(self, client: TestClient, session: Session):
        """测试更新菜单"""
        from sysmanage.model.menu import Menu
        
        menu = Menu(
            menu_name="待更新菜单",
            parent_id=0,
            menu_type="C",
            create_time=datetime.now()
        )
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        response = client.put("/menu/update", json={
            "id": menu.id,
            "menu_name": "更新后的菜单名",
            "path": "/updated-path"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_menu_not_found(self, client: TestClient):
        """测试更新不存在的菜单"""
        response = client.put("/menu/update", json={
            "id": 99999,
            "menu_name": "测试"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_delete_menu(self, client: TestClient, session: Session):
        """测试删除菜单"""
        from sysmanage.model.menu import Menu
        
        menu = Menu(
            menu_name="待删除菜单",
            parent_id=0,
            menu_type="C",
            create_time=datetime.now()
        )
        session.add(menu)
        session.commit()
        session.refresh(menu)
        
        response = client.delete(f"/menu/delete?id={menu.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_delete_menu_with_children(self, client: TestClient, session: Session):
        """测试删除有子菜单的菜单"""
        from sysmanage.model.menu import Menu
        
        parent = Menu(
            menu_name="有子菜单的父菜单",
            parent_id=0,
            menu_type="M",
            create_time=datetime.now()
        )
        session.add(parent)
        session.commit()
        session.refresh(parent)
        
        child = Menu(
            menu_name="子菜单",
            parent_id=parent.id,
            menu_type="C",
            create_time=datetime.now()
        )
        session.add(child)
        session.commit()
        
        response = client.delete(f"/menu/delete?id={parent.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "子菜单" in data["msg"]
    
    def test_get_user_menus(self, client: TestClient, session: Session):
        """测试获取用户菜单"""
        from sysmanage.model.user import User
        
        user = User(
            username="menu_test_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        response = client.get(f"/menu/user/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
