---
name: fullstack
description: 全栈开发命令。前后端并行执行，生成完整功能代码。
---

# 全栈开发命令

## 使用方式

```
/fullstack [功能描述]
```

## 功能说明

强制并行执行前后端开发：

```
┌─────────────────────────────────────────┐
│              /fullstack                  │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┴───────────┐
      ▼                       ▼
┌─────────────┐       ┌─────────────┐
│  backend-   │       │  frontend-  │
│  developer  │       │  developer  │
└──────┬──────┘       └──────┬──────┘
       │                     │
       └──────────┬──────────┘
                  ▼
         ┌─────────────┐
         │ code-reviewer│
         └─────────────┘
```

## 执行流程

1. **需求拆分** - 将功能拆分为前后端任务
2. **并行开发**
   - backend-developer → API + 数据模型
   - frontend-developer → 页面 + 组件
3. **自动审查** - code-reviewer 审查所有代码
4. **结果汇总** - 整合前后端输出

## 示例

```
/fullstack 用户管理功能
```

输出：
```
✅ 全栈开发完成

【后端】
- POST /api/users - 创建用户
- GET /api/users - 用户列表
- PUT /api/users/{id} - 更新用户
- DELETE /api/users/{id} - 删除用户

【前端】
- UserList.vue - 用户列表页
- UserForm.vue - 用户表单组件
- userApi.ts - API 调用封装

【审查结果】
✓ 代码质量通过
⚠️ 建议：添加分页参数校验
```

## 自动行为

1. **API 契约对齐** - 确保前后端接口定义一致
2. **类型同步** - 前端类型定义与后端响应匹配
3. **错误处理** - 前后端统一错误码处理

## 选项

```
/fullstack 用户管理 --backend-only   # 仅后端
/fullstack 用户管理 --frontend-only  # 仅前端
/fullstack 用户管理 --no-review      # 跳过审查
```
