# 🧩 Claude Code 插件体系

本目录包含整合后的 4 个核心插件，消除了原有配置中的重复内容。

## 插件列表

| 插件 | 说明 | 包含组件 |
|------|------|----------|
| **code-quality** | 代码质量检查与审查 | `/check`, `/review`, `code-review` Skill, `code-reviewer` Agent |
| **security** | 安全审计 | `/security`, `security-guard` Skill, `security-auditor` Agent |
| **debugger** | 调试排查与性能分析 | `/debug`, `/perf`, `bug-detective` Skill, `performance` Skill, `debugger` Agent |
| **fullstack** | 全栈开发 | `/dev`, `/crud`, `crud-development` Skill, `ui-pc` Skill, `backend-architect` Agent, `frontend-developer` Agent |

## 共享模板

所有插件引用 `templates/` 目录下的共享模板：

| 模板 | 说明 |
|------|------|
| `code-patterns.md` | 后端四层架构 + 前端 Vue 组件模板 |
| `security-patterns.md` | OWASP 检查清单 + 漏洞修复模式 |
| `review-patterns.md` | 代码审查清单 + 报告格式 |
| `debug-patterns.md` | 排查流程 + 错误速查表 |

## 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🧩 Claude Code 插件体系                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ 📦 code-quality │  │ 📦 security     │  │ 📦 fullstack    │             │
│  │    Plugin       │  │    Plugin       │  │    Plugin       │             │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤             │
│  │ /check          │  │ /security       │  │ /crud           │             │
│  │ /review         │  │ security-guard  │  │ /dev            │             │
│  │ code-review     │  │ security-auditor│  │ crud-development│             │
│  │ code-reviewer   │  │                 │  │ ui-pc           │             │
│  └────────┬────────┘  └────────┬────────┘  │ frontend-dev    │             │
│           │                    │           │ backend-arch    │             │
│           │                    │           └────────┬────────┘             │
│           │                    │                    │                      │
│  ┌────────┴────────┐           │                    │                      │
│  │ 📦 debugger     │           │                    │                      │
│  │    Plugin       │           │                    │                      │
│  ├─────────────────┤           │                    │                      │
│  │ /debug          │           │                    │                      │
│  │ /perf           │           │                    │                      │
│  │ bug-detective   │           │                    │                      │
│  │ performance     │           │                    │                      │
│  │ debugger        │           │                    │                      │
│  └────────┬────────┘           │                    │                      │
│           │                    │                    │                      │
│           └────────────────────┼────────────────────┘                      │
│                                │                                           │
│                    ┌───────────┴───────────┐                               │
│                    │   📚 templates/       │                               │
│                    │   (共享模板库)         │                               │
│                    ├───────────────────────┤                               │
│                    │ code-patterns.md      │                               │
│                    │ security-patterns.md  │                               │
│                    │ review-patterns.md    │                               │
│                    │ debug-patterns.md     │                               │
│                    └───────────────────────┘                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 使用方式

### Commands
```bash
# 代码质量
/check                    # 快速检查
/review --mode full       # 全面审查

# 安全
/security                 # 安全扫描
/security --agent         # 深度审计

# 调试
/debug "错误描述"          # 问题排查
/perf --target db         # 性能分析

# 开发
/dev 用户管理模块          # 全栈开发
/crud User                # CRUD 生成
```

### 联动机制
- `/review --mode full` 自动调用 `security` + `debugger` 插件
- `/review --mode security --agent` 调用 `security-auditor` Agent
- `/dev --agent` 调用 `backend-architect` + `frontend-developer` Agent

## 迁移说明

原有配置已整合到插件中：

| 原文件 | 新位置 |
|--------|--------|
| `commands/check.md` | `plugins/code-quality/check.md` |
| `commands/review.md` | `plugins/code-quality/review.md` |
| `commands/security.md` | `plugins/security/security-command.md` |
| `commands/debug.md` | `plugins/debugger/debug-command.md` |
| `commands/perf.md` | `plugins/debugger/perf-command.md` |
| `skills/code-review/` | `plugins/code-quality/code-review-skill.md` |
| `skills/security-guard/` | `plugins/security/security-guard-skill.md` |
| `skills/bug-detective/` | `plugins/debugger/bug-detective-skill.md` |
| `skills/performance/` | `plugins/debugger/performance-skill.md` |
| `skills/crud-development/` | `plugins/fullstack/crud-development-skill.md` |
| `skills/ui-pc/` | `plugins/fullstack/ui-pc-skill.md` |
| `agents/code-reviewer.md` | `plugins/code-quality/code-reviewer-agent.md` |
| `agents/security-auditor.md` | `plugins/security/security-auditor-agent.md` |
| `agents/debugger.md` | `plugins/debugger/debugger-agent.md` |
| `agents/backend-architect.md` | `plugins/fullstack/backend-architect-agent.md` |
| `agents/frontend-developer.md` | `plugins/fullstack/frontend-developer-agent.md` |
