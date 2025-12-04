"""
UserController 用户管理模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestUserController:
    """用户控制器测试类"""
    
    def test_query_by_page(self, client: TestClient, session: Session):
        """测试分页查询用户"""
        from sysmanage.model.user import User
        
        # 创建测试用户
        for i in range(3):
            user = User(
                username=f"page_test_user_{i}",
                password="test123",
                dept_id=1,
                status="1",
                create_time=datetime.now()
            )
            session.add(user)
        session.commit()
        
        response = client.post("/user/queryByPage", json={
            "page": 1,
            "pageSize": 10
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["total"] >= 3
    
    def test_query_by_page_with_filter(self, client: TestClient, session: Session):
        """测试带过滤条件的分页查询"""
        from sysmanage.model.user import User
        
        user = User(
            username="filter_test_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/user/queryByPage", json={
            "page": 1,
            "pageSize": 10,
            "username": "filter_test"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_query_by_id(self, client: TestClient, session: Session):
        """测试根据ID查询用户"""
        from sysmanage.model.user import User
        
        user = User(
            username="id_query_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        response = client.get(f"/user/queryById?id={user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == "id_query_user"
    
    def test_query_by_id_not_found(self, client: TestClient):
        """测试查询不存在的用户"""
        response = client.get("/user/queryById?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert "没有数据" in data.get("msg", "")
    
    def test_insert_user(self, client: TestClient):
        """测试新增用户"""
        response = client.post("/user/insert", json={
            "username": "new_test_user",
            "password": "newpass123",
            "dept_id": 1,
            "email": "test@example.com",
            "status": "1"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "id" in data["data"]
    
    def test_update_user(self, client: TestClient, session: Session):
        """测试更新用户"""
        from sysmanage.model.user import User
        
        user = User(
            username="update_test_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        response = client.put("/user/update", json={
            "id": user.id,
            "email": "updated@example.com",
            "mobile": "13800138000"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_update_user_not_found(self, client: TestClient):
        """测试更新不存在的用户"""
        response = client.put("/user/update", json={
            "id": 99999,
            "email": "test@example.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "不存在" in data["msg"]
    
    def test_delete_user(self, client: TestClient, session: Session):
        """测试删除用户"""
        from sysmanage.model.user import User
        
        user = User(
            username="delete_test_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        response = client.delete(f"/user/delete?id={user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "成功" in data["msg"]
    
    def test_delete_user_not_found(self, client: TestClient):
        """测试删除不存在的用户"""
        response = client.delete("/user/delete?id=99999")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_assign_roles(self, client: TestClient, session: Session):
        """测试为用户分配角色"""
        from sysmanage.model.user import User
        from sysmanage.model.role import Role
        
        user = User(
            username="role_assign_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        
        role = Role(
            role_name="测试角色",
            remark="用于测试",
            create_time=datetime.now()
        )
        session.add(role)
        session.commit()
        session.refresh(user)
        session.refresh(role)
        
        response = client.post("/user/assignRoles", json={
            "id": user.id,
            "role_ids": [role.id]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_get_user_roles(self, client: TestClient, session: Session):
        """测试获取用户角色"""
        from sysmanage.model.user import User
        
        user = User(
            username="get_roles_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        response = client.get(f"/user/roles/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_update_status(self, client: TestClient, session: Session):
        """测试更新用户状态"""
        from sysmanage.model.user import User
        
        user = User(
            username="status_test_user",
            password="test123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # 锁定用户
        response = client.put("/user/updateStatus", json={
            "id": user.id,
            "status": "0"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "锁定" in data["msg"]
