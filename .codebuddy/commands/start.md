---
name: start
description: 项目启动命令。调用 project-bootstrapper 执行完整的项目启动流程。
---

# 项目启动命令

## 使用方式

```
/start [项目名称或描述]
```

## 功能说明

调用 project-bootstrapper Agent，执行 6 阶段项目启动流程：

```
阶段1: 项目初始化 → README.md, 目录结构
阶段2: 需求分析   → doc/PRD.md
阶段3: 数据库设计 → doc/database-design.md, sql/schema.sql
阶段4: 原型设计   → prototype/*.html
阶段5: 任务拆分   → doc/frontend-tasks.md, doc/backend-tasks.md
阶段6: 开发准备   → 环境配置, 依赖安装
```

## 示例

```
/start 订单管理系统
```

输出：
```
🚀 启动项目：订单管理系统

【阶段1: 项目初始化】
✓ 创建目录结构
✓ 生成 README.md

请提供以下信息：
1. 项目类型：管理后台/移动端H5/小程序/API服务？
2. 技术栈偏好：前端框架、后端框架？
3. 核心功能列表？
```

## 模式选择

project-bootstrapper 会自动检测项目状态：

| 状态 | 模式 | 说明 |
|------|------|------|
| doc/PRD.md 不存在 | 🆕 新项目模式 | 完整 6 阶段流程 |
| PRD 存在，功能未定义 | 🔄 迭代模式 | 增量添加功能 |
| PRD 存在，功能已定义 | 🛠️ 开发执行模式 | 按任务清单开发 |

## 快捷选项

```
/start 订单管理系统 --type=admin      # 管理后台
/start 订单管理系统 --tech=vue+fastapi # 指定技术栈
/start 订单管理系统 --skip-prototype   # 跳过原型设计
```

## 检查点

以下环节需要用户确认：
- PRD 确认
- 数据库设计确认
- 原型风格选择
- 任务清单确认

## 输出物

完成后项目包含：
```
{project}/
├── README.md
├── doc/
│   ├── PRD.md
│   ├── database-design.md
│   ├── func.md
│   ├── frontend-tasks.md
│   └── backend-tasks.md
├── sql/
│   └── schema.sql
└── prototype/
    └── *.html
```
