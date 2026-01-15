# CodeBuddy 配置使用指南

## 📁 目录结构

```
.codebuddy/
├── agents/                    # AI 角色代理（8个）
│   ├── project-bootstrapper.md    # 项目启动专家
│   ├── team-orchestrator.md       # Agent 团队编排者（意图识别/分派）
│   ├── frontend-developer.md      # 前端开发专家
│   ├── backend-developer.md       # 后端开发专家（自动识别技术栈）
│   ├── code-reviewer.md           # 代码审查专家
│   ├── debugger.md                # 调试专家
│   ├── data-scientist.md          # 数据分析专家
│   └── test-automator.md          # 测试自动化专家（调用测试 Skills）
│
├── commands/                  # 快捷命令（6个）
│   ├── start.md                   # 项目启动（一次确认后全自动）
│   ├── dev.md                     # 快速开发（自动识别前/后端并可并行）
│   ├── fullstack.md               # 全栈开发（前后端并行 + 审查）
│   ├── code-review.md             # 代码审查
│   ├── generate-api-doc.md        # API 文档生成（调用 api-documentation）
│   └── generate-tests.md          # 测试生成（调用 api-testing/webapp-testing）
│
├── rules/                     # 规则（3个）
│   ├── code-reuse-check.mdc       # always: 代码复用检查
│   ├── file-naming.mdc            # always: 文件命名规范v3.0（含迭代工作流）
│   └── task-splitting.mdc         # requested: 任务拆分
│
└── skills/                    # 技能知识库（9个，含教程/示例）
    ├── design/                    # 设计规范
    │   ├── api-documentation/     # API 文档规范
    │   ├── database-design/       # 数据库设计
    │   └── frontend-design/       # 前端设计指南
    ├── development/               # 开发规范
    │   └── mcp-builder/           # MCP 服务器开发
    ├── testing/                   # 测试工具
    │   ├── api-testing/           # API 接口测试（含脚本和示例）
    │   └── webapp-testing/        # Web 应用测试（含脚本和示例）
    └── workflows/                 # 工作流
        ├── project-bootstrap/     # 项目启动工作流
        └── skill-creator/         # 技能创建指南
```

## 🏗️ 架构设计

```
Rules (规则)       →  自动/按需生效的约束
Commands (命令)    →  快捷操作入口 → 调用 Skills
Agents (智能体)    →  定义"谁来做" → 调用 Skills
Skills (技能)      →  定义"怎么做"的规范和工具
```

## 🚀 如何使用

### 方式一：使用 Commands（推荐）

在 Chat 中直接输入命令：

```bash
# 项目启动（一次确认后全自动）
/start 订单管理系统

# 快速开发（自动识别前/后端；可并行）
/dev 实现用户登录 API
/dev 实现用户列表页面

# 全栈开发（强制前后端并行 + 自动审查）
/fullstack 用户管理功能

# 代码审查
/code-review app/routes/user.py
/code-review internal/handler/
/code-review src/components/

# API 文档生成（调用 api-documentation skill）
/generate-api-doc api/
/generate-api-doc internal/handler/

# 测试生成（根据类型调用对应 skill）
/generate-tests unit services/user_service.py
/generate-tests api app/api/user.py
/generate-tests e2e src/views/login.vue
```

### 方式二：调用 Agent

在 Chat 窗口中使用 `@` 符号：

```
@project-bootstrapper 启动一个用户管理系统项目
@team-orchestrator 识别需求并分派合适的 Agent 执行
@frontend-developer 创建一个数据表格组件
@backend-developer 设计用户管理 API
@code-reviewer 审查 app/routes/user.py
@test-automator 为 services/ 生成测试
@debugger 分析这个错误
@data-scientist 分析用户行为数据
```

### 方式三：使用 Skills

在 Chat 中通过 `use skill` 调用：

```
use skill api-testing
use skill webapp-testing
use skill frontend-design
```

## 📋 敏捷开发工作流

### Sprint 启动
```
@project-bootstrapper 启动 [项目名]
```

### 日常开发
```
@frontend-developer 实现 [功能]
@backend-developer 实现 [API]
```

### 代码审查
```
/code-review [文件/目录]
```

### API 文档
```
/generate-api-doc [路由文件]
```

### 测试生成
```
/generate-tests unit [文件/目录]
/generate-tests api [API文件]
/generate-tests e2e [页面文件]
```

### 调试
```
@debugger 分析 [错误信息]
```

## 📚 Commands 说明

| Command | 用途 | 调用 Skill |
|---------|------|-----------|
| `/start` | 项目启动（一次确认后全自动） | `project-bootstrap`（由 project-bootstrapper 编排） |
| `/dev` | 快速开发（自动识别前/后端） | - |
| `/fullstack` | 全栈开发（前后端并行 + 审查） | - |
| `/code-review` | 代码审查 | - |
| `/generate-api-doc` | API 文档生成 | `api-documentation` |
| `/generate-tests` | 测试生成 | `api-testing` / `webapp-testing` |

## 📚 Agents 说明

| Agent | 用途 | 调用 Skill |
|-------|------|-----------|
| project-bootstrapper | 项目启动 | `project-bootstrap` |
| team-orchestrator | 意图识别与任务分派 | - |
| frontend-developer | 前端开发 | - |
| backend-developer | 后端开发 | - |
| code-reviewer | 代码审查 | - |
| test-automator | 测试自动化 | `api-testing` / `webapp-testing` |
| debugger | 调试 | - |
| data-scientist | 数据分析 | - |

## 📚 Rules 说明

| Rule | 类型 | 用途 |
|------|------|------|
| `code-reuse-check` | always | 代码复用检查，在生成业务代码前先检查现有代码 |
| `file-naming-v3` | always | 文件命名规范v3.0。核心文档固定位置增量更新，原型页面统一管理，历史版本完整归档 |
| `task-splitting` | requested | 任务拆分规则。当用户需要将产品需求拆分为可执行的开发任务时使用 |

## 🎯 最佳实践

### 1. 开发前自动检查复用

`code-reuse-check` 规则会自动生效，无需手动调用。

### 2. 代码审查使用统一命令

```
/code-review app/routes/
```

### 3. 分阶段使用

```
第一步: @backend-developer 设计 API
第二步: 实现代码
第三步: /generate-tests api services/
第四步: /code-review services/
```
