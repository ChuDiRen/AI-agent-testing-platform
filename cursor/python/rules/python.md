你是一个资深的Python专家，请在开发中遵循如下规则：
- 严格遵循 **SOLID、DRY、KISS、YAGNI** 原则
- 遵循 **OWASP 安全最佳实践**（如输入验证、SQL注入防护）
- 采用 **分层架构设计**，确保职责分离
- 代码变更需通过 **单元测试覆盖**（测试覆盖率 ≥ 80%）

---

## 二、技术栈规范
### 技术栈要求
- **框架**：FastAPI + Python 3.9+
- **依赖**：
  - 核心：FastAPI, SQLAlchemy, Pydantic, Alembic
  - 数据库：asyncpg (PostgreSQL) 或其他异步数据库驱动
  - 其他：uvicorn, python-multipart, python-jose[cryptography]

---

## 三、应用逻辑设计规范
### 1. 分层架构原则
| 层级          | 职责                                                                 | 约束条件                                                                 |
|---------------|----------------------------------------------------------------------|--------------------------------------------------------------------------|
| **API**       | 处理 HTTP 请求与响应，定义 API 接口                                 | - 禁止直接操作数据库<br>- 必须通过 Service 层调用                          |
| **Service**   | 业务逻辑实现，事务管理，数据校验                                   | - 必须通过 Repository 访问数据库<br>- 返回 Pydantic 模型而非 SQLAlchemy 模型 |
| **Repository** | 数据持久化操作，定义数据库查询逻辑                                 | - 使用 SQLAlchemy 异步操作<br>- 避免 N+1 查询问题                          |
| **Model**     | 数据库表结构映射对象和数据验证模型                                 | - SQLAlchemy 模型仅用于数据库交互<br>- Pydantic 模型用于 API 输入输出      |

---

## 四、核心代码规范
### 1. SQLAlchemy 模型规范
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database.base import BaseModel

class UserModel(BaseModel):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关联关系使用懒加载
    profile = relationship("UserProfileModel", back_populates="user", lazy="select")
```

### 2. Pydantic 模型规范
```python
from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    """用户创建模型"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        return v

class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

### 3. Repository层规范
```python
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database.user import UserModel
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[UserModel]):
    def __init__(self, db: AsyncSession):
        super().__init__(UserModel, db)
    
    async def get_by_username(self, username: str) -> Optional[UserModel]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self) -> List[UserModel]:
        """获取活跃用户列表"""
        result = await self.db.execute(
            select(UserModel).where(UserModel.is_active == True)
        )
        return result.scalars().all()
```

### 4. Service层规范
```python
from typing import Optional
from app.models.schemas.user import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository
from app.core.exceptions import BusinessException
from app.utils.security import get_password_hash

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """创建用户"""
        # 业务验证
        existing_user = await self.user_repo.get_by_username(user_data.username)
        if existing_user:
            raise BusinessException("用户名已存在")
        
        # 密码加密
        hashed_password = get_password_hash(user_data.password)
        
        # 创建用户
        user_dict = user_data.dict(exclude={'password'})
        user_dict['hashed_password'] = hashed_password
        
        user = await self.user_repo.create(user_dict)
        return UserResponse.from_orm(user)
```

### 5. API层规范
```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas.user import UserCreate, UserResponse
from app.models.schemas.common import APIResponse
from app.services.user_service import UserService
from app.api.deps import get_user_service

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("/", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
) -> APIResponse[UserResponse]:
    """创建用户"""
    try:
        user = await user_service.create_user(user_data)
        return APIResponse(message="用户创建成功", data=user)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 五、异步编程规范
### 1. 数据库异步操作
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 异步引擎配置
engine = create_async_engine(
    "postgresql+asyncpg://user:password@localhost/dbname",
    echo=True,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 2. 并发处理
```python
import asyncio
from typing import List

async def process_users_batch(user_ids: List[int]) -> List[UserResponse]:
    """批量处理用户"""
    tasks = [process_single_user(user_id) for user_id in user_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 过滤异常结果
    valid_results = [r for r in results if not isinstance(r, Exception)]
    return valid_results
```

---

## 六、安全与性能规范
1. **输入校验**：
   - 使用 Pydantic 模型进行数据验证
   - 使用参数化查询防止 SQL 注入
2. **密码安全**：
   - 使用 bcrypt 或 Argon2 进行密码哈希
   - 实现 JWT 令牌认证
3. **性能优化**：
   - 使用异步操作避免阻塞
   - 实现数据库连接池
   - 避免 N+1 查询问题

---

## 七、代码风格规范
1. **命名规范**：
   - 类名：`PascalCase`（如 `UserService`）
   - 函数/变量名：`snake_case`（如 `create_user`）
   - 常量：`UPPER_SNAKE_CASE`（如 `MAX_LOGIN_ATTEMPTS`）
2. **类型注解**：
   - 所有函数必须添加类型注解
   - 使用 `typing` 模块的类型提示
3. **文档字符串**：
   - 使用 Google 风格的 docstring
   - 所有公共方法必须添加文档字符串

---

## 八、测试规范
### 1. 测试结构
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
    assert response.status_code == 201
    assert response.json()["data"]["username"] == "testuser"
```

---

## 九、部署规范
1. **环境配置**：
   - 使用 `.env` 文件管理环境变量
   - 生产环境禁用调试模式
2. **容器化**：
   - 使用 Docker 进行应用容器化
   - 多阶段构建优化镜像大小
3. **监控日志**：
   - 使用结构化日志记录
   - 集成应用性能监控（APM）

---

## 十、扩展性设计规范
1. **依赖注入**：
   - 使用 FastAPI 的依赖注入系统
   - 接口与实现分离
2. **配置管理**：
   - 使用 Pydantic Settings 管理配置
   - 支持多环境配置
3. **API 版本管理**：
   - 使用路径版本控制（如 `/api/v1/`）
   - 保持向后兼容性
