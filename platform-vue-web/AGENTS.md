# AGENTS.md - 大熊AI代码生成器 Frontend

> 本文档为 AI 助手提供项目上下文和开发指南，遵循 [agents.md](https://github.com/agentsmd/agents.md) 规范。

## 项目概述

基于 **Vue 3 + Element Plus** 的 AI 代码生成器前端，支持 Vue 和 React 混合开发（通过 veaury 实现互操作）。

### 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3 + React 18 (混合) |
| UI 组件库 | Element Plus, vue-element-plus-x, Radix UI |
| 路由 | Vue Router 4 |
| 状态管理 | Vuex 4 |
| HTTP 客户端 | Axios |
| 构建工具 | Vite 4 |
| CSS | TailwindCSS, WindiCSS |
| AI SDK | LangGraph SDK, LangChain Core |
| 互操作 | veaury (Vue + React) |
| 代码编辑 | CodeMirror 5 |

### 运行端口

- **前端服务**: `http://localhost:5173`
- **API 代理**: `/api` → `http://127.0.0.1:5000`

---

## 目录结构

```
platform-vue-web/
├── index.html                # HTML 入口
├── package.json              # 依赖配置 (pnpm)
├── vite.config.js            # Vite 配置 ⭐
├── tailwind.config.js        # TailwindCSS 配置
├── .env                      # 环境变量
│
├── public/                   # 静态资源
│   └── vue-element-plus-x.css
│
└── src/
    ├── main.js               # Vue 应用入口
    ├── App.vue               # 根组件
    ├── axios.js              # Axios 配置 (拦截器、Token刷新)
    ├── style.css             # 全局样式
    │
    ├── router/               # 路由配置
    │   └── index.js          # 路由定义 + 动态路由 + 权限守卫
    │
    ├── store/                # Vuex 状态管理
    │   └── index.js          # 用户信息、权限、菜单、主题
    │
    ├── directives/           # 自定义指令
    │   └── permission.js     # v-permission, v-role 权限指令
    │
    ├── composables/          # Vue Composables
    │   ├── useTestExecution.js  # 测试执行
    │   ├── useTheme.js          # 主题切换
    │   └── useWebSocket.js      # WebSocket 连接
    │
    ├── components/           # 公共组件 (Vue)
    │   ├── BaseForm/         # 通用表单组件
    │   ├── BaseTable/        # 通用表格组件
    │   ├── BasePagination/   # 分页组件
    │   ├── BaseSearch/       # 搜索组件
    │   ├── CodeEditor.vue    # 代码编辑器
    │   ├── JsonEditor.vue    # JSON 编辑器
    │   ├── JsonViewer.vue    # JSON 查看器
    │   ├── YamlViewer.vue    # YAML 查看器
    │   ├── IconSelect.vue    # 图标选择器
    │   └── ...
    │
    ├── styles/               # 样式文件
    │   ├── theme.css         # 主题变量
    │   ├── common-list.css   # 列表页通用样式
    │   └── common-form.css   # 表单页通用样式
    │
    ├── utils/                # 工具函数
    │   └── timeFormatter.js  # 时间格式化
    │
    ├── agent-react/          # React 组件 (AI聊天) ⭐
    │   ├── AgentChatApp.jsx  # React 主应用
    │   ├── globals.css       # React 全局样式
    │   ├── components/       # React UI 组件
    │   │   ├── thread/       # 聊天线程组件
    │   │   ├── ui/           # 基础 UI 组件 (Radix)
    │   │   └── icons/        # 图标组件
    │   ├── providers/        # React Context
    │   ├── hooks/            # React Hooks
    │   ├── lib/              # 工具函数
    │   └── locales/          # 国际化 (en, zh-CN)
    │
    └── views/                # 页面组件 (Vue)
        ├── 403.vue           # 无权限页面
        ├── 404.vue           # 页面不存在
        ├── 500.vue           # 服务器错误
        ├── login/            # 登录页
        ├── home/             # 主页布局 (FHeader, FMenu, FTagList)
        ├── statistics/       # 统计面板
        ├── system/           # 系统管理 (RBAC)
        │   ├── users/        # 用户管理
        │   ├── role/         # 角色管理
        │   ├── menu/         # 菜单管理
        │   └── dept/         # 部门管理
        ├── apitest/          # API 测试模块 ⭐
        │   ├── project/      # 项目管理
        │   ├── apiinfo/      # 接口管理
        │   ├── apiinfocase/  # 用例管理
        │   ├── testplan/     # 测试计划
        │   ├── task/         # 测试任务
        │   ├── history/      # 测试历史
        │   ├── environment/  # 环境管理
        │   ├── folder/       # 文件夹管理
        │   ├── keyword/      # 关键字管理
        │   ├── mock/         # Mock 服务
        │   ├── apidoc/       # 文档导入
        │   ├── apimeta/      # 元数据管理
        │   ├── database/     # 数据库配置
        │   ├── report/       # 报告查看
        │   └── execution/    # 执行视图
        ├── aiassistant/      # AI 测试助手 ⭐
        │   ├── agentchat/    # 智能体聊天 (React 集成)
        │   ├── model/        # AI 模型管理
        │   ├── prompt/       # 提示词模板
        │   └── testcase/     # 测试用例
        ├── generator/        # 代码生成器
        ├── msgmanage/        # 消息管理
        │   ├── robot/        # 机器人配置
        │   └── template/     # 消息模板
        └── plugin/           # 插件市场
```

---

## 开发规范

### 代码风格

- **Vue 组件**: 使用 Composition API (`<script setup>`)
- **命名规范**:
  - 组件文件: `PascalCase.vue` (如 `UserList.vue`)
  - JS 文件: `camelCase.js` (如 `user.js`)
  - CSS 类名: `kebab-case`
- **路径别名**:
  - `~/` → `src/` (Vue 组件)
  - `@/` → `src/agent-react/` (React 组件内部)

### 模块结构规范

每个业务模块遵循以下结构：
```
views/{module}/
├── {Module}List.vue      # 列表页
├── {Module}Form.vue      # 表单页 (新增/编辑)
├── {module}.js           # API 请求
└── components/           # 模块私有组件 (可选)
    └── ...
```

### Vue 页面模板

#### 列表页 (xxxList.vue)

```vue
<template>
  <div class="common-list-container">
    <!-- 搜索区域 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="名称">
          <el-input v-model="searchForm.name" placeholder="请输入" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 操作按钮 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>数据列表</span>
          <el-button type="primary" v-permission="'module:add'" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增
          </el-button>
        </div>
      </template>

      <!-- 表格 -->
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.pageNum"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        @current-change="loadData"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { queryByPage, deleteData } from './xxx.js'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({ name: '' })
const pagination = reactive({ pageNum: 1, pageSize: 10, total: 0 })

const loadData = async () => {
  loading.value = true
  try {
    const res = await queryByPage({ ...searchForm, ...pagination })
    if (res.data.code === 200) {
      tableData.value = res.data.data.list
      pagination.total = res.data.data.total
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.pageNum = 1
  loadData()
}

const handleReset = () => {
  Object.assign(searchForm, { name: '' })
  handleSearch()
}

const handleAdd = () => router.push('/XxxForm')
const handleEdit = (row) => router.push({ path: '/XxxForm', query: { id: row.id } })

const handleDelete = async (row) => {
  await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
  const res = await deleteData({ id: row.id })
  if (res.data.code === 200) {
    ElMessage.success('删除成功')
    loadData()
  }
}

onMounted(() => loadData())
</script>
```

#### 表单页 (xxxForm.vue)

```vue
<template>
  <div class="common-form-container">
    <el-card>
      <template #header>
        <span>{{ isEdit ? '编辑' : '新增' }}</span>
      </template>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio :label="1">启用</el-radio>
            <el-radio :label="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
          <el-button @click="router.back()">返回</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { queryById, insertData, updateData } from './xxx.js'

const router = useRouter()
const route = useRoute()
const formRef = ref()

const isEdit = computed(() => !!route.query.id)
const form = reactive({ name: '', status: 1 })
const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const loadData = async () => {
  if (!isEdit.value) return
  const res = await queryById({ id: route.query.id })
  if (res.data.code === 200) {
    Object.assign(form, res.data.data)
  }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  const api = isEdit.value ? updateData : insertData
  const res = await api(form)
  if (res.data.code === 200) {
    ElMessage.success(isEdit.value ? '更新成功' : '新增成功')
    router.back()
  }
}

onMounted(() => loadData())
</script>
```

#### API 请求文件 (xxx.js)

```javascript
import axios from '~/axios.js'

// 分页查询
export const queryByPage = (data) => axios.post('/api/Xxx/queryByPage', data)

// 根据 ID 查询
export const queryById = (params) => axios.get('/api/Xxx/queryById', { params })

// 新增
export const insertData = (data) => axios.post('/api/Xxx/insert', data)

// 更新
export const updateData = (data) => axios.put('/api/Xxx/update', data)

// 删除
export const deleteData = (params) => axios.delete('/api/Xxx/delete', { params })
```

### 权限指令

```vue
<!-- 按钮级权限控制 -->
<el-button v-permission="'system:user:add'">新增</el-button>
<el-button v-permission="['system:user:edit', 'system:user:delete']">编辑或删除</el-button>

<!-- 角色控制 -->
<div v-role="'admin'">仅管理员可见</div>
```

### 权限标识规范

采用三段式命名：`模块:功能:操作`

```
system:user:list    - 用户列表
system:user:add     - 新增用户
system:user:edit    - 编辑用户
system:user:delete  - 删除用户
apitest:project:list - 项目列表
ai:model:list       - AI模型列表
```

---

## 常用命令

```bash
# 安装依赖 (推荐 pnpm)
pnpm install

# 开发模式
pnpm dev

# 生产构建
pnpm build

# 预览构建结果
pnpm preview
```

---

## 环境变量 (.env)

```env
# API 代理目标 (后端地址)
VITE_API_BASE_URL=http://127.0.0.1:5000

# LangGraph Agent 配置
VITE_AGENT_API_URL=http://localhost:2024
VITE_AGENT_ASSISTANT_ID=agent
```

---

## 核心模块说明

### 1. 系统管理 (RBAC)

| 路由 | 组件 | 说明 |
|------|------|------|
| /userList | userList.vue | 用户管理 |
| /userForm | userForm.vue | 用户表单 |
| /roleList | roleList.vue | 角色管理 |
| /roleForm | roleForm.vue | 角色表单 |
| /menuList | menuList.vue | 菜单管理 |
| /menuForm | menuForm.vue | 菜单表单 |
| /deptList | deptList.vue | 部门管理 |
| /deptForm | deptForm.vue | 部门表单 |

### 2. API 测试 ⭐

| 路由 | 组件 | 说明 |
|------|------|------|
| /ApiProjectList | ApiProjectList.vue | 项目管理 |
| /ApiInfoList | ApiInfoList.vue | 接口管理 |
| /ApiInfoForm | ApiInfoForm.vue | 接口编辑 |
| /ApiInfoCaseList | ApiInfoCaseList.vue | 用例管理 |
| /ApiInfoCaseForm | ApiInfoCaseForm.vue | 用例编辑 |
| /TestPlanList | TestPlanList.vue | 测试计划 |
| /TestTaskList | TestTaskList.vue | 测试任务 |
| /ApiHistoryList | ApiHistoryList.vue | 测试历史 |
| /ApiEnvironmentList | ApiEnvironmentList.vue | 环境管理 |
| /ApiFolderTree | ApiFolderTree.vue | 文件夹管理 |
| /ApiKeyWordList | ApiKeyWordList.vue | 关键字管理 |
| /ApiMockList | ApiMockList.vue | Mock 服务 |
| /ApiDocView | ApiDocView.vue | 文档导入 |
| /ApiMetaList | ApiMetaList.vue | 元数据管理 |
| /ApiDbBaseList | ApiDbBaseList.vue | 数据库配置 |
| /ApiReportViewer | ApiReportViewer.vue | 报告查看 |

### 3. AI 测试助手 ⭐

| 路由 | 组件 | 说明 |
|------|------|------|
| /AgentChatIntegrated | AgentChatIntegrated.vue | 智能体聊天 (React) |
| /AiModelList | AiModelList.vue | AI 模型管理 |
| /AiModelForm | AiModelForm.vue | AI 模型表单 |
| /PromptTemplateList | PromptTemplateList.vue | 提示词模板 |
| /PromptTemplateForm | PromptTemplateForm.vue | 提示词表单 |
| /TestCaseList | TestCaseList.vue | 测试用例 |
| /TestCaseForm | TestCaseForm.vue | 用例表单 |

### 4. 消息管理

| 路由 | 组件 | 说明 |
|------|------|------|
| /RobotConfigList | RobotConfigList.vue | 机器人配置 |
| /RobotConfigForm | RobotConfigForm.vue | 机器人表单 |
| /RobotMsgConfigList | RobotMsgConfigList.vue | 消息模板 |
| /RobotMsgConfigForm | RobotMsgConfigForm.vue | 模板表单 |

### 5. 代码生成器

| 路由 | 组件 | 说明 |
|------|------|------|
| /GenTableList | GenTableList.vue | 表配置管理 |
| /GeneratorCode | GeneratorCode.vue | 代码生成 |
| /GenHistory | GenHistory.vue | 生成历史 |

### 6. 插件市场

| 路由 | 组件 | 说明 |
|------|------|------|
| /PluginMarket | PluginMarket.vue | 插件市场 |

---

## Vue + React 混合开发

本项目使用 `veaury` 实现 Vue 和 React 组件互操作：

```javascript
// 在 Vue 中使用 React 组件
import { applyPureReactInVue } from 'veaury'
import ReactComponent from './ReactComponent.jsx'

const VueWrappedReact = applyPureReactInVue(ReactComponent)
```

### React 组件目录

React 组件位于 `src/agent-react/` 目录：

| 目录 | 说明 |
|------|------|
| components/thread/ | 聊天线程组件 |
| components/ui/ | 基础 UI 组件 (Radix) |
| providers/ | React Context (Stream, Thread) |
| hooks/ | React Hooks |
| lib/ | 工具函数 |
| locales/ | 国际化 (en, zh-CN) |

### 路径别名说明

- `~/` - 指向 `src/` (Vue 组件使用)
- `@/` - 在 `agent-react/` 目录内部指向 `src/agent-react/` (React 组件使用)

---

## 动态路由

路由根据后端菜单数据动态生成：

```javascript
import { addDynamicRoutes } from '~/router/index.js'

// 登录成功后调用
addDynamicRoutes(menuTree)
```

路由匹配规则：
1. 如果 `path` 以 `/` + 大写字母开头，直接使用
2. 否则根据 `component` 字段匹配 `views/**/*.vue`

---

## Axios 配置

### Token 自动刷新

```javascript
// axios.js 已配置自动 Token 刷新
// 401 错误时自动调用 /api/refreshToken
// 刷新成功后重新发送原请求
```

### 响应结构

```javascript
// 后端统一响应格式
{
  code: 200,      // 200成功, -1失败
  msg: "消息",
  data: {},       // 数据对象
  trace_id: "xxx" // 请求追踪ID
}
```

---

## 默认账号

- **用户名**: `admin`
- **密码**: `admin123`
- **角色**: 超级管理员 (拥有所有权限)

---

## 注意事项

1. **API 代理**: 所有 `/api` 请求会代理到后端 `http://127.0.0.1:5000`，并去除 `/api` 前缀
2. **权限控制**: 使用 `v-permission` 指令控制按钮显示
3. **路由守卫**: 未登录自动跳转 `/login`，无权限跳转 `/403`
4. **样式隔离**: Vue 组件使用 Element Plus，React 组件使用 Radix UI + TailwindCSS
5. **包管理器**: 推荐使用 `pnpm`，已配置 sass-embedded 覆盖
6. **动态路由**: 登录后根据菜单权限动态添加路由

---

## 现有功能清单

### Vue 页面组件 (73个)

| 模块 | 组件 | 说明 |
|------|------|------|
| 基础 | 403.vue, 404.vue, 500.vue | 错误页面 |
| 登录 | login.vue | 登录页 |
| 主页 | home.vue, FHeader.vue, FMenu.vue, FTagList.vue | 布局组件 |
| 统计 | statistics.vue | 统计面板 |
| 用户 | userList.vue, userForm.vue | 用户管理 |
| 角色 | roleList.vue, roleForm.vue | 角色管理 |
| 菜单 | menuList.vue, menuForm.vue | 菜单管理 |
| 部门 | deptList.vue, deptForm.vue | 部门管理 |
| 项目 | ApiProjectList.vue, ApiProjectForm.vue | 项目管理 |
| 接口 | ApiInfoList.vue, ApiInfoForm.vue, ApiInfoEditor.vue | 接口管理 |
| 用例 | ApiInfoCaseList.vue, ApiInfoCaseForm.vue | 用例管理 |
| 计划 | TestPlanList.vue, TestPlanForm.vue | 测试计划 |
| 任务 | TestTaskList.vue, TestTaskForm.vue | 测试任务 |
| 历史 | ApiHistoryList.vue, ApiHistoryDetail.vue | 测试历史 |
| 环境 | ApiEnvironmentList.vue | 环境管理 |
| 文件夹 | ApiFolderTree.vue | 文件夹管理 |
| 关键字 | ApiKeyWordList.vue, ApiKeyWordForm.vue | 关键字管理 |
| Mock | ApiMockList.vue | Mock 服务 |
| 文档 | ApiDocView.vue | 文档导入 |
| 元数据 | ApiMetaList.vue, ApiMetaForm.vue | 元数据管理 |
| 数据库 | ApiDbBaseList.vue, ApiDbBaseForm.vue | 数据库配置 |
| 报告 | ApiReportViewer.vue | 报告查看 |
| 执行 | TestExecutionView.vue | 执行视图 |
| AI聊天 | AgentChatIntegrated.vue | 智能体聊天 |
| AI模型 | AiModelList.vue, AiModelForm.vue | AI 模型管理 |
| 提示词 | PromptTemplateList.vue, PromptTemplateForm.vue | 提示词模板 |
| 测试用例 | TestCaseList.vue, TestCaseForm.vue | AI 测试用例 |
| 机器人 | RobotConfigList.vue, RobotConfigForm.vue | 机器人配置 |
| 消息 | RobotMsgConfigList.vue, RobotMsgConfigForm.vue | 消息模板 |
 | 插件 | PluginMarket.vue | 插件市场 |
 | 生成器 | GenTableList.vue, GeneratorCode.vue, GenHistory.vue | 代码生成 |
 | 生成器 | GenTableForm.vue | 表配置表单 |

### API 请求文件 (35个)

 | 文件 | 说明 |
 |------|------|
 | login.js | 登录认证 |
 | user.js | 用户管理 |
 | role.js | 角色管理 |
 | menu.js | 菜单管理 |
 | dept.js | 部门管理 |
 | apiProject.js | 项目管理 |
 | apiinfo.js | 接口管理 |
 | apiInfoCase.js | 用例管理 |
 | testPlan.js | 测试计划 |
 | testTask.js | 测试任务 |
 | apiHistory.js | 测试历史 |
 | apiEnvironment.js | 环境管理 |
 | apiFolder.js | 文件夹管理 |
 | apiKeyWord.js | 关键字管理 |
 | apiMock.js | Mock 服务 |
 | apiDoc.js | 文档导入 |
 | apiMeta.js | 元数据管理 |
 | dbBase.js | 数据库配置 |
 | aimodel.js | AI 模型 |
 | prompttemplate.js | 提示词模板 |
 | testcase.js | 测试用例 |
 | robotConfig.js | 机器人配置 |
 | robotMsgConfig.js | 消息模板 |
 | plugin.js | 插件管理 |
 | statistics.js | 统计数据 |
 | gentable.js | 表配置管理 |
 | generator.js | 代码生成 |
 | genhistory.js | 生成历史 |

---

## 相关文档

- [README.md](./README.md) - 项目详细说明
- [后端项目](../platform-fastapi-server/AGENTS.md) - FastAPI 后端
- [Element Plus](https://element-plus.org/) - Vue UI 组件库
- [veaury](https://github.com/devilwjp/veaury) - Vue + React 互操作
- [Radix UI](https://www.radix-ui.com/) - React UI 组件库
