# Bug Detective Skill

Bug 侦探技能，提供问题排查能力。

## 触发条件
- `/debug` 命令
- 用户报告错误或异常
- 代码运行失败

## 排查能力

参考 `@templates/debug-patterns.md`：

### 排查流程
```
1️⃣ 复现问题 → 获取错误信息、确认复现步骤
2️⃣ 定位范围 → 前端/后端？哪个模块？
3️⃣ 分析原因 → 查看日志、断点调试
4️⃣ 验证修复 → 修复代码、回归测试
```

### 错误识别
- 后端错误：Connection refused、IntegrityError、TimeoutError
- 前端错误：Cannot read property、Network Error、404

### 调试命令
```bash
# 后端
tail -f logs/app.log | grep ERROR
uvicorn main:app --reload --log-level debug

# 前端
npm run build 2>&1 | head -50
rm -rf node_modules/.vite
```

## 输出要求

1. 描述问题现象
2. 记录排查过程
3. 分析根本原因
4. 提供修复方案

## 与其他组件协作

- 深度排查 → 调用 `debugger` Agent
- 性能问题 → 调用 `performance` Skill
