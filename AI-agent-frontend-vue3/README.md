# AI Agent Testing Platform - Vue3前端

> Copyright (c) 2025 左岚. All rights reserved.

基于 Vue 3 + TypeScript + Vite + Element Plus 构建的AI智能代理测试平台前端应用。

## 🚀 快速开始

### 环境要求
- Node.js >= 18.0.0
- pnpm >= 8.0.0

### 安装依赖
```bash
pnpm install
```

### 开发环境启动
```bash
pnpm dev
```
前端服务将运行在：http://localhost:5173

### 构建生产版本
```bash
pnpm build
```

### 预览生产版本
```bash
pnpm preview
```

## 📁 项目结构

```
src/
├── api/          # API接口配置
├── assets/       # 静态资源
├── components/   # 公共组件
├── router/       # 路由配置
├── store/        # 状态管理
├── utils/        # 工具函数
├── views/        # 页面组件
├── App.vue       # 根组件
└── main.ts       # 入口文件
```

## ⚙️ 配置说明

### 环境变量
复制 `.env.example` 为 `.env` 并根据实际情况修改：

```bash
# API基础URL
VITE_API_BASE_URL=http://localhost:8000/api

# 应用标题
VITE_APP_TITLE=AI Agent Testing Platform
```

### 端口配置
- 前端开发服务器：5173
- 后端API服务：8000
- 开发环境下，前端会自动代理 `/api` 请求到后端服务

## 🛠️ 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - JavaScript的超集
- **Vite** - 下一代前端构建工具
- **Element Plus** - Vue 3组件库
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue状态管理库
- **Axios** - HTTP客户端

## 📝 开发规范

### 代码规范
- 所有代码文件顶部必须包含版权声明
- 使用TypeScript进行类型检查
- 遵循ESLint和Prettier代码格式化规范
- 组件命名使用PascalCase
- 文件命名使用kebab-case

### 提交规范
```bash
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

## 🔧 可用脚本

- `pnpm dev` - 启动开发服务器
- `pnpm build` - 构建生产版本
- `pnpm preview` - 预览生产版本
- `pnpm type-check` - TypeScript类型检查
- `pnpm lint` - 代码检查和修复
- `pnpm format` - 代码格式化

## 📞 技术支持

如遇到问题，请联系左岚团队技术支持。
