# 后端注解/装饰器技能

## 触发条件
- 关键词：注解、装饰器、Depends、Decorator、依赖注入、FastAPI
- 场景：当用户需要使用 FastAPI 装饰器和依赖注入时

## 核心规范

### 规范1：FastAPI 常用装饰器

| 装饰器 | 用途 | 示例 |
|--------|------|------|
| `@router.get()` | GET 请求 | `@router.get("/list")` |
| `@router.post()` | POST 请求 | `@router.post("/create")` |
| `@router.put()` | PUT 请求 | `@router.put("/update")` |
| `@router.delete()` | DELETE 请求 | `@router.delete("/delete")` |

### 规范2：依赖注入 (Depends)

```python
from fastapi import Depends, Query
from sqlmodel import Session
from core.database import get_session
from core.dependencies import check_permission

# 数据库会话注入
@router.get("/list")
async def get_list(session: Session = Depends(get_session)):
    pass

# 权限校验注入
@router.post("/create", dependencies=[Depends(check_permission("user:add"))])
async def create(data: UserCreate, session: Session = Depends(get_session)):
    pass

# 多个依赖组合
@router.put("/update", dependencies=[
    Depends(check_permission("user:edit")),
    Depends(check_token)
])
async def update(data: UserUpdate, session: Session = Depends(get_session)):
    pass
```

### 规范3：参数注入装饰器

```python
from fastapi import Query, Path, Body, Header, Cookie

# Query 参数
@router.get("/queryById")
async def query_by_id(
    id: int = Query(..., description="记录ID"),
    name: str = Query(None, description="名称，可选")
):
    pass

# Path 参数
@router.get("/detail/{id}")
async def get_detail(
    id: int = Path(..., description="记录ID")
):
    pass

# Body 参数
@router.post("/create")
async def create(
    data: UserCreate = Body(..., embed=True)
):
    pass
```

### 规范4：本项目权限装饰器

```python
# core/dependencies.py 中定义的权限校验
from core.dependencies import check_permission

# 使用方式
@router.post("/insert", dependencies=[Depends(check_permission("module:add"))])
@router.put("/update", dependencies=[Depends(check_permission("module:edit"))])
@router.delete("/delete", dependencies=[Depends(check_permission("module:delete"))])
@router.post("/queryByPage", dependencies=[Depends(check_permission("module:query"))])
```

### 规范5：自定义装饰器

```python
from functools import wraps
from core.logger import get_logger

logger = get_logger(__name__)

# 日志装饰器
def log_operation(operation: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.info(f"开始执行: {operation}")
            try:
                result = await func(*args, **kwargs)
                logger.info(f"执行成功: {operation}")
                return result
            except Exception as e:
                logger.error(f"执行失败: {operation}, 错误: {e}")
                raise
        return wrapper
    return decorator

# 使用
@router.post("/create")
@log_operation("创建用户")
async def create_user(data: UserCreate):
    pass
```

### 规范6：异常处理装饰器

```python
# core/exceptions.py 中定义
from core.exceptions import exception_handler

@exception_handler("用户创建失败")
def create_user(data):
    # 业务逻辑
    pass
```

## 禁止事项
- ❌ 不使用 Depends 直接在函数内创建数据库会话
- ❌ 权限校验写在函数体内而不是装饰器
- ❌ 不为 Query 参数添加描述

## 检查清单
- [ ] 是否使用 Depends 注入数据库会话
- [ ] 是否使用 check_permission 进行权限校验
- [ ] Query/Path 参数是否有描述
- [ ] 是否有适当的日志记录
