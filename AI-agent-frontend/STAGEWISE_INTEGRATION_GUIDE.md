# Stagewise 深度集成使用指南

## 概述

本项目已成功集成 Stagewise 工具，采用深度定制集成方案，提供完整的 AI 辅助开发体验。

## 🚀 快速启动

### 1. 启动服务

```bash
# 启动前端开发服务器（端口 5173）
npm run dev

# 启动后端服务器（端口 8000）
cd ../AI-agent-backend
python main.py

# 启动 Stagewise 工具（端口 3100）
npx stagewise --silent
```

### 2. 访问地址

- **前端应用**: http://localhost:5173/
- **后端 API**: http://localhost:8000
- **Stagewise 工具**: http://localhost:3100
- **API 文档**: http://localhost:8000/docs

## 🔧 集成特性

### Vite 深度集成
- ✅ 自定义 Stagewise 插件集成到 Vite 构建流程
- ✅ HMR（热模块替换）支持
- ✅ 开发模式下自动注入工具栏脚本
- ✅ 代理配置自动处理 Stagewise 请求

### Vue 3 增强功能
- ✅ Vue 组件分析和优化建议
- ✅ TypeScript 支持
- ✅ Composition API 集成
- ✅ Element Plus UI 组件支持

### 自定义插件系统
- ✅ Vue 增强插件（组件分析、性能检查）
- ✅ Vite 集成插件（构建监控、HMR 状态）
- ✅ 插件加载器和管理系统

## 📁 项目结构

```
AI-agent-frontend/
├── .stagewise/                    # Stagewise 配置目录
│   ├── plugins/                   # 自定义插件
│   │   ├── vue-enhanced.js        # Vue 增强插件
│   │   └── vite-integration.js    # Vite 集成插件
│   └── plugin-loader.js           # 插件加载器
├── stagewise.json                 # Stagewise 主配置文件
├── vite.config.ts                 # Vite 配置（含 Stagewise 集成）
└── package.json                   # 项目依赖（含 Stagewise）
```

## ⚙️ 配置说明

### stagewise.json 配置
```json
{
  "port": 3100,                    // Stagewise 服务端口
  "appPort": 5173,                 // 前端应用端口
  "autoPlugins": true,             // 自动加载插件
  "framework": {
    "name": "vue",
    "version": "3.5.18",
    "features": {
      "typescript": true,
      "router": true,
      "store": "pinia",
      "ui": "element-plus"
    }
  }
}
```

### Vite 集成配置
- 自定义 `stagewisePlugin()` 函数
- 代理配置支持 Stagewise 工具栏和 WebSocket
- 开发模式下自动注入初始化脚本

## 🎯 功能特性

### 1. AI 辅助开发
- **智能代码建议**: 基于上下文的代码补全和优化建议
- **组件分析**: Vue 组件结构分析和性能优化建议
- **实时反馈**: 开发过程中的实时代码质量检查

### 2. 开发工具集成
- **构建监控**: 实时监控 Vite 构建状态和性能
- **HMR 集成**: 热模块替换状态监控和调试
- **包分析**: 构建产物分析和优化建议

### 3. 用户界面
- **工具栏**: 底部右侧可拖拽工具栏
- **快捷键**: 
  - `Ctrl+Shift+S`: 切换工具栏显示/隐藏
  - `Ctrl+Shift+F`: 聚焦到工具栏
- **主题**: 自动适应系统主题

## 🔍 使用方法

### 1. 基本操作
1. 启动所有服务后，Stagewise 会自动在浏览器中打开
2. 在前端应用页面右下角可以看到 Stagewise 工具栏
3. 点击工具栏图标可以访问各种 AI 辅助功能

### 2. Vue 增强功能
- **组件分析**: 点击 🔍 图标分析当前页面的 Vue 组件
- **性能检查**: 点击 ⚡ 图标检查组件渲染性能
- **Vue 检查器**: 点击 🔧 图标打开 Vue 开发工具

### 3. Vite 集成功能
- **构建信息**: 查看当前构建状态和统计信息
- **HMR 状态**: 监控热模块替换状态
- **开发服务器**: 查看开发服务器配置信息
- **包分析**: 分析构建产物和依赖关系

## 🛠️ 故障排除

### 常见问题

#### 1. Stagewise 无法启动
```bash
# 检查端口占用
netstat -ano | findstr :3100

# 清理 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install
```

#### 2. 插件加载失败
- 检查 `.stagewise/plugins/` 目录是否存在
- 确认插件文件格式正确
- 查看控制台错误信息

#### 3. 代理配置问题
- 确认后端服务运行在端口 8000
- 检查 `vite.config.ts` 中的代理配置
- 重启前端开发服务器

#### 4. 工具栏不显示
- 检查浏览器控制台是否有 JavaScript 错误
- 确认 Stagewise 服务正常运行
- 尝试刷新页面或清除浏览器缓存

### 调试模式
```bash
# 启用详细日志
npx stagewise --verbose

# 启用调试模式
npx stagewise --verbose --debug
```

## 📝 开发说明

### 自定义插件开发
1. 在 `.stagewise/plugins/` 目录创建新的 `.js` 文件
2. 实现插件接口（init, getToolbarActions, destroy）
3. 在 `stagewise.json` 中注册插件
4. 重启 Stagewise 服务

### 配置修改
- 修改 `stagewise.json` 后需要重启 Stagewise
- 修改 `vite.config.ts` 后需要重启前端服务
- 插件文件修改后需要重启 Stagewise

## 🔗 相关链接

- [Stagewise 官方文档](https://stagewise.io/docs)
- [Stagewise GitHub](https://github.com/stagewise-io/stagewise)
- [Vue 3 官方文档](https://vuejs.org/)
- [Vite 官方文档](https://vitejs.dev/)

---

**版权声明**: Copyright (c) 2025 左岚. All rights reserved.
