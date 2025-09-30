# Vue FastAPI Admin - Naive UI版本

> Copyright (c) 2025 左岚. All rights reserved.

基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台，完全兼容 vue-fastapi-admin 项目。

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
前端服务将运行在：http://localhost:3000

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
├── directives/   # 自定义指令
├── layout/       # 布局组件
├── locales/      # 国际化
├── plugins/      # 插件配置
├── router/       # 路由配置
├── store/        # 状态管理
├── styles/       # 样式文件
├── utils/        # 工具函数
├── views/        # 页面组件
├── App.vue       # 根组件
└── main.js       # 入口文件
```

## ⚙️ 配置说明

### 环境变量
复制 `.env` 文件并根据实际情况修改：

```bash
# 应用配置
VITE_APP_TITLE=AI Agent Testing Platform
VITE_APP_PORT=3000
VITE_APP_BASE_API=http://localhost:8000

# 路由模式 hash | history
VITE_USE_HASH=false
```

### 端口配置
- 前端开发服务器：3000
- 后端API服务：8000
- 开发环境下，前端会自动代理 `/api` 请求到后端服务

## 🛠️ 技术栈

- **Vue 3** - 渐进式JavaScript框架
- **Naive UI** - Vue 3组件库
- **TypeScript** - JavaScript的超集
- **Vite** - 下一代前端构建工具
- **Vue Router** - 官方路由管理器
- **Pinia** - Vue状态管理库
- **UnoCSS** - 原子化CSS引擎
- **Axios** - HTTP客户端
- **Vue I18n** - 国际化插件

## 📝 开发规范

### 代码规范
- 所有代码文件顶部必须包含版权声明
- 使用ESLint和Prettier代码格式化规范
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
- `pnpm lint` - 代码检查
- `pnpm lint:fix` - 代码检查和修复
- `pnpm prettier` - 代码格式化

## 🎨 特性

- **现代化UI**：基于Naive UI的现代化界面设计，参考 vue-fastapi-admin 风格
- **Tags标签页**：支持多页面快速切换，右键菜单操作，智能滚动定位
- **响应式布局**：完美适配桌面端和移动端，优化移动端体验
- **增强工具栏**：全屏切换、语言选择、GitHub链接、主题切换等功能
- **智能面包屑**：动态生成导航路径，支持点击跳转
- **用户中心**：完善的用户头像下拉菜单，个人资料管理
- **动态路由**：基于权限的动态路由生成
- **权限控制**：细粒度的权限控制系统
- **主题切换**：支持明暗主题切换，统一设计变量
- **国际化**：支持多语言切换
- **组件自动导入**：自动导入组件和API
- **图标系统**：基于Iconify的图标系统

## 🆕 最新更新

### v1.1.3 (2025-09-30)
- 🎨 重构工作台页面，参考vue-fastapi-admin设计风格
- ✨ 简化布局结构，使用AppPage组件
- ✨ 优化统计数据显示，使用NStatistic组件
- ✨ 添加项目卡片列表展示
- 📱 完善响应式设计，支持移动端适配
- 🎨 统一设计语言，提升视觉效果

### v1.1.2 (2025-09-30)
- 🐛 修复 `/workbench` 路由404错误
- ✨ 优化基础路由配置，支持未登录访问工作台
- 🔧 更新路由守卫白名单
- 🎨 完善权限store路由逻辑，避免重复路由

### v1.1.1 (2025-09-30)
- 🐛 修复登录页面logo显示问题
- ✨ 设计全新的机器人主题SVG logo
- ✨ 添加logo动画效果（浮动+旋转）
- 🎨 优化各页面logo视觉效果
- 🔧 更新favicon和浏览器标签图标

### v1.1.0 (2025-09-30)
- ✨ 新增 Tags 标签页导航功能
- ✨ 增强头部工具栏（全屏、语言切换、GitHub链接）
- ✨ 优化侧边栏 Logo 和菜单样式
- ✨ 改进面包屑导航体验
- ✨ 完善用户头像下拉菜单
- 🎨 统一色彩搭配和设计变量
- 🎨 优化整体视觉效果和交互体验
- 📱 改进响应式设计和移动端适配

## 📞 技术支持

如遇到问题，请联系左岚团队技术支持。

## 📄 许可证

MIT License
