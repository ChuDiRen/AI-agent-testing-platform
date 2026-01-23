"""
Pytest 配置文件

提供测试 fixtures 和配置
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool
from faker import Faker

from app.main import app
from app.core.security import get_password_hash
from app.models import user, role, department


# Faker 实例
fake = Faker()


@pytest.fixture(scope="session")
def test_engine():
    """创建测试数据库引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="session")
def test_db(test_engine):
    """创建测试数据库表"""
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def test_session(test_db):
    """创建测试会话"""
    session = Session(test_db)
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(test_db):
    """创建测试客户端"""
    def override_get_session():
        try:
            yield Session(test_db)
        finally:
            pass

    from app.core.deps import get_session
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_admin_user(test_session):
    """创建测试管理员用户"""
    # 创建角色
    admin_role = role.Role(
        name="系统管理员",
        code="superadmin",
        description="测试管理员角色",
        status=1,
        sort=1,
        is_system=True
    )
    test_session.add(admin_role)
    test_session.flush()

    # 创建用户
    admin_user = user.User(
        username="admin_test",
        password_hash=get_password_hash("admin123"),
        email=fake.email(),
        full_name=fake.name(),
        is_superuser=True,
        is_active=True,
        role_id=admin_role.id,
        status=1
    )
    test_session.add(admin_user)
    test_session.commit()

    return admin_user


@pytest.fixture
def test_regular_user(test_session):
    """创建测试普通用户"""
    # 创建角色
    user_role = role.Role(
        name="普通用户",
        code="user",
        description="测试普通用户角色",
        status=1,
        sort=2,
        is_system=False
    )
    test_session.add(user_role)
    test_session.flush()

    # 创建用户
    regular_user = user.User(
        username=fake.user_name(),
        password_hash=get_password_hash("user123"),
        email=fake.email(),
        full_name=fake.name(),
        is_superuser=False,
        is_active=True,
        role_id=user_role.id,
        status=1
    )
    test_session.add(regular_user)
    test_session.commit()

    return regular_user


@pytest.fixture
def test_department(test_session):
    """创建测试部门"""
    dept = department.Department(
        name=fake.company(),
        code=fake.slug(),
        description="测试部门",
        status=1,
        sort=1
    )
    test_session.add(dept)
    test_session.commit()

    return dept


@pytest.fixture
def admin_auth_headers(client, test_admin_user):
    """获取管理员认证头"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin_test",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_auth_headers(client, test_regular_user):
    """获取普通用户认证头"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_regular_user.username,
            "password": "user123"
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def temp_upload_file(tmp_path):
    """创建临时上传文件"""
    import io

    file_path = tmp_path / "test_document.txt"
    file_path.write_text("这是一个测试文档的内容。")

    return file_path


@pytest.fixture
def sample_document_data():
    """生成示例文档数据"""
    return {
        "title": fake.sentence(),
        "description": fake.text(),
        "permission": "private",
        "tags": ["技术", "文档"]
    }


@pytest.fixture
def sample_chat_message():
    """生成示例聊天消息"""
    return {
        "message": fake.sentence(),
        "conversation_id": f"conv_{fake.uuid4()}"
    }


# Pytest 配置
def pytest_configure(config):
    """Pytest 配置钩子"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
