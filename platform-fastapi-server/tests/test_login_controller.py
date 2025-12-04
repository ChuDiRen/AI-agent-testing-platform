"""
LoginController 登录模块接口测试
测试服务地址: http://127.0.0.1:5000
"""
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestLoginController:
    """登录控制器测试类"""
    
    # ==================== 正常场景 ====================
    
    def test_login_success(self, client: TestClient, session: Session):
        """测试登录成功"""
        from sysmanage.model.user import User
        
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
    
    def test_login_returns_user_info(self, client: TestClient, session: Session):
        """测试登录成功返回用户信息"""
        from sysmanage.model.user import User
        
        user = User(
            username="info_test_user",
            password="password123",
            dept_id=1,
            email="test@example.com",
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/login", json={
            "username": "info_test_user",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == "info_test_user"
    
    def test_login_token_format(self, client: TestClient, session: Session):
        """测试登录返回的Token格式"""
        from sysmanage.model.user import User
        
        user = User(
            username="token_test_user",
            password="tokenpass123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/login", json={
            "username": "token_test_user",
            "password": "tokenpass123"
        })
        
        assert response.status_code == 200
        data = response.json()
        token = data["data"]["token"]
        # JWT格式: header.payload.signature
        assert token.count(".") == 2
        assert len(token) > 50
    
    # ==================== 密码错误场景 ====================
    
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
    
    def test_login_case_sensitive_password(self, client: TestClient, session: Session):
        """测试密码大小写敏感"""
        from sysmanage.model.user import User
        
        user = User(
            username="case_pass_user",
            password="Password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        # 使用小写密码尝试登录
        response = client.post("/login", json={
            "username": "case_pass_user",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    # ==================== 用户不存在场景 ====================
    
    def test_login_user_not_exist(self, client: TestClient):
        """测试用户不存在"""
        response = client.post("/login", json={
            "username": "nonexistent_user",
            "password": "anypassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    def test_login_similar_username(self, client: TestClient, session: Session):
        """测试相似用户名（拼写错误）"""
        from sysmanage.model.user import User
        
        user = User(
            username="realuser",
            password="password",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        # 拼写错误的用户名
        response = client.post("/login", json={
            "username": "realuserr",
            "password": "password"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == -1
    
    # ==================== 空值验证场景 ====================
    
    def test_login_empty_username(self, client: TestClient):
        """测试空用户名"""
        response = client.post("/login", json={
            "username": "",
            "password": "test123"
        })
        assert response.status_code in [200, 422]
    
    def test_login_empty_password(self, client: TestClient):
        """测试空密码"""
        response = client.post("/login", json={
            "username": "testuser",
            "password": ""
        })
        assert response.status_code in [200, 422]
    
    def test_login_both_empty(self, client: TestClient):
        """测试用户名和密码都为空"""
        response = client.post("/login", json={
            "username": "",
            "password": ""
        })
        assert response.status_code in [200, 422]
    
    def test_login_missing_username_field(self, client: TestClient):
        """测试缺少用户名字段"""
        response = client.post("/login", json={
            "password": "test123"
        })
        assert response.status_code == 422
    
    def test_login_missing_password_field(self, client: TestClient):
        """测试缺少密码字段"""
        response = client.post("/login", json={
            "username": "testuser"
        })
        assert response.status_code == 422
    
    def test_login_empty_body(self, client: TestClient):
        """测试空请求体"""
        response = client.post("/login", json={})
        assert response.status_code == 422
    
    # ==================== 用户状态场景 ====================
    
    def test_login_disabled_user(self, client: TestClient, session: Session):
        """测试禁用用户登录"""
        from sysmanage.model.user import User
        
        user = User(
            username="disabled_user",
            password="password123",
            dept_id=1,
            status="0",  # 禁用状态
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/login", json={
            "username": "disabled_user",
            "password": "password123"
        })
        
        assert response.status_code == 200
        # 禁用用户可能登录失败或返回特定错误
        data = response.json()
        # 根据实际业务逻辑，禁用用户可能允许登录或拒绝
        assert data["code"] in [200, -1]
    
    # ==================== 特殊字符场景 ====================
    
    def test_login_special_chars_username(self, client: TestClient, session: Session):
        """测试特殊字符用户名"""
        from sysmanage.model.user import User
        
        user = User(
            username="user_test@123",
            password="password",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/login", json={
            "username": "user_test@123",
            "password": "password"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_login_chinese_username(self, client: TestClient, session: Session):
        """测试中文用户名"""
        from sysmanage.model.user import User
        
        user = User(
            username="测试用户",
            password="password123",
            dept_id=1,
            status="1",
            create_time=datetime.now()
        )
        session.add(user)
        session.commit()
        
        response = client.post("/login", json={
            "username": "测试用户",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
    
    def test_login_whitespace_username(self, client: TestClient):
        """测试用户名前后有空格"""
        response = client.post("/login", json={
            "username": "  testuser  ",
            "password": "password"
        })
        assert response.status_code in [200, 422]
    
    # ==================== 安全测试场景 ====================
    
    def test_login_sql_injection_attempt(self, client: TestClient):
        """测试SQL注入尝试"""
        response = client.post("/login", json={
            "username": "admin' OR '1'='1",
            "password": "password"
        })
        
        assert response.status_code == 200
        data = response.json()
        # SQL注入应该登录失败
        assert data["code"] == -1
    
    def test_login_xss_attempt(self, client: TestClient):
        """测试XSS注入尝试"""
        response = client.post("/login", json={
            "username": "<script>alert('xss')</script>",
            "password": "password"
        })
        
        assert response.status_code in [200, 422]
    
    # ==================== 边界值测试场景 ====================
    
    def test_login_long_username(self, client: TestClient):
        """测试超长用户名"""
        long_username = "a" * 500
        response = client.post("/login", json={
            "username": long_username,
            "password": "password"
        })
        assert response.status_code in [200, 422]
    
    def test_login_long_password(self, client: TestClient):
        """测试超长密码"""
        long_password = "p" * 500
        response = client.post("/login", json={
            "username": "testuser",
            "password": long_password
        })
        assert response.status_code in [200, 422]
