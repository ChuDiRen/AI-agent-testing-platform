"""
LoginController 登录模块单元测试
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestLoginController:
    """登录控制器测试类"""
    
    def test_login_success(self, client: TestClient, session: Session):
        """测试登录成功"""
        from sysmanage.model.user import User
        
        # 创建测试用户
        user = User(
            username="login_test_user",
            password="test123456",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/login", json={
            "username": "login_test_user",
            "password": "test123456"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "token" in data["data"]
        assert data["msg"] == "登录成功"
    
    def test_login_wrong_password(self, client: TestClient, session: Session):
        """测试密码错误"""
        from sysmanage.model.user import User
        
        user = User(
            username="wrong_pass_user",
            password="correct_password",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/login", json={
            "username": "wrong_pass_user",
            "password": "wrong_password"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
        assert "错误" in data["msg"]
    
    def test_login_user_not_exist(self, client: TestClient):
        """测试用户不存在"""
        response = client.post("/login", json={
            "username": "nonexistent_user",
            "password": "anypassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_login_empty_username(self, client: TestClient):
        """测试空用户名"""
        response = client.post("/login", json={
            "username": "",
            "password": "test123"
        })
        # 应该返回验证错误或登录失败
        assert response.status_code in [200, 422]
    
    def test_login_empty_password(self, client: TestClient):
        """测试空密码"""
        response = client.post("/login", json={
            "username": "testuser",
            "password": ""
        })
        assert response.status_code in [200, 422]


class TestLoginSchema:
    """登录Schema测试"""
    
    def test_login_request_valid(self):
        """测试有效的登录请求"""
        from login.schemas.login_schema import LoginRequest
        
        request = LoginRequest(username="testuser", password="testpass")
        assert request.username == "testuser"
        assert request.password == "testpass"
    
    def test_login_request_model_dump(self):
        """测试模型转字典"""
        from login.schemas.login_schema import LoginRequest
        
        request = LoginRequest(username="user1", password="pass1")
        data = request.model_dump()
        assert data["username"] == "user1"
        assert data["password"] == "pass1"
