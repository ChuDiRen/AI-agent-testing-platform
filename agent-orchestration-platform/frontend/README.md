# AI Agent 编排平台 - 前端应用

基于 Vue 3 + Element Plus 构建的 AI Agent 编排与工作流管理平台前端应用。

## 功能特性

- ✅ Agent 管理界面（列表、配置表单）
- ✅ Workflow 可视化编辑器（拖放节点）
- ✅ Tool/MCP 集成管理
- ✅ Execution 实时监控（WebSocket）
- ✅ Usage 统计图表（ECharts）
- ✅ 计费统计界面

## 技术栈

- **框架**: Vue 3.5.17 (Composition API)
- **构建工具**: Vite 7.0.4
- **UI 库**: Element Plus 2.10.5
- **状态管理**: Pinia 2.2.8
- **路由**: Vue Router 4.5.1
- **工作流编辑器**: Vue Flow 1.36.0
- **图表库**: ECharts 6.0.0
- **HTTP 客户端**: Axios 1.11.0

## 快速开始

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 配置后端地址

编辑 `vite.config.js`，修改后端代理地址：

```javascript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 后端地址
      changeOrigin: true
    }
  }
}
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问地址：http://localhost:5173

## 项目结构

```
frontend/
├── src/
│   ├── main.js                    # 应用入口
│   ├── App.vue                   # 根组件
│   ├── router/                    # 路由配置
│   │   └── index.js
│   ├── store/                     # Pinia 状态管理
│   │   ├── agent.js              # Agent 状态
│   │   └── execution.js          # Execution 状态
│   ├── api/                      # API 封装
│   │   └── index.js
│   └── views/                    # 页面组件
│       ├── agents/                 # Agent 管理
│       │   ├── AgentList.vue
│       │   └── AgentForm.vue
│       ├── workflows/               # Workflow 管理
│       │   ├── WorkflowList.vue
│       │   └── WorkflowEditor.vue
│       ├── tools/                  # Tool 管理
│       │   └── ToolList.vue
│       ├── monitoring/              # 执行监控
│       │   └── Monitoring.vue
│       └── billing/                # 计费统计
│           └── Billing.vue
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

## 开发指南

### 添加新的页面

1. 在 `src/views/` 创建页面组件
2. 在 `src/router/index.js` 注册路由
3. 如果需要 API，在 `src/api/index.js` 添加方法

### 使用 Pinia Store

```javascript
import { useAgentStore } from '@/store/agent'

const agentStore = useAgentStore()
await agentStore.fetchAgents()
```

### WebSocket 连接

```javascript
import { useExecutionStore } from '@/store/execution'

const executionStore = useExecutionStore()
executionStore.connectWebSocket(executionId)
```

### Vue Flow 工作流编辑

```vue
<VueFlow
  v-model:nodes="nodes"
  v-model:edges="edges"
  @node-click="onNodeClick"
>
  <template #node-custom="data">
    <!-- 自定义节点渲染 -->
  </template>
</VueFlow>
```

## 部署

### 构建生产版本

```bash
npm run build
```

### 环境变量

可以通过 `.env` 文件配置：

```env
VITE_API_BASE_URL=http://localhost:8000
```

## 许可证

MIT License
