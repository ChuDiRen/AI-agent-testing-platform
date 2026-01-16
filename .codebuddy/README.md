# 前后端分离开发团队

## 概述

本系统基于 **Command + Skill + Agent** 架构，提供完整的前后端分离项目开发团队，支持从需求分析到部署上线的全流程开发。

### 核心特点

- **智能协调**：团队协调器统一调度，高效协作
- **专业分工**：7个主流程Agent + 1个辅助Agent
- **标准化流程**：10阶段开发流程，质量可控
- **多技术栈**：支持Java Spring Boot、Python FastAPI、Vue3
- **自动化测试**：API测试、E2E测试全覆盖
- **一键部署**：支持Docker、云服务等多种部署方式

## 快速开始

### 一键式开发（推荐）

```
用户：我需要做一个移动端H5商城，包含商品列表、购物车、订单功能
协调器：自动完成需求分析、技术选型、原型设计、任务拆分、开发、测试、部署
```

### 按需调用

```
/start-project mobile-h5 --backend=python --frontend=vant
/design-prototype
/develop-frontend TASK001
/test-api
/deploy
```

## 团队成员

> 详见 [shared/team-members.md](shared/team-members.md)

| Agent | 角色 | 核心职责 |
|-------|------|---------|
| Team Orchestrator | 团队协调器 | 统筹全流程，协调各Agent |
| Product Manager | 产品经理 | 需求分析、原型设计、任务拆分 |
| Frontend Developer | 前端开发 | Vue3开发、组件设计 |
| Backend Developer | 后端开发 | Java/Python开发、API设计 |
| Code Reviewer | 代码审查专家 | 代码质量审查、安全检测 |
| Test Automator | 测试专家 | API测试、E2E测试 |
| Deployment Specialist | 部署专家 | Docker部署、CI/CD |
| Debugger | 调试专家（辅助） | 错误定位、问题修复 |

## 开发流程

> 详见 [shared/workflow-stages.md](shared/workflow-stages.md)

```
阶段1：需求分析 → 阶段2：原型设计 → 阶段3：任务拆分 →
阶段4：API文档 → 阶段5：分端开发 → 阶段6：联调测试 →
阶段7：代码评审 → 阶段8：接口测试 → 阶段9：E2E测试 →
阶段10：部署上线
```

## 技术栈

> 详见 [shared/tech-stack.md](shared/tech-stack.md)

| 类型 | 推荐 | 适用场景 |
|------|------|---------|
| Java后端 | Spring Boot 3.x + MyBatis-Plus | 企业系统、电商平台 |
| Python后端 | FastAPI + SQLAlchemy | 数据分析、移动H5 |
| 前端 | Vue3 + Element Plus/Vant | PC端/移动端 |

## 快捷命令

> 详见 [shared/commands-reference.md](shared/commands-reference.md)

| 命令 | 功能 | 命令 | 功能 |
|------|------|------|------|
| `/start-project` | 启动项目 | `/develop-frontend` | 前端开发 |
| `/design-prototype` | 设计原型 | `/develop-backend` | 后端开发 |
| `/split-tasks` | 任务拆分 | `/test-api` | API测试 |
| `/generate-api-doc` | 生成API文档 | `/test-e2e` | E2E测试 |
| `/deploy` | 部署上线 | `/debug` | 调试问题 |

## 工作模式

### 模式1：一键式开发

用户只需提供需求，协调器自动完成全流程，每阶段需确认。

### 模式2：分阶段推进

```
用户：阶段1：需求分析
协调器：完成需求分析
用户：确认
用户：阶段2：原型设计
...
```

### 模式3：按需调用

直接使用命令，灵活控制流程。

## 文件结构

```
.codebuddy/
├── README.md                  # 本文档
├── shared/                    # 公共文档
│   ├── team-members.md       # 团队成员
│   ├── workflow-stages.md    # 工作流程
│   ├── tech-stack.md         # 技术栈
│   ├── commands-reference.md # 命令参考
│   └── project-structure.md  # 项目结构
├── agents/                    # Agent定义
├── commands/                  # 快捷命令
├── skills/                    # 技能
└── rules/                     # 规则
```

## 质量保障

- **类型安全**：强制使用TypeScript/类型注解
- **代码规范**：ESLint + Prettier / Black
- **代码审查**：测试前专业审查
- **自动化测试**：覆盖率 ≥ 80%
- **标准化流程**：10阶段质量把控

---

**开始使用**：输入 `/start-project` 即可！
