---
name: dev
description: 快速开发命令。自动识别前后端任务，分派给合适的 Agent 执行。
---

# 快速开发命令

## 使用方式

```
/dev [需求描述]
```

## 功能说明

自动识别需求类型，分派给合适的 Agent：

| 识别关键词 | 分派 Agent |
|-----------|-----------|
| API、接口、服务、后端 | backend-developer |
| 页面、组件、UI、前端 | frontend-developer |
| 同时包含前后端关键词 | 并行执行两个 Agent |

## 执行流程

```
1. 解析用户需求
2. 识别任务类型（前端/后端/全栈）
3. 分派给对应 Agent
4. 执行完成后自动触发 code-reviewer
5. 返回代码 + 审查结果
```

## 示例

### 后端任务
```
/dev 实现用户登录 API
```
→ 分派给 backend-developer

### 前端任务
```
/dev 实现用户列表页面
```
→ 分派给 frontend-developer

### 全栈任务
```
/dev 实现用户管理功能，包含列表页和 CRUD 接口
```
→ 并行分派给 backend-developer + frontend-developer

## 自动行为

1. **技术栈检测** - 自动识别项目技术栈（FastAPI/Spring Boot/Vue/React）
2. **代码复用检查** - 检查现有代码，避免重复开发
3. **自动审查** - 代码生成后自动触发审查

## 跳过审查

如不需要自动审查：
```
/dev 实现用户登录 API --no-review
```
