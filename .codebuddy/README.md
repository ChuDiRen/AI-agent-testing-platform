# CodeBuddy 配置使用指南

## 📁 目录结构

```
.codebuddy/
├── agents/                    # AI 角色代理
│   ├── project-bootstrapper.md    # 项目启动专家
│   ├── riper-developer.md         # RIPER-5 功能迭代专家
│   ├── frontend-developer.md      # 前端开发专家
│   ├── backend-architect-python.md # Python 后端架构师
│   ├── backend-architect-go.md    # Go 后端架构师
│   ├── code-reviewer.md           # 代码审查专家
│   ├── debugger.md                # 调试专家
│   ├── data-scientist.md          # 数据分析专家
│   ├── test-automator-python.md   # Python 测试自动化
│   └── test-automator-go.md       # Go 测试自动化
├── commands/                  # 快捷命令
│   ├── bootstrap-project.md       # 项目启动
│   ├── feature-iteration.md       # RIPER-5 功能迭代
│   ├── code-reuse-check.md        # 代码复用检查
│   ├── code-review-python.md      # Python 代码审查
│   ├── code-review-go.md          # Go 代码审查
│   ├── generate-api-doc-python.md # Python API 文档生成
│   ├── generate-api-doc-go.md     # Go API 文档生成
│   ├── generate-tests-python.md   # Python 测试生成
│   └── generate-tests-go.md       # Go 测试生成
└── skills/                    # 技能知识库
    ├── workflows/                 # 工作流
    │   ├── project-bootstrap.md   # 项目启动工作流
    │   ├── riper5-workflow.md     # RIPER-5 开发模式
    │   └── task-splitting.md      # 任务拆分方法
    ├── design/                    # 设计规范
    │   ├── prototype-design.md    # 原型设计
    │   └── api-documentation.md   # API 文档规范
    ├── development/               # 开发规范
    │   ├── frontend-development.md    # 前端开发规范
    │   ├── backend-development.md     # 后端开发规范
    │   └── code-review-checklist.md   # 代码复用检查
    └── testing/                   # 测试工具
        ├── api-testing/           # API 接口测试
        └── webapp-testing/        # Web 应用测试
```

## 🏗️ 架构设计

```
Skills (知识库)     →  定义"怎么做"的规范和模板
    ↓ 被引用
Agents (智能体)     →  定义"谁来做"，引用 Skills
    ↓ 被调用
Commands (命令)     →  定义"做什么"，调用 Agents
```

## 🚀 如何使用

### 方式一: 调用 Agent

在 Chat 窗口中使用 `@` 符号：

```
@project-bootstrapper 启动一个用户管理系统项目
@riper-developer 重构用户认证模块
@frontend-developer 创建一个数据表格组件
@backend-architect-python 设计用户管理 API
@code-reviewer 审查 app/routes/user.py
@test-automator-python 为 services/user_service.py 生成测试
```

### 方式二: 使用 Commands

直接在 Chat 中输入命令：

```
/bootstrap-project 电商管理后台 管理后台
/feature-iteration 添加用户权限管理功能
/code-reuse-check 用户认证
/code-review-python app/routes/
/generate-tests-python services/
/generate-api-doc-python api/
```

## 📋 核心工作流

### 1. 项目启动流程

```
/bootstrap-project [项目名称] [项目类型]

流程：初始化 → 需求 → 原型 → 任务拆分 → API设计 → 开发准备
```

### 2. 功能迭代流程 (RIPER-5)

```
/feature-iteration [功能描述]

流程：RESEARCH → INNOVATE → PLAN → EXECUTE → REVIEW
```

### 3. 代码开发流程

```
1. /code-reuse-check [功能描述]     # 检查是否有可复用代码
2. @frontend-developer 或 @backend-architect-python  # 开发
3. @code-reviewer 审查代码          # 代码审查
4. @test-automator-python 生成测试  # 测试生成
```

## 📚 Skills 使用

Skills 是知识库，被 Agents 和 Commands 引用：

| 类别 | Skill | 用途 |
|------|-------|------|
| workflows | project-bootstrap.md | 项目启动完整流程 |
| workflows | riper5-workflow.md | RIPER-5 开发协议 |
| workflows | task-splitting.md | 任务拆分方法 |
| design | prototype-design.md | 原型设计规范 |
| design | api-documentation.md | API 文档规范 |
| development | frontend-development.md | 前端开发规范 |
| development | backend-development.md | 后端开发规范 |
| development | code-review-checklist.md | 代码复用检查 |
| testing | api-testing/ | API 测试工具 |
| testing | webapp-testing/ | Web 测试工具 |

## 🎯 最佳实践

### 1. 明确指定 Agent

❌ 不好: "帮我看看这个代码"
✅ 好的: "@code-reviewer 审查 app/routes/user.py"

### 2. 提供上下文

❌ 不好: "生成测试"
✅ 好的: "@test-automator-python 为 services/user_service.py 生成测试，需要包含异步测试和 Mock"

### 3. 分阶段使用

```
第一步: @backend-architect-python 设计 API
第二步: 实现代码
第三步: @test-automator-python 生成测试
第四步: @code-reviewer 审查代码
```

### 4. 复杂任务使用 RIPER-5

```
/feature-iteration 重构用户权限系统

然后按提示输入：
- ENTER RESEARCH MODE
- ENTER INNOVATE MODE
- ENTER PLAN MODE
- ENTER EXECUTE MODE
- ENTER REVIEW MODE
```

## 🔧 故障排查

### Agent 没有响应

1. 确保使用 `@agent-name` 格式
2. 检查 agent 名称是否正确
3. 重启编辑器

### Commands 不生效

1. 确保使用 `/command-name` 格式
2. 提供必要的参数
3. 检查 .codebuddy 目录权限
