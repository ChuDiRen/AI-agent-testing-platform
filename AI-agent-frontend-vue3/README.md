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
- ✅ 用户管理（CRUD、导出、批量操作）
- ✅ 角色管理（CRUD、权限分配）
- ✅ 菜单管理（CRUD、树形结构）
- ✅ 部门管理（CRUD、树形结构）

### 测试管理
- ✅ API 自动化测试（用例管理、执行、报告）
- ✅ Web 自动化测试（Selenium/Playwright）
- ✅ App 自动化测试（Appium）
- ✅ 测试用例管理（CRUD、批量操作、导入导出）
- ✅ 测试报告（生成、查看、导出Excel/PDF）
- ✅ 测试执行引擎（支持多种测试类型）

### AI 功能
- ✅ AI 智能助手（多轮对话、上下文记忆）
- ✅ 测试用例自动生成（基于需求描述）
- ✅ 测试建议与分析
- ✅ 会话管理（创建、编辑、删除）

### 数据管理
- ✅ 测试数据管理（CRUD、导入导出）
- ✅ 数据库备份与恢复
- ✅ 数据清理与优化
- ✅ 统计分析

### 其他功能
- ✅ 消息通知（实时推送、已读标记）
- ✅ 个人中心（资料编辑、密码修改）
- ✅ 仪表板（数据统计、图表展示）

## 默认账号

- 用户名: `BNTang`
- 密码: `1234qwer`

## 新增功能说明

### 测试报告模块
- 支持生成执行报告、汇总报告、详细报告
- 实时统计测试结果（通过率、执行率）
- 支持导出Excel和PDF格式
- 报告详情包含执行记录、截图、日志

### AI助手模块
- 智能对话：支持多轮对话，理解上下文
- 用例生成：根据需求描述自动生成测试用例
- 测试建议：提供测试策略和最佳实践建议
- 会话管理：保存历史对话，随时继续

### 测试执行引擎
- API测试：HTTP请求、断言验证、性能测试
- Web测试：浏览器自动化、元素定位、截图
- App测试：移动端自动化、多平台支持

## License

MIT

---

**开发团队**: 左岚团队
**更新时间**: 2025-10-04
**版本**: v2.0.0 - 全功能完整版

