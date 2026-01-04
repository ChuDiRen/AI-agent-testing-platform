# 单元测试技能

## 触发条件
- 关键词：单元测试、Unit Test、pytest、测试用例、mock、断言
- 场景：当用户需要编写单元测试时

## 核心规范

### 规范1：测试文件结构

```
tests/
├── __init__.py
├── conftest.py              # 全局 fixtures
├── unit/                    # 单元测试
│   ├── __init__.py
│   ├── test_services/       # Service 层测试
│   │   ├── test_user_service.py
│   │   └── test_test_service.py
│   ├── test_models/         # Model 层测试
│   │   └── test_user.py
│   └── test_utils/          # 工具函数测试
│       └── test_helpers.py
└── integration/             # 集成测试
    └── test_api/
```

### 规范2：测试命名规范

```python
# 测试文件命名：test_<模块名>.py
# test_user_service.py

# 测试类命名：Test<被测类名>
class TestUserService:
    
    # 测试方法命名：test_<方法名>_<场景>_<预期结果>
    def test_create_user_with_valid_data_returns_user(self):
        pass
    
    def test_create_user_with_duplicate_email_raises_error(self):
        pass
    
    def test_get_user_with_invalid_id_returns_none(self):
        pass
```

### 规范3：基础测试用例

```python
# tests/unit/test_services/test_user_service.py
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.user_service import UserService
from app.models.user import User
from app.core.exceptions import NotFoundError, ConflictError

class TestUserService:
    """用户服务单元测试"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock 用户仓库"""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_repository):
        """创建服务实例"""
        return UserService(repository=mock_repository)
    
    # 测试正常场景
    def test_get_user_returns_user_when_exists(self, service, mock_repository):
        """测试获取存在的用户"""
        # Arrange
        expected_user = User(id=1, username="test", email="test@example.com")
        mock_repository.get.return_value = expected_user
        
        # Act
        result = service.get_user(1)
        
        # Assert
        assert result.id == 1
        assert result.username == "test"
        mock_repository.get.assert_called_once_with(1)
    
    # 测试异常场景
    def test_get_user_raises_not_found_when_not_exists(self, service, mock_repository):
        """测试获取不存在的用户"""
        # Arrange
        mock_repository.get.return_value = None
        
        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            service.get_user(999)
        
        assert "not found" in str(exc_info.value).lower()
    
    # 测试边界条件
    @pytest.mark.parametrize("user_id", [0, -1, None])
    def test_get_user_with_invalid_id_raises_error(self, service, user_id):
        """测试无效用户ID"""
        with pytest.raises(ValueError):
            service.get_user(user_id)
```

### 规范4：异步测试

```python
import pytest
from unittest.mock import AsyncMock

class TestAsyncUserService:
    """异步服务测试"""
    
    @pytest.fixture
    def mock_async_repository(self):
        repo = AsyncMock()
        return repo
    
    @pytest.fixture
    def service(self, mock_async_repository):
        return UserService(repository=mock_async_repository)
    
    @pytest.mark.asyncio
    async def test_create_user_async(self, service, mock_async_repository):
        """测试异步创建用户"""
        # Arrange
        user_data = {"username": "test", "email": "test@example.com"}
        expected_user = User(id=1, **user_data)
        mock_async_repository.create.return_value = expected_user
        
        # Act
        result = await service.create_user(user_data)
        
        # Assert
        assert result.id == 1
        mock_async_repository.create.assert_awaited_once()
```

### 规范5：Mock 使用

```python
from unittest.mock import Mock, patch, MagicMock
import pytest

class TestWithMock:
    
    # Mock 对象方法
    def test_with_mock_method(self):
        mock_obj = Mock()
        mock_obj.method.return_value = "result"
        
        result = mock_obj.method("arg")
        
        assert result == "result"
        mock_obj.method.assert_called_with("arg")
    
    # Mock 异常
    def test_with_mock_exception(self):
        mock_obj = Mock()
        mock_obj.method.side_effect = ValueError("error")
        
        with pytest.raises(ValueError):
            mock_obj.method()
    
    # Mock 多次调用返回不同值
    def test_with_side_effect_list(self):
        mock_obj = Mock()
        mock_obj.method.side_effect = [1, 2, 3]
        
        assert mock_obj.method() == 1
        assert mock_obj.method() == 2
        assert mock_obj.method() == 3
    
    # Patch 装饰器
    @patch('app.services.user_service.send_email')
    def test_with_patch(self, mock_send_email):
        mock_send_email.return_value = True
        
        # 测试代码
        result = some_function_that_sends_email()
        
        mock_send_email.assert_called_once()
    
    # Patch 上下文管理器
    def test_with_patch_context(self):
        with patch('app.services.user_service.send_email') as mock_send:
            mock_send.return_value = True
            # 测试代码
```

### 规范6：Fixtures 使用

```python
# tests/conftest.py
import pytest
from sqlmodel import Session, create_engine, SQLModel
from app.models import User

@pytest.fixture(scope="session")
def engine():
    """创建测试数据库引擎"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def db(engine):
    """创建数据库会话"""
    with Session(engine) as session:
        yield session
        session.rollback()

@pytest.fixture
def sample_user(db):
    """创建示例用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def sample_users(db):
    """创建多个示例用户"""
    users = [
        User(username=f"user{i}", email=f"user{i}@example.com", password_hash="hashed")
        for i in range(5)
    ]
    db.add_all(users)
    db.commit()
    return users
```

### 规范7：参数化测试

```python
import pytest

class TestParameterized:
    
    @pytest.mark.parametrize("input,expected", [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("", ""),
        ("123", "123"),
    ])
    def test_uppercase(self, input, expected):
        """测试大写转换"""
        assert input.upper() == expected
    
    @pytest.mark.parametrize("email,is_valid", [
        ("test@example.com", True),
        ("test@example", False),
        ("test.com", False),
        ("", False),
        ("test@.com", False),
    ])
    def test_email_validation(self, email, is_valid):
        """测试邮箱验证"""
        result = validate_email(email)
        assert result == is_valid
    
    # 多参数组合
    @pytest.mark.parametrize("a", [1, 2])
    @pytest.mark.parametrize("b", [3, 4])
    def test_combination(self, a, b):
        """测试参数组合：(1,3), (1,4), (2,3), (2,4)"""
        assert a + b > 0
```

### 规范8：测试覆盖率

```bash
# 运行测试并生成覆盖率报告
pytest tests/ --cov=app --cov-report=html --cov-report=term

# 设置最低覆盖率要求
pytest tests/ --cov=app --cov-fail-under=80

# 查看未覆盖的代码行
pytest tests/ --cov=app --cov-report=term-missing
```

```ini
# pytest.ini 配置
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov=app --cov-report=term-missing
asyncio_mode = auto

[coverage:run]
source = app
omit = 
    app/migrations/*
    app/__init__.py
    
[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

## 禁止事项
- ❌ 测试依赖外部服务
- ❌ 测试之间有依赖关系
- ❌ 测试数据污染
- ❌ 只测试正常场景
- ❌ 测试代码没有断言

## 检查清单
- [ ] 是否覆盖了正常和异常场景
- [ ] 是否覆盖了边界条件
- [ ] 是否使用了 Mock 隔离依赖
- [ ] 测试是否可重复执行
- [ ] 覆盖率是否达标（>80%）
