 # 复刻 vue-fastapi-admin 项目提示词

> 用于让大模型帮你复刻一个「功能等价但技术栈可不同」的后台管理系统。

你可以直接整体复制本文件内容，粘贴到大模型对话框中使用。  
如需更换技术栈，只需要修改其中用【】括起来的部分即可。

---

## 角色设定

你现在扮演一名资深全栈架构师 + 高级工程师。  
任务：在不抄袭具体代码实现的前提下，复刻一个与「vue-fastapi-admin」功能完全等价的前后端分离后台管理系统，只是技术栈可以不同。

我希望你对功能、架构、数据库、接口、前端交互等做完整设计，并输出可直接落地实施的代码结构与实现方案。如果需要，可以分多轮逐步生成代码。

---

## 一、目标与技术栈约束

### 1. 项目目标

- 做一个通用后台管理系统，功能与「vue-fastapi-admin」保持一致，包括但不限于：
  - 登录 / JWT 鉴权
  - 用户管理
  - 角色管理
  - 菜单管理（用于生成动态路由）
  - API 管理（保存可授权的后端接口清单）
  - 部门管理（树形结构，包含闭包表或等价方案）
  - 审计日志（记录每次接口调用）
  - 个人资料 / 修改密码
  - 工作台首页（展示欢迎信息和示例卡片）
  - 顶部导航、侧边菜单、面包屑、多标签页等基础中后台布局

- 权限模型要求：
  - RBAC：用户-角色-菜单-API 四层模型
  - 支持“菜单级”权限控制（决定左侧菜单 & 路由是否可见）
  - 支持“接口级”权限控制（决定后端 API 是否可访问）
  - 支持“按钮级”权限控制（前端通过一个指令 / Hook / 组件，基于接口权限控制按钮显隐）
  - 超级管理员拥有所有菜单和 API 权限

### 2. 技术栈要求

后端技术栈（与当前 `platform-fastapi-server` 保持一致）：

- FastAPI 0.104.x 作为 Web 框架
- Uvicorn 作为 ASGI 服务
- SQLAlchemy 2.x 异步 ORM + aiomysql 作为 MySQL 驱动
- Alembic 作为数据库迁移工具
- Pydantic 2.x + pydantic-settings 用于配置管理与数据校验
- JWT 认证基于 python-jose[cryptography] + passlib[bcrypt]
- Redis 作为缓存 / 会话等通用存储
- RabbitMQ 通过 pika 集成消息队列
- httpx 作为异步 HTTP 客户端
- pytest + pytest-asyncio 用于自动化测试
- 要求：
  - 提供 RESTful 风格接口
  - 支持 JWT 鉴权
  - 使用异步数据库访问与会话管理
  - 提供中间件或依赖机制，便于实现审计日志记录
  - 有清晰的配置管理机制（本地/dev/prod 环境变量区分）

前端技术栈（与当前 `platform-vue-web` 保持一致）：

- Vue 3（`<script setup>`）+ Vite 构建工具
- Element Plus 作为 UI 组件库，搭配 @element-plus/icons-vue 图标
- Vue Router 4 作为前端路由
- Vuex 4 作为全局状态管理
- Axios 用于 HTTP 请求
- WindiCSS 作为原子化样式方案（通过 vite-plugin-windicss）
- @vueuse/integrations + universal-cookie 用于增强型工具与 Cookie 管理
- 要求：
  - 单页应用（SPA）
  - 支持动态路由加载
  - 使用 Element Plus 快速构建中后台界面
  - 预留国际化支持结构（至少可以方便扩展中/英文）
  - 使用 Vuex 管理用户信息、权限、标签页等全局状态

部署与其他：

- 使用 Docker 构建镜像
- 使用 Nginx（或等价方案）托管前端静态资源，并反向代理后端 API
- 区分 dev / prod 环境配置（API 地址、日志等级等）

---

## 二、功能与模块要求

请按照下面功能列表，保证新项目实现的功能与原项目等价。

### 1. 基础模块

**登录 / 退出**

- 用户使用用户名 + 密码登录
- 登录成功返回 JWT access token（可附带过期时间）
- 退出登录时清除本地 token、重置前端路由与状态

**个人中心**

- 查看当前用户信息（用户名、邮箱、角色、是否激活、是否超级管理员、头像等）
- 修改登录密码（需要验证旧密码）

**工作台（首页）**

- 显示欢迎语、当前用户名称
- 显示一些统计卡片（可先用 mock 数据）
- 显示项目卡片列表（可先用 mock 数据）

### 2. 系统管理模块（System）

**用户管理**

- 支持条件查询、分页显示（用户名、邮箱、所属部门等）
- 支持创建、编辑、删除用户
- 支持为用户分配角色（多选）
- 支持重置用户密码（重置为一个默认值）
- 列表中展示用户状态（是否激活、是否超级管理员、最后登录时间）

**角色管理**

- 支持条件查询、分页显示
- 支持创建、编辑、删除角色
- 支持为角色分配“菜单权限”和“API 权限”
- 可以查看某个角色当前已授权的菜单和 API 列表

**菜单管理**

- 支持展示完整菜单树（父子关系）
- 支持创建、编辑、删除菜单项
- 菜单字段包括：name、path、component、menu_type（目录/菜单）、icon、order、parent_id、is_hidden、keepalive、redirect 等
- 删除菜单时，如果存在子菜单，需要阻止删除并给出提示

**API 管理**

- 存储可授权的 API 列表，字段包括：path、method、summary、tags 等
- 支持分页查询、条件搜索
- 支持创建、编辑、删除 API 元数据
- 支持一个“刷新 API 列表”的功能：
  - 从后端路由配置中扫描出所有业务接口
  - 更新 API 表（新增/更新）以保持一致

**部门管理**

- 部门是树形结构（支持多级部门）
- 字段包括：name、desc、parent_id、order、is_deleted 等
- 插入、更新、删除部门时，保持树结构正确
- 用一个闭包表或等价机制（如 DeptClosure），快速查询某个部门下的全部子部门层级（你可以按自己的技术栈选用合适实现）

**审计日志管理**

- 记录所有（或大部分）业务接口调用日志：
  - user_id、username、module、summary、method、path、status、response_time、request_args(JSON)、response_body(JSON)、created_at 等字段
- 提供一个分页查询接口，支持多条件过滤：
  - username、module、method、summary、path、status、时间范围等
- 后端通过中间件自动写入日志（不要在每个业务 handler 里手写）

### 3. 权限 / 动态路由 / 按钮级权限

**权限模型**

- 用户与角色：多对多
- 角色与菜单：多对多
- 角色与 API：多对多
- 用户与部门：一对多（一个用户属于一个部门）
- 超级管理员角色拥有所有菜单和 API

**菜单与路由**

- 后端提供接口 `/base/usermenu`（路径名称可不同，但语义一致）：
  - 返回当前登录用户有权访问的菜单树（父子结构）
- 前端根据这个菜单树动态构建路由：
  - 顶级菜单使用一个 Layout 布局组件
  - 子菜单映射到实际页面组件
  - 如果菜单没有子菜单，可以生成一个默认子路由，让页面正常渲染

**接口权限与按钮权限**

- 后端提供接口 `/base/userapi`（路径名称可不同，但语义一致）：
  - 返回字符串列表，形如：`get/api/v1/user/list`
  - 规则：`HTTP_METHOD(小写) + 接口路径`
- 前端在全局状态存储这些“接口权限标识”
- 前端实现一个通用的按钮权限控制机制：
  - 例如一个指令 / Hook / 组件：`hasPermission('get/api/v1/user/list')`
  - 超级管理员总是有权限
  - 否则检查当前用户可访问的 api 列表中是否包含该标识
  - 若无权限，则在界面上隐藏该按钮（或者禁用）

---

## 三、数据库与接口设计要求

### 1. 数据库概念表

核心表（建议）：

- user  
  id, username, alias, email, phone, password_hash, is_active, is_superuser, last_login, dept_id, created_at, updated_at

- role  
  id, name, desc, created_at, updated_at

- menu  
  id, name, menu_type, icon, path, component, order, parent_id, is_hidden, keepalive, redirect, created_at, updated_at

- api  
  id, path, method, summary, tags, created_at, updated_at

- dept  
  id, name, desc, parent_id, order, is_deleted, created_at, updated_at

- dept_closure（如果你选用闭包表）  
  id, ancestor, descendant, level

- audit_log  
  id, user_id, username, module, summary, method, path, status, response_time, request_args(JSON), response_body(JSON), created_at, updated_at

多对多中间表（可使用 ORM 自动生成或手动建表）：

- user_role
- role_menu
- role_api

### 2. 接口设计

统一前缀：例如 `/api/v1`

模块划分：

- `/base`：登录、获取用户信息、用户菜单、用户接口权限、修改密码
- `/user`：用户管理
- `/role`：角色管理与角色授权
- `/menu`：菜单管理
- `/api`：API 元数据管理与刷新
- `/dept`：部门管理
- `/auditlog`：审计日志管理

要求你输出：

- 每个接口的：HTTP 方法、URL、请求参数、请求体结构、响应结构（包括分页结构）
- 统一响应格式，例如：
  - 成功：`{ code: 200, msg: string, data: any }`
  - 分页：`{ code: 200, msg: string, data: any[], total: number, page: number, page_size: number }`
  - 失败：`{ code: <错误码>, msg: string }`

---

## 四、前端架构与页面交互要求

### 1. 路由与权限

- 使用 Vue Router 4 作为路由库
- 基础路由：
  - 登录页、404 页、重定向页等
- 动态路由：
  - 应用启动时：
    - 若没有 token，仅注册基础路由 + 占位路由
    - 若有 token：
      - 请求当前用户信息
      - 请求 `/base/usermenu` 和 `/base/userapi`
      - 根据菜单数据构建动态路由并注入
      - 把用户可访问的 api 列表存入权限状态
- 路由守卫：
  - 未登录时访问需要权限的页面，重定向到登录页
  - 登录后访问登录页时，可选择自动跳转到首页
  - 每次路由切换时，更新页面标题，可触发加载动画（可选）

### 2. 状态管理

要求有以下几个核心 store / slice：

- user：
  - 保存用户 info、登录状态
  - 提供 login/logout/getUserInfo 等 action
- permission：
  - 保存 accessRoutes（动态路由）与 accessApis（接口权限标识列表）
  - 提供 generateRoutes 与 getAccessApis 等 action
- tags / tabs：
  - 保存当前打开的路由页签
  - 支持关闭单个、关闭其他、关闭全部等功能
- app：
  - 全局 UI 配置：侧边栏折叠、主题模式、语言等

### 3. 通用组件与 CRUD 模式

请为通用 CRUD 页面设计一个统一模式，例如：

- 页面布局：
  - 顶部：查询条件区域（表单）
  - 中部：数据表格 + 分页
  - 下部/弹窗：创建/编辑表单

- 封装组件与逻辑：
  - 通用表格组件：接收列配置、数据源、分页、加载状态
  - 通用弹窗组件：接收表单 schema / 字段配置
  - 通用 useCRUD Hook / 组合式函数：接收 doCreate、doUpdate、doDelete、fetchList 等函数，统一处理 loading、弹窗开关、当前编辑记录等

示例页面（要求你给出设计和组件结构，而不只是描述）：

- 用户列表页面
- 角色列表页面（包含角色授权侧边抽屉 / 弹窗）
- API 管理页面（包含“刷新接口”按钮）
- 部门管理页面（使用树状组件）
- 审计日志页面（复杂查询条件 + 表格展示）

---

## 五、非功能与部署要求

### 1. 日志与监控

- 后端需有统一日志输出格式（时间、级别、消息）
- 审计日志通过中间件自动采集
- 可以预留接口扩展 Prometheus / OpenTelemetry 等（可选）

### 2. 配置与环境

- 提供配置文件 / 环境变量区分：
  - dev：本地开发
  - prod：生产环境
- 至少包括：
  - 数据库连接信息
  - JWT 秘钥与过期时间
  - CORS 配置
  - 服务端口
  - 前端 API Base URL 等

### 3. Docker 与部署

- 给出后端 Dockerfile 与前端 Dockerfile 的设计要点（或者 docker-compose.yml）
- 给出 Nginx 配置示例：
  - 前端静态资源托管
  - `/api/` 前缀反向代理到后端

---

## 六、你的输出方式要求

请分阶段、有条理地输出：

1. 先给出：
   - 系统总体架构图（文字描述即可，可选用 Mermaid）
   - 模块列表 + 功能说明
   - 数据库表结构设计（字段、类型、约束）
   - 完整接口设计表（至少列出核心字段与路由）

2. 然后给出后端架构与代码骨架：
   - 目录结构
   - 每个模块的文件说明
   - 关键模型 / 控制器 / 路由示例代码（可以是伪代码，但结构清晰）

3. 再给出前端架构与代码骨架：
   - 目录结构
   - 路由/状态管理/页面组件之间关系
   - 一个典型 CRUD 页面的组件拆分和伪代码示例

4. 最后给出：
   - 非功能（日志、鉴权、安全）注意点清单
   - CI/CD 与部署建议（可以简略）

整个过程中请尽量：

- 使用我在前面指定的技术栈
- 让实现风格与 vue-fastapi-admin 的功能和体验等价
- 保持结构清晰、可直接用于实际开发
