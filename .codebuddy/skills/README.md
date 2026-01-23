# CodeBuddy Skills

本目录包含项目级别的 Skills（技能），用于扩展 AI 助手的专业能力。

## 目录结构

```
skills/
├── design/              # 设计类技能
│   ├── api-documentation/   # API 文档生成
│   ├── architecture-design/ # 架构设计 ⭐新增
│   ├── database-design/     # 数据库设计
│   ├── ui-ux-pro-max/      # UI/UX专业设计 ⭐新增
│   └── frontend-design/     # 前端界面设计（已弃用，使用ui-ux-pro-max）
│
├── development/         # 开发类技能
│   ├── code-review/         # 代码审查 ⭐新增
│   ├── java-springboot-dev/ # Java Spring Boot 开发
│   ├── mcp-builder/         # MCP 服务器开发
│   ├── python-fastapi-dev/  # Python FastAPI 开发
│   └── vue3-frontend-dev/   # Vue3 前端开发
│
├── testing/             # 测试类技能
│   ├── api-testing/         # API 接口测试
│   └── webapp-testing/      # Web 应用测试
│
├── deployment/          # 部署类技能 ⭐新增
│   └── docker-deploy/       # Docker 部署
│
└── workflows/           # 工作流类技能
    ├── brainstorm/          # 需求分析 ⭐新增
    ├── skill-creator/       # 技能创建
    └── task-splitting/      # 任务拆分 ⭐新增
```

## Skills 清单（14 个）

| 分类 | Skill | 描述 | 关联Agent |
|------|-------|------|-----------|
| **design** | api-documentation | API 文档生成 | backend-developer |
| | architecture-design | 系统架构设计 ⭐ | architect |
| | database-design | 数据库表结构设计 | backend-developer |
| | ui-ux-pro-max | UI/UX专业设计，支持50+风格、97配色、57字体搭配 | frontend-developer |
| | frontend-design | 高质量前端界面设计（已弃用）| frontend-developer |
| **development** | code-review | 代码质量审查 ⭐ | code-reviewer |
| | java-springboot-dev | Java Spring Boot 开发 | backend-developer |
| | mcp-builder | MCP 服务器开发 | - |
| | python-fastapi-dev | Python FastAPI 开发 | backend-developer |
| | vue3-frontend-dev | Vue3 前端开发 | frontend-developer |
| **testing** | api-testing | pytest + httpx API 测试 | test-automator |
| | webapp-testing | Playwright Web 测试 | test-automator |
| **deployment** | docker-deploy | Docker 容器化部署 ⭐ | deployment-specialist |
| **workflows** | brainstorm | 需求分析与头脑风暴 ⭐ | product-manager |
| | skill-creator | 技能创建指南 | - |
| | task-splitting | 任务拆分 ⭐ | product-manager |

## Agent + Skill 映射表

| Agent | 使用的 Skills |
|-------|--------------|
| team-orchestrator | - |
| product-manager | brainstorm, task-splitting |
| architect | architecture-design |
| frontend-developer | ui-ux-pro-max, vue3-frontend-dev |
| backend-developer | database-design, api-documentation, java-springboot-dev, python-fastapi-dev |
| code-reviewer | code-review |
| test-automator | api-testing, webapp-testing |
| deployment-specialist | docker-deploy |
| debugger | - |

## Command + Skill + Agent 对应关系

| Command | Agent | Skill |
|---------|-------|-------|
| /start-project | team-orchestrator | 调度其他Agent |
| /analyze-requirement | product-manager | brainstorm |
| /design-prototype | frontend-developer | ui-ux-pro-max |
| /generate-api-doc | backend-developer | api-documentation |
| /generate-sequence-diagram | architect | - |
| /split-tasks | product-manager | task-splitting |
| /develop-frontend | frontend-developer | vue3-frontend-dev |
| /develop-backend | backend-developer | java-springboot-dev / python-fastapi-dev |
| /test-api | test-automator | api-testing |
| /test-e2e | test-automator | webapp-testing |
| /deploy | deployment-specialist | docker-deploy |

## Skill 文件结构

每个 Skill 必须遵循以下结构：

```
skill-name/
├── SKILL.md              # 必需：核心指令文件
│   ├── YAML 前置元数据
│   │   ├── name: 技能名称（必需）
│   │   └── description: 描述（必需）
│   └── Markdown 指令正文
└── 可选资源/
    ├── scripts/          # 可执行脚本
    ├── examples/         # 示例代码
    └── assets/           # 模板、图标等
```

## 使用方式

智能体在执行任务时，使用 `use_skill` 工具加载技能：

```
use_skill("skill-name")
```

例如：
```
use_skill("brainstorm")        # 需求分析
use_skill("ui-ux-pro-max")    # 原型设计
use_skill("database-design")    # 数据库设计
use_skill("api-documentation")  # API文档
use_skill("task-splitting")     # 任务拆分
use_skill("docker-deploy")      # 部署
```

## 相关 Rules

以下规则位于 `.codebuddy/rules/` 目录：

| Rule | 类型 | 描述 |
|------|------|------|
| code-reuse-check | always | 代码复用检查（生成代码前自动检查）|
| task-splitting | requested | 任务拆分规则（按需使用）|
| file-naming | requested | 文件命名规范 |
