# CodeBuddy 配置使用指南

## 📁 目录结构

```
.codebuddy/
├── agents/                    # AI 角色代理（7个）
│   ├── project-bootstrapper.md    # 项目启动专家
│   ├── frontend-developer.md      # 前端开发专家
│   ├── backend-developer.md       # 后端开发专家（自动识别技术栈）
│   ├── code-reviewer.md           # 代码审查专家
│   ├── debugger.md                # 调试专家
│   ├── data-scientist.md          # 数据分析专家
│   └── test-automator.md          # 测试自动化专家（自动识别技术栈）
│
├── commands/                  # 快捷命令（3个，自动识别技术栈）
│   ├── code-review.md             # 代码审查
│   ├── generate-api-doc.md        # API 文档生成
│   └── generate-tests.md          # 测试生成
│
├── rules/                     # 规则（2个）
│   ├── code-reuse-check.mdc       # always: 代码复用检查
│   └── task-splitting.mdc         # requested: 任务拆分
│
└── skills/                    # 技能知识库（9个）
    ├── design/                    # 设计规范
    │   ├── api-documentation/     # API 文档规范
    │   ├── database-design/       # 数据库设计
    │   ├── frontend-design/       # 前端设计指南
    │   └── prototype-design/      # 原型设计
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
Commands (命令)    →  快捷操作入口（自动识别技术栈）
Agents (智能体)    →  定义"谁来做"（自动识别技术栈）
Skills (技能)      →  定义"怎么做"的规范和工具
```

## 🚀 如何使用

### 方式一：使用 Commands（推荐）

在 Chat 中直接输入命令（自动识别 Python/Go/JS）：

```bash
# 代码审查（自动识别技术栈）
/code-review app/routes/user.py
/code-review internal/handler/
/code-review src/components/

# API 文档生成（自动识别技术栈）
/generate-api-doc api/
/generate-api-doc internal/handler/

# 测试生成（自动识别技术栈）
/generate-tests services/user_service.py
/generate-tests pkg/service/
```

### 方式二：调用 Agent

在 Chat 窗口中使用 `@` 符号：

```
@project-bootstrapper 启动一个用户管理系统项目
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
use skill prototype-design
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
/generate-tests [文件/目录]
```

### 调试
```
@debugger 分析 [错误信息]
```

## 📚 Commands 说明

| Command | 用途 | 特点 |
|---------|------|------|
| `/code-review` | 代码审查 | 自动识别 Python/Go/JS |
| `/generate-api-doc` | API 文档生成 | 自动识别 FastAPI/Gin 等 |
| `/generate-tests` | 测试生成 | 自动识别 pytest/go test/Jest |

## 📚 Agents 说明

| Agent | 用途 | 特点 |
|-------|------|------|
| project-bootstrapper | 项目启动 | 含原型设计、任务拆分 |
| frontend-developer | 前端开发 | React/Vue 专家 |
| backend-developer | 后端开发 | 自动识别 Go/Python/Java |
| code-reviewer | 代码审查 | 质量、安全、可维护性 |
| test-automator | 测试自动化 | 自动识别测试框架 |
| debugger | 调试 | 错误分析专家 |
| data-scientist | 数据分析 | SQL 和数据洞察 |

## 📚 Rules 说明

| Rule | 类型 | 用途 |
|------|------|------|
| code-reuse-check | always | 开发前自动检查可复用代码 |
| task-splitting | requested | 按需进行任务拆分 |

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
第三步: /generate-tests services/
第四步: /code-review services/
```
