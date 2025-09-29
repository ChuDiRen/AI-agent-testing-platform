# Vue FastAPI Admin - Naive UI 迁移指南

> Copyright (c) 2025 左岚. All rights reserved.

## 📋 项目概述

本项目是基于 [vue-fastapi-admin](https://github.com/mizhexiaoxiao/vue-fastapi-admin) 的完全重构版本，采用方案B：完全重构方案，实现了与目标项目完全一致的功能和UI风格。

## 🎯 重构目标

- ✅ **完全兼容**：API格式、响应结构、功能特性完全一致
- ✅ **技术栈统一**：Vue3 + Naive UI + UnoCSS + FastAPI
- ✅ **架构优化**：保持现有五层架构，优化API结构
- ✅ **UI风格一致**：完全匹配目标项目的界面设计

## 🏗️ 项目结构

### 前端项目 (AI-agent-frontend-naive)
```
AI-agent-frontend-naive/
├── src/
│   ├── api/              # API接口定义
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   │   └── common/       # 通用组件
│   ├── directives/       # 自定义指令
│   ├── layout/           # 布局组件
│   ├── locales/          # 国际化
│   │   ├── zh-CN.js      # 中文语言包
│   │   └── en-US.js      # 英文语言包
│   ├── plugins/          # 插件配置
│   ├── router/           # 路由配置
│   │   ├── guard/        # 路由守卫
│   │   └── routes/       # 路由定义
│   ├── store/            # 状态管理
│   │   └── modules/      # 状态模块
│   │       ├── app/      # 应用状态
│   │       ├── user/     # 用户状态
│   │       ├── permission/ # 权限状态
│   │       └── tags/     # 标签状态
│   ├── styles/           # 样式文件
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   │   ├── login/        # 登录页面
│   │   ├── workbench/    # 工作台
│   │   └── error-page/   # 错误页面
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── package.json          # 项目配置
├── vite.config.js        # Vite配置
├── uno.config.js         # UnoCSS配置
└── .env                  # 环境变量
```

### 后端API扩展
```
AI-agent-backend/app/
├── api/v1/
│   ├── base.py           # 基础模块API (新增)
│   └── __init__.py       # 路由注册 (更新)
├── dto/
│   ├── auth_dto.py       # 认证DTO (新增)
│   └── base_dto.py       # 基础响应DTO (新增)
└── service/
    └── auth_service.py   # 认证服务 (新增)
```

## 🚀 快速开始

### 方式一：一键启动 (推荐)
```bash
# 测试API连接
./test-api-connection.sh

# 启动完整项目 (前端 + 后端)
./start-full-project.sh

# 停止所有服务
./stop-project.sh
```

### 方式二：分别启动
```bash
# 1. 安装前端依赖
./setup-naive-frontend.sh

# 2. 启动后端服务
cd AI-agent-backend
python main.py

# 3. 测试API连接
./test-api-connection.sh

# 4. 启动前端服务
cd AI-agent-frontend-naive
pnpm dev
```

### 访问应用
- 前端：http://localhost:3000
- 后端：http://localhost:8000
- API文档：http://localhost:8000/docs

### 默认登录信息
- 用户名：admin
- 密码：123456

### 🔧 故障排除
如果遇到API连接问题，请运行：
```bash
./test-api-connection.sh
```
该脚本会测试所有关键API接口的连通性。

## 🛠️ 技术栈对比

| 组件 | 原项目 | 新项目 | 状态 |
|------|--------|--------|------|
| 前端框架 | Vue 3 | Vue 3 | ✅ 一致 |
| UI组件库 | Element Plus | Naive UI | 🔄 已迁移 |
| CSS框架 | - | UnoCSS | ➕ 新增 |
| 状态管理 | Pinia | Pinia | ✅ 一致 |
| 路由管理 | Vue Router | Vue Router | ✅ 一致 |
| 构建工具 | Vite | Vite | ✅ 一致 |
| 后端框架 | FastAPI | FastAPI | ✅ 一致 |
| 数据库 | SQLite | SQLite | ✅ 一致 |

## 🎨 核心特性

### 前端特性
- **现代化UI**：基于Naive UI的现代化界面设计
- **响应式布局**：完美适配桌面端和移动端
- **动态路由**：基于权限的动态路由生成
- **权限控制**：细粒度的权限控制系统
- **主题切换**：支持明暗主题切换
- **国际化**：支持中英文切换
- **组件自动导入**：自动导入组件和API
- **图标系统**：基于Iconify的图标系统

### 后端特性
- **兼容API**：完全兼容vue-fastapi-admin的API格式
- **统一响应**：Success/Fail统一响应格式
- **JWT认证**：完整的JWT认证体系
- **权限管理**：RBAC权限管理系统
- **五层架构**：保持现有的企业级架构

## 🎯 项目亮点

1. **100%功能兼容** - 与目标项目vue-fastapi-admin完全一致
2. **现代化UI** - 基于Naive UI的精美界面，响应式设计
3. **完整权限系统** - RBAC权限管理，支持菜单和API权限
4. **开发友好** - 组件自动导入、热更新、类型提示、UnoCSS
5. **生产就绪** - 完整的错误处理、日志记录、性能优化
6. **丰富组件** - QueryBar、CrudTable、CrudModal等通用组件
7. **完善工具** - 一键部署、API测试、功能检测脚本

## 📝 完整功能列表

### ✅ 已实现功能

**基础功能**
- ✅ 用户登录/登出
- ✅ 用户信息管理
- ✅ 密码修改
- ✅ 权限验证
- ✅ 动态路由
- ✅ 主题切换
- ✅ 国际化支持

**系统管理**
- ✅ 用户管理 - 增删改查、角色分配、密码重置
- ✅ 角色管理 - 增删改查、权限设置
- ✅ 菜单管理 - 树形结构、增删改查
- ✅ API管理 - 接口管理、权限控制
- ✅ 部门管理 - 树形结构、增删改查
- ✅ 审计日志 - 操作记录、日志查询

**页面功能**
- ✅ 工作台 - 数据统计、项目展示
- ✅ 个人资料 - 信息修改、密码更新
- ✅ 错误页面 - 404页面

### API接口

**认证相关**
- `POST /api/v1/base/access_token` - 用户登录
- `GET /api/v1/base/userinfo` - 获取用户信息
- `GET /api/v1/base/usermenu` - 获取用户菜单
- `GET /api/v1/base/userapi` - 获取用户API权限
- `POST /api/v1/base/update_password` - 修改密码

**用户管理**
- `GET /api/v1/user/list` - 获取用户列表
- `GET /api/v1/user/get` - 获取用户详情
- `POST /api/v1/user/create` - 创建用户
- `POST /api/v1/user/update` - 更新用户
- `DELETE /api/v1/user/delete` - 删除用户
- `POST /api/v1/user/reset_password` - 重置密码

**角色管理**
- `GET /api/v1/role/list` - 获取角色列表
- `POST /api/v1/role/create` - 创建角色
- `POST /api/v1/role/update` - 更新角色
- `DELETE /api/v1/role/delete` - 删除角色
- `POST /api/v1/role/authorized` - 设置角色权限
- `GET /api/v1/role/authorized` - 获取角色权限

**菜单管理**
- `GET /api/v1/menu/list` - 获取菜单列表
- `POST /api/v1/menu/create` - 创建菜单
- `POST /api/v1/menu/update` - 更新菜单
- `DELETE /api/v1/menu/delete` - 删除菜单

### 响应格式
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

## 🔧 开发指南

### 添加新页面
1. 在 `src/views/` 下创建页面组件
2. 在后端添加对应的菜单配置
3. 确保用户有相应的权限

### 添加新API
1. 在后端创建对应的路由和服务
2. 在前端 `src/api/index.js` 中添加API调用
3. 使用统一的响应格式

### 自定义主题
1. 修改 `src/styles/variables.scss` 中的CSS变量
2. 调整 `uno.config.js` 中的主题配置

## 📦 部署指南

### 前端部署
```bash
cd AI-agent-frontend-naive
pnpm build
# 将 dist 目录部署到Web服务器
```

### 后端部署
```bash
cd AI-agent-backend
# 使用现有的部署方式
```

## 🐛 常见问题

### Q: 如何切换回Element Plus？
A: 可以继续使用原有的 `AI-agent-frontend` 项目，两个前端项目可以并存。

### Q: 数据库需要迁移吗？
A: 不需要，后端API完全兼容，可以使用现有数据库。

### Q: 如何添加新的UI组件？
A: 参考Naive UI官方文档，组件会自动导入。

## 📞 技术支持

如遇到问题，请联系左岚团队技术支持。

## 📄 许可证

MIT License

---

**注意**：本项目是对现有AI Agent Testing Platform的UI升级，保持了所有原有功能的同时，提供了更现代化的用户界面体验。
