# AI Agent Testing Platform - Backend

基于FastAPI的AI智能测试平台后端服务

## 功能特性

### 核心功能

- ✅ 用户管理、角色管理、菜单管理、部门管理
- ✅ 测试用例管理（API/Web/App）
- ✅ 测试报告生成与导出
- ✅ 消息通知、数据管理

### AI功能

- ✅ 多模型AI对话（GPT-3.5/4/4-Turbo, Claude 3 Sonnet/Opus/3.5）
- ✅ 流式响应（SSE）
- ✅ 模型动态切换
- ✅ 会话历史管理

### RAG知识库

- ✅ 多格式文档支持（PDF/Word/TXT/Markdown/HTML）
- ✅ 智能文档分块
- ✅ 向量化存储（Qdrant）
- ✅ 语义相似度搜索
- ✅ BGE-large-zh-v1.5中文向量模型

### 任务队列

- ✅ Celery + Redis异步处理
- ✅ 大文件后台处理
- ✅ 实时进度跟踪
- ✅ 自动失败重试
- ✅ 批量处理支持

## 技术栈

- **Web框架**: FastAPI 0.104.1
- **数据库**: SQLite (可扩展到PostgreSQL/MySQL)
- **ORM**: SQLAlchemy 2.0 (异步)
- **AI SDK**: OpenAI 1.12.0, Anthropic 0.18.0
- **LangChain**: 0.1.0
- **向量数据库**: Qdrant 1.7.0
- **向量模型**: sentence-transformers 2.3.0 (BGE-large-zh-v1.5)
- **任务队列**: Celery 5.3.0 + Redis 5.0.0
- **文档解析**: pypdf, python-docx, markdown, beautifulsoup4

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Redis

```bash
# Windows: 下载Redis for Windows或使用Docker
docker run -d -p 6379:6379 redis:latest

# Linux/Mac
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis  # Mac
```

### 3. 初始化系统

```bash
python init_system.py
```

### 4. 启动服务

```bash
# 启动Redis
redis-server

# 启动Celery Worker
python start_celery_worker.py

# 启动FastAPI服务
python run.py

# (可选) 启动Flower监控
celery -A app.core.celery_app flower --port=5555
```

### 5. 访问服务

- API文档: <http://localhost:8000/docs>
- Flower监控: <http://localhost:5555>

### 6. 登录凭证

- 用户名: `BNTang`
- 密码: `1234qwer`

## 配置AI模型

### 1. 获取API Key

- OpenAI: <https://platform.openai.com/api-keys>
- Claude: <https://console.anthropic.com/settings/keys>

### 2. 配置模型

访问 <http://localhost:8000/docs，使用以下接口配置：>

```bash
PUT /api/v1/ai/models/{model_id}
{
  "api_key": "your-api-key",
  "is_enabled": true
}
```

## 项目结构

```
AI-agent-backend-fastapi/
├── app/
│   ├── api/              # API路由
│   ├── core/             # 核心配置
│   ├── models/           # 数据模型
│   ├── schemas/          # Pydantic Schema
│   ├── services/         # 业务逻辑
│   └── tasks/            # Celery任务
├── init_system.py        # 系统初始化脚本
├── start_celery_worker.py # Celery Worker启动脚本
├── run.py                # 主程序入口
└── requirements.txt      # 依赖列表
```

## API接口

### 认证接口

- POST `/api/v1/auth/login` - 用户登录（返回access_token和refresh_token）
- POST `/api/v1/auth/refresh` - 刷新访问令牌（使用refresh_token获取新的access_token）
- POST `/api/v1/auth/register` - 用户注册

### AI对话接口

- POST `/api/v1/ai/chat` - AI对话（支持流式）
- GET `/api/v1/ai/models` - 获取模型列表
- PUT `/api/v1/ai/models/{id}` - 更新模型配置
- POST `/api/v1/ai/models/{id}/test` - 测试模型连接

### 知识库接口

- POST `/api/v1/knowledge/bases` - 创建知识库
- GET `/api/v1/knowledge/bases` - 获取知识库列表
- POST `/api/v1/knowledge/documents/upload` - 上传文档
- POST `/api/v1/knowledge/search` - 搜索知识库
- GET `/api/v1/knowledge/tasks/{task_id}` - 查询任务状态

### 用户管理接口

- GET `/api/v1/users` - 获取用户列表
- POST `/api/v1/users` - 创建用户
- PUT `/api/v1/users/{id}` - 更新用户
- DELETE `/api/v1/users/{id}` - 删除用户

## 开发说明

### 环境变量

创建 `.env` 文件：

```env
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./app.db

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

### 数据库迁移

```bash
# 重新初始化数据库
python init_system.py
```

### 运行测试

```bash
pytest
```

## 常见问题

### Q: Worker无法启动?

A: 检查Redis是否运行: `redis-cli ping`

### Q: 任务一直PENDING?

A: 确保Worker已启动: `python start_celery_worker.py`

### Q: 文档上传失败?

A: 检查文件格式是否支持,文件大小是否超限

### Q: AI对话无响应?

A: 检查API Key是否配置正确,模型是否已启用

## 最新优化 (v2.1.0)

✨ 本版本进行了全面的功能完善和性能优化:

### 核心优化

- ✅ **安全增强**: Token黑名单、密码强度验证、API密钥加密
- ✅ **全局异常处理**: 统一异常处理、结构化日志、错误追踪
- ✅ **数据库优化**: 连接池配置、健康检查、慢查询监控
- ✅ **AI服务增强**: 真实AI测试用例生成、Token使用统计、上下文管理优化
- ✅ **知识库优化**: 文档去重、混合检索、结果重排序、统计分析
- ✅ **性能监控**: 请求追踪、性能指标记录、慢请求警告

### 新增功能

- 🔐 用户登出接口(Token黑名单)
- 📊 健康检查端点(支持K8s探针)
- 📈 知识库统计分析
- 🔍 增强的混合检索(向量+关键词)
- 📝 详细的部署文档

详细内容请查看: [OPTIMIZATION_SUMMARY.md](./OPTIMIZATION_SUMMARY.md)

## 文档

- 📖 [部署指南](./DEPLOYMENT.md) - 详细的部署和配置说明
- 📋 [优化总结](./OPTIMIZATION_SUMMARY.md) - 完整的优化内容说明
- 📚 API文档: <http://localhost:8000/docs>

## 许可证

Copyright (c) 2025 左岚. All rights reserved.

## 联系方式

- 开发团队: 左岚团队
- 版本: v2.1.0 (已全面优化)
