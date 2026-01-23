 # vue-fastapi-admin 前端设计文档

 本文档基于 `web/` 目录下的实际代码结构，对前端技术栈、模块划分与关键实现进行说明。

 ## 一、技术栈与总体设计

 - 框架：Vue 3（组合式 API，`<script setup>` 语法）
 - 构建工具：Vite
 - UI 组件库：Naive UI
 - 状态管理：Pinia
 - 路由：Vue Router 4
 - 样式：UnoCSS + SCSS，自定义全局样式
 - HTTP：Axios 封装 + 请求/响应拦截器
 - i18n：vue-i18n，支持中英文多语言

 设计目标：

 - 与后端 RBAC 权限模型强耦合的动态路由与按钮权限控制；
 - 中后台典型布局（顶栏 + 侧边菜单 + 标签页 + 内容区域）；
 - 通用 CRUD 表格、查询条件、弹窗表单封装，减少重复代码。

 ## 二、项目结构概览

 前端主要目录结构（节选）：

 - `web/src/main.js`：应用入口
 - `web/src/App.vue`：根组件
 - `web/src/layout/`：通用布局（顶栏、侧边栏、标签栏、内容区域）
 - `web/src/router/`：路由与路由守卫
 - `web/src/store/`：Pinia Store 定义
 - `web/src/api/`：业务接口调用封装
 - `web/src/views/`：业务页面
 - `web/src/components/`：通用组件（表格、弹窗、查询栏等）
 - `web/src/directives/`：自定义指令（权限控制）
 - `web/src/utils/`：工具函数（HTTP、存储、通用方法等）

 ## 三、应用入口与初始化流程

 入口文件：`web/src/main.js`

 - 创建 Vue 应用实例；
 - 注册 Naive UI、UnoCSS、i18n、Pinia 等插件；
 - 调用 `setupRouter(app)` 完成路由初始化；
 - 挂载至 DOM 根节点。

 路由初始化由 [web/src/router/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/router/index.js#L1-L18) 负责：

 - 使用 `createRouter` 创建路由实例；
 - 根据 `VITE_USE_HASH` 环境变量选择 `createWebHistory` 或 `createWebHashHistory`；
 - 初始只挂载 `basicRoutes`（登录页、重定向页、错误页等）；
 - 在 `setupRouter` 中调用 `addDynamicRoutes`：
   - 若无 token，仅添加占位路由 `EMPTY_ROUTE`；
   - 若有 token，拉取用户信息与菜单/接口权限，生成动态路由并注入；
   - 注册路由守卫 `setupRouterGuard(router)`，处理鉴权、页面标题、加载动画等。

 ## 四、路由与菜单设计

 ### 4.1 路由配置

 路由配置入口：`web/src/router/routes/index.js`

 - `basicRoutes`：
   - 登录页、根路由重定向、错误页等基础路由；
 - `EMPTY_ROUTE`：
   - 当尚未获取到用户菜单路由时，临时使用的占位路由；
 - `NOT_FOUND_ROUTE`：
   - 兜底 404 配置。

 动态路由生成逻辑在 [web/src/store/modules/permission/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/store/modules/permission/index.js#L60-L93)：

 - `generateRoutes`：
   - 调用 `api.getUserMenu()` 获取后端根据当前用户角色筛选后的菜单树；
   - 通过 `buildRoutes` 将菜单数据转换为 Vue Router 路由配置；
   - 将生成的路由保存到 `accessRoutes` 状态中；
 - `getAccessApis`：
   - 调用 `api.getUserApi()` 获取用户可访问接口列表，存储在 `accessApis` 中，用于按钮权限控制。

 `buildRoutes` 关键特性：

 - 顶级菜单统一使用布局组件 `Layout`，子菜单则直接映射到对应业务视图；
 - 支持两种情况：
   - 菜单有子菜单：children 全部来自 `e.children`；
   - 菜单无子菜单：自动创建一个默认子路由，path 为空字符串，这样保持视图渲染的一致性。

 ### 4.2 菜单与视图映射

 - 后端菜单 `component` 字段与前端视图路径约定：
   - 顶级菜单：`component = "Layout"`；
   - 子菜单/页面：`component = "/system/user"`，对应视图文件路径为：
     - `/src/views/system/user/index.vue`
 - 在 `buildRoutes` 中，通过 `vueModules` 动态导入视图组件：
   - `vueModules[\`/src/views${e_child.component}/index.vue\`]`

 ## 五、状态管理设计（Pinia）

 Pinia Store 根入口：`web/src/store/index.js`

 核心模块：

 - `modules/user`：用户信息与登录状态管理
   - `userInfo`：用户基本信息；
   - `getUserInfo`：调用后端 `/base/userinfo` 接口；
   - `logout`：清除 token、重置 tags 与 permission、重置路由并跳转登录页；
 - `modules/permission`：路由与接口权限管理
   - `accessRoutes`：动态路由列表；
   - `accessApis`：接口权限标识列表；
   - `generateRoutes` / `getAccessApis` 用于初始化权限数据；
 - `modules/tags`：多标签页（Tab）管理
   - 记录打开过的路由，支持关闭、固定、批量关闭等操作；
 - `modules/app`：全局 UI 配置
   - 菜单折叠、主题切换、语言切换等。

 状态管理策略：

 - 用户退出登录时，通过 `logout` 动作调用：
   - `useTagsStore().resetTags()` 清理多标签状态；
   - `usePermissionStore().resetPermission()` 清理权限与动态路由；
   - `resetRouter()` 移除运行时动态路由；
   - 清理 token 并重置 `userInfo`。

 ## 六、HTTP 请求封装与错误处理

 ### 6.1 Axios 实例

 文件：[/web/src/utils/http/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/utils/http/index.js#L1-L19)

 - `createAxios`：
   - 添加默认配置（如超时时间）；
   - 注册请求与响应拦截器；
 - `request`：
   - 基于 `createAxios` 创建的实例；
   - `baseURL` 为环境变量 `VITE_BASE_API`，通常指向后端 `/api/v1`。

 ### 6.2 拦截器

 - 请求拦截器：
   - 统一在请求头中注入 token；
   - 支持 `noNeedToken` 选项跳过 token 注入（如登录接口）；
 - 响应拦截器：
   - 统一处理业务 code、错误提示；
   - 当返回 401 时，触发登出逻辑并跳转到登录页面。

 ### 6.3 业务 API 封装

 文件：[/web/src/api/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/api/index.js#L1-L42)

 - 将后端接口按资源模块分组：
   - 基础：`login`、`getUserInfo`、`getUserMenu`、`getUserApi`、`updatePassword` 等；
   - 用户：`getUserList`、`createUser`、`updateUser`、`deleteUser`、`resetPassword`；
   - 角色：`getRoleList`、`createRole`、`updateRole`、`deleteRole`、`updateRoleAuthorized`、`getRoleAuthorized`；
   - 菜单：`getMenus`、`createMenu`、`updateMenu`、`deleteMenu`；
   - API：`getApis`、`createApi`、`updateApi`、`deleteApi`、`refreshApi`；
   - 部门：`getDepts`、`createDept`、`updateDept`、`deleteDept`；
   - 审计日志：`getAuditLogList`。

 ## 七、权限控制与指令设计

 ### 7.1 接口权限

 - 接口权限由后端 `/base/userapi` 接口返回：
   - 列表元素形如 `get/api/v1/user/list`；
 - 在 `permission` Store 模块中存入 `accessApis`；
 - 通过工具函数或直接在组件内进行权限判断。

 ### 7.2 按钮级权限指令

 文件：[/web/src/directives/permission.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/directives/permission.js#L1-L34)

 - 指令名：`v-permission`；
 - 使用方式：
   - `v-permission="'get/api/v1/user/list'"`；
 - 实现逻辑：
   - 调用 `hasPermission` 判断当前用户是否拥有某权限字符串；
   - 若用户为超级管理员，则直接放行；
   - 否则检查 `userPermissionStore.apis` 中是否包含该权限；
   - 未包含时移除对应 DOM 元素，实现按钮级隐藏。

 此设计实现了“接口权限即按钮权限”，前后端使用同一套权限标识。

 ## 八、通用组件与 CRUD 设计

 系统管理类页面（用户/角色/菜单/API/部门等）大量采用通用 CRUD 组件：

 - 列表视图：
   - `CommonPage`：统一的页面布局容器；
   - `QueryBar` / `QueryBarItem`：顶部查询条件区域；
   - `CrudTable`：封装分页表格、搜索、查询、重置等逻辑；
 - 弹窗表单：
   - `CrudModal`：通用弹窗组件，结合表单组件实现新增/编辑；
 - 数据驱动：
   - 通过组合式函数 `useCRUD`（位于 `web/src/composables/useCRUD.js`）统一封装增删改查流程；
   - 每个业务页只需要传入 `doCreate`、`doUpdate`、`doDelete`、`refresh` 等实现。

 典型示例：API 管理页面 [web/src/views/system/api/index.vue](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/views/system/api/index.vue#L1-L67)

 - 使用 `useCRUD` 管理 API 列表增删改；
 - 使用 `CrudTable` 展示数据，支持分页与查询；
 - 使用 `CrudModal` 进行创建/编辑；
 - 顶部提供“刷新 API”按钮，通过调用 `/api/v1/api/refresh` 与后端同步接口列表。

 ## 九、布局与页面设计

 布局组件位于 `web/src/layout/`：

 - `index.vue`：整体布局入口；
 - `components/header`：顶栏，包含：
   - 面包屑、全屏、主题切换、语言切换、用户头像等；
 - `components/sidebar`：侧边栏菜单；
 - `components/tags`：多标签页，用于展示当前打开的路由；
 - `components/AppMain.vue`：主体内容区域，承载当前路由对应的视图组件。

 首页工作台示例：[web/src/views/workbench/index.vue](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/views/workbench/index.vue#L1-L47)

 - 通过 `AppPage` 组件包裹页面；
 - 顶部展示欢迎语与统计卡片；
 - 下方展示项目相关卡片列表。

 ## 十、国际化设计

 国际化配置：

 - 语言包文件：
   - `web/i18n/messages/cn.json`
   - `web/i18n/messages/en.json`
 - 语言入口：`web/i18n/index.js`

 页面通过 `$t('xxx.yyy')` 访问国际化文案，例如：

 - 工作台欢迎语定义于 `views.workbench.*`，在 [en.json](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/i18n/messages/en.json#L1-L24) 中可见；
 - 顶栏、错误页、系统设置等均采用统一的 i18n key。

 ## 十一、小结

 - 前端通过动态路由 + 接口权限，实现了与后端 RBAC 深度配合的权限体系；
 - 通用 CRUD 组件大幅减少增删改查页面的样板代码；
 - 使用 Pinia、Vue 3 组合式 API 与 Naive UI，使代码结构清晰、扩展性良好。

