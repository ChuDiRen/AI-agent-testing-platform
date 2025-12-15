---
allowed-tools: Read, Glob, Grep
argument-hint: [功能描述] | [模块名称]
description: 在生成代码之前检查是否已有相关的业务服务或功能，避免重复开发
---

# 代码复用检查

检查复用情况：$ARGUMENTS

## 核心原则

> **严格要求：在生成任何业务代码之前，必须主动查看现有代码和文档，全面确认是否已有相关的业务服务或功能。**

**参考** `skills/development/code-review-checklist.md` 获取完整的检查流程。

## 当前状态

- 功能清单文档：!find . -name "func.md" | head -3
- Service 层：!find . -name "*service*" -o -name "*Service*" | head -10
- Repository 层：!find . -name "*repository*" -o -name "*Repository*" -o -name "*dao*" | head -10
- API 层：!find . -name "*api*" -o -name "*Api*" | head -10
- 组件层：!find . -name "*.vue" -o -name "*.tsx" | head -10

## 任务

全面检查现有代码，确认是否有可复用的功能。

### 检查清单

**后端项目**：
- [ ] Service层：查看是否已有类似的业务服务
- [ ] Repository层：查看是否已有相关的数据访问接口
- [ ] Model层：查看是否已有相关的数据模型
- [ ] Utils层：查看是否已有相关的工具函数

**前端项目**：
- [ ] API层：查看是否已有相关的接口封装
- [ ] 组件层：查看是否已有相关的组件
- [ ] Composables/Hooks：查看是否已有相关的组合式函数
- [ ] Store层：查看是否已有相关的状态管理

### 复用决策

| 优先级 | 场景 | 处理方式 |
|-------|------|---------|
| 1 | 发现完全匹配的功能 | 直接复用现有代码 |
| 2 | 发现类似功能 | 在现有类中扩展方法 |
| 3 | 发现相关但不完全匹配 | 评估是否可以重构复用 |
| 4 | 确认没有相关功能 | 创建新的类或服务 |

## 完成检查

- [ ] 已查看完整的功能清单文档
- [ ] 已逐层检查各个层级的现有功能
- [ ] 已确认没有重复或类似的现有功能
- [ ] 已选择合适的复用或扩展策略
