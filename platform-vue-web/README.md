# AI Agent Testing Platform - Vue Frontend

基于 Vue 3 + Element Plus 的 AI 智能体测试平台前端

## 技术栈

- **框架**: Vue 3
- **UI组件库**: Element Plus
- **路由**: Vue Router
- **状态管理**: Vuex
- **HTTP客户端**: Axios
- **构建工具**: Vite

## 项目结构

```
platform-vue-web/
├── src/
│   ├── App.vue              # 根组件
│   ├── main.js              # 入口文件
│   ├── axios.js             # Axios配置
│   ├── router/              # 路由配置
│   │   └── index.js
│   ├── store/               # Vuex状态管理
│   │   └── index.js
│   ├── directives/          # 自定义指令 🆕
│   │   └── permission.js    # 权限指令（v-permission, v-role）
│   ├── components/          # 公共组件
│   │   ├── JsonEditor.vue   # JSON编辑器组件 🆕
│   │   └── YamlViewer.vue   # YAML查看器组件 🆕
│   └── views/               # 页面组件
│       ├── 403.vue          # 403 无权限访问页面 🆕
│       ├── 404.vue          # 404 页面不存在
│       ├── 500.vue          # 500 服务器错误页面 🆕
│       ├── login/           # 登录
│       ├── home/            # 主页
│       ├── users/           # 用户管理（已扩展RBAC字段）
│       │   ├── user.js
│       │   ├── userList.vue
│       │   └── userForm.vue
│       ├── system/          # 系统管理 🆕
│       │   ├── role/        # 角色管理
│       │   │   ├── role.js
│       │   │   ├── roleList.vue
│       │   │   └── roleForm.vue
│       │   ├── menu/        # 菜单管理
│       │   │   ├── menu.js
│       │   │   ├── menuList.vue
│       │   │   └── menuForm.vue
│       │   └── dept/        # 部门管理
│       │       ├── dept.js
│       │       ├── deptList.vue
│       │       └── deptForm.vue
│       ├── apitest/         # API测试
│       │   ├── project/     # 项目管理
│       │   ├── keyword/     # 关键字管理
│       │   └── apiMate/     # 素材管理
│       └── aiassistant/     # AI测试助手模块 ⭐新增
│           ├── chat/        # AI对话功能
│           │   ├── index.vue
│           │   ├── AiChatInterface.vue  # ChatGPT风格对话界面
│           │   └── aiConversation.js    # 对话API服务
│           ├── model/       # AI模型管理
│           │   ├── index.vue
│           │   ├── AiModelList.vue
│           │   └── aimodel.js
│           ├── prompt/      # 提示词模板管理
│           │   ├── index.vue
│           │   ├── PromptTemplateList.vue
│           │   └── prompttemplate.js
│           └── testcase/    # 测试用例管理
│               ├── index.vue
│               ├── TestCaseList.vue
│               └── testcase.js
├── public/
├── index.html
├── package.json
└── vite.config.js
```

## 安装依赖

```bash
npm install
```

或使用 pnpm（推荐）：

```bash
pnpm install
```

## 开发模式

```bash
npm run dev
```

访问：http://localhost:5173

## 生产构建

```bash
npm run build
```

## AI测试助手功能 ⭐新增

### 1. AI对话界面 (AiChatInterface.vue)

完整的ChatGPT风格对话界面，支持实时流式输出和测试用例生成。

**核心特性**：
- ✅ ChatGPT风格的聊天界面
- ✅ 实时流式输出（Server-Sent Events）
- ✅ 多轮对话，自动上下文管理
- ✅ 支持文件上传（TXT/Word/PDF需求文档）
- ✅ 可配置AI模型和提示词模板
- ✅ 测试用例实时解析和展示
- ✅ 测试用例在线编辑和保存
- ✅ 对话历史管理（保存/恢复/删除）

**使用示例**：
```vue
<template>
  <AiChatInterface />
</template>

<script setup>
import AiChatInterface from '~/views/aiassistant/chat/AiChatInterface.vue'
</script>
```

### 2. AI模型管理 (AiModelList.vue)

管理和配置多个AI模型（DeepSeek、通义千问等）。

**功能**：
- 分页查询、新增、编辑、删除AI模型
- 启用/禁用模型
- 测试模型连接
- 支持自定义API地址和密钥

### 3. 提示词模板管理 (PromptTemplateList.vue)

管理不同场景的AI提示词模板。

**功能**：
- 按测试类型（API/Web/App/通用）分类管理
- 支持变量替换
- 激活/停用模板
- 模板内容在线编辑

### 4. 测试用例管理 (TestCaseList.vue)

管理AI生成的测试用例。

**功能**：
- 分页查询、新增、编辑、删除测试用例
- 高级搜索（项目、测试类型、优先级）
- JSON/YAML双格式支持
- 批量导出为YAML文件
- 在线JSON编辑器

### 5. 公共组件

#### JsonEditor.vue
JSON编辑器组件，支持：
- 语法高亮
- 格式化
- 验证
- 实时预览

#### YamlViewer.vue
YAML查看器组件，支持：
- 语法高亮
- 复制
- 下载
- 编辑模式

## RBAC权限管理功能 🆕

### 1. 权限指令

#### v-permission 指令

用于控制按钮或元素的显示/隐藏，基于用户权限：

```vue
<template>
  <!-- 单个权限 -->
  <el-button v-permission="'system:user:add'">新增用户</el-button>
  
  <!-- 多个权限（满足任一即可） -->
  <el-button v-permission="['system:user:edit', 'system:user:delete']">
    编辑或删除
  </el-button>
</template>
```

#### v-role 指令

用于控制元素显示/隐藏，基于用户角色：

```vue
<template>
  <!-- 单个角色 -->
  <div v-role="'admin'">仅管理员可见</div>
  
  <!-- 多个角色（满足任一即可） -->
  <div v-role="['admin', '超级管理员']">管理员或超管可见</div>
</template>
```

### 2. Vuex状态管理

#### 状态 (State)

```javascript
{
  userInfo: null,      // 用户信息
  roles: [],           // 用户角色列表
  permissions: [],     // 用户权限列表
  menuTree: []         // 用户菜单树
}
```

#### 方法 (Mutations)

- `setUserInfo(userInfo)` - 设置用户信息
- `setRoles(roles)` - 设置用户角色
- `setPermissions(permissions)` - 设置用户权限
- `setMenuTree(menuTree)` - 设置菜单树
- `clearUserInfo()` - 清除用户信息（登出）

#### 计算属性 (Getters)

- `hasPermission(perm)` - 判断是否有某个权限
- `hasRole(role)` - 判断是否有某个角色

### 3. 管理界面

#### 3.1 角色管理

**列表页面** (/roleList)：
- ✅ 角色列表（分页、搜索）
- ✅ 跳转到新增/编辑表单
- ✅ 删除角色
- ✅ 为角色分配菜单权限（树形选择对话框）

**表单页面** (/roleForm)：
- ✅ 新增角色
- ✅ 编辑角色
- ✅ 表单验证
- ✅ 提交后返回列表

#### 3.2 菜单管理

**列表页面** (/menuList)：
- ✅ 菜单树形展示
- ✅ 刷新数据
- ✅ 跳转到新增/编辑表单
- ✅ 删除菜单

**表单页面** (/menuForm)：
- ✅ 新增菜单（支持选择上级菜单）
- ✅ 编辑菜单
- ✅ 菜单类型选择（菜单/按钮）
- ✅ 权限标识配置
- ✅ 表单验证

#### 3.3 部门管理

**列表页面** (/deptList)：
- ✅ 部门树形展示
- ✅ 刷新数据
- ✅ 跳转到新增/编辑表单
- ✅ 删除部门

**表单页面** (/deptForm)：
- ✅ 新增部门（支持选择上级部门）
- ✅ 编辑部门
- ✅ 部门排序
- ✅ 表单验证

#### 3.4 用户管理

**列表页面** (/userList)：
- ✅ 用户列表（分页、搜索）
- ✅ 显示字段：id、用户名、邮箱、联系电话、部门ID、状态、性别、创建时间
- ✅ 跳转到新增/编辑表单
- ✅ 删除用户

**表单页面** (/userForm)：
- ✅ 新增用户
- ✅ 编辑用户
- ✅ 完整字段支持：
  * `id`: 用户ID（编辑时自动填充，禁用修改）
  * `username`: 用户名（必填）
  * `password`: 密码（必填）
  * `email`: 邮箱（可选，带格式验证）
  * `mobile`: 联系电话（可选，带手机号格式验证）
  * `dept_id`: 部门ID（可选，数字输入）
  * `ssex`: 性别（单选：0男/1女/2保密，默认保密）
  * `status`: 状态（单选：0锁定/1有效，默认有效）
  * `avatar`: 头像URL（可选）
  * `description`: 描述（可选，文本域）
- ✅ 表单验证（用户名、密码必填，邮箱和手机号格式验证）
- ✅ 提交后返回列表

**字段统一说明**：
- 所有 RBAC 模块（User、Role、Menu、Dept）统一使用 `id` 作为主键
- 简化前后端字段映射，代码更简洁统一

### 4. API请求文件

#### 用户管理 API (views/users/user.js)

```javascript
import { queryByPage, insertData, updateData, deleteData, 
         assignRoles, getUserRoles, updateStatus } from '~/views/users/user.js'
```

#### 角色管理 API (views/system/role/role.js)

```javascript
import { queryByPage, insertData, updateData, deleteData,
         assignMenus, getRoleMenus } from '~/views/system/role/role.js'
```

#### 菜单管理 API (views/system/menu/menu.js)

```javascript
import { getMenuTree, insertData, updateData, deleteData,
         getUserMenus } from '~/views/system/menu/menu.js'
```

#### 部门管理 API (views/system/dept/dept.js)

```javascript
import { getDeptTree, insertData, updateData, deleteData } from '~/views/system/dept/dept.js'
```

## 默认登录账号

- **用户名**: admin
- **密码**: admin123
- **角色**: 超级管理员（拥有所有权限）

## 权限标识规范

权限标识采用三段式命名：`模块:功能:操作`

**示例**：

- `system:user:view` - 查看用户
- `system:user:add` - 新增用户
- `system:user:edit` - 编辑用户
- `system:user:delete` - 删除用户
- `system:user:role` - 分配角色
- `system:role:view` - 查看角色
- `system:role:menu` - 分配权限
- `system:menu:view` - 查看菜单
- `system:dept:view` - 查看部门

## 菜单类型

- **类型 0（菜单）**: 显示在侧边栏，有路由路径和组件
- **类型 1（按钮）**: 不显示在侧边栏，仅作为权限标识

## 错误页面 🆕

系统提供了三种错误页面，使用Element Plus的`el-result`组件：

### 403 - 无权限访问
- **路由**: `/403`
- **使用场景**: 用户无权限访问某个页面或资源
- **自动跳转**: axios拦截器捕获HTTP 403状态码时自动跳转

### 404 - 页面不存在
- **路由**: `/:pathMatch(.*)*`（所有未匹配的路由）
- **使用场景**: 访问不存在的页面

### 500 - 服务器错误
- **路由**: `/500`
- **使用场景**: 服务器内部错误
- **自动跳转**: axios拦截器捕获HTTP 500状态码时自动跳转

**手动跳转示例**：
```javascript
// 跳转到403页面
this.$router.push('/403')

// 跳转到500页面
this.$router.push('/500')
```

## 开发规范

1. **权限控制**：所有需要权限控制的按钮/元素，必须使用 `v-permission` 或 `v-role` 指令
2. **API调用**：统一使用 `axios.js` 中配置的axios实例
3. **响应处理**：已在axios拦截器中统一处理成功/失败提示
4. **错误处理**：HTTP 403/500错误会自动跳转到对应错误页面
5. **代码风格**：遵循Vue 3 Composition API风格

## 注意事项

1. 权限指令会直接从DOM中移除无权限的元素
2. 后端API需正确配置CORS
3. 确保后端服务已启动并在 `/api` 路径下可访问
4. 首次登录使用 admin/admin123 账号

## 版本信息

- **版本**: 2.0.0
- **框架**: Vue 3
- **UI组件**: Element Plus
- **Node**: 14+

## 后续计划

- [ ] 动态路由加载（根据用户菜单权限）
- [ ] 数据权限过滤（部门级别）
- [ ] 权限缓存优化
- [ ] 更多权限验证场景

