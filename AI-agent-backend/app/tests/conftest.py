"""
Pytest配置文件
定义测试夹具和配置
"""

import os
import sys
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app
from app.db.base import Base
from app.db.session import get_db
from app.entity.user import User
from app.repository.user_repository import UserRepository
from app.service.user_service import UserService
from app.core.security import create_token_pair

# 测试数据库URL
TEST_DATABASE_URL = "sqlite:///./test.db"

# 创建测试数据库引擎
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建测试会话工厂
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def test_db_engine():
    """
    测试数据库引擎夹具
    """
    # 创建测试数据库表
    Base.metadata.create_all(bind=test_engine)
    
    yield test_engine
    
    # 清理测试数据库
    Base.metadata.drop_all(bind=test_engine)
    
    # 删除测试数据库文件
    if os.path.exists("./test.db"):
        os.remove("./test.db")


@pytest.fixture
def test_db(test_db_engine) -> Generator[Session, None, None]:
    """
    测试数据库会话夹具
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """
    测试客户端夹具
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db: Session) -> User:
    """
    测试用户夹具
    """
    repository = UserRepository(test_db)
    service = UserService(repository)
    
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User",
        "is_active": True,
        "is_verified": True
    }
    
    user = service.create(user_data)
    test_db.commit()
    
    return user


@pytest.fixture
def test_superuser(test_db: Session) -> User:
    """
    测试超级用户夹具
    """
    repository = UserRepository(test_db)
    service = UserService(repository)
    
    user_data = {
        "username": "testsuperuser",
        "email": "superuser@example.com",
        "password": "superpassword123",
        "full_name": "Test Superuser",
        "is_active": True,
        "is_verified": True,
        "is_superuser": True
    }
    
    user = service.create(user_data)
    test_db.commit()
    
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """
    认证头夹具
    """
    tokens = create_token_pair(test_user.id)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
def superuser_auth_headers(test_superuser: User) -> dict:
    """
    超级用户认证头夹具
    """
    tokens = create_token_pair(test_superuser.id)
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest.fixture
def sample_user_data() -> dict:
    """
    示例用户数据夹具
    """
    return {
        "username": "sampleuser",
        "email": "sample@example.com",
        "password": "samplepassword123",
        "full_name": "Sample User",
        "bio": "This is a sample user for testing"
    }


@pytest.fixture
def sample_indicator_parameter_data() -> dict:
    """
    示例指标参数数据夹具
    """
    return {
        "indicator_name": "test_indicator",
        "sequence_number": 1,
        "parameter_name": "test_parameter",
        "parameter_value": "test_value",
        "parameter_type": "string",
        "parameter_description": "Test parameter description",
        "is_required": 1,
        "default_value": "default_test_value",
        "parameter_group": "test_group",
        "sort_order": 1
    }


@pytest.fixture
def sample_rbac_user_data() -> dict:
    """
    示例RBAC用户数据夹具
    """
    return {
        "username": "rbacuser",
        "password": "123456",
        "email": "rbac@example.com",
        "mobile": "13800138000",
        "ssex": "0",
        "description": "RBAC测试用户"
    }


@pytest.fixture
def sample_role_data() -> dict:
    """
    示例角色数据夹具
    """
    return {
        "role_name": "测试角色",
        "remark": "这是一个测试角色"
    }


@pytest.fixture
def sample_menu_data() -> dict:
    """
    示例菜单数据夹具
    """
    return {
        "parent_id": 0,
        "menu_name": "测试菜单",
        "menu_type": "0",
        "path": "/test",
        "component": "Test",
        "perms": "test:view",
        "icon": "el-icon-test",
        "order_num": 1
    }


@pytest.fixture
def sample_department_data() -> dict:
    """
    示例部门数据夹具
    """
    return {
        "parent_id": 0,
        "dept_name": "测试部门",
        "order_num": 1
    }


@pytest.fixture
def db_session(test_db: Session) -> Session:
    """
    数据库会话别名夹具（为了兼容RBAC测试）
    """
    return test_db


@pytest.fixture(autouse=True)
def clear_cache():
    """
    清理缓存夹具（自动使用）
    """
    # 在每个测试前清理缓存
    from app.utils.redis_client import redis_client
    if redis_client.is_available():
        redis_client.flush_all()
    
    yield
    
    # 在每个测试后清理缓存
    if redis_client.is_available():
        redis_client.flush_all()


@pytest.fixture
def mock_redis(monkeypatch):
    """
    模拟Redis夹具
    """
    class MockRedisClient:
        def __init__(self):
            self.data = {}
        
        def is_available(self):
            return True
        
        def set(self, key, value, ttl=None):
            self.data[key] = value
            return True
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def delete(self, key):
            return self.data.pop(key, None) is not None
        
        def exists(self, key):
            return key in self.data
        
        def flush_all(self):
            self.data.clear()
            return True
    
    mock_client = MockRedisClient()
    monkeypatch.setattr("app.utils.redis_client.redis_client", mock_client)
    
    return mock_client


# 测试标记
pytest_plugins = []

# 测试配置
def pytest_configure(config):
    """
    Pytest配置
    """
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as requiring authentication"
    )


# 测试收集配置
def pytest_collection_modifyitems(config, items):
    """
    修改测试收集项
    """
    for item in items:
        # 为所有测试添加单元测试标记（如果没有其他标记）
        if not any(mark.name in ["integration", "slow"] for mark in item.iter_markers()):
            item.add_marker(pytest.mark.unit)


# 测试报告配置
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    设置测试环境
    """
    # 设置测试环境变量
    os.environ["ENVIRONMENT"] = "testing"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # 清理测试环境
    pass
