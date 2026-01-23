# Cyberpunk - API Automation Agent Platform

基于 FastAPI + React + TypeScript 的现代化 API 自动化测试平台，融合 AI Agent 智能测试生成、RAG 知识库和实时执行监控。

## 特性

- **AI 驱动测试生成**：基于 LangChain 和 OpenAI 的智能测试用例生成
- **RAG 知识库**：支持 API 文档智能检索和知识图谱探索
- **实时执行控制台**：可视化测试执行过程和结果分析
- **现代化技术栈**：FastAPI + React 19 + TypeScript + Ant Design + TailwindCSS
- **多模态支持**：支持文档、图片等多种格式的 API 文档解析

## 技术栈

### 后端
- Python 3.11+
- FastAPI - 高性能异步 Web 框架
- LangChain - AI Agent 编排框架
- OpenAI - 大语言模型
- Pydantic - 数据验证

### 前端
- React 19
- TypeScript
- Ant Design - UI 组件库
- TailwindCSS - 样式框架
- Vite - 构建工具
- React Router - 路由管理

## 快速开始

### 后端启动

#### 方法一：使用 uv（推荐）

```bash
# 安装 uv
pip install uv

# 创建并激活虚拟环境
uv venv
.\.venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -r requirements.txt

# 配置环境变量
cp app/.env.example app/.env
# 编辑 app/.env 文件，填入你的 OpenAI API Key

# 启动服务
python run.py
```

#### 方法二：使用 pip

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp app/.env.example app/.env
# 编辑 app/.env 文件，填入你的 OpenAI API Key

# 启动服务
python run.py
```

后端服务将运行在 http://localhost:8000

API 文档访问：http://localhost:8000/docs

### 前端启动

```bash
# 进入前端目录
cd web

# 安装依赖（推荐使用 pnpm）
npm i -g pnpm  # 如果未安装 pnpm
pnpm install

# 启动开发服务器
pnpm dev
```

前端应用将运行在 http://localhost:5173

## 项目结构

```
cyberpunk/
├── app/                      # 后端应用
│   ├── api_agent/            # API Agent 模块
│   ├── api_healer/           # API 修复模块
│   ├── api_parser/           # API 解析模块
│   ├── core/                 # 核心功能
│   │   ├── anything_rag.py   # RAG 引擎
│   │   ├── config.py         # 配置管理
│   │   ├── llm_service.py    # LLM 服务
│   │   └── ...
│   ├── deep_agents/          # 深度 Agent
│   ├── mcp_servers/          # MCP 服务器
│   ├── multimodal/           # 多模态处理
│   ├── rag/                  # RAG 核心
│   ├── api_server.py         # API 服务器入口
│   ├── main.py               # 主程序
│   └── .env                  # 环境变量配置
├── web/                      # 前端应用
│   ├── src/
│   │   ├── components/       # 组件
│   │   ├── layouts/          # 布局
│   │   ├── pages/            # 页面
│   │   │   ├── AgentWorkbench.tsx
│   │   │   ├── ApiRepository.tsx
│   │   │   ├── KnowledgeGraphExplorer.tsx
│   │   │   ├── RagKnowledgeBase.tsx
│   │   │   └── ...
│   │   ├── theme/            # 主题配置
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── run.py                    # 启动脚本
├── requirements.txt          # Python 依赖
├── pyproject.toml            # 项目配置
└── README.md                 # 项目说明
```

## 主要功能模块

### 1. Agent 工作台
- AI Agent 对话界面
- 智能测试用例生成
- 实时执行反馈

### 2. API 仓库
- API 文档管理
- Swagger/OpenAPI 导入
- API 分类和搜索

### 3. RAG 知识库
- 文档智能检索
- 向量化存储
- 语义搜索

### 4. 知识图谱
- API 关系可视化
- 实体关系探索
- 依赖分析

### 5. 测试执行
- 实时执行控制台
- 测试结果分析
- 质量分析仪表板

## 环境变量配置

在 `app/.env` 文件中配置以下变量：

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# Application
ENVIRONMENT=development
DEBUG=true
HOST=0.0.0.0
PORT=8000

# MCP Servers
ENABLE_RAG_SERVER=true
ENABLE_CHART_SERVER=true
ENABLE_AUTOMATION_SERVER=true
```

## 开发指南

### 后端开发

```bash
# 运行测试
pytest

# 代码格式化
black app/
ruff check app/
```

### 前端开发

```bash
# 类型检查
pnpm type-check

# 代码检查
pnpm lint

# 构建生产版本
pnpm build
```

## 部署

### Docker 部署（待完善）

```bash
# 构建镜像
docker build -t cyberpunk .

# 运行容器
docker run -d -p 8000:8000 cyberpunk
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
