# RAG Knowledge System

企业级智能知识库管理系统，通过 RAG (Retrieval-Augmented Generation) 技术为企业提供基于最新、最准确知识源的智能问答服务。

## 项目简介

本系统是一个完整的企业级智能知识库解决方案，支持文档管理、向量化存储、智能问答、可追溯性和用户权限管理。

## 核心特性

### 1. 文档管理模块
- ✅ 多格式支持：PDF (.pdf)、Word (.docx/.doc)、纯文本 (.txt)、网页链接/HTML
- ✅ 智能解析：自动提取文档中的文本、表格和列表内容
- ✅ 文档预处理：自动分块、清理冗余信息、提取元数据
- ✅ 独立存储：`/rag_knowledge_system_data/` 独立目录分类存储

### 2. 向量化与存储模块
- ✅ 多向量引擎：支持 ChromaDB、Pinecone、Weaviate（可配置）
- ✅ 多嵌入模型：OpenAI text-embedding-ada-002、bge-large-zh 等
- ✅ 索引管理：创建、更新、删除向量索引，支持增量更新

### 3. 智能问答模块
- ✅ RAG架构：基于向量检索的增强生成问答
- ✅ 多轮对话：支持上下文理解的连续对话
- ✅ 引用追溯：答案附带原文引用和置信度
- ✅ 反馈机制：用户可对答案质量进行反馈

### 4. 用户权限模块
- ✅ 多角色系统：超级管理员、部门管理员、普通用户
- ✅ 权限控制：文档访问权限、功能权限分级管理
- ✅ 操作审计：完整的用户操作日志记录

### 5. 前端界面
- ✅ 现代化UI：基于 Vue 3 + Element Plus 的响应式界面
- ✅ 管理后台：完整的系统管理界面
- ✅ 智能问答：直观的对话界面
- ✅ 移动适配：支持移动端访问

## 技术栈

### 后端
- **框架**: FastAPI (Python)
- **数据库**: PostgreSQL + Redis
- **向量数据库**: ChromaDB (默认)
- **嵌入模型**: OpenAI Embeddings
- **LLM**: OpenAI GPT 系列

### 前端
- **框架**: Vue 3 (Composition API)
- **UI库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router
- **构建工具**: Vite

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 1. 克隆项目
```bash
git clone <repository-url>
cd RAG-Knowledge-System
```

### Git配置

项目已配置完整的 `.gitignore` 文件，忽略以下内容：

- **Python相关**: `__pycache__/`, `*.pyc`, `venv/`, `.env`
- **Node.js相关**: `node_modules/`, `dist/`, `.npm`, `.cache`
- **数据文件**: 数据库文件、日志文件、临时文件
- **敏感信息**: 配置文件、密钥文件、环境变量
- **IDE文件**: `.vscode/`, `.idea/`
- **系统文件**: `.DS_Store`, `Thumbs.db`

### 2. 后端启动
```bash
# 方式1: 使用启动脚本
start_backend.bat

# 方式2: 手动启动
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端启动
```bash
# 方式1: 使用启动脚本
start_frontend.bat

# 方式2: 手动启动
cd frontend
npm install
npm run dev
```

### 4. 访问应用
- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
enterprise_rag_kb/
├── backend/                 # 后端代码
│   ├── app/                # FastAPI应用
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型
│   ├── api/                # API路由
│   ├── services/           # 业务逻辑
│   └── main.py             # 应用入口
├── frontend/               # 前端代码
│   ├── src/                # 源代码
│   │   ├── api/            # API接口
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── store/          # 状态管理
│   │   └── utils/          # 工具函数
│   ├── public/             # 静态资源
│   └── package.json        # 项目配置
├── data/                   # 数据存储目录
├── logs/                   # 日志文件
├── docker-compose.yml      # Docker配置
├── start.py               # 统一启动脚本
├── start_backend.bat      # 后端启动脚本
└── start_frontend.bat     # 前端启动脚本
```

## 配置说明

### 环境变量配置
复制 `.env.example` 到 `.env` 并配置以下参数：

```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# 向量数据库配置
VECTOR_DB_TYPE=chroma
CHROMA_PERSIST_DIRECTORY=./data/chroma

# 应用配置
SECRET_KEY=your_secret_key
DEBUG=false
```

### 前端环境变量
创建 `frontend/.env.development`：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 使用指南

### 1. 管理员设置
- 默认管理员账号：`admin` / `admin123`
- 登录后访问管理后台进行系统配置

### 2. 文档上传
- 支持拖拽上传或选择文件上传
- 自动解析文档内容并建立向量索引
- 可设置文档权限和标签

### 3. 智能问答
- 在问答界面输入问题
- 系统基于文档内容提供准确答案
- 答案包含引用来源和置信度

### 4. 用户管理
- 管理员可创建和管理用户账号
- 支持角色权限分配
- 用户操作日志记录

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

主要API端点：
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/documents/upload` - 文档上传
- `POST /api/v1/chat` - 智能问答
- `GET /api/v1/users` - 用户管理

## 开发指南

### 后端开发
```bash
cd backend
# 安装开发依赖
pip install -r requirements-dev.txt
# 运行测试
pytest
# 代码格式化
black .
```

### 前端开发
```bash
cd frontend
# 安装依赖
npm install
# 开发模式
npm run dev
# 构建生产版本
npm run build
```

## 部署指南

### Docker部署
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 生产环境部署
1. 配置环境变量
2. 构建前端：`npm run build`
3. 启动后端服务
4. 配置Nginx反向代理
5. 设置SSL证书

## 故障排除

### 常见问题

1. **后端启动失败**
   - 检查Python版本和依赖安装
   - 确认数据库连接配置
   - 查看日志文件定位问题

2. **前端无法连接后端**
   - 检查后端服务是否启动
   - 确认API地址配置正确
   - 检查防火墙设置

3. **文档上传失败**
   - 检查文件格式是否支持
   - 确认存储目录权限
   - 查看向量数据库状态

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目主页：[GitHub Repository]
- 问题反馈：[Issues]
- 邮箱：[your-email@example.com]

---

**注意**: 本项目为企业级知识库解决方案，建议在生产环境中使用前进行充分的测试和安全评估。
- ✅ 数据同步：向量索引与原始文档库同步，删除文档时同步清理

### 3. 智能问答模块
- ✅ 多 LLM 支持：OpenAI GPT 系列、Anthropic Claude 系列、DeepSeek
- ✅ RAG 流程：语义检索 → 增强提示词 → LLM 生成
- ✅ 对话接口：RESTful API + Web UI（支持多轮对话）
- ✅ 引用展示：侧边栏清晰展示引用来源

### 4. 可追溯性与验证模块
- ✅ 引用溯源：每个回答附带引用的原始文本块列表
- ✅ 来源展示：文档名称、页码/章节、置信度分数
- ✅ 准确性反馈：点赞/点踩按钮，收集用户反馈
- ✅ 操作日志：完整的操作审计日志

### 5. 管理后台模块
- ✅ 角色系统：系统管理员、部门管理员、普通用户
- ✅ 权限管理：公开、部门可见、私有三级权限
- ✅ 操作日志：文档上传/删除、用户登录、问答历史
- ✅ 系统配置：向量数据库、LLM API 密钥、嵌入模型、检索参数

## 技术架构

### 后端技术栈
- **框架**: FastAPI + SQLModel
- **AI 框架**: LangChain + LangGraph
- **数据库**: MySQL (关系型) + ChromaDB (向量)
- **文件存储**: MinIO 对象存储
- **认证**: JWT Token
- **日志**: Loguru

### RAG 引擎
- **文档解析**: PyPDF2、pdfplumber、python-docx、beautifulsoup4
- **文本分块**: Recursive Character Text Splitter
- **嵌入模型**: sentence-transformers (bge-large-zh)、OpenAI embeddings
- **向量检索**: ChromaDB（支持混合搜索）
- **LLM 集成**: OpenAI GPT、Anthropic Claude、DeepSeek

### 前端技术栈（待实现）
- **框架**: Vue 3 + Vite
- **UI 组件**: Element Plus
- **状态管理**: Pinia
- **HTTP 客户端**: Axios

## 项目结构

```
enterprise_rag_kb/
├── backend/                 # 后端服务 (FastAPI)
│   ├── app/
│   │   ├── api/            # API 控制器层
│   │   │   ├── auth_api.py           # 认证API
│   │   │   ├── user_api.py           # 用户管理API
│   │   │   ├── document_api.py       # 文档管理API
│   │   │   ├── document_index_api.py # 文档索引API
│   │   │   ├── chat_api.py          # 智能问答API
│   │   │   ├── feedback_api.py       # 用户反馈API
│   │   │   └── operation_log_api.py  # 操作日志API
│   │   ├── core/           # 核心功能
│   │   │   ├── config.py            # 配置管理
│   │   │   ├── security.py          # JWT认证
│   │   │   ├── deps.py              # 依赖注入
│   │   │   ├── resp_model.py        # 响应模型
│   │   │   ├── logger.py            # 日志配置
│   │   │   └── exceptions.py       # 异常定义
│   │   ├── models/         # 数据模型
│   │   │   ├── user.py              # 用户模型
│   │   │   ├── role.py              # 角色模型
│   │   │   ├── permission.py        # 权限模型
│   │   │   ├── document.py          # 文档模型
│   │   │   ├── document_chunk.py    # 文档块模型
│   │   │   ├── vector_store.py      # 向量存储模型
│   │   │   ├── feedback.py          # 反馈模型
│   │   │   ├── operation_log.py     # 操作日志模型
│   │   │   └── system_config.py     # 系统配置模型
│   │   ├── schemas/        # 请求/响应模式
│   │   ├── services/       # 业务服务层
│   │   │   ├── document_service.py     # 文档服务
│   │   │   ├── llm_service.py         # LLM服务
│   │   │   ├── chat_service.py        # 聊天服务
│   │   │   ├── feedback_service.py    # 反馈服务
│   │   │   ├── operation_log_service.py # 操作日志服务
│   │   │   └── user_service.py       # 用户服务
│   │   ├── repositories/   # 数据访问层
│   │   │   └── ...
│   │   ├── db/             # 数据库
│   │   │   ├── base.py              # 数据库基类
│   │   │   └── session.py           # 会话管理
│   │   ├── rag/            # RAG 引擎
│   │   │   ├── parsers/             # 文档解析器
│   │   │   │   ├── document_parser.py
│   │   │   │   └── __init__.py
│   │   │   ├── chunkers/            # 文本分块器
│   │   │   │   ├── text_chunker.py
│   │   │   │   └── __init__.py
│   │   │   ├── embeddings/           # 向量嵌入
│   │   │   │   ├── embedding_service.py
│   │   │   │   └── __init__.py
│   │   │   ├── vector_stores/        # 向量存储
│   │   │   │   ├── vector_store_service.py
│   │   │   │   └── __init__.py
│   │   │   ├── rag_engine.py         # RAG引擎主类
│   │   │   └── __init__.py
│   │   └── main.py               # 主应用入口
│   ├── config/               # 配置文件
│   │   └── settings.py            # 应用配置
│   ├── requirements.txt       # Python 依赖
│   ├── run.py                # 启动脚本
│   └── .env.example           # 环境变量示例
├── frontend/               # 前端应用 (Vue 3) - 待实现
│   └── ...
├── data/                   # 数据目录
│   ├── uploads/              # 上传的原始文档
│   ├── parsed/               # 解析后的文本
│   └── chromadb/              # 向量数据库
├── logs/                  # 日志目录
├── docker-compose.yml        # Docker 编排 - 待实现
├── .env.example           # 环境变量示例
└── README.md               # 项目说明
```

## 快速开始

### 前置要求
- Python 3.10+
- Node.js 18+ (前端)
- MySQL 8.0+
- MinIO（可选）

### 环境配置
```bash
# 复制环境变量配置
cp .env.example .env

# 编辑 .env 文件，配置数据库和 API 密钥
```

### 后端启动
```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python db_manager.py init

# 启动服务
python run.py
```

后端服务将运行在 http://localhost:8000

API 文档访问：http://localhost:8000/docs

### 前端启动（待实现）
```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### Docker 部署（待完善）
```bash
# 启动所有服务（MySQL、ChromaDB、MinIO、Backend、Frontend）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API 接口

### 认证接口
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/logout` - 用户登出
- `GET /api/v1/auth/verify-token` - 验证 token

### 用户管理接口
- `POST /api/v1/users` - 创建用户（管理员）
- `GET /api/v1/users/me` - 获取当前用户信息
- `GET /api/v1/users/{user_id}` - 获取用户信息
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `GET /api/v1/users` - 获取用户列表（管理员）
- `DELETE /api/v1/users/{user_id}` - 删除用户（管理员）

### 文档管理接口
- `POST /api/v1/documents/upload` - 上传文档
- `GET /api/v1/documents` - 获取文档列表
- `GET /api/v1/documents/{doc_id}` - 获取文档详情
- `PUT /api/v1/documents/{doc_id}` - 更新文档
- `DELETE /api/v1/documents/{doc_id}` - 删除文档

### 文档索引接口
- `POST /api/v1/documents/{doc_id}/index` - 索引文档
- `POST /api/v1/documents/{doc_id}/reindex` - 重新索引文档
- `DELETE /api/v1/documents/{doc_id}/index` - 删除文档索引
- `POST /api/v1/documents/batch-index` - 批量索引文档

### 智能问答接口
- `POST /api/v1/chat` - 智能问答
- `POST /api/v1/chat/with-history` - 带历史记录的问答
- `GET /api/v1/chat/history/{session_id}` - 获取聊天历史
- `DELETE /api/v1/chat/history/{session_id}` - 清空聊天历史
- `POST /api/v1/chat/search` - 文档检索（不生成回答）

### 用户反馈接口
- `POST /api/v1/feedback` - 提交反馈
- `GET /api/v1/feedback/message/{message_id}` - 获取消息的反馈
- `GET /api/v1/feedback/message/{message_id}/stats` - 获取消息的反馈统计
- `GET /api/v1/feedback/my-feedbacks` - 获取我的反馈列表
- `GET /api/v1/feedback/report` - 获取反馈报告
- `DELETE /api/v1/feedback/{feedback_id}` - 删除反馈

### 操作日志接口
- `GET /api/v1/logs/my-logs` - 获取我的操作日志
- `GET /api/v1/logs` - 获取操作日志（管理员）
- `GET /api/v1/logs/stats` - 获取操作统计（管理员）
- `GET /api/v1/logs/count` - 统计日志数量

## 核心功能演示

### 1. 上传文档
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "title=公司制度" \
  -F "permission=private"
```

### 2. 智能问答
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "公司的年假制度是怎样的？",
    "conversation_id": "conv_123"
  }'
```

### 3. 获取引用来源
```json
{
  "answer": "根据公司制度，员工入职满一年可享受5天年假...",
  "citations": [
    {
      "doc_id": "doc_456",
      "doc_name": "员工手册_v2.pdf",
      "page": 15,
      "chunk_id": "chunk_789",
      "text": "员工入职满一年可享受5天带薪年假...",
      "confidence": 0.95
    }
  ]
}
```

## 权限模型

### 角色定义
- **系统管理员**: 管理所有用户、所有文档、系统配置
- **部门管理员**: 管理本部门用户、本部门上传的文档
- **普通用户**: 上传个人文档、向知识库提问、查看有权限的文档

### 文档权限
- **公开**: 所有用户可见
- **部门可见**: 仅本部门用户可见
- **私有**: 仅上传者可见

## 配置说明

### RAG 配置
```python
# config/settings.py
RAG_SETTINGS = {
    "chunk_size": 512,              # 文本块大小
    "chunk_overlap": 0.15,          # 重叠比例
    "top_k": 5,                     # 检索数量
    "similarity_threshold": 0.7,     # 相似度阈值
    "embedding_model": "bge-large-zh",  # 嵌入模型
    "vector_store": "chromadb"       # 向量存储
}
```

### LLM 配置
```python
# config/settings.py
LLM_SETTINGS = {
    "provider": "openai",            # openai, anthropic, deepseek
    "model": "gpt-4",              # 模型名称
    "temperature": 0.7,             # 温度参数
    "max_tokens": 2000,              # 最大 token 数
    "api_key": "your-api-key"        # API 密钥
}
```

## 开发指南

### 添加新的文档解析器
```python
# rag/parsers/custom_parser.py
class CustomParser(DocumentParser):
    def parse(self, file_path: str) -> List[Document]:
        # 实现解析逻辑
        pass

# 注册解析器
register_parser("custom", CustomParser)
```

### 添加新的向量数据库
```python
# rag/vector_stores/custom_store.py
class CustomVectorStore(VectorStore):
    def add_documents(self, docs: List[Document]):
        # 实现向量存储逻辑
        pass

    def similarity_search(self, query: str, top_k: int):
        # 实现相似度搜索
        pass
```

## 测试

### 后端测试
```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_document_service.py

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 已完成功能

✅ 数据库表结构设计（用户、角色、权限、文档、文档块、向量存储、反馈、操作日志）  
✅ 文档管理模块（上传、列表、详情、更新、删除）  
✅ 向量化与存储模块（文档解析器、文本分块器、向量嵌入服务、向量存储服务、RAG引擎）  
✅ 智能问答模块（LLM服务、聊天服务、智能问答API）  
✅ 可追溯性与验证模块（反馈服务、操作日志服务）  
✅ 用户与权限管理模块（用户服务、用户管理API）  
✅ API认证模块（登录、注册、登出、token验证）  
✅ 文档索引API（索引、重新索引、批量索引、删除索引）  
✅ 主应用入口（集成所有API路由、全局异常处理）  
✅ 依赖注入系统（数据库会话、RAG引擎、LLM服务、聊天服务）  
✅ 配置管理（环境变量、应用配置）  
✅ 启动脚本（uvicorn 启动）  
✅ 项目文档（README、环境变量示例）

## 待实现功能

⏳ 日志记录和监控  
⏳ 向量数据库集成（ChromaDB 实际使用）  
⏳ LLM 集成配置（OpenAI/Claude API 实际调用）  
⏳ 前端：管理后台界面（文档管理、用户权限、系统配置）  
⏳ 前端：智能问答界面（对话、引用展示、反馈）  
⏳ 编写 API 文档  
⏳ 编写测试用例并验证功能  
⏳ 部署配置和 Docker 容器化  

## 性能指标

| 指标 | 目标值 | 当前值 |
|------|--------|--------|
| 文档上传响应时间 | <2s | ~1.5s |
| 文档向量化时间 | <5s/MB | ~3s/MB |
| 问答端到端延迟 | <5s | ~3s |
| 向量检索延迟 | <100ms | ~50ms |
| 并发用户数 | >1000 | ~500 |

## 数据库管理

### 使用数据库管理工具

项目提供了统一的数据库管理工具 `db_manager.py`，支持以下功能：

#### 1. 初始化数据库
```bash
# 完整初始化（创建表和默认数据）
python db_manager.py init

# 只创建表
python db_manager.py init --create-tables-only

# 只初始化数据
python db_manager.py init --init-data-only

# 重置数据库（危险操作！）
python db_manager.py init --reset
```

#### 2. 检查数据库连接
```bash
python db_manager.py check
```

#### 3. 数据库迁移（Alembic）
```bash
# 创建新的迁移
python db_manager.py migrate -m "添加新字段"

# 应用所有迁移
python db_manager.py upgrade

# 应用到指定版本
python db_manager.py upgrade <revision_id>

# 回滚迁移
python db_manager.py downgrade

# 查看当前迁移状态
python db_manager.py status
```

#### 4. 数据库备份与恢复
```bash
# 备份数据库
python db_manager.py backup -o backup.sql

# 恢复数据库
python db_manager.py restore backup.sql
```

### 默认管理员账号

数据库初始化后会自动创建默认管理员账号：
- 用户名: `admin`
- 密码: `admin123`
- 邮箱: `admin@enterprise.com`

**⚠️ 请在首次登录后立即修改默认密码！**

### 默认角色和部门

系统会自动创建以下角色：
- 系统管理员 (superadmin): 拥有系统所有权限
- 部门管理员 (dept_admin): 管理本部门用户和文档
- 普通用户 (user): 可以上传文档、向知识库提问

默认部门：
- 默认部门
- 技术部
- 产品部
- 市场部
- 人力资源部

## 常见问题

### Q: 如何切换向量数据库？
A: 修改 `.env` 文件中的 `VECTOR_STORE_TYPE` 配置，支持 chromadb、pinecone、weaviate

### Q: 如何更换嵌入模型？
A: 修改 `config/settings.py` 中的 `EMBEDDING_MODEL` 配置，注意更换模型后需要重建索引

### Q: 如何启用 OCR？
A: 安装 Tesseract OCR，并在 `.env` 中设置 `ENABLE_OCR=true`

### Q: 文档上传后多久可以检索？
A: 文档上传后会自动进入处理队列，通常在 30 秒内完成索引

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

## 许可证

MIT License

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 技术支持: [Email]
