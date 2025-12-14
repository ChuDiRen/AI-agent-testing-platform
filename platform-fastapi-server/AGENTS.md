# AGENTS.md - AI Agent Testing Platform Backend

> 本文档为 AI 助手提供项目上下文和开发指南，遵循 [agents.md](https://github.com/agentsmd/agents.md) 规范。

## 项目概述

这是一个基于 **FastAPI + SQLModel** 的 AI 智能体测试平台后端服务，提供完整的 API 测试、AI 对话式测试用例生成、RBAC 权限管理和代码生成器功能。

### 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI 0.104.1 |
| ORM | SQLModel 0.0.14 |
| 数据库 | MySQL / SQLite (可切换) |
| 认证 | JWT (python-jose) |
| 对象存储 | MinIO |
| 消息队列 | RabbitMQ / 内存队列 |
| AI 流式 | SSE (sse-starlette) |

### 运行端口

- **后端服务**: `http://localhost:5000`
- **API 文档**: `http://localhost:5000/docs`
- **WebSocket**: `ws://localhost:5000/ws/test-execution/{execution_id}`

---

## 目录结构

```
platform-fastapi-server/
├── app.py                    # FastAPI 应用入口
├── run.py                    # 启动脚本 (uvicorn, port=5000)
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量配置
│
├── config/                   # 配置文件
│   ├── dev_settings.py       # 开发环境配置 ⭐
│   ├── test_settings.py      # 测试环境配置
│   └── prod_settings.py      # 生产环境配置
│
├── core/                     # 核心模块
│   ├── database.py           # 数据库连接和会话管理
│   ├── dependencies.py       # 依赖注入 (JWT验证、会话)
│   ├── JwtUtil.py            # JWT 工具类
│   ├── resp_model.py         # 统一响应模型 respModel
│   ├── logger.py             # 日志配置
│   ├── middleware.py         # 中间件 (TraceID, CORS)
│   ├── AiStreamService.py    # AI 流式调用服务
│   ├── ConversationService.py # 对话上下文管理
│   ├── WebSocketManager.py   # WebSocket 连接管理
│   └── QueueFactory.py       # 消息队列工厂
│
├── login/                    # 登录模块
│   ├── api/LoginController.py
│   └── schemas/login_schema.py
│
├── sysmanage/                # 系统管理模块 (RBAC)
│   ├── api/                  # UserController, RoleController, MenuController, DeptController
│   ├── model/                # User, Role, Menu, Dept, UserRole, RoleMenu
│   └── schemas/              # 请求/响应 Schema
│
├── apitest/                  # API 测试模块
│   ├── api/                  # 14 个 Controller
│   ├── model/                # 数据模型
│   ├── schemas/              # Schema 定义
│   └── service/              # 业务服务 (执行器、YAML生成)
│
├── aiassistant/              # AI 测试助手模块 ⭐
│   ├── api/                  # AiConversation, AiModel, PromptTemplate, TestCase
│   ├── model/                # AI 相关数据模型
│   └── schemas/              # Schema 定义
│
├── generator/                # 代码生成器模块
│   ├── api/                  # GeneratorController, GenTableController
│   ├── service/              # AST 代码生成器
│   └── templates/            # Jinja2 模板
│
├── msgmanage/                # 消息管理模块 (机器人推送)
├── plugin/                   # 插件管理模块
│
├── tests/                    # 测试目录
│   ├── api/                  # API 单元测试
│   ├── e2e/                  # 端到端测试
│   └── conftest.py           # pytest 配置
│
├── data/                     # SQLite 数据库文件
└── temp/                     # 临时文件 (报告、日志、YAML)
```

---

## 开发规范

### 代码风格

- **注释**: 所有注释位于代码右侧，格式为 `# 注释`
- **类型注解**: 所有函数必须有类型注解
- **命名规范**: 
  - 类名: `PascalCase` (如 `UserController`)
  - 函数/变量: `snake_case` (如 `query_by_page`)
  - 常量: `UPPER_SNAKE_CASE`
- **遵循 PEP 8 规范**

### Controller 模板

新建 Controller 时遵循以下模式：

```python
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from core.database import get_session
from core.resp_model import respModel
from core.dependencies import get_current_user
from core.logger import get_logger

logger = get_logger(__name__)

module_route = APIRouter(prefix="/{ModuleName}", tags=["{模块中文名}"])

@module_route.post("/queryByPage", summary="分页查询")
def query_by_page(
    query: {ModuleName}Query,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """分页查询{模块}列表"""
    # 构建查询
    statement = select({Model})
    # 添加过滤条件...
    # 分页处理...
    return respModel.ok_resp(obj={"list": results, "total": total})

@module_route.get("/queryById", summary="根据ID查询")
def query_by_id(
    id: int = Query(..., description="{模块}ID"),
    session: Session = Depends(get_session)
):
    """根据ID查询{模块}详情"""
    item = session.get({Model}, id)
    if not item:
        return respModel.error_resp("{模块}不存在")
    return respModel.ok_resp(obj=item)

@module_route.post("/insert", summary="新增")
def insert(
    data: {ModuleName}Create,
    session: Session = Depends(get_session)
):
    """新增{模块}"""
    item = {Model}(**data.model_dump())
    session.add(item)
    session.commit()
    session.refresh(item)
    return respModel.ok_resp(obj=item, msg="新增成功")

@module_route.put("/update", summary="更新")
def update(
    data: {ModuleName}Update,
    session: Session = Depends(get_session)
):
    """更新{模块}"""
    item = session.get({Model}, data.id)
    if not item:
        return respModel.error_resp("{模块}不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    session.commit()
    return respModel.ok_resp(msg="更新成功")

@module_route.delete("/delete", summary="删除")
def delete(
    id: int = Query(..., description="{模块}ID"),
    session: Session = Depends(get_session)
):
    """删除{模块}"""
    item = session.get({Model}, id)
    if not item:
        return respModel.error_resp("{模块}不存在")
    session.delete(item)
    session.commit()
    return respModel.ok_resp(msg="删除成功")
```

### Model 模板

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class {ModelName}(SQLModel, table=True):
    __tablename__ = "t_{table_name}"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, description="名称")
    status: int = Field(default=1, description="状态: 0禁用 1启用")
    create_time: Optional[datetime] = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(default=None)
```

### Schema 模板

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class {ModuleName}Query(BaseModel):
    """分页查询参数"""
    pageNum: int = Field(default=1, ge=1)
    pageSize: int = Field(default=10, ge=1, le=100)
    name: Optional[str] = None

class {ModuleName}Create(BaseModel):
    """创建参数"""
    name: str = Field(..., max_length=100)
    status: int = Field(default=1)

class {ModuleName}Update(BaseModel):
    """更新参数"""
    id: int
    name: Optional[str] = None
    status: Optional[int] = None
```

### 统一响应格式

所有接口使用 `respModel` 返回统一格式：

```python
from core.resp_model import respModel

# 成功响应
return respModel.ok_resp(obj=data, msg="操作成功")

# 错误响应
return respModel.error_resp("错误信息")

# 响应结构
{
    "code": 200,      # 200成功, 500失败
    "msg": "消息",
    "data": {}        # 数据对象
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
uvicorn app:application --host 0.0.0.0 --port 5000 --reload
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/api/test_user_api.py -v

# 生成覆盖率报告
pytest tests/ --cov=. --cov-report=html
```

### 数据库操作

```bash
# 初始化数据库
python scripts/init_database.py init

# 仅创建表结构
python scripts/init_database.py create-tables

# 重置数据库 (危险!)
python scripts/init_database.py reset
```

---

## 配置说明

### 环境变量 (.env)

```env
# 数据库类型: sqlite 或 mysql
DB_TYPE=sqlite
SQLITE_DATABASE=./data/ai_agent.db

# MySQL配置 (DB_TYPE=mysql 时使用)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=testdb

# JWT配置
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=480

# 消息队列: memory 或 rabbitmq
QUEUE_TYPE=memory

# AI API Keys (可选)
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
```

### 默认账号

- **用户名**: `admin`
- **密码**: `admin123`

---

## 核心模块说明

### 1. 登录认证

- **POST /login** - 用户登录，返回 JWT token
- **GET /userinfo** - 获取当前用户信息
- **POST /refreshToken** - 刷新 token

### 2. RBAC 权限 (sysmanage)

- 用户管理: `/user/*`
- 角色管理: `/role/*`
- 菜单管理: `/menu/*`
- 部门管理: `/dept/*`

### 3. API 测试 (apitest)

- 项目管理: `/ApiProject/*`
- 接口管理: `/ApiInfo/*`
- 用例管理: `/ApiInfoCase/*`
- 测试集合: `/ApiCollectionInfo/*`
- 测试历史: `/ApiHistory/*`
- 报告查看: `/ApiReportViewer/*`

### 4. AI 测试助手 (aiassistant) ⭐

- AI 模型管理: `/AiModel/*`
- 提示词模板: `/PromptTemplate/*`
- 测试用例: `/TestCase/*`
- **流式对话**: `POST /AiConversation/stream` (SSE)

### 5. 代码生成器 (generator)

- 表配置: `/GenTable/*`
- 代码生成: `/Generator/*`

---

## 依赖注入

```python
from core.database import get_session
from core.dependencies import get_current_user

# 数据库会话
session: Session = Depends(get_session)

# 当前登录用户 (需要 JWT 认证)
current_user: dict = Depends(get_current_user)
```

---

## 注意事项

1. **数据库选择**: 开发环境默认使用 SQLite，生产环境建议 MySQL
2. **路由注册**: 新增 Controller 后需在 `app.py` 中注册路由
3. **CORS**: 生产环境需配置具体允许的域名
4. **密码安全**: 生产环境必须修改 SECRET_KEY
5. **文件上传**: 需要 MinIO 服务支持
6. **WebSocket**: 测试执行进度通过 WebSocket 实时推送

---

## 相关文档

- [README.md](./README.md) - 项目详细说明
- [tests/README.md](./tests/README.md) - 测试指南
- [API 文档](http://localhost:5000/docs) - Swagger UI (启动后访问)
