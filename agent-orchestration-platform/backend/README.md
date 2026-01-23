# AI Agent 编排平台 - 后端服务

基于 FastAPI 构建的 AI Agent 编排与工作流管理平台后端服务。

## 功能特性

- ✅ Agent 管理（CRUD）
- ✅ Tool/MCP 工具管理
- ✅ Workflow 工作流管理
- ✅ LangGraph 执行引擎
- ✅ WebSocket 实时监控
- ✅ 用量统计与计费
- ✅ 结构化日志系统

## 技术栈

- **框架**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0 + aiomysql (异步)
- **验证**: Pydantic 2.5.0
- **工作流**: LangGraph 0.2.0
- **日志**: 结构化日志（JSON 格式）

## 快速开始

### 1. 安装依赖

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：
- `DATABASE_URL`: MySQL 数据库连接
- `OPENAI_API_KEY`: OpenAI API 密钥
- `SECRET_KEY`: JWT 加密密钥

### 3. 创建数据库

```bash
mysql -u root -p
CREATE DATABASE agent_orchestration CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 运行数据库迁移（可选）

```bash
alembic upgrade head
```

### 5. 启动服务

```bash
# 开发模式（热重载）
python run.py

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

## API 端点

### Agent 管理
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/Agent/` | 创建 Agent |
| GET | `/api/v1/Agent/` | 获取 Agent 列表 |
| GET | `/api/v1/Agent/{id}` | 获取单个 Agent |
| PUT | `/api/v1/Agent/{id}` | 更新 Agent |
| DELETE | `/api/v1/Agent/{id}` | 删除 Agent |

### Tool 管理
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/Tool/` | 创建 Tool |
| GET | `/api/v1/Tool/` | 获取 Tool 列表 |
| POST | `/api/v1/Tool/{id}/test` | 测试 Tool 连接 |
| PUT | `/api/v1/Tool/{id}` | 更新 Tool |
| DELETE | `/api/v1/Tool/{id}` | 删除 Tool |

### Workflow 管理
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/Workflow/` | 创建 Workflow |
| GET | `/api/v1/Workflow/` | 获取 Workflow 列表 |
| POST | `/api/v1/Workflow/{id}/publish` | 发布 Workflow |
| PUT | `/api/v1/Workflow/{id}` | 更新 Workflow |
| DELETE | `/api/v1/Workflow/{id}` | 删除 Workflow |

### Execution 执行
| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/Execution/` | 创建 Execution |
| WS | `/api/v1/Execution/ws/{id}` | WebSocket 实时监控 |
| POST | `/api/v1/Execution/{id}/start` | 开始执行 |
| POST | `/api/v1/Execution/{id}/cancel` | 取消执行 |

### Billing 计费
| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/Billing/usage` | 获取使用量统计 |
| GET | `/api/v1/Billing/agent-breakdown` | Agent 成本统计 |
| GET | `/api/v1/Billing/usage/history` | 使用量历史 |

## 项目结构

```
backend/
├── app/
│   ├── main.py                    # 应用入口
│   ├── core/                      # 核心模块
│   │   ├── config.py            # 配置管理
│   │   ├── logger.py            # 日志配置
│   │   └── resp_model.py        # 响应模型
│   ├── db/                        # 数据库
│   │   ├── session.py            # 会话管理
│   │   └── base.py              # SQLAlchemy 基类
│   ├── models/                    # 数据模型
│   │   └── __init__.py         # Agent, Tool, Workflow, Execution, Usage
│   ├── schemas/                   # Pydantic 模型
│   │   └── __init__.py         # Create/Update/Response schemas
│   ├── crud/                      # CRUD 操作
│   │   ├── base.py              # 通用 CRUD 基类
│   │   ├── agent_crud.py         # Agent CRUD
│   │   ├── tool_crud.py          # Tool CRUD
│   │   ├── workflow_crud.py      # Workflow CRUD
│   │   └── execution_crud.py     # Execution CRUD
│   ├── services/                  # 业务服务
│   │   ├── execution_service.py   # LangGraph 执行引擎
│   │   ├── websocket_service.py   # WebSocket 管理
│   │   └── monitoring_service.py # 执行监控
│   └── api/v1/endpoints/          # API 端点
│       ├── agents.py
│       ├── workflows.py
│       ├── tools.py
│       ├── executions.py
│       └── billing.py
├── requirements.txt
├── .env
├── run.py
└── README.md
```

## 开发指南

### 添加新的 API 端点

1. 在 `app/models/` 定义数据模型
2. 在 `app/schemas/` 定义请求/响应模型
3. 在 `app/crud/` 创建 CRUD 操作
4. 在 `app/api/v1/endpoints/` 创建端点
5. 在 `app/main.py` 注册路由

示例：

```python
# app/models/example.py
from app.db.base import Base
from sqlalchemy import Column, Integer, String

class Example(Base):
    __tablename__ = "examples"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

# app/schemas/example_schema.py
from pydantic import BaseModel

class ExampleCreate(BaseModel):
    name: str

class ExampleResponse(BaseModel):
    id: int
    name: str

# app/crud/example_crud.py
from app.crud.base import CRUDBase
from app.models import Example

class CRUDExample(CRUDBase[Example, ExampleCreate, ExampleCreate]):
    pass

example = CRUDExample(Example)

# app/api/v1/endpoints/example.py
from fastapi import APIRouter, Depends
from app.crud.example_crud import example
from app.schemas import ExampleCreate, ExampleResponse
from app.db.session import get_db
from app.core.resp_model import RespModel

router = APIRouter(prefix="/Example", tags=["Example"])

@router.post("/", response_model=RespModel)
async def create_example(example_in: ExampleCreate, db = Depends(get_db)):
    example = await example.create(db, obj_in=example_in)
    return RespModel.ok_resp(data=example)
```

### 日志使用

```python
from app.core.logger import setup_logger

logger = setup_logger(name="module")

logger.info("Info message")
logger.error("Error message", exc_info=True)
logger.warning("Warning message")
```

## 测试

```bash
# 运行所有测试
pytest app/tests/ -v

# 运行特定测试文件
pytest app/tests/test_agents.py -v

# 查看覆盖率
pytest --cov=app --cov-report=html
```

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t agent-orchestration-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env agent-orchestration-backend
```

### 生产环境建议

1. 设置 `DEBUG=False`
2. 使用强密码
3. 配置 CORS 白名单
4. 启用 HTTPS
5. 配置日志轮转
6. 使用数据库连接池
7. 设置资源限制

## 许可证

MIT License
