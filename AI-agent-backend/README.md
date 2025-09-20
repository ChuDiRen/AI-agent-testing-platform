# AI Agent Backend

企业级五层架构FastAPI应用 - AI智能代理后端服务

## 项目概述

AI Agent Backend是一个基于FastAPI的企业级后端应用，采用严格的五层架构设计，提供高性能、可扩展的API服务。项目遵循最佳实践，包含完整的认证授权、缓存、日志、测试和部署方案。

## 架构设计

### 五层架构

```
┌─────────────────┐
│   Controller    │  ← HTTP请求处理层
├─────────────────┤
│      DTO        │  ← 数据传输对象层
├─────────────────┤
│    Service      │  ← 业务逻辑层
├─────────────────┤
│   Repository    │  ← 数据访问层
├─────────────────┤
│     Entity      │  ← 数据库实体层
└─────────────────┘
```

### 技术栈

- **框架**: FastAPI 0.104.1
- **数据库**: SQLAlchemy 2.0 + Alembic
- **缓存**: Redis
- **认证**: JWT (python-jose)
- **密码**: bcrypt
- **日志**: Loguru
- **测试**: Pytest
- **容器**: Docker + Docker Compose
- **代码质量**: Black + isort + flake8 + mypy

## 项目结构

```
AI-agent-backend/
├── app/                          # 应用主目录
│   ├── controller/               # Controller层 - HTTP请求处理
│   │   ├── __init__.py
│   │   ├── base.py              # Controller基类
│   │   └── user_controller.py   # 用户Controller
│   ├── dto/                     # DTO层 - 数据传输对象
│   │   ├── __init__.py
│   │   ├── base.py              # DTO基类
│   │   ├── user/                # 用户DTO
│   │   └── indicator_parameter/ # 指标参数DTO
│   ├── service/                 # Service层 - 业务逻辑
│   │   ├── __init__.py
│   │   ├── base.py              # Service基类
│   │   └── user_service.py      # 用户Service
│   ├── repository/              # Repository层 - 数据访问
│   │   ├── __init__.py
│   │   ├── base.py              # Repository基类
│   │   ├── user_repository.py   # 用户Repository
│   │   └── indicator_parameter_repository.py
│   ├── entity/                  # Entity层 - 数据库实体
│   │   ├── __init__.py
│   │   ├── base.py              # Entity基类
│   │   ├── user.py              # 用户实体
│   │   └── indicator_parameter.py
│   ├── core/                    # 核心功能
│   │   ├── __init__.py
│   │   ├── config.py            # 配置管理
│   │   ├── security.py          # 安全认证
│   │   └── logger.py            # 日志配置
│   ├── db/                      # 数据库
│   │   ├── __init__.py
│   │   ├── base.py              # 数据库基类
│   │   └── session.py           # 会话管理
│   ├── middleware/              # 中间件
│   │   ├── __init__.py
│   │   ├── cors.py              # CORS中间件
│   │   ├── auth.py              # 认证中间件
│   │   └── logging.py           # 日志中间件
│   ├── utils/                   # 工具模块
│   │   ├── __init__.py
│   │   ├── helpers.py           # 助手函数
│   │   ├── redis_client.py      # Redis客户端
│   │   └── exceptions.py        # 自定义异常
│   └── tests/                   # 测试模块
│       ├── __init__.py
│       ├── conftest.py          # 测试配置
│       ├── test_base.py         # 测试基类
│       └── test_user_controller.py
├── alembic/                     # 数据库迁移
│   ├── versions/                # 迁移版本
│   ├── env.py                   # 环境配置
│   └── script.py.mako           # 脚本模板
├── scripts/                     # 脚本目录
│   ├── init_db.py               # 数据库初始化
│   └── run_migrations.py        # 迁移脚本
├── logs/                        # 日志目录
├── uploads/                     # 上传文件目录
├── main.py                      # 应用入口
├── requirements.txt             # Python依赖
├── .env                         # 环境变量
├── .env.example                 # 环境变量示例
├── alembic.ini                  # Alembic配置
├── Dockerfile                   # 生产环境Docker
├── Dockerfile.dev               # 开发环境Docker
├── docker-compose.yml           # 生产环境编排
├── docker-compose.dev.yml       # 开发环境编排
├── .gitignore                   # Git忽略文件
└── README.md                    # 项目文档
```

## 快速开始

### 环境要求

- Python 3.11+
- Redis (可选，用于缓存)
- PostgreSQL (生产环境推荐) 或 SQLite (开发环境)

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd AI-agent-backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑环境变量
vim .env
```

#### 数据库配置

项目支持通过环境变量控制数据库类型：

**使用 SQLite（开发环境推荐）**：
```bash
DATABASE_TYPE=sqlite
SQLITE_FILE=./ai_agent.db
```

**使用 PostgreSQL（生产环境推荐）**：
```bash
DATABASE_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ai_agent_db
```

### 初始化数据库

```bash
# 初始化数据库
python scripts/init_db.py

# 或者使用Alembic迁移
python scripts/run_migrations.py init
python scripts/run_migrations.py upgrade
```

### 启动应用

#### 快速启动（推荐）

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh && ./start.sh
```

#### 手动启动

```bash
# 开发环境
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 启动Redis（可选，用于缓存）

```bash
# 使用Docker启动Redis
docker run -d --name ai-agent-redis -p 6379:6379 redis:7-alpine

# 或者如果本地安装了Redis
redis-server
```

**注意**: Redis是可选的，应用在没有Redis的情况下仍可正常运行，只是缓存功能会被禁用。

### 使用Docker

```bash
# 开发环境
docker-compose -f docker-compose.dev.yml up -d

# 生产环境
docker-compose up -d
```

## API文档

启动应用后，访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 主要功能

### 用户管理

- 用户注册、登录、注销
- 密码修改、重置
- 用户信息管理
- 权限控制

### 指标参数管理

- 指标参数CRUD操作
- 批量参数管理
- 参数验证和类型转换
- 参数分组和排序

### 认证授权

- JWT令牌认证
- 角色权限控制
- 中间件认证
- 令牌刷新

### 缓存系统

- Redis缓存支持
- 自动缓存管理
- 缓存失效策略

## 开发指南

### 代码规范

```bash
# 代码格式化
black .
isort .

# 代码检查
flake8 .
mypy .
```

### 新增功能特性

#### 数据验证增强
- **DataValidator**: 提供邮箱、手机号、密码强度等通用验证
- **BusinessValidator**: 提供业务逻辑相关的验证
- **配置验证**: AI代理配置、测试用例步骤等专项验证

#### 事务管理
- **@transactional装饰器**: 自动事务管理
- **transaction_scope上下文管理器**: 手动事务控制
- **TransactionManager**: 支持保存点的高级事务管理

#### 安全增强
- **SecurityHeadersMiddleware**: 自动添加安全响应头
- **RateLimitMiddleware**: IP级别的速率限制
- **RequestValidationMiddleware**: 请求内容安全检查
- **CSRFProtectionMiddleware**: CSRF攻击防护

#### 响应标准化
- **StandardResponse**: 统一的API响应格式
- **PaginatedResponse**: 分页数据响应格式
- **ResponseBuilder**: 响应构建器
- **APIResponse**: 快捷响应工具类

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest app/tests/test_user_controller.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

### 数据库管理

#### 数据库切换

使用数据库切换脚本可以轻松在SQLite和PostgreSQL之间切换：

```bash
# 查看当前数据库配置
python scripts/switch_database.py show

# 切换到SQLite（开发环境）
python scripts/switch_database.py sqlite --file ./ai_agent.db

# 切换到PostgreSQL（生产环境）
python scripts/switch_database.py postgresql \
  --host localhost \
  --port 5432 \
  --user postgres \
  --password your_password \
  --database ai_agent_db
```

#### 数据库迁移

```bash
# 创建迁移
python scripts/run_migrations.py create "migration message"

# 应用迁移
python scripts/run_migrations.py upgrade

# 回滚迁移
python scripts/run_migrations.py downgrade <revision>
```

## 部署指南

### Docker部署

```bash
# 构建镜像
docker build -t ai-agent-backend .

# 运行容器
docker run -d -p 8000:8000 ai-agent-backend
```

### 生产环境配置

1. 设置环境变量
2. 配置数据库连接
3. 设置Redis缓存
4. 配置SSL证书
5. 设置反向代理

## 监控和日志

### 日志配置

- 使用Loguru进行日志管理
- 支持文件轮转和压缩
- 结构化日志输出

### 健康检查

- 应用健康检查端点: `/health`
- 数据库连接检查
- Redis连接检查

## 安全特性

- JWT令牌认证
- 密码加密存储
- CORS跨域配置
- 请求速率限制
- 输入数据验证
- SQL注入防护

## 性能优化

- 数据库连接池
- Redis缓存
- 异步处理
- 分页查询
- 索引优化

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 项目维护者: AI Agent Team
- 邮箱: support@aiagent.com
- 文档: https://docs.aiagent.com

## 更新日志

### v1.0.0 (2023-12-01)

- 初始版本发布
- 完整的五层架构实现
- 用户管理功能
- 指标参数管理
- JWT认证系统
- Redis缓存支持
- Docker容器化
- 完整的测试覆盖
