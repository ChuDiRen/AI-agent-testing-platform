# /review - 智能代码审查

## 描述
全面代码审查，自动联动 Skills 和 Agents 进行深度分析。

## 使用方式
```
/review [目标] [--mode <模式>] [--agent]
```

## 参数
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `目标` | 文件/目录/PR | 当前变更文件 |
| `--mode` | `quick`/`full`/`security`/`performance` | `quick` |
| `--agent` | 使用独立 Agent（上下文隔离） | 否 |

## 审查模式

| 模式 | 检查范围 | 联动组件 | 耗时 |
|------|----------|----------|------|
| `quick` | 代码规范 + 明显问题 | `code-review` Skill | 1-2 分钟 |
| `full` | 规范 + 质量 + 性能 + 安全 | 多个 Skills | 3-5 分钟 |
| `security` | 仅安全检查 | `security` 插件 | 2-3 分钟 |
| `performance` | 仅性能检查 | `debugger` 插件 | 2-3 分钟 |

## 联动机制

### 自动激活
| 模式 | 激活的插件/Skill |
|------|-----------------|
| quick | `code-review` |
| full | `code-review` + `security` + `debugger` |
| security | `security` 插件 |
| performance | `debugger` 插件 |

### Agent 调用
使用 `--agent` 参数时调用对应 Agent：
- `--mode full --agent` → `code-reviewer` Agent
- `--mode security --agent` → `security-auditor` Agent

## 输出格式

参考 `@templates/review-patterns.md` 中的报告格式。

## 示例
```bash
/review                              # 快速审查当前变更
/review src/views/user/              # 审查指定目录
/review --mode full                  # 全面审查
/review --mode security --agent      # 安全专项（使用 Agent）
/review PR#123                       # 审查 PR
```
