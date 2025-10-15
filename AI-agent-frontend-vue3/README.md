# AI Agent Testing Platform - Frontend

基于Vue 3 + TypeScript + Element Plus的AI智能测试平台前端

## 功能特性

### 核心功能

- ✅ 用户管理、角色管理、菜单管理、部门管理
- ✅ 测试用例管理（API/Web/App）
- ✅ 测试报告生成与导出
- ✅ 数据可视化（ECharts）
- ✅ 消息通知

### AI功能

- ✅ AI智能对话（支持流式显示）
- ✅ AI自动生成测试用例（文本/文件输入）
- ✅ 多模型切换（DeepSeek、通义千问）
- ✅ 会话历史管理
- ✅ Markdown渲染
- ✅ 提示词模板管理

### 认证与安全

- ✅ JWT Token认证
- ✅ Token自动刷新机制
- ✅ 401错误自动重试
- ✅ 路由权限守卫

### RAG知识库

- ✅ 知识库管理
- ✅ 文档上传（支持拖拽）
- ✅ 语义搜索
- ✅ 任务进度显示

## 技术栈

- **框架**: Vue 3.5.18
- **语言**: TypeScript 5.7.3
- **UI库**: Element Plus 2.9.1
- **状态管理**: Pinia 2.3.0
- **路由**: Vue Router 4.5.0
- **HTTP客户端**: Axios 1.11.0
- **图表**: ECharts 5.6.0
- **构建工具**: Vite 7.0.5
- **CSS**: WindiCSS 3.5.6

## 快速开始

### 1. 安装依赖

```bash
npm install
# 或
pnpm install
```

### 2. 启动开发服务器

```bash
npm run dev
# 或
pnpm dev
```

访问: <http://localhost:5173>

### 3. 构建生产版本

```bash
npm run build
# 或
pnpm build
```

### 4. 预览生产版本

```bash
npm run preview
# 或
pnpm preview
```

## 项目结构

```
AI-agent-frontend-vue3/
├── src/
│   ├── api/              # API接口
│   │   ├── ai-enhanced.ts # AI增强API
│   │   ├── knowledge.ts  # 知识库API
│   │   └── ...
│   ├── assets/           # 静态资源
│   ├── components/       # 公共组件
│   ├── composables/      # 组合式函数
│   │   └── useAIChat.ts  # AI聊天Hook
│   ├── router/           # 路由配置
│   ├── stores/           # Pinia状态管理
│   ├── styles/           # 全局样式
│   ├── types/            # TypeScript类型
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   │   ├── ai/           # AI相关页面
│   │   │   └── ChatEnhanced.vue # 增强版聊天
│   │   ├── knowledge/    # 知识库页面
│   │   │   ├── KnowledgeBase.vue # 知识库列表
│   │   │   └── KnowledgeDetail.vue # 知识库详情
│   │   └── ...
│   ├── App.vue           # 根组件
│   └── main.ts           # 入口文件
├── public/               # 公共资源
├── index.html            # HTML模板
├── vite.config.ts        # Vite配置
├── tsconfig.json         # TypeScript配置
└── package.json          # 项目配置
```

## 主要功能

### 1. AI智能对话

- 支持多种AI模型（GPT-3.5/4, Claude 3系列）
- 流式响应,逐字显示
- 会话历史管理
- Markdown格式渲染
- 代码高亮显示

### 2. RAG知识库

- 知识库CRUD管理
- 文档上传（支持拖拽）
- 支持多种文档格式（PDF/Word/TXT/Markdown/HTML）
- 语义相似度搜索
- 实时任务进度显示

### 3. 测试用例管理

- 测试用例CRUD
- 支持API/Web/App三种类型
- 批量操作
- 数据导出（CSV/JSON）

### 4. 数据可视化

- 测试用例统计图表
- 测试报告趋势分析
- 实时数据更新

## 开发说明

### 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0 或 pnpm >= 8.0.0

### 环境变量

创建 `.env.development` 文件：

```env
# API地址
VITE_API_BASE_URL=http://localhost:8000
VITE_API_PREFIX=/api/v1
```

创建 `.env.production` 文件：

```env
# API地址
VITE_API_BASE_URL=https://your-api-domain.com
VITE_API_PREFIX=/api/v1
```

### 代码规范

```bash
# ESLint检查
npm run lint

# 类型检查
npm run type-check
```

### 常用命令

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 预览生产版本
npm run preview

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

## 常见问题

### Q: 开发服务器启动失败?

A: 检查端口5173是否被占用,或修改vite.config.ts中的端口配置

### Q: API请求失败?

A: 检查后端服务是否启动,环境变量配置是否正确

### Q: 流式对话无法显示?

A: 检查浏览器是否支持EventSource API

### Q: 文档上传失败?

A: 检查文件大小是否超限,格式是否支持

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 最新优化 (v2.1.0)

✨ 本版本进行了全面的前端优化:

### 核心优化

- ✅ **请求拦截器增强**: 自动重试、Token刷新队列、并发控制
- ✅ **Markdown渲染**: AI回复支持Markdown格式和代码高亮
- ✅ **用户体验**: 加载骨架屏、主题切换、键盘快捷键
- ✅ **错误处理**: 增强的错误提示和恢复机制
- ✅ **性能优化**: 请求重试、网络错误检测

### 新增组件

- 📝 MarkdownRenderer - Markdown渲染组件
- 💀 LoadingSkeleton - 加载骨架屏组件

### 新增Hook

- 🎨 useTheme - 主题管理(支持 light/dark/auto)
- ⌨️  useKeyboard - 键盘快捷键管理

### 功能增强

- 🔄 请求自动重试(最多3次)
- 🔐 优化的Token刷新机制(防止并发)
- 🌙 暗黑模式支持
- 💅 代码块语法高亮
- ⚡ 更流畅的用户交互体验

## 使用示例

### 主题切换

```typescript
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleDark, setTheme } = useTheme()

// 切换暗黑模式
toggleDark()

// 设置特定主题
setTheme('dark')  // 'light' | 'dark' | 'auto'
```

### 键盘快捷键

```typescript
import { useKeyboard, CommonShortcuts } from '@/composables/useKeyboard'

const { register } = useKeyboard()

// 注册快捷键
register({
  ...CommonShortcuts.SAVE,
  callback: () => handleSave()
})
```

## 许可证

Copyright (c) 2025 左岚. All rights reserved.

## 联系方式

- 开发团队: 左岚团队
- 版本: v2.1.0 (已全面优化)
