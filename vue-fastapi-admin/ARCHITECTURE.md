 # vue-fastapi-admin 架构设计

 本文档基于当前仓库代码结构与实现进行整理，旨在帮助快速理解整个系统的技术架构与运行机制。

 ## 一、整体架构概览

 系统采用前后端分离架构：

 - 前端：Vue 3 + Vite + Naive UI + Pinia + Vue Router + Axios
 - 后端：FastAPI + Tortoise ORM + Aerich 迁移 + JWT 鉴权
 - 数据库：默认 SQLite，可切换 MySQL / PostgreSQL
 - 部署：前端打包为静态资源，由 Nginx 提供；后端通过 Uvicorn 运行 FastAPI 应用

 ### 1.1 系统架构图

 ```mermaid
 graph TD
   subgraph Client[浏览器]
     UI[Vue3 + Naive UI\n前端界面]
   end

   subgraph Frontend[前端应用 - web/]
     Router[Vue Router\n动态菜单路由]
     Store[Pinia Store\nuser/permission/tags/app]
     HTTP[Axios 封装\nweb/src/utils/http]
   end

   subgraph Backend[后端服务 - app/]
     FastAPI[FastAPI 应用 app:app\n(app/__init__.py)]
     Middleware[中间件\nCORS + 审计日志 + 后台任务]
     APIv1[REST API /api/v1\n路由分组]
     Service[业务控制器\napp/controllers]
     ORM[Tortoise ORM\napp/models]
   end

   subgraph DB[数据库]
     DBMain[(SQLite / MySQL / PostgreSQL)]
   end

   subgraph Infra[运维部署]
     Nginx[Nginx: web.conf\n静态资源 + /api 反向代理]
     Uvicorn[Uvicorn\nrun.py]
   end

   UI --> Router
   Router --> HTTP
   HTTP -->|"VITE_BASE_API=/api/v1"| FastAPI

   FastAPI --> Middleware
   Middleware --> APIv1
   APIv1 --> Service
   Service --> ORM
   ORM --> DBMain

   Nginx -->|/| UI
   Nginx -->|/api/ -> 127.0.0.1:9999| FastAPI
   Uvicorn --> FastAPI
 ```

 ### 1.2 目录结构与职责

 - 后端核心目录
   - `app/__init__.py`：创建 FastAPI 实例、注册中间件与路由、生命周期管理
   - `app/core/init_app.py`：数据库初始化、数据初始化（超级管理员、菜单、API、角色）
   - `app/api/`：FastAPI 路由聚合，按业务模块划分 v1 版本接口
   - `app/controllers/`：面向资源的业务控制器，封装 CRUD 逻辑
   - `app/models/`：Tortoise ORM 模型定义（用户、角色、菜单、API、部门、审计日志等）
   - `app/schemas/`：Pydantic 请求/响应模型与通用返回结构
   - `app/utils/`：JWT、密码加密等通用工具
   - `app/core/middlewares.py`：自定义中间件（审计日志、后台任务）

 - 前端核心目录
   - `web/src/router/`：基础路由 + 动态路由生成 + 路由守卫
   - `web/src/store/`：Pinia 状态管理（用户、权限、标签页、应用配置等）
   - `web/src/api/`：与后端 REST API 的调用封装
   - `web/src/views/`：业务页面（系统管理、工作台、登录等）
   - `web/src/directives/permission.js`：基于接口权限的按钮级别指令控制
   - `web/src/utils/http/`：Axios 实例与拦截器封装

 ## 二、后端架构设计

 ### 2.1 应用启动流程

 1. 入口文件 [run.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/run.py#L1-L13) 使用 Uvicorn 启动 `app:app`。
 2. `app` 在 [app/__init__.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/__init__.py#L20-L41) 中创建：
    - 配置应用基本信息（标题、描述、版本）
    - 通过 `make_middlewares` 注册中间件
    - 注册全局异常处理器
    - 注册 `/api` 前缀的路由
    - 使用 `lifespan` 钩子在启动时初始化数据库与基础数据，在关闭时释放数据库连接
 3. `init_data` 在 [app/core/init_app.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/core/init_app.py#L185-L233) 中依次完成：
    - `init_db`：基于 Aerich 迁移初始化数据库结构
    - `init_superuser`：初始化 admin 超级管理员
    - `init_menus`：生成默认菜单结构
    - `init_apis`：扫描路由生成 API 列表
    - `init_roles`：初始化管理员、普通用户角色及其默认权限

 ### 2.2 路由与模块划分

 - 顶层路由聚合：
   - [app/api/__init__.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/__init__.py#L1-L9) 中定义 `api_router`，并挂载 `v1_router` 到 `/api/v1`
 - v1 版本路由分组：
   - [app/api/v1/__init__.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/__init__.py#L3-L20)
   - 模块划分：
     - `/base`：登录、获取当前用户信息、菜单、API 权限、修改密码
     - `/user`：用户管理（分页、增删改查、重置密码）
     - `/role`：角色管理及权限分配
     - `/menu`：菜单管理
     - `/api`：API 元数据管理及刷新
     - `/dept`：部门组织架构管理
     - `/auditlog`：操作审计日志查询
 - 权限控制：
   - 除 `/base` 登录相关接口外，其余模块在 v1 路由层统一挂载 `DependPermission` 依赖，用于 RBAC 接口访问控制。

 ### 2.3 中间件与审计日志

 中间件由 [make_middlewares](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/core/init_app.py#L32-L52) 组装：

 - `CORSMiddleware`：跨域访问控制，可配置跨域来源、方法、头等
 - `BackGroundTaskMiddleware`：后台任务支持（例如日志写入、异步处理）
 - `HttpAuditLogMiddleware`：
   - 拦截 `GET/POST/PUT/DELETE` 请求
   - 记录请求方法、路径、状态码、请求参数与响应数据
   - 支持排除路径（例如 `/api/v1/base/access_token`、`/docs`、`/openapi.json` 等）
   - 日志数据落库到 `audit_log` 表，实现接口级审计

 ### 2.4 权限模型（RBAC）

 权限实体模型定义在 [app/models/admin.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/models/admin.py#L9-L88)：

 - 用户（User）：
   - 多角色：`roles = ManyToManyField("models.Role")`
   - 关联部门：`dept_id`
   - `is_superuser` 标记超级管理员，拥有所有菜单和 API 权限
 - 角色（Role）：
   - 多菜单：`menus = ManyToManyField("models.Menu")`
   - 多 API：`apis = ManyToManyField("models.Api")`
 - 菜单（Menu）：
   - 支持目录 / 菜单 / 按钮类型（由 `MenuType` 枚举定义）
   - `parent_id` 形成树状菜单结构
   - `component` 映射到前端视图路径
 - API（Api）：
   - 记录路径、请求方法、摘要与标签
   - 被角色关联后用于接口级权限判定

 运行时权限控制流程：

 1. 登录成功后，后端生成包含用户 ID、用户名、是否超级管理员等信息的 JWT。
 2. 前端将 token 存储到本地，并在 Axios 请求头中携带。
 3. 后端 `DependAuth` 解析 token，将 `user_id` 放入上下文变量 `CTX_USER_ID`。
 4. `/base/usermenu` 根据用户角色返回可访问菜单树；
 5. `/base/userapi` 返回该用户可访问的 `method + path` 字符串列表；
 6. 前端基于这些数据动态生成路由，按钮级别控制通过自定义指令 `v-permission` 实现。

 ## 三、前端架构与数据流

 ### 3.1 路由与动态菜单

 - 路由入口：[web/src/router/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/router/index.js#L1-L18)
   - 使用 `createWebHistory` 或 `createWebHashHistory`（由 `VITE_USE_HASH` 控制）
   - 初始化 `basicRoutes`（登录、404 等基础路由）
   - 在 `setupRouter` 中调用 `addDynamicRoutes` 注入业务路由
 - 动态路由加载：
   - `addDynamicRoutes` 流程：
     1. 检查是否存在 token
     2. 通过 `useUserStore().getUserInfo()` 拉取当前用户信息
     3. 通过 `usePermissionStore().generateRoutes()` 获取后端返回的菜单数据并构建路由
     4. 通过 `router.addRoute` 注入到运行时路由表
     5. 加载完毕后移除占位路由 `EMPTY_ROUTE`，并添加 `NOT_FOUND_ROUTE`
 - 基于菜单构建路由逻辑在 [web/src/store/modules/permission/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/store/modules/permission/index.js#L60-L93)：
   - `buildRoutes` 将后端菜单结构转换为前端路由对象，父菜单组件统一使用 `Layout`。
   - 支持有子菜单与无子菜单两种情况：
     - 有子菜单：children 直接映射子菜单的 `component`
     - 无子菜单：生成一个默认子路由，path 为空字符串，component 为当前菜单对应视图

 ### 3.2 状态管理（Pinia）

 关键 Store 模块：

 - `user` 模块：[web/src/store/modules/user/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/store/modules/user/index.js#L7-L65)
   - 维护当前用户信息（id、username、email、avatar、roles 等）
   - 提供 `getUserInfo`、`logout`、`setUserInfo` 等动作
 - `permission` 模块：
   - 管理动态路由 `accessRoutes` 与接口权限 `accessApis`
   - 提供 `generateRoutes` 与 `getAccessApis` 两个关键动作
 - `tags` 模块：
   - 管理多页签（浏览过的路由），支持关闭、固定等操作
 - `app` 模块：
   - 全局 UI 状态，如侧边栏折叠、主题模式、语言等

 ### 3.3 HTTP 请求层

 - Axios 创建与封装在 [web/src/utils/http/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/utils/http/index.js#L1-L19)：
   - 默认超时 12 秒
   - 通过 `reqResolve/reqReject` 与 `resResolve/resReject` 实现统一的请求与响应拦截
   - `baseURL` 从环境变量 `VITE_BASE_API` 读取，一般配置为 `/api/v1`
 - 业务 API 封装在 [web/src/api/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/api/index.js#L1-L42)：
   - 将后端 REST 接口按资源进行归类，例如：
     - `login`、`getUserInfo`、`getUserMenu`、`getUserApi` 等基础能力
     - 用户、角色、菜单、API、部门、审计日志等模块的 CRUD

 ## 四、功能模块图

 ### 4.1 功能模块概览

 ```mermaid
 graph LR
   Login[登录认证] --> Token[JWT 颁发]
   Token --> UserInfo[用户信息]
   Token --> MenuPermission[菜单权限]
   Token --> ApiPermission[接口权限]

   UserInfo --> Workbench[工作台]
   MenuPermission --> System[系统管理]
   System --> UserMgr[用户管理]
   System --> RoleMgr[角色管理]
   System --> MenuMgr[菜单管理]
   System --> ApiMgr[API 管理]
   System --> DeptMgr[部门管理]
   System --> AuditLogMgr[审计日志]
 ```

 ### 4.2 功能与模块对应关系

 | 功能模块     | 前端视图                                | 后端路由前缀          | 主要表            |
 | ------------ | ---------------------------------------- | --------------------- | ----------------- |
 | 登录认证     | `web/src/views/login/index.vue`         | `/api/v1/base`        | `user`            |
 | 工作台       | `web/src/views/workbench/index.vue`     | 多接口综合            | 多表              |
 | 用户管理     | `web/src/views/system/user/index.vue`   | `/api/v1/user`        | `user`、`role`    |
 | 角色管理     | `web/src/views/system/role/index.vue`   | `/api/v1/role`        | `role`、`menu`、`api` |
 | 菜单管理     | `web/src/views/system/menu/index.vue`   | `/api/v1/menu`        | `menu`            |
 | API 管理     | `web/src/views/system/api/index.vue`    | `/api/v1/api`         | `api`             |
 | 部门管理     | `web/src/views/system/dept/index.vue`   | `/api/v1/dept`        | `dept`、`dept_closure` |
 | 审计日志     | `web/src/views/system/auditlog/index.vue` | `/api/v1/auditlog`  | `audit_log`       |
 | 个人资料     | `web/src/views/profile/index.vue`       | `/api/v1/base`、`/user` | `user`          |

 ## 五、小结

 - 整体采用“前端动态路由 + 后端 RBAC 权限 + API 元数据”模式，扩展性较好。
 - 权限控制粒度覆盖：菜单、路由、接口、按钮。
 - 数据库设计已在现有 [DatabaseDesign.md](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/DatabaseDesign.md) 中详细列出，此处不再重复。

