# /agent - SubAgent 调度中心

## 描述
调用专业 SubAgent 处理复杂任务，独立上下文不污染主对话。

## 使用方式
```
/agent <agent名称> [任务描述]
```

## 可用 SubAgents

### 开发类
| Agent | 说明 | 适用场景 |
|-------|------|----------|
| `frontend-developer` | 前端开发专家 | Vue3/React 组件开发 |
| `backend-architect` | 后端架构师 | API 设计、架构决策 |
| `database-architect` | 数据库架构师 | 表设计、SQL 优化 |

### 质量类
| Agent | 说明 | 适用场景 |
|-------|------|----------|
| `code-reviewer` | 代码审查专家 | 代码质量审查 |
| `security-auditor` | 安全审计专家 | 安全漏洞扫描 |
| `debugger` | 调试专家 | Bug 排查定位 |
| `test-engineer` | 测试工程师 | 测试用例设计 |

### 其他
| Agent | 说明 | 适用场景 |
|-------|------|----------|
| `api-documenter` | API 文档专家 | 接口文档生成 |
| `prompt-engineer` | 提示词工程师 | Prompt 优化 |
| `ai-engineer` | AI 工程师 | AI 功能开发 |
| `python-pro` | Python 专家 | Python 高级开发 |

## 示例

```bash
# 安全审计
/agent security-auditor 审查用户认证模块的安全性

# 前端开发
/agent frontend-developer 创建用户管理页面，包含列表、搜索、分页

# 数据库设计
/agent database-architect 设计订单系统的表结构

# Bug 排查
/agent debugger 接口返回 500 错误，日志显示数据库连接失败

# 代码审查
/agent code-reviewer 审查最近提交的代码变更
```

## SubAgent vs 直接对话

| 维度 | SubAgent | 直接对话 |
|------|----------|----------|
| 上下文 | 独立隔离 | 共享 |
| 专业度 | 专注单一领域 | 通用 |
| 适用场景 | 深度分析 | 快速交互 |
| 工具权限 | 可限制 | 完整 |

## 使用建议

### 何时用 SubAgent
- ✅ 需要深度专业分析
- ✅ 不想污染当前对话上下文
- ✅ 任务相对独立

### 何时直接对话
- ✅ 简单快速的问题
- ✅ 需要基于之前对话的上下文
- ✅ 多轮交互的任务

## 高级用法

### 串联调用
```bash
# 先设计，再审查
/agent database-architect 设计用户表结构
/agent code-reviewer 审查刚才生成的 SQL
```

### 配合 Commands
```bash
# 开发后审查
/crud user --fields "name:string,email:string"
/agent code-reviewer 审查生成的代码
```
