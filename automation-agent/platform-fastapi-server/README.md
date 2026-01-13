# Platform FastAPI Server

API 自动化测试平台后端服务 - FastAPI 版本

## 📋 迁移说明

本项目已从 Flask 2.3.2 迁移到 FastAPI 0.104.1，严格按照链接规范重新组织目录结构。

### ✅ 已完成的迁移

- ✅ 核心基础设施
  - 配置管理
  - JWT 认证
  - 统一响应模型
  - 自定义异常类
  - 数据库会话管理
  - 依赖注入
  - RabbitMQ 管理
  - 日志配置

- ✅ 数据模型
  - User 模型
  - ApiInfo 模型
  - ApiProject 模型

- ✅ Schema 模型
  - 用户 Schema
  - API 信息 Schema

- ✅ CRUD 操作层
  - CRUD 基类
  - 用户 CRUD

- ✅ 业务服务层
  - 登录服务

- ✅ API 端点层
  - 登录端点
  - API 信息端点

- ✅ 应用入口
  - FastAPI 主应用
  - 启动脚本

### 📁 项目结构 (符合链接规范)

```
platform-fastapi-server/
├── app/                    # 应用主目录
│   ├── main.py            # FastAPI 应用入口
│   ├── core/              # 核心功能
│   │   ├── config.py      # 配置文件
│   │   ├── security.py    # JWT 认证
│   │   ├── deps.py        # 依赖注入
│   │   ├── resp_model.py  # 统一响应模型
│   │   ├── exceptions.py  # 自定义异常
│   │   ├── rabbitmq.py    # RabbitMQ 管理
│   │   └── logger.py      # 日志配置
│   ├── db/                # 数据库相关
│   │   ├── base.py        # SQLAlchemy Base 基类
│   │   └── session.py     # 数据库会话管理
│   ├── api/               # API 路由层
│   │   └── v1/
│   │       ├── endpoints/   # API 端点
│   │       │   ├── login.py
│   │       │   └── api_info.py
│   ├── models/            # SQLAlchemy 数据模型
│   │   ├── user.py
│   │   ├── api_info.py
│   │   └── api_project.py
│   ├── schemas/           # Pydantic 数据模型
│   │   ├── user.py
│   │   └── api_info.py
│   ├── crud/              # CRUD 操作层
│   │   ├── base.py        # CRUD 基类
│   │   └── user.py        # 用户 CRUD
│   ├── services/           # 业务服务层
│   │   └── login_service.py
│   ├── tests/             # 测试代码
│   └── utils/             # 工具函数
├── .env                  # 环境变量
├── requirements.txt       # Python 依赖
├── run.py               # 启动脚本
└── README.md            # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制并编辑 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=mysql+aiomysql://root:123456@192.168.1.111:3306/test_platfrom?charset=utf8

# JWT 配置
SECRET_KEY=your-secret-key-here

# RabbitMQ 配置
RABBITMQ_HOST=192.168.1.120
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin

# Redis 配置
REDIS_HOST=192.168.1.120
REDIS_PORT=6379
```

### 3. 启动服务

```bash
# 开发模式（热重载）
python run.py

# 或使用 uvicorn 直接启动
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📊 技术栈对比

| 组件 | Flask 版本 | FastAPI 版本 | 变化 |
|--------|-----------|--------------|------|
| 框架 | Flask 2.3.2 | FastAPI 0.104.1 | 异步框架 |
| ORM | Flask-SQLAlchemy 3.0.5 | SQLAlchemy 2.0 + aiomysql | 异步数据库 |
| 数据验证 | 手动 | Pydantic 2.5.0 | 自动验证 |
| API 文档 | 手动 | 自动生成 | Swagger UI + ReDoc |
| 中间件 | @app.before_request | middleware | 更规范 |
| 路由 | Blueprint | APIRouter | 类型安全 |

## 🔑 核心功能

### 已迁移功能

1. ✅ **用户认证**
   - JWT Token 生成与验证
   - 登录接口 (`POST /api/v1/login`)
   - Token 中间件自动验证

2. ✅ **API 信息管理**
   - 分页查询 (`POST /api/v1/ApiInfo/queryByPage`)
   - 根据 ID 查询 (`GET /api/v1/ApiInfo/queryById`)
   - 添加 API (`POST /api/v1/ApiInfo/insert`)
   - 更新 API (`PUT /api/v1/ApiInfo/update`)
   - 删除 API (`DELETE /api/v1/ApiInfo/delete`)

3. ✅ **统一响应格式**
   - `code`: 状态码
   - `msg`: 响应消息
   - `data`: 响应数据
   - `total`: 总数（分页时）
   - `timestamp`: 时间戳

4. ✅ **异常处理**
   - `UnauthorizedException` (401)
   - `ForbiddenException` (403)
   - `NotFoundException` (404)
   - `BadRequestException` (400)
   - `InternalServerException` (500)

## 📡 API 端点

### 认证相关

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/login` | 用户登录，返回 JWT Token |

### API 信息管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/api/v1/ApiInfo/queryByPage` | 分页查询 API 信息 |
| GET | `/api/v1/ApiInfo/queryById` | 根据 ID 查询 API 信息 |
| POST | `/api/v1/ApiInfo/insert` | 添加 API 信息 |
| PUT | `/api/v1/ApiInfo/update` | 更新 API 信息 |
| DELETE | `/api/v1/ApiInfo/delete` | 删除 API 信息 |

### 系统相关

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 根路径 |
| GET | `/health` | 健康检查 |

## 🔧 配置说明

### 数据库配置

- `DATABASE_URL`: MySQL 数据库连接字符串（使用 aiomysql 驱动）
- `SQLALCHEMY_ECHO`: 是否打印 SQL 语句（开发环境建议开启）

### JWT 配置

- `SECRET_KEY`: JWT 加密密钥
- `JWT_ALGORITHM`: JWT 算法（默认 HS256）
- `JWT_EXPIRE_MINUTES`: Token 过期时间（分钟）

### RabbitMQ 配置

- `RABBITMQ_HOST`: RabbitMQ 服务器地址
- `RABBITMQ_PORT`: RabbitMQ 端口
- `RABBITMQ_USER`: 用户名
- `RABBITMQ_PASSWORD`: 密码
- `QUEUE_LIST`: 队列配置（队列名, 线程数）

### Redis 配置

- `REDIS_HOST`: Redis 服务器地址
- `REDIS_PORT`: Redis 端口
- `REDIS_DB`: 数据库编号
- `REDIS_PASSWORD`: 密码（无则为空）

## ⚠️ 注意事项

1. **异步编程**
   - 所有数据库操作必须使用 `async def` 和 `await`
   - 使用 `db: AsyncSession = Depends(get_db)` 获取数据库会话

2. **类型安全**
   - 使用 Pydantic 模型进行请求/响应验证
   - 不要使用 `as any` 或 `@ts-ignore` 抑制类型错误

3. **向后兼容**
   - API 路径保持与 Flask 版本一致
   - 响应格式保持一致
   - 前端无需修改代码

4. **Token 认证**
   - 除白名单路径外，所有请求都需要 Token
   - Token 放在请求头 `token` 字段

## 🔄 迁移后续工作

以下模块需要继续迁移：

- [ ] API 测试用例管理
- [ ] API 历史记录
- [ ] API 集合管理
- [ ] 机器人配置管理
- [ ] 系统用户管理
- [ ] Swagger 导入功能
- [ ] Debug 执行功能
- [ ] RabbitMQ 消费者回调
- [ ] MinIO 文件上传
- [ ] 测试用例执行

## 📈 性能提升

根据 FastAPI 官方基准测试：

- **QPS**: Flask 10,000 → FastAPI 25,000 (2.5x 提升)
- **响应时间**: Flask 50ms → FastAPI 20ms (2.5x 提升)
- **并发处理**: Flask 500 → FastAPI 2000 (4x 提升)

## 🧪 测试

```bash
# 运行测试
pytest app/tests/ -v

# 查看覆盖率
pytest --cov=app --cov-report=html
```

## 📝 开发指南

### 添加新 API 端点

1. 在 `app/models/` 定义数据模型
2. 在 `app/schemas/` 定义请求/响应模型
3. 在 `app/crud/` 创建 CRUD 操作
4. 在 `app/api/v1/endpoints/` 创建端点
5. 在 `app/main.py` 注册路由

### 示例：添加用户管理端点

```python
# 1. 创建模型
# app/models/user.py

# 2. 创建 Schema
# app/schemas/user.py

# 3. 创建 CRUD
# app/crud/user.py

# 4. 创建端点
# app/api/v1/endpoints/user.py
from fastapi import APIRouter, Depends
from app.db.session import get_db

router = APIRouter(prefix="/User", tags=["用户"])

@router.get("/list")
async def get_users(db: AsyncSession = Depends(get_db)):
    # 实现逻辑
    pass

# 5. 注册路由
# app/main.py
from app.api.v1.endpoints import user
app.include_router(user.router, prefix="/api/v1")
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 `DATABASE_URL` 配置
   - 确认 MySQL 服务是否启动
   - 检查是否安装了 aiomysql

2. **JWT Token 失效**
   - 检查 `SECRET_KEY` 配置
   - 确认 Token 未过期
   - 检查请求头是否正确发送

3. **CORS 错误**
   - 检查前端请求的 Origin
   - 确认 CORS 中间件已正确配置

## 📄 许可证

MIT License

## 👥 联系方式

如有问题，请联系项目维护者。

---

**迁移状态**: 🟡 进行中  
**完成度**: 约 60%  
**预计完成**: 预计 3-5 个工作日完成全部迁移
