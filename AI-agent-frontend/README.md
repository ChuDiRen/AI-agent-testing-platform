# AI Agent Frontend

基于 Vue 3 + TypeScript + Vite 构建的AI智能代理前端应用。

## 快速开始

### 安装依赖
```bash
npm install
```

### 开发环境启动
```bash
npm run dev
```
前端服务将运行在：http://localhost:5173

### 构建生产版本
```bash
npm run build
```

## 配置说明

- 前端开发服务器端口：5173
- 后端API服务端口：8000
- 开发环境下，前端会自动代理 `/api` 请求到后端服务

## 技术栈

- Vue 3 + TypeScript
- Element Plus UI组件库
- Vite 构建工具
- Axios HTTP客户端
- Vue Router 路由管理
- Pinia 状态管理

## Token管理机制

### 自动Token检测与清理
系统在启动时会自动检测并清理无效的token，包括：
- 版本不匹配的token
- 格式错误的JWT token
- 已过期的token

### Token版本控制
- 每次设置新token时会自动标记版本
- 系统启动时检查token版本，清理过期版本
- 确保token的一致性和安全性

### 智能Token刷新
- 请求拦截器会验证token有效性
- 401错误时自动尝试刷新token
- 刷新失败时自动清理所有token数据并跳转登录页

### Token状态显示
- 开发环境下显示实时token状态
- 支持token即将过期提醒
- 提供手动刷新token功能

### 统一错误处理
- 集成token验证到错误处理系统
- 认证错误时自动清理token数据
- 提供友好的用户体验

## 核心文件说明

- `src/utils/tokenValidator.ts` - Token验证和清理工具
- `src/utils/errorHandler.ts` - 统一错误处理
- `src/components/TokenStatus.vue` - Token状态显示组件
- `src/api/http.ts` - HTTP拦截器，集成token管理
- `src/store/user.ts` - 用户状态管理，集成token版本控制
