# Performance Skill

性能分析技能，提供性能问题识别和优化能力。

## 触发条件
- `/perf` 命令
- `/review --mode performance` 命令
- 用户报告性能问题

## 分析能力

参考 `@templates/debug-patterns.md`：

### 后端性能
- N+1 查询检测
- 慢查询识别
- 连接池配置
- 缓存策略

### 前端性能
- 组件渲染分析
- 虚拟列表优化
- 资源懒加载
- 代码分割

### 数据库性能
- 索引分析
- 查询计划
- 连接管理

## 检测模式

### N+1 查询
```python
# 检测模式：循环中的查询
for item in items:
    related = session.exec(select(...).where(...))
```

### 重复渲染
```javascript
// 检测模式：非响应式对象
const obj = { ... }  // 在 setup 中直接定义
```

## 输出要求

1. 识别性能瓶颈
2. 量化性能影响
3. 提供优化代码
4. 评估优化效果

## 与其他组件协作

- 代码审查中 → 被 `code-quality` 插件调用
- 深度分析 → 调用 `debugger` Agent
