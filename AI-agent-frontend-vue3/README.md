# AI Agent Testing Platform - 前端

基于 Vue 3 + TypeScript + Element Plus 的 AI 智能测试平台前端应用。

## 技术栈

- **框架**: Vue 3.5 + TypeScript 5.8
- **构建工具**: Vite 7.1
- **UI 组件**: Element Plus 2.11
- **状态管理**: Pinia 3.0
- **路由**: Vue Router 4.5
- **HTTP 客户端**: Axios 1.12
- **CSS**: WindiCSS 3.5

## 快速开始

### 环境要求

- Node.js >= 18
- pnpm >= 8

### 安装依赖

```bash
pnpm install
```

### 开发模式

```bash
pnpm dev
```

访问 http://localhost:5173

### 生产构建

```bash
pnpm build
```

### 预览构建

```bash
pnpm preview
```

## 环境配置

创建 `.env.development` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
```

创建 `.env.production` 文件：

```env
VITE_API_BASE_URL=https://api.your-domain.com
```

## 项目结构

```
src/
├── api/              # API 接口
├── assets/           # 静态资源
├── components/       # 公共组件
├── composables/      # 组合式函数
├── router/           # 路由配置
├── store/            # 状态管理
├── types/            # 类型定义
├── utils/            # 工具函数
└── views/            # 页面组件
    ├── login/        # 登录
    ├── system/       # 系统管理
    ├── user/         # 用户中心
    ├── api/          # API测试
    ├── web/          # Web测试
    ├── app/          # App测试
    ├── ai/           # AI助手
    ├── data/         # 测试数据
    └── message/      # 消息通知
```

## 核心功能

### 系统管理
- 用户管理（CRUD、导出）
- 角色管理（CRUD、权限分配）
- 菜单管理（CRUD、树形结构）
- 部门管理（CRUD）

### 测试管理
- API 自动化测试
- Web 自动化测试
- App 自动化测试
- 测试用例管理
- 测试报告

### 其他功能
- AI 智能助手
- 测试数据管理
- 消息通知
- 个人中心

## 默认账号

- 用户名: `BNTang`
- 密码: `1234qwer`

## License

MIT

---

**开发团队**: 左岚团队  
**更新时间**: 2025-10-03

