# 团队成员（Agent + Skill 协作版）

## Agent 团队概览

| Agent | 角色 | 使用技能 | 核心职责 |
|-------|------|----------|---------|
| team-orchestrator | 团队协调器 | - | 统筹流程、调度Agent |
| product-manager | 产品经理 | brainstorm, task-splitting | 需求分析、任务拆分 |
| architect | 架构师 | architecture-design | 架构设计、阶段审核 |
| frontend-developer | 前端开发 | ui-ux-pro-max, vue3-frontend-dev | 原型设计、前端开发 |
| backend-developer | 后端开发 | database-design, api-documentation, java-springboot-dev, python-fastapi-dev | 数据库设计、API开发 |
| code-reviewer | 代码审查 | code-review | 代码质量审查 |
| test-automator | 测试专家 | api-testing, webapp-testing | API测试、E2E测试 |
| deployment-specialist | 部署专家 | docker-deploy | Docker部署 |
| debugger | 调试专家 | - | 按需调试 |

## 团队架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Team Orchestrator                            │
│                          （团队协调器）                               │
│                 使用 task 工具调度其他 Agent                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Product Manager │ │    Architect    │ │ Frontend Dev    │
│   产品经理       │ │     架构师      │ │   前端开发      │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ Skills:         │ │ Skills:         │ │ Skills:         │
│ • brainstorm    │ │ • architecture- │ │ • ui-ux-pro-   │
│ • task-splitting│ │   design        │ │   max          │
└─────────────────┘ └─────────────────┘ │ • vue3-frontend │
                                        │   -dev          │
         ┌───────────────────┐          └─────────────────┘
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Backend Dev    │ │  Code Reviewer  │ │ Test Automator  │
│   后端开发      │ │   代码审查      │ │   测试专家      │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ Skills:         │ │ Skills:         │ │ Skills:         │
│ • database-     │ │ • code-review   │ │ • api-testing   │
│   design        │ └─────────────────┘ │ • webapp-testing│
│ • api-          │                     └─────────────────┘
│   documentation │
│ • java-         │          ▼
│   springboot-dev│ ┌─────────────────┐
│ • python-       │ │ Deployment Spec │
│   fastapi-dev   │ │   部署专家      │
└─────────────────┘ ├─────────────────┤
                    │ Skills:         │
         ┌──────────│ • docker-deploy │
         │          └─────────────────┘
         ▼
┌─────────────────┐
│    Debugger     │
│   调试专家      │
│  （按需调用）    │
└─────────────────┘
```

## Command + Skill + Agent 对应关系

| Command | 执行 Agent | 使用 Skill | 输出 |
|---------|-----------|------------|------|
| /start-project | team-orchestrator | 调度所有Agent | 完整项目设计 |
| /analyze-requirement | product-manager | brainstorm | docs/requirement.md |
| /design-prototype | frontend-developer | ui-ux-pro-max | prototypes/*.html + design-system.md |
| /generate-api-doc | backend-developer | api-documentation | docs/api-docs/ |
| /generate-sequence-diagram | architect | - | docs/sequence-diagrams/ |
| /split-tasks | product-manager | task-splitting | docs/tasks-*.md |
| /develop-frontend | frontend-developer | vue3-frontend-dev | frontend/ |
| /develop-backend | backend-developer | java-springboot-dev / python-fastapi-dev | backend/ |
| /test-api | test-automator | api-testing | tests/api/ |
| /test-e2e | test-automator | webapp-testing | tests/e2e/ |
| /deploy | deployment-specialist | docker-deploy | deploy/ |

## 工作流程中的 Agent 调度

### /start-project 完整流程

```
阶段1: 需求收集
  └─ team-orchestrator（自身处理）

阶段2: 需求分析
  └─ task → product-manager + skill:brainstorm
  └─ task → architect（审核）

阶段3: 技术选型
  └─ team-orchestrator（用户选择）

阶段4: 原型设计
  └─ task → frontend-developer + skill:ui-ux-pro-max

阶段5: 数据库设计
  └─ task → backend-developer + skill:database-design
  └─ task → architect（审核）

阶段6: 接口设计
  └─ task → backend-developer + skill:api-documentation
  └─ task → architect（审核）

阶段7: 架构设计
  └─ task → architect + skill:architecture-design

阶段8: 时序图设计
  └─ task → architect

阶段9: 任务拆分
  └─ task → product-manager + skill:task-splitting
  └─ task → architect（审核）

阶段10: 脚手架初始化
  └─ task → frontend-developer + skill:vue3-frontend-dev
  └─ task → backend-developer + skill:java-springboot-dev
```

## Agent 调用规范

### 使用 task 工具调用

```
task(
  subagent_name: "{agent名称}",
  description: "{任务简述}",
  prompt: "
【阶段N：{阶段名}】

## 项目信息
- 项目目录：{path}
- 相关文件：{files}

## 任务要求
1. 使用 use_skill 加载 {skill_name} 技能
2. {具体步骤}

## 输出要求
{output_files}

## 验收标准
- [ ] {标准1}
- [ ] {标准2}
"
)
```

### Agent 内部流程

```
1. 接收任务 prompt
   ↓
2. use_skill("{skill_name}") 加载技能
   ↓
3. 阅读输入文件
   ↓
4. 按技能指导执行任务
   ↓
5. 输出到指定路径
   ↓
6. 返回执行摘要
```

## 文件位置

| 文件类型 | 位置 |
|----------|------|
| Agent 定义 | `.codebuddy/agents/{name}.md` |
| Skill 定义 | `.codebuddy/skills/{category}/{name}/SKILL.md` |
| Command 定义 | `.codebuddy/commands/{name}.md` |
| 共享配置 | `.codebuddy/shared/` |
| 规则定义 | `.codebuddy/rules/` |
