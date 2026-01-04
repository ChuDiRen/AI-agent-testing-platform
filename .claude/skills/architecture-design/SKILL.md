# 架构设计技能

## 触发条件
- 关键词：架构、架构设计、系统设计、微服务、分层、模块化
- 场景：当用户需要进行系统架构设计或重构时

## 核心规范

### 规范1：分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│              (Controllers / API Endpoints)               │
├─────────────────────────────────────────────────────────┤
│                    Application Layer                     │
│                (Services / Use Cases)                    │
├─────────────────────────────────────────────────────────┤
│                      Domain Layer                        │
│              (Entities / Domain Services)                │
├─────────────────────────────────────────────────────────┤
│                  Infrastructure Layer                    │
│         (Repositories / External Services)               │
└─────────────────────────────────────────────────────────┘
```

### 规范2：项目目录结构

```
project/
├── app/
│   ├── api/                    # API 层
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   └── tests.py
│   │   └── deps.py             # 依赖注入
│   │
│   ├── services/               # 业务服务层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── test_service.py
│   │
│   ├── models/                 # 数据模型层
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── test.py
│   │
│   ├── schemas/                # 请求/响应模式
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── test.py
│   │
│   ├── repositories/           # 数据访问层
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── user_repository.py
│   │
│   ├── core/                   # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       └── helpers.py
│
├── tests/                      # 测试目录
├── alembic/                    # 数据库迁移
├── main.py                     # 应用入口
└── requirements.txt
```

### 规范3：依赖注入模式

```python
# app/api/deps.py
from typing import Generator
from fastapi import Depends
from sqlmodel import Session

from app.core.database import engine
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(
    repo: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repo)

# app/api/v1/users.py
from fastapi import APIRouter, Depends
from app.api.deps import get_user_service
from app.services.user_service import UserService

router = APIRouter()

@router.get("/users")
async def list_users(
    service: UserService = Depends(get_user_service)
):
    return await service.list_users()
```

### 规范4：Repository 模式

```python
# app/repositories/base.py
from typing import Generic, TypeVar, Optional, List
from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model
    
    def get(self, id: int) -> Optional[ModelType]:
        return self.db.get(self.model, id)
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        statement = select(self.model).offset(skip).limit(limit)
        return self.db.exec(statement).all()
    
    def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: int) -> bool:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

# app/repositories/user_repository.py
from app.models.user import User
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)
    
    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.db.exec(statement).first()
```

### 规范5：Service 层设计

```python
# app/services/user_service.py
from typing import List, Optional
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundError, ConflictError

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository
    
    async def list_users(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserResponse]:
        users = self.repository.get_multi(skip=skip, limit=limit)
        return [UserResponse.from_orm(u) for u in users]
    
    async def get_user(self, user_id: int) -> UserResponse:
        user = self.repository.get(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return UserResponse.from_orm(user)
    
    async def create_user(self, user_in: UserCreate) -> UserResponse:
        # 检查邮箱是否已存在
        existing = self.repository.get_by_email(user_in.email)
        if existing:
            raise ConflictError("Email already registered")
        
        # 创建用户
        user_data = user_in.dict()
        user_data["password_hash"] = get_password_hash(user_data.pop("password"))
        user = self.repository.create(user_data)
        return UserResponse.from_orm(user)
```

### 规范6：事件驱动架构

```python
# app/events/event_bus.py
from typing import Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    name: str
    data: dict
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class EventBus:
    _handlers: Dict[str, List[Callable]] = {}
    
    @classmethod
    def subscribe(cls, event_name: str, handler: Callable):
        if event_name not in cls._handlers:
            cls._handlers[event_name] = []
        cls._handlers[event_name].append(handler)
    
    @classmethod
    async def publish(cls, event: Event):
        handlers = cls._handlers.get(event.name, [])
        for handler in handlers:
            await handler(event)

# 使用示例
async def on_user_created(event: Event):
    # 发送欢迎邮件
    await send_welcome_email(event.data["email"])

EventBus.subscribe("user.created", on_user_created)

# 在 Service 中发布事件
await EventBus.publish(Event(
    name="user.created",
    data={"user_id": user.id, "email": user.email}
))
```

### 规范7：配置管理

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AI Testing Platform"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # 数据库配置
    DATABASE_URL: str
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # JWT 配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

## 禁止事项
- ❌ 跨层直接调用（如 Controller 直接访问 Repository）
- ❌ 业务逻辑写在 Controller 层
- ❌ 循环依赖
- ❌ 硬编码配置
- ❌ 忽略异常处理

## 检查清单
- [ ] 是否遵循分层原则
- [ ] 是否使用依赖注入
- [ ] 是否有清晰的模块边界
- [ ] 是否有统一的异常处理
- [ ] 是否有配置管理
- [ ] 是否考虑了可扩展性
