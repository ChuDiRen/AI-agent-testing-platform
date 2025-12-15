---
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint: [功能描述] | [需求文档路径]
description: 使用 RIPER-5 模式进行功能迭代开发，通过严格的五阶段协议确保代码修改的可控性和质量
---

# 功能迭代

使用 RIPER-5 模式进行功能迭代：$ARGUMENTS

## 当前状态

- 目标文件：@$ARGUMENTS（如果提供了文件路径）
- 相关代码：!grep -r "$ARGUMENTS" --include="*.py" --include="*.ts" --include="*.vue" -l | head -10

## 任务

调用 `riper-developer` Agent 使用 RIPER-5 严格协议进行功能迭代。

### RIPER-5 模式概览

```
RESEARCH → INNOVATE → PLAN → EXECUTE → REVIEW
  研究       创新       规划     执行      审查
```

### 模式转换信号

只有在明确信号时才能转换模式：
- `ENTER RESEARCH MODE`
- `ENTER INNOVATE MODE`
- `ENTER PLAN MODE`
- `ENTER EXECUTE MODE`
- `ENTER REVIEW MODE`

### 标准流程

1. **ENTER RESEARCH MODE**：分析现有代码和需求
2. **ENTER INNOVATE MODE**：讨论解决方案
3. **ENTER PLAN MODE**：制定详细计划
4. 用户确认计划
5. **ENTER EXECUTE MODE**：执行计划
6. **ENTER REVIEW MODE**：验证实施结果

## 完成检查

- [ ] 所有计划项目已执行
- [ ] 实施与计划完全匹配
- [ ] 代码质量符合规范
- [ ] 无偏差检测
- [ ] Git 提交信息规范
