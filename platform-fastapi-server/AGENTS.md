# AGENTS.md - 大熊AI代码生成器 Backend

> 本文档为 AI 助手提供项目上下文和开发指南，遵循 [agents.md](https://github.com/agentsmd/agents.md) 规范。

## 项目概述

基于 **FastAPI + SQLModel** 的 AI 代码生成器后端服务，提供完整的 RBAC 权限管理和基于 AST 的智能代码生成器功能。

### 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI >= 0.115.0 |
| ORM | SQLModel >= 0.0.16 |
| 数据库 | MySQL / SQLite (可切换) |
| 认证 | JWT (python-jose) |
| 配置管理 | Pydantic Settings |
| 模板引擎 | Jinja2 |
| 依赖注入 | FastAPI Depends |

### 运行端口

- **后端服务**: `http://localhost:5000`
- **API 文档**: `http://localhost:5000/docs`
- **ReDoc**: `http://localhost:5000/redoc`

---

## 目录结构

```
platform-fastapi-server/
├── app/                      # 应用主目录
│   ├── main.py               # FastAPI 应用入口
│   ├── api/                  # API 路由层
│   │   └── v1/               # API v1 版本
│   │       └── endpoints/    # 端点控制器
│   │           ├── AuthController.py         # 认证控制器
│   │           ├── UsersController.py        # 用户管理
│   │           ├── RolesController.py        # 角色管理
│   │           ├── MenusController.py        # 菜单管理
│   │           ├── DepartmentsController.py  # 部门管理
│   │           ├── GenTablesController.py    # 代码生成-表配置
│   │           ├── GeneratorController.py    # 代码生成器
│   │           └── __init__.py
│   ├── config/               # 配置文件
│   │   ├── __init__.py
│   │   ├── dev_settings.py   # 开发环境配置 (默认启用)
│   │   ├── test_settings.py  # 测试环境配置
│   │   └── prod_settings.py  # 生产环境配置
│   ├── database/             # 数据库模块
│   │   ├── __init__.py
│   │   ├── database.py       # 数据库连接和会话管理
│   │   └── init_data.py      # 初始化数据
│   ├── dependencies/         # 依赖注入
│   │   ├── __init__.py
│   │   └── dependencies.py   # JWT认证、权限检查等
│   ├── exceptions/           # 异常处理
│   │   ├── __init__.py
│   │   └── exceptions.py     # 自定义异常
│   ├── logger/               # 日志模块
│   │   ├── __init__.py
│   │   └── logger.py         # 日志配置
│   ├── middleware/           # 中间件
│   │   ├── __init__.py
│   │   └── middleware.py     # TraceID、CORS等
│   ├── models/               # 数据模型 (SQLModel)
│   │   ├── __init__.py
│   │   ├── UserModel.py      # 用户模型
│   │   ├── RoleModel.py      # 角色模型
│   │   ├── MenuModel.py      # 菜单模型
│   │   ├── DeptModel.py      # 部门模型
│   │   ├── UserRoleModel.py  # 用户角色关联
│   │   ├── RoleMenuModel.py  # 角色菜单关联
│   │   ├── GenTable.py       # 代码生成-表配置
│   │   ├── GenTableColumn.py # 代码生成-字段配置
│   │   └── GenHistory.py     # 代码生成-生成历史
│   ├── responses/            # 响应模型
│   │   ├── __init__.py
│   │   └── resp_model.py     # 统一响应格式
│   ├── schemas/              # 请求/响应 Schema (Pydantic)
│   │   ├── __init__.py
│   │   ├── LoginSchema.py    # 登录相关
│   │   ├── UserSchema.py     # 用户相关
│   │   ├── RoleSchema.py     # 角色相关
│   │   ├── MenuSchema.py     # 菜单相关
│   │   ├── DeptSchema.py     # 部门相关
│   │   ├── GenTableSchema.py # 代码生成-表配置
│   │   └── GeneratorSchema.py# 代码生成-生成请求
│   ├── security/             # 安全模块
│   │   ├── __init__.py
│   │   └── JwtUtil.py        # JWT 工具类
│   ├── services/             # 业务服务层
│   │   ├── __init__.py
│   │   ├── UserService.py          # 用户服务
│   │   ├── RoleService.py          # 角色服务
│   │   ├── MenuService.py          # 菜单服务
│   │   ├── DeptService.py          # 部门服务
│   │   ├── GenTableService.py      # 代码生成-表配置服务
│   │   ├── GeneratorService.py     # 代码生成服务
│   │   ├── DbMetaService.py        # 数据库元数据服务
│   │   ├── ASTCodeGenerator.py     # AST 代码生成器
│   │   └── TemplateManager.py      # 模板管理器
│   ├── templates/            # Jinja2 模板
│   │   ├── controller.jinja2  # Controller 层模板
│   │   ├── model.jinja2       # Model 层模板
│   │   └── schema.jinja2      # Schema 层模板
│   ├── tests/                # 测试目录
│   │   └── __init__.py
│   ├── utils/                # 工具模块
│   │   ├── __init__.py
│   │   └── time_utils.py     # 时间工具类
│   └── __init__.py
├── run.py                    # 启动脚本
└── requirements.txt          # 项目依赖
```

---

## 开发规范

### 代码风格

- **注释**: 位于代码右侧，格式为 `# 注释内容`
- **类型注解**: 所有函数必须有类型注解
- **异步支持**: 使用 `async/await` 模式
- **命名规范**:
  - 类名: `PascalCase` (如 `UserController`)
  - 函数/变量: `snake_case` (如 `query_by_page`)
  - 常量: `UPPER_SNAKE_CASE`
- **遵循 PEP 8 规范**

### 模块结构规范

当前项目采用扁平化结构，所有模块在同一层级：

```
app/
├── api/v1/endpoints/{Module}Controller.py  # Controller 层
├── models/{Module}Model.py                 # Model 层 (SQLModel)
├── schemas/{Module}Schema.py               # Schema 层 (Pydantic)
├── services/{Module}Service.py             # Service 层
└── ...                                     # 其他公共模块
```

### Controller 模板

```python
from app.database.database import get_session
from app.dependencies.dependencies import check_permission
from app.logger.logger import get_logger
from app.responses.resp_model import respModel
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.schemas.UserSchema import UserQuery, UserCreate, UserUpdate
from app.services.UserService import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("/queryByPage", summary="分页查询用户", 
             dependencies=[Depends(check_permission("system:user:query"))])
async def queryByPage(query: UserQuery, session: Session = Depends(get_session)):
    """分页查询用户"""
    try:
        datas, total = UserService.query_by_page(session, query)
        return respModel.ok_resp_list(lst=datas, total=total)
    except Exception as e:
        logger.error(f"分页查询用户失败: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@router.get("/queryById", summary="根据ID查询用户",
            dependencies=[Depends(check_permission("system:user:query"))])
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    """根据ID查询用户"""
    try:
        data = UserService.query_by_id(session, id)
        if data:
            return respModel.ok_resp(obj=data)
        else:
            return respModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        logger.error(f"查询用户失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(f"服务器错误,请联系管理员:{e}")

@router.post("/insert", summary="新增用户",
             dependencies=[Depends(check_permission("system:user:add"))])
async def insert(user: UserCreate, session: Session = Depends(get_session)):
    """新增用户"""
    try:
        data = UserService.create(session, user)
        return respModel.ok_resp(msg="添加成功", dic_t={"id": data.id})
    except Exception as e:
        session.rollback()
        logger.error(f"新增用户失败: {e}", exc_info=True)
        return respModel.error_resp(msg=f"添加失败:{e}")

@router.put("/update", summary="更新用户",
            dependencies=[Depends(check_permission("system:user:edit"))])
async def update(user: UserUpdate, session: Session = Depends(get_session)):
    """更新用户"""
    try:
        db_user = UserService.update(session, user)
        if db_user:
            return respModel.ok_resp(msg="修改成功")
        else:
            return respModel.error_resp(msg="用户不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"更新用户失败: ID={user.id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"修改失败，请联系管理员:{e}")

@router.delete("/delete", summary="删除用户",
               dependencies=[Depends(check_permission("system:user:delete"))])
async def delete(id: int = Query(...), session: Session = Depends(get_session)):
    """删除用户"""
    try:
        success = UserService.delete(session, id)
        if success:
            return respModel.ok_resp(msg="删除成功")
        else:
            return respModel.error_resp(msg="用户不存在")
    except Exception as e:
        session.rollback()
        logger.error(f"删除用户失败: ID={id}, 错误: {e}", exc_info=True)
        return respModel.error_resp(msg=f"服务器错误,删除失败：{e}")
```

### Model 模板

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "t_user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=64, description="用户名")
    password: str = Field(max_length=128, description="密码")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    status: int = Field(default=1, description="状态: 0锁定 1有效")
    create_time: Optional[datetime] = Field(default_factory=datetime.now, description="创建时间")
    update_time: Optional[datetime] = Field(default=None, description="更新时间")
```

### Schema 模板

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserQuery(BaseModel):
    """分页查询参数"""
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)
    username: Optional[str] = None
    status: Optional[int] = None
    dept_id: Optional[int] = None

class UserCreate(BaseModel):
    """创建参数"""
    username: str = Field(..., max_length=64, description="用户名")
    password: str = Field(..., max_length=128, description="密码")
    email: Optional[str] = Field(default=None, max_length=100, description="邮箱")
    dept_id: Optional[int] = Field(default=None, description="部门ID")
    status: int = Field(default=1, description="状态: 0锁定 1有效")

class UserUpdate(BaseModel):
    """更新参数"""
    id: int
    username: Optional[str] = Field(default=None, max_length=64)
    email: Optional[str] = Field(default=None, max_length=100)
    status: Optional[int] = None
    dept_id: Optional[int] = None
```

### 统一响应格式

所有接口使用 `respModel` 返回统一格式：

```python
from app.responses.resp_model import respModel

# 成功响应 - 单条数据
return respModel.ok_resp(obj=data, msg="操作成功")

# 成功响应 - 列表数据 (带分页)
return respModel.ok_resp_list(lst=items, total=total, msg="查询成功")

# 成功响应 - 简单数据
return respModel.ok_resp_simple(lst=data, msg="操作成功")

# 成功响应 - 树形数据
return respModel.ok_resp_tree(treeData=data, msg="查询成功")

# 错误响应
return respModel.error_resp("错误信息")

# 响应结构
{
    "code": 200,        # 200成功, -1失败
    "msg": "消息",
    "data": {},         # 数据对象
    "total": 0,         # 总记录数 (列表响应)
    "trace_id": "xxx"   # 请求追踪ID
}
```

---

## 常用命令

### 启动服务

```bash
# 开发模式 (热重载)
cd platform-fastapi-server
python run.py

# 或直接使用 uvicorn
uvicorn app.main:application --host 0.0.0.0 --port 5000 --reload
```

### 运行测试

```bash
# 运行所有测试
pytest app/tests/ -v

# 运行特定模块测试
pytest app/tests/api/test_user_controller.py -v

# 生成覆盖率报告
pytest app/tests/ --cov=. --cov-report=html
```

### 数据库操作

首次启动时，应用会自动初始化数据库表和基础数据。

---

## 配置说明

### 配置文件 (config/dev_settings.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 数据库类型: sqlite 或 mysql
    DB_TYPE: str = "sqlite"
    
    # SQLite配置
    SQLITE_DATABASE: str = "./data/ai_agent.db"
    
    # MySQL配置 (DB_TYPE=mysql时使用)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "root"
    MYSQL_DATABASE: str = "platform_back"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
```

### 环境切换

通过修改导入语句切换环境：

```python
# 开发环境 (默认)
from app.config.dev_settings import settings

# 测试环境
from app.config.test_settings import settings

# 生产环境
from app.config.prod_settings import settings
```

### 默认账号

- **用户名**: `admin`
- **密码**: `admin123`

---

## 核心模块说明

### 1. 用户认证

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| POST /auth/login | 登录 | 用户登录获取Token | 无 |
| GET /auth/userinfo | 用户信息 | 获取当前登录用户信息 | 无 |

### 2. RBAC 权限管理系统

#### 2.1 用户管理

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| POST /api/v1/users/queryByPage | 分页查询 | 分页查询用户列表 | system:user:query |
| GET /api/v1/users/queryById | 查询详情 | 根据ID查询用户 | system:user:query |
| POST /api/v1/users/insert | 新增 | 新增用户 | system:user:add |
| PUT /api/v1/users/update | 更新 | 更新用户信息 | system:user:edit |
| DELETE /api/v1/users/delete | 删除 | 删除用户 | system:user:delete |
| POST /api/v1/users/assignRoles | 分配角色 | 为用户分配角色 | system:user:edit |
| GET /api/v1/users/roles/{user_id} | 查询角色 | 获取用户的角色列表 | system:user:query |
| PUT /api/v1/users/updateStatus | 更新状态 | 更新用户锁定/启用状态 | system:user:edit |

#### 2.2 角色管理

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| POST /api/v1/roles/queryByPage | 分页查询 | 分页查询角色列表 | system:role:query |
| GET /api/v1/roles/queryById | 查询详情 | 根据ID查询角色 | system:role:query |
| POST /api/v1/roles/insert | 新增 | 新增角色 | system:role:add |
| PUT /api/v1/roles/update | 更新 | 更新角色信息 | system:role:edit |
| DELETE /api/v1/roles/delete | 删除 | 删除角色 | system:role:delete |
| POST /api/v1/roles/assignMenus | 分配菜单 | 为角色分配菜单权限 | system:role:edit |
| GET /api/v1/roles/menus/{role_id} | 查询菜单 | 获取角色的菜单权限 | system:role:query |

#### 2.3 菜单/权限管理

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| GET /api/v1/menus/tree | 查询树 | 获取菜单树 | system:menu:query |
| GET /api/v1/menus/queryById | 查询详情 | 根据ID查询菜单 | system:menu:query |
| POST /api/v1/menus/insert | 新增 | 新增菜单 | system:menu:add |
| PUT /api/v1/menus/update | 更新 | 更新菜单信息 | system:menu:edit |
| DELETE /api/v1/menus/delete | 删除 | 删除菜单 | system:menu:delete |
| GET /api/v1/menus/user/{user_id} | 用户菜单 | 获取用户的菜单权限(动态路由) | 无 |

#### 2.4 部门管理

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| GET /api/v1/departments/tree | 查询树 | 获取部门树 | system:dept:query |
| GET /api/v1/departments/queryById | 查询详情 | 根据ID查询部门 | system:dept:query |
| POST /api/v1/departments/insert | 新增 | 新增部门 | system:dept:add |
| PUT /api/v1/departments/update | 更新 | 更新部门信息 | system:dept:edit |
| DELETE /api/v1/departments/delete | 删除 | 删除部门 | system:dept:delete |

### 3. 代码生成器

#### 3.1 表配置管理

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| GET /GenTable/dbTables | 获取表列表 | 获取数据库可导入的表列表 | generator:table:query |
| POST /GenTable/importTables | 导入表 | 批量导入表配置 | generator:table:import |
| POST /GenTable/queryByPage | 分页查询 | 分页查询表配置 | generator:table:query |
| GET /GenTable/queryById | 查询详情 | 根据ID查询表配置(含字段) | generator:table:query |
| PUT /GenTable/update | 更新 | 更新表配置 | generator:table:edit |
| DELETE /GenTable/delete | 删除 | 删除表配置 | generator:table:delete |

#### 3.2 代码生成

| 接口 | 方法 | 说明 | 权限 |
|------|------|------|------|
| POST /Generator/preview | 预览 | 预览生成代码 | generator:code:preview |
| POST /Generator/download | 下载 | 下载生成代码(ZIP) | generator:code:download |
| POST /Generator/batchDownload | 批量下载 | 批量下载生成代码 | generator:code:batch |
| GET /Generator/history | 历史 | 获取生成历史记录 | generator:history:list |

---

## 依赖注入

```python
from app.database.database import get_session
from app.dependencies.dependencies import get_current_user, check_permission
from fastapi import Depends

# 数据库会话
session: Session = Depends(get_session)

# 当前登录用户 (需要 JWT 认证)
current_user: dict = Depends(get_current_user)

# 权限检查 (需要对应权限标识)
dependencies=[Depends(check_permission("system:user:query"))]
```

### JWT 工具类 (app/security/JwtUtil.py)

```python
from app.security.JwtUtil import JwtUtils

# 创建 Token
token = JwtUtils.create_token(user_id=1, username="admin")

# 验证 Token
payload = JwtUtils.verify_token(token)

# 刷新 Token
new_token = JwtUtils.refresh_token(token)

# 检查是否过期
is_expired = JwtUtils.is_token_expired(token)
```

---

## 路由注册

新增 Controller 后需在 `app/main.py` 中注册路由：

```python
from app.api.v1.endpoints import {Module}Controller
application.include_router({Module}Controller.router)
```

---

## 代码生成器

### 核心组件

1. **ASTCodeGenerator** (`app/services/ASTCodeGenerator.py`)
   - 基于 Jinja2 模板生成代码
   - 支持 Model/Schema/Controller/Service 四层代码生成
   - 智能类型映射 (数据库类型 → Python 类型)
   - 支持前后端代码生成

2. **TemplateManager** (`app/services/TemplateManager.py`)
   - 模板渲染管理器
   - 支持自定义模板目录
   - 禁用缓存，确保每次读取最新模板

3. **后端模板文件** (`app/templates/`)
   - `controller.jinja2` - Controller 层模板（调用Service层）
   - `service.jinja2` - Service 业务层模板
   - `model.jinja2` - Model 层模板
   - `schema.jinja2` - Schema 层模板

4. **前端模板文件** (`app/templates/`)
   - `list.vue.jinja2` - 列表页模板
   - `form.vue.jinja2` - 表单页模板（支持新增/编辑/查看）
   - `api.js.jinja2` - API 请求模板

### 生成代码结构

**后端代码 (4层架构)**：

```
{module_name}/
├── model/
│   └── {ClassName}Model.py          # SQLModel 数据模型
├── schemas/
│   └── {ClassName}Schema.py         # Pydantic Schema
├── services/
│   └── {ClassName}Service.py        # Service 业务层
└── api/
    └── {ClassName}Controller.py      # FastAPI 控制器
```

**前端代码**：

```
{business_name}/
├── {BusinessName}List.vue            # 列表页
├── {BusinessName}Form.vue            # 表单页
└── {business_name}.js                 # API 请求
```

---

## 注意事项

1. **数据库选择**: 开发环境默认使用 SQLite，生产环境建议 MySQL
2. **路由注册**: 新增 Controller 后需在 `app/main.py` 中注册路由
3. **CORS**: 生产环境需配置具体允许的域名 (当前为 `*`)
4. **密码安全**: 生产环境必须修改 SECRET_KEY
5. **代码复用**: 开发前先检查现有服务，避免重复开发
6. **异步模式**: Controller 使用 `async def`，Service 可使用同步方法
7. **权限标识**: 使用 `check_permission("xxx:xxx:xxx")` 进行权限控制
8. **主键命名**: 所有 RBAC 模型统一使用 `id` 作为主键

---

## 现有功能清单

### Controller 列表

| 模块 | Controller | 说明 |
|------|------------|------|
| api/v1/endpoints | AuthController | 认证控制器 |
| api/v1/endpoints | UsersController | 用户管理 |
| api/v1/endpoints | RolesController | 角色管理 |
| api/v1/endpoints | MenusController | 菜单管理 |
| api/v1/endpoints | DepartmentsController | 部门管理 |
| api/v1/endpoints | GenTablesController | 代码生成-表配置 |
| api/v1/endpoints | GeneratorController | 代码生成器 |

### Model 列表

| 模块 | Model | 表名 | 说明 |
|------|-------|------|------|
| models | User | t_user | 用户 |
| models | Role | t_role | 角色 |
| models | Menu | t_menu | 菜单 |
| models | Dept | t_dept | 部门 |
| models | UserRole | t_user_role | 用户角色关联 |
| models | RoleMenu | t_role_menu | 角色菜单关联 |
| models | GenTable | t_gen_table | 代码生成-表配置 |
| models | GenTableColumn | t_gen_table_column | 代码生成-字段配置 |
| models | GenHistory | t_gen_history | 代码生成-历史记录 |

### Service 列表

| 模块 | Service | 说明 |
|------|---------|------|
| services | UserService | 用户服务 |
| services | RoleService | 角色服务 |
| services | MenuService | 菜单服务 |
| services | DeptService | 部门服务 |
| services | GenTableService | 表配置服务 |
| services | GeneratorService | 代码生成服务 |
| services | DbMetaService | 数据库元数据服务 |
| services | ASTCodeGenerator | AST 代码生成器 |
| services | TemplateManager | 模板管理器 |

---

## 相关文档

- [README.md](./README.md) - 项目详细说明
- [API 文档](http://localhost:5000/docs) - Swagger UI (启动后访问)
