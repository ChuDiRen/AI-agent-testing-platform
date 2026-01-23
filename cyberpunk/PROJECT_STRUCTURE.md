# Cyberpunk 项目结构说明

## 目录结构

```
cyberpunk/
├── app/                          # 后端应用目录
│   ├── api_agent/                # API Agent 模块
│   │   ├── api/                  # API 路由
│   │   ├── db/                   # 数据库
│   │   ├── main.py               # Agent 主程序
│   │   ├── models.py             # 数据模型
│   │   └── settings.py           # 配置
│   ├── api_healer/               # API 修复模块
│   │   └── core.py               # 核心逻辑
│   ├── api_parser/               # API 解析模块
│   │   └── core.py               # 解析核心
│   ├── core/                     # 核心功能模块
│   │   ├── anything_rag.py       # RAG 引擎
│   │   ├── api_parser.py         # API 解析器
│   │   ├── config.py             # 配置管理
│   │   ├── database_config.py    # 数据库配置
│   │   ├── data_persistence.py   # 数据持久化
│   │   ├── document_indexer.py   # 文档索引
│   │   ├── entity_extractor.py   # 实体提取
│   │   ├── error_handler.py      # 错误处理
│   │   ├── full_rag_engine.py    # 完整 RAG 引擎
│   │   ├── knowledge_graph.py    # 知识图谱
│   │   ├── llm_service.py        # LLM 服务
│   │   ├── logging_config.py     # 日志配置
│   │   ├── mcp_client.py         # MCP 客户端
│   │   ├── models.py             # 数据模型
│   │   ├── multimodal_processor.py # 多模态处理
│   │   ├── relationship_extractor.py # 关系提取
│   │   ├── session_manager.py    # 会话管理
│   │   ├── simple_rag.py         # 简单 RAG
│   │   ├── task_manager.py       # 任务管理
│   │   └── virtual_file_system.py # 虚拟文件系统
│   ├── deep_agents/              # 深度 Agent
│   │   ├── config.py             # 配置
│   │   ├── core.py               # 核心逻辑
│   │   └── simple_core.py        # 简化核心
│   ├── mcp_servers/              # MCP 服务器
│   │   ├── automation_quality_server.py # 自动化质量服务器
│   │   ├── chart_server.py       # 图表服务器
│   │   └── rag_server.py         # RAG 服务器
│   ├── multimodal/               # 多模态模块
│   │   └── core.py               # 核心逻辑
│   ├── rag/                      # RAG 模块
│   │   └── core.py               # RAG 核心
│   ├── api_server.py             # FastAPI 服务器入口
│   ├── main.py                   # 主程序入口
│   ├── .env                      # 环境变量配置（需自行创建）
│   └── .env.example              # 环境变量模板
├── web/                          # 前端应用目录
│   ├── public/                   # 静态资源
│   │   └── vite.svg              # Vite 图标
│   ├── src/                      # 源代码
│   │   ├── assets/               # 资源文件
│   │   │   └── react.svg         # React 图标
│   │   ├── components/           # 组件
│   │   │   ├── api-repository/   # API 仓库组件
│   │   │   │   ├── ApiDetail.tsx
│   │   │   │   ├── ApiList.tsx
│   │   │   │   ├── ApiTree.tsx
│   │   │   │   ├── data.ts
│   │   │   │   ├── ImportApiModal.tsx
│   │   │   │   └── types.ts
│   │   │   ├── ui/               # UI 基础组件
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   └── Input.tsx
│   │   │   └── Logo.tsx          # Logo 组件
│   │   ├── layouts/              # 布局
│   │   │   └── DashboardLayout.tsx # 仪表板布局
│   │   ├── lib/                  # 工具库
│   │   │   └── utils.ts          # 工具函数
│   │   ├── pages/                # 页面
│   │   │   ├── AgentWorkbench.tsx # Agent 工作台
│   │   │   ├── ApiRepository.tsx  # API 仓库
│   │   │   ├── EnvironmentSettings.tsx # 环境设置
│   │   │   ├── HomeOverview.tsx   # 首页概览
│   │   │   ├── Integrations.tsx   # 集成管理
│   │   │   ├── JobQueueHistory.tsx # 任务队列历史
│   │   │   ├── KnowledgeGraphExplorer.tsx # 知识图谱
│   │   │   ├── LiveExecutionConsole.tsx # 实时执行控制台
│   │   │   ├── Login.tsx          # 登录页
│   │   │   ├── PromptLibrary.tsx  # 提示词库
│   │   │   ├── QualityAnalyticsDashboard.tsx # 质量分析
│   │   │   ├── RagChunkDebugger.tsx # RAG 调试器
│   │   │   ├── RagKnowledgeBase.tsx # RAG 知识库
│   │   │   ├── TeamPermissions.tsx # 团队权限
│   │   │   ├── TestCaseManagement.tsx # 测试用例管理
│   │   │   ├── TestRunReportDetail.tsx # 测试报告详情
│   │   │   ├── TestSuiteOrchestration.tsx # 测试套件编排
│   │   │   ├── UserProfileSettings.tsx # 用户设置
│   │   │   └── WorkspaceSelection.tsx # 工作空间选择
│   │   ├── theme/                # 主题
│   │   │   └── antdTheme.ts      # Ant Design 主题配置
│   │   ├── App.tsx               # 应用主组件
│   │   ├── index.css             # 全局样式
│   │   └── main.tsx              # 应用入口
│   ├── .gitignore                # Git 忽略文件
│   ├── eslint.config.js          # ESLint 配置
│   ├── index.html                # HTML 入口
│   ├── package.json              # 项目依赖
│   ├── pnpm-lock.yaml            # pnpm 锁文件
│   ├── postcss.config.js         # PostCSS 配置
│   ├── README.md                 # 前端说明
│   ├── tailwind.config.js        # Tailwind 配置
│   ├── tsconfig.json             # TypeScript 配置
│   ├── tsconfig.app.json         # 应用 TS 配置
│   ├── tsconfig.node.json        # Node TS 配置
│   └── vite.config.ts            # Vite 配置
├── .dockerignore                 # Docker 忽略文件
├── .gitignore                    # Git 忽略文件
├── Dockerfile                    # Docker 配置
├── Makefile                      # Make 命令
├── PROJECT_STRUCTURE.md          # 本文件
├── QUICKSTART.md                 # 快速启动指南
├── README.md                     # 项目说明
├── pyproject.toml                # Python 项目配置
├── requirements.txt              # Python 依赖
├── run.py                        # 启动脚本
└── start.bat                     # Windows 启动脚本
```

## 模块说明

### 后端模块

#### 1. API Agent (`app/api_agent/`)
- 负责 API 相关的智能处理
- 包含 API 路由、数据库操作和业务逻辑

#### 2. API Healer (`app/api_healer/`)
- API 自动修复功能
- 检测和修复 API 问题

#### 3. API Parser (`app/api_parser/`)
- 解析各种格式的 API 文档
- 支持 OpenAPI、GraphQL、Postman 等

#### 4. Core (`app/core/`)
核心功能模块，包含：
- **RAG 引擎**：检索增强生成
- **LLM 服务**：大语言模型集成
- **知识图谱**：API 关系图谱
- **任务管理**：异步任务调度
- **数据持久化**：数据存储管理

#### 5. Deep Agents (`app/deep_agents/`)
- 深度学习 Agent
- 复杂任务处理

#### 6. MCP Servers (`app/mcp_servers/`)
- Model Context Protocol 服务器
- 提供 RAG、图表、自动化等服务

### 前端模块

#### 1. 页面 (`web/src/pages/`)
- **AgentWorkbench**：AI Agent 交互界面
- **ApiRepository**：API 文档管理
- **KnowledgeGraphExplorer**：知识图谱可视化
- **RagKnowledgeBase**：RAG 知识库管理
- **LiveExecutionConsole**：实时测试执行
- **QualityAnalyticsDashboard**：质量分析仪表板

#### 2. 组件 (`web/src/components/`)
- **api-repository**：API 仓库相关组件
- **ui**：基础 UI 组件

#### 3. 布局 (`web/src/layouts/`)
- **DashboardLayout**：主仪表板布局

## 技术栈

### 后端
- **FastAPI**：Web 框架
- **LangChain**：AI Agent 编排
- **OpenAI**：大语言模型
- **Pydantic**：数据验证

### 前端
- **React 19**：UI 框架
- **TypeScript**：类型安全
- **Ant Design**：组件库
- **TailwindCSS**：样式框架
- **Vite**：构建工具

## 数据流

```
用户请求 → 前端 (React) → API (FastAPI) → Agent (LangChain) → LLM (OpenAI)
                                    ↓
                            RAG 知识库 / 知识图谱
                                    ↓
                            测试生成 / 执行
                                    ↓
                            结果返回 → 前端展示
```

## 配置文件

- `app/.env`：后端环境变量
- `web/.env`：前端环境变量（可选）
- `pyproject.toml`：Python 项目配置
- `package.json`：前端项目配置
