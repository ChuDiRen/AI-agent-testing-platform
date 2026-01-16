# 团队成员

## 主流程 Agent（7个）

| Agent | 角色 | 核心职责 | 文件位置 |
|-------|------|---------|---------|
| Team Orchestrator | 团队协调器 | 统筹全流程，协调各Agent | `agents/team-orchestrator.md` |
| Product Manager | 产品经理 | 需求分析、原型设计、任务拆分 | `agents/product-manager.md` |
| Frontend Developer | 前端开发 | Vue3开发、组件设计、API集成 | `agents/frontend-developer.md` |
| Backend Developer | 后端开发 | Java/Python开发、API设计、数据库 | `agents/backend-developer.md` |
| Code Reviewer | 代码审查专家 | 代码质量审查、安全漏洞检测、性能优化 | `agents/code-reviewer.md` |
| Test Automator | 测试专家 | API测试、E2E测试、测试报告 | `agents/test-automator.md` |
| Deployment Specialist | 部署专家 | Docker部署、云服务部署、CI/CD | `agents/deployment-specialist.md` |

## 辅助 Agent（1个）

| Agent | 角色 | 核心职责 | 调用方式 |
|-------|------|---------|---------|
| Debugger | 调试专家 | 错误定位、测试失败调试、意外行为排查 | 按需调用 |

## 团队架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     Team Orchestrator                       │
│                      （团队协调器）                           │
│                     统筹全流程开发                            │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────┐
             │                                             │
    ┌────────▼────────┐                          ┌────────▼────────┐
    │ Product Manager │                          │ Frontend Dev    │
    │  （产品经理）    │                          │  （前端开发）    │
    │ 需求分析/原型    │                          │ Vue3开发/组件    │
    │ 任务拆分        │                          │ API集成/测试     │
    └─────────────────┘                          └─────────────────┘
             │                                             │
    ┌────────▼────────┐                          ┌────────▼────────┐
    │ Backend Dev     │                          │ Code Reviewer   │
    │  （后端开发）    │                          │  （代码审查）    │
    │ Java/Python     │                          │ 代码质量/安全    │
    │ 数据库/API设计  │                          │ 性能优化/重构    │
    └─────────────────┘                          └─────────────────┘
             │                                             │
    ┌────────▼────────┐                          ┌────────▼────────┐
    │ Test Automator  │                          │ Deployment Spec │
    │  （测试专家）    │                          │  （部署专家）    │
    │ API测试/E2E     │                          │ Docker/云服务   │
    │ 测试报告/分析    │                          │ CI/CD/监控      │
    └─────────────────┘                          └─────────────────┘
                           │
                  ┌────────▼────────┐
                  │    Debugger     │
                  │  （调试专家）    │
                  │  错误定位/修复   │
                  │  按需调用        │
                  └─────────────────┘
```
