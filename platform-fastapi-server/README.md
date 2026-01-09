# 大熊AI代码生成器 - FastAPI Backend

基于 **FastAPI + SQLModel** 的 AI 代码生成器后端服务，提供完整的 RBAC 权限管理和基于 AST 的智能代码生成器功能。

## 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI >= 0.115.0 |
| ORM | SQLModel >= 0.0.16 |
| 数据库 | MySQL / SQLite (可配置切换) |
| 认证 | python-jose (JWT) |
| 配置管理 | Pydantic Settings |
| 模板引擎 | Jinja2 |

## 项目结构

```
platform-fastapi-server/
├── app/                     # 应用主目录
│   ├── main.py             # FastAPI 应用入口
│   ├── api/                 # API 路由层
│   │   └── v1/             # API v1 版本
│   │       └── endpoints/   # 端点控制器
│   │           ├── AuthController.py       # 认证控制器
│   │           ├── UsersController.py      # 用户管理
│   │           ├── RolesController.py      # 角色管理
│   │           ├── MenusController.py      # 菜单管理
│   │           ├── DepartmentsController.py # 部门管理
│   │           ├── GenTablesController.py  # 代码生成-表配置
│   │           └── GeneratorController.py  # 代码生成器
│   ├── config/             # 配置文件
│   │   ├── dev_settings.py   # 开发环境配置
│   │   ├── test_settings.py  # 测试环境配置
│   │   └── prod_settings.py  # 生产环境配置
│   ├── database/           # 数据库模块
│   │   ├── database.py       # 数据库连接和会话管理
│   │   └── init_data.py      # 初始化数据
│   ├── dependencies/       # 依赖注入
│   │   └── dependencies.py   # JWT认证、权限检查等
│   ├── exceptions/         # 异常处理
│   │   └── exceptions.py     # 自定义异常
│   ├── logger/             # 日志模块
│   │   └── logger.py         # 日志配置
│   ├── middleware/         # 中间件
│   │   └── middleware.py     # TraceID、CORS等
│   ├── models/             # 数据模型 (SQLModel)
│   │   ├── UserModel.py             # 用户模型
│   │   ├── RoleModel.py             # 角色模型
│   │   ├── MenuModel.py             # 菜单模型
│   │   ├── DeptModel.py             # 部门模型
│   │   ├── UserRoleModel.py         # 用户角色关联
│   │   ├── RoleMenuModel.py         # 角色菜单关联
│   │   ├── GenTable.py              # 代码生成-表配置
│   │   ├── GenTableColumn.py        # 代码生成-字段配置
│   │   └── GenHistory.py            # 代码生成-生成历史
│   ├── responses/          # 响应模型
│   │   └── resp_model.py     # 统一响应格式
│   ├── schemas/            # 请求/响应 Schema (Pydantic)
│   │   ├── LoginSchema.py           # 登录相关
│   │   ├── UserSchema.py            # 用户相关
│   │   ├── RoleSchema.py            # 角色相关
│   │   ├── MenuSchema.py            # 菜单相关
│   │   ├── DeptSchema.py            # 部门相关
│   │   ├── GenTableSchema.py        # 代码生成-表配置
│   │   └── GeneratorSchema.py       # 代码生成-生成请求
│   ├── security/           # 安全模块
│   │   └── JwtUtil.py         # JWT 工具类
│   ├── services/           # 业务服务层
│   │   ├── UserService.py          # 用户服务
│   │   ├── RoleService.py          # 角色服务
│   │   ├── MenuService.py          # 菜单服务
│   │   ├── DeptService.py          # 部门服务
│   │   ├── GenTableService.py      # 代码生成-表配置服务
│   │   ├── GeneratorService.py     # 代码生成服务
│   │   ├── DbMetaService.py        # 数据库元数据服务
│   │   ├── ASTCodeGenerator.py     # AST 代码生成器
│   │   └── TemplateManager.py      # 模板管理器
│   ├── templates/          # Jinja2 模板
│   │   ├── controller.jinja2       # Controller 层模板
│   │   ├── model.jinja2            # Model 层模板
│   │   └── schema.jinja2           # Schema 层模板
│   ├── tests/              # 测试目录
│   └── utils/              # 工具模块
│       └── time_utils.py       # 时间工具类
├── run.py                 # 启动脚本
└── requirements.txt       # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置说明

#### 数据库配置（支持 MySQL 和 SQLite 切换）

编辑 `app/config/dev_settings.py` 配置文件：

**使用 SQLite（默认，开箱即用）**：
```python
DB_TYPE = "sqlite"  # 使用 SQLite
SQLITE_DATABASE = "./data/ai_agent.db"  # SQLite 数据库文件路径
```

**使用 MySQL**：
```python
DB_TYPE = "mysql"  # 使用 MySQL
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "platform_back"
```

#### 其他配置

```python
# JWT 密钥配置
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
```

### 3. 启动应用

#### 开发模式（热重载）

```bash
python run.py
```

或

```bash
uvicorn app.main:application --host 0.0.0.0 --port 5000 --reload
```

#### 生产模式

```bash
uvicorn app.main:application --host 0.0.0.0 --port 5000 --workers 4
```

### 4. 访问 API 文档

启动应用后访问：

- **交互式文档 (Swagger UI)**: http://localhost:5000/docs
- **备选文档 (ReDoc)**: http://localhost:5000/redoc
- **OpenAPI JSON**: http://localhost:5000/openapi.json

### 5. 默认账号

- **用户名**: `admin`
- **密码**: `admin123`

---

## 主要功能模块

### 1. 用户认证

| 接口 | 方法 | 说明 |
|------|------|------|
| POST /auth/login | 登录 | 用户登录获取 Token |
| GET /auth/userinfo | 用户信息 | 获取当前登录用户信息 |

### 2. RBAC 权限管理系统

#### 2.1 用户管理

| 接口 | 方法 | 说明 |
|------|------|------|
| POST /api/v1/users/queryByPage | 分页查询 | 分页查询用户列表 |
| GET /api/v1/users/queryById | 查询详情 | 根据 ID 查询用户 |
| POST /api/v1/users/insert | 新增 | 新增用户 |
| PUT /api/v1/users/update | 更新 | 更新用户信息 |
| DELETE /api/v1/users/delete | 删除 | 删除用户 |
| POST /api/v1/users/assignRoles | 分配角色 | 为用户分配角色 |
| GET /api/v1/users/roles/{user_id} | 查询角色 | 获取用户的角色列表 |
| PUT /api/v1/users/updateStatus | 更新状态 | 更新用户锁定/启用状态 |

**用户字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | int | 用户 ID（主键） |
| username | str | 用户名（唯一索引） |
| password | str | 密码（加密存储） |
| dept_id | int | 部门 ID |
| email | str | 邮箱 |
| mobile | str | 联系电话 |
| status | int | 状态（0 锁定 1 有效） |
| ssex | int | 性别（0 男 1 女 2 保密） |
| avatar | str | 头像 URL |
| description | str | 描述 |
| create_time | datetime | 创建时间 |
| modify_time | datetime | 修改时间 |
| last_login_time | datetime | 最近访问时间 |

#### 2.2 角色管理

| 接口 | 方法 | 说明 |
|------|------|------|
| POST /api/v1/roles/queryByPage | 分页查询 | 分页查询角色列表 |
| GET /api/v1/roles/queryById | 查询详情 | 根据 ID 查询角色 |
| POST /api/v1/roles/insert | 新增 | 新增角色 |
| PUT /api/v1/roles/update | 更新 | 更新角色信息 |
| DELETE /api/v1/roles/delete | 删除 | 删除角色 |
| POST /api/v1/roles/assignMenus | 分配菜单 | 为角色分配菜单权限 |
| GET /api/v1/roles/menus/{role_id} | 查询菜单 | 获取角色的菜单权限 |

#### 2.3 菜单/权限管理

| 接口 | 方法 | 说明 |
|------|------|------|
| GET /api/v1/menus/tree | 查询树 | 获取菜单树 |
| GET /api/v1/menus/queryById | 查询详情 | 根据 ID 查询菜单 |
| POST /api/v1/menus/insert | 新增 | 新增菜单 |
| PUT /api/v1/menus/update | 更新 | 更新菜单信息 |
| DELETE /api/v1/menus/delete | 删除 | 删除菜单 |
| GET /api/v1/menus/user/{user_id} | 用户菜单 | 获取用户的菜单权限（用于前端动态路由） |

#### 2.4 部门管理

| 接口 | 方法 | 说明 |
|------|------|------|
| GET /api/v1/departments/tree | 查询树 | 获取部门树 |
| GET /api/v1/departments/queryById | 查询详情 | 根据 ID 查询部门 |
| POST /api/v1/departments/insert | 新增 | 新增部门 |
| PUT /api/v1/departments/update | 更新 | 更新部门信息 |
| DELETE /api/v1/departments/delete | 删除 | 删除部门 |

### 3. 代码生成器

基于 **AST + Jinja2 模板** 的智能代码生成器，支持数据库表反向工程，快速生成高质量 CRUD 代码。

#### 3.1 核心特性

**智能分析**：
- 数据库表结构自动解析（MySQL/SQLite）
- 字段类型智能映射（数据库类型 → Python 类型）
- 外键关联关系识别
- 主键、索引、注释自动提取

**高质量代码生成**：
- 基于 Jinja2 模板生成规范的 Python 代码
- SQLModel 数据模型（完整字段定义）
- Pydantic Schema（查询/创建/更新模型）
- FastAPI 控制器（完整 CRUD 接口）
- 代码格式化与类型注解

**灵活配置**：
- 自定义类名、模块名、业务名
- 字段级别配置（是否查询、是否编辑等）
- 查询方式配置（等于/模糊/范围）
- 生成路径自定义

**多种生成方式**：
- 代码预览（实时查看生成效果）
- ZIP 压缩包下载（包含 README）
- 批量生成（一键生成多表）
- 生成历史追溯

#### 3.2 表配置管理

| 接口 | 方法 | 说明 |
|------|------|------|
| GET /GenTable/dbTables | 获取表列表 | 获取数据库可导入的表列表 |
| POST /GenTable/importTables | 导入表 | 批量导入表配置 |
| POST /GenTable/queryByPage | 分页查询 | 分页查询表配置 |
| GET /GenTable/queryById | 查询详情 | 根据 ID 查询表配置（含字段） |
| PUT /GenTable/update | 更新 | 更新表配置 |
| DELETE /GenTable/delete | 删除 | 删除表配置 |

#### 3.3 代码生成

| 接口 | 方法 | 说明 |
|------|------|------|
| POST /Generator/preview | 预览 | 预览生成代码 |
| POST /Generator/download | 下载 | 下载生成代码（ZIP） |
| POST /Generator/batchDownload | 批量下载 | 批量下载生成代码 |
| GET /Generator/history | 历史 | 获取生成历史记录 |

#### 3.4 使用流程

1. **导入表配置**：

```bash
# 获取数据库表列表
GET /GenTable/dbTables

# 批量导入表
POST /GenTable/importTables
{
  "table_names": ["t_user", "t_role"]
}
```

2. **配置表信息**（可选）：

```bash
# 修改类名、模块名等配置
PUT /GenTable/update
{
  "id": 1,
  "class_name": "User",
  "module_name": "sysmanage",
  "business_name": "user",
  "function_name": "用户管理"
}
```

3. **预览代码**：

```bash
POST /Generator/preview
{
  "table_id": 1
}
```

4. **下载代码**：

```bash
POST /Generator/download
{
  "table_id": 1,
  "gen_type": "1"
}
```

5. **集成到项目**：
   - 解压下载的 ZIP 文件
   - 复制文件到对应模块目录
   - 在 `app/main.py` 中注册路由
   - 重启应用即可使用

#### 3.5 生成的代码结构

```
{module_name}/
├── model/
│   └── {ClassName}.py          # SQLModel 数据模型
├── schemas/
│   └── {business_name}_schema.py  # Pydantic Schema
└── api/
    └── {ClassName}Controller.py   # FastAPI 控制器
```

#### 3.6 代码示例

**生成的 Model**：

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "t_user"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=64)
    password: str = Field(max_length=128)
    email: Optional[str] = Field(default=None, max_length=100)
    create_time: Optional[datetime] = Field(default_factory=datetime.now)
```

**生成的 Controller**：

```python
@router.post("/queryByPage")
async def queryByPage(query: UserQuery, session: Session = Depends(get_session)):
    # 完整的分页查询实现
    ...

@router.get("/queryById")
async def queryById(id: int = Query(...), session: Session = Depends(get_session)):
    # 根据 ID 查询实现
    ...
```

#### 3.7 权限控制

代码生成器模块已集成 RBAC 权限控制：

| 权限标识 | 说明 |
|----------|------|
| generator:table:list | 查看表配置列表 |
| generator:table:query | 查询表配置详情 |
| generator:table:import | 导入表配置 |
| generator:table:edit | 修改表配置 |
| generator:table:delete | 删除表配置 |
| generator:code:generate | 生成代码 |
| generator:code:preview | 预览代码 |
| generator:code:download | 下载代码 |
| generator:code:batch | 批量生成 |
| generator:history:list | 查看生成历史 |
| generator:history:query | 查询历史详情 |

**默认权限分配**：
- 超级管理员：所有权限
- 管理员：所有代码生成器权限
- 普通用户：无权限（需单独授权）

#### 3.8 技术亮点

- ✅ 基于 Jinja2 模板确保代码质量和规范性
- ✅ 智能类型映射（支持 datetime/int/float/str 等）
- ✅ 驼峰命名自动转换
- ✅ 完整的字段注释和文档
- ✅ 支持复杂查询条件（模糊查询/范围查询）
- ✅ 代码生成历史记录
- ✅ 批量生成提升效率
- ✅ ZIP 压缩包包含 README 使用说明

---

## 数据库初始化

首次启动时，应用会自动创建所有数据表并初始化基础数据。

---

## 统一响应格式

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {},
  "total": 0,
  "trace_id": "xxx"
}
```

**响应类型**：

| 方法 | 说明 |
|------|------|
| ok_resp | 单条数据响应 |
| ok_resp_list | 列表数据响应（带分页） |
| ok_resp_simple | 简单数据响应 |
| ok_resp_tree | 树形数据响应 |
| error_resp | 错误响应 |

---

## 开发规范

- **注释**：所有注释位于代码右侧，格式为 `# 注释内容`
- **类型注解**：所有函数必须有类型注解
- **异步模式**：Controller 使用 `async def`
- **遵循 PEP 8 规范**
- **权限控制**：使用 `check_permission("xxx:xxx:xxx")`
- **主键命名**：所有 RBAC 模型统一使用 `id` 作为主键

---

## 技术特性

- ✅ **FastAPI + SQLModel**：现代化高性能框架组合
- ✅ **同步 SQLModel**：保持与原 Flask 代码接近
- ✅ **支持 MySQL 和 SQLite 数据库切换**
- ✅ **完整 RBAC 权限管理系统**
  - 用户-角色-菜单权限模型
  - 部门管理（树形结构）
  - 菜单管理（支持菜单和按钮级权限）
  - 用户状态管理（启用/锁定）
  - **统一主键命名**（简洁高效）
- ✅ **依赖注入**：数据库会话、JWT 认证、权限检查
- ✅ **统一响应格式**：标准化的 API 响应结构
- ✅ **自动 API 文档生成**：Swagger UI / ReDoc
- ✅ **数据验证**：Pydantic 字段验证
- ✅ **类型提示**：完整的类型注解
- ✅ **JWT 认证**：安全的用户认证机制
- ✅ **CORS 支持**：跨域资源共享
- ✅ **请求追踪**：TraceID 日志追踪
- ✅ **自动初始化**：启动时自动创建表和基础数据

---

## 版本信息

| 项目 | 版本 |
|------|------|
| 版本 | 2.0.0 |
| 框架 | FastAPI |
| ORM | SQLModel |
| Python | 3.8+ |

---

## 注意事项

1. **数据库选择**：
   - 开发/测试环境推荐使用 SQLite（开箱即用，无需安装）
   - 生产环境推荐使用 MySQL（性能更好，支持并发）

2. **MySQL 配置**：使用 MySQL 时，确保数据库已启动并可访问

3. **生产环境**：
   - 修改 CORS 配置，指定具体允许的域名
   - 使用强密码和安全的 SECRET_KEY
   - 建议使用虚拟环境进行开发

4. **权限标识**：权限检查使用 `check_permission("系统:模块:操作")` 格式

---

## 相关文档

- [AGENTS.md](./AGENTS.md) - AI 助手开发指南
- [API 文档](http://localhost:5000/docs) - Swagger UI（启动后访问）
