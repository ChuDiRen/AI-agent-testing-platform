 # vue-fastapi-admin 接口设计文档

 本文档基于当前后端 FastAPI 路由与前端 API 调用封装进行整理，主要关注 v1 版本接口（`/api/v1`）。

 - 后端路由聚合：[app/api/v1/__init__.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/__init__.py#L13-L21)
 - 前端调用封装：[web/src/api/index.js](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/web/src/api/index.js#L1-L42)

 ## 一、鉴权与基础接口（/api/v1/base）

 路由文件：[/app/api/v1/base/base.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/base/base.py#L19-L103)

 ### 1.1 获取访问令牌

 - 方法：`POST`
 - 路径：`/api/v1/base/access_token`
 - 描述：用户登录，返回 JWT 访问令牌
 - 请求体（CredentialsSchema）：
   - `username`: string 用户名
   - `password`: string 密码
 - 响应：
   - `access_token`: string JWT 字符串
   - `username`: string 用户名

 ### 1.2 获取当前用户信息

 - 方法：`GET`
 - 路径：`/api/v1/base/userinfo`
 - 描述：获取当前登录用户基本信息
 - 鉴权：需要携带 JWT（DependAuth）
 - 响应字段：
   - `id`, `username`, `email`, `roles`, `is_superuser`, `is_active`, `avatar` 等

 ### 1.3 获取当前用户菜单

 - 方法：`GET`
 - 路径：`/api/v1/base/usermenu`
 - 描述：根据用户角色返回可访问菜单树，用于前端构建动态路由
 - 响应结构（简化）：
   - `name`: string 菜单名称
   - `path`: string 菜单路径
   - `icon`: string 图标
   - `order`: number 排序
   - `keepalive`: boolean 是否缓存
   - `component`: string 前端组件路径
   - `children`: Menu[] 子菜单列表

 ### 1.4 获取当前用户接口权限

 - 方法：`GET`
 - 路径：`/api/v1/base/userapi`
 - 描述：返回当前用户有权访问的接口标识列表
 - 响应：
   - `data`: string[] 列表，元素形如 `get/api/v1/user/list`
   - 用于前端 `v-permission` 指令进行按钮级权限控制

 ### 1.5 修改密码

 - 方法：`POST`
 - 路径：`/api/v1/base/update_password`
 - 描述：当前登录用户修改自己的登录密码
 - 请求体（UpdatePassword）：
   - `old_password`: string 旧密码
   - `new_password`: string 新密码
 - 响应：
   - 成功时返回统一 `Success` 结构，`msg = "修改成功"`

 ## 二、用户管理接口（/api/v1/user）

 路由文件：[/app/api/v1/users/users.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/users/users.py#L16-L81)

 ### 2.1 分页查询用户列表

 - 方法：`GET`
 - 路径：`/api/v1/user/list`
 - 描述：按条件分页查询系统用户
 - 查询参数：
   - `page`: int 页码，默认 1
   - `page_size`: int 每页数量，默认 10
   - `username`: string 用户名，模糊查询
   - `email`: string 邮箱，模糊查询
   - `dept_id`: int 部门 ID，精确匹配
 - 响应：
   - `data`: 用户列表，每个元素不包含密码字段，并附带部门信息
   - `total`, `page`, `page_size`

 ### 2.2 查看单个用户

 - 方法：`GET`
 - 路径：`/api/v1/user/get`
 - 查询参数：
   - `user_id`: int 用户 ID
 - 响应：
   - 单个用户详情，不包含密码字段

 ### 2.3 创建用户

 - 方法：`POST`
 - 路径：`/api/v1/user/create`
 - 请求体（UserCreate）：
   - `username`, `email`, `password`, `is_active`, `is_superuser`, `role_ids`, `dept_id` 等
 - 业务规则：
   - 若邮箱已存在，返回失败：`400` + `"The user with this email already exists in the system."`

 ### 2.4 更新用户

 - 方法：`POST`
 - 路径：`/api/v1/user/update`
 - 请求体（UserUpdate）：
   - 包含 `id` 及可更新字段、角色 ID 列表等

 ### 2.5 删除用户

 - 方法：`DELETE`
 - 路径：`/api/v1/user/delete`
 - 查询参数：
   - `user_id`: int 用户 ID

 ### 2.6 重置密码

 - 方法：`POST`
 - 路径：`/api/v1/user/reset_password`
 - 请求体：
   - `user_id`: int 用户 ID（`Body(..., embed=True)`）
 - 行为：
   - 将指定用户密码重置为默认值 `123456`

 ## 三、角色管理接口（/api/v1/role）

 路由文件：[/app/api/v1/roles/roles.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/roles/roles.py#L15-L72)

 ### 3.1 分页查询角色列表

 - 方法：`GET`
 - 路径：`/api/v1/role/list`
 - 查询参数：
   - `page`: int 页码
   - `page_size`: int 每页数量
   - `role_name`: string 角色名称，模糊查询

 ### 3.2 查看角色详情

 - 方法：`GET`
 - 路径：`/api/v1/role/get`
 - 查询参数：
   - `role_id`: int 角色 ID

 ### 3.3 创建角色

 - 方法：`POST`
 - 路径：`/api/v1/role/create`
 - 请求体（RoleCreate）：
   - `name`: string 角色名称
   - `desc`: string 描述等
 - 业务规则：
   - 若角色名已存在则抛出 `HTTPException(400, "The role with this rolename already exists in the system.")`

 ### 3.4 更新角色

 - 方法：`POST`
 - 路径：`/api/v1/role/update`
 - 请求体（RoleUpdate）：
   - 包含 `id` 及可修改字段

 ### 3.5 删除角色

 - 方法：`DELETE`
 - 路径：`/api/v1/role/delete`
 - 查询参数：
   - `role_id`: int 角色 ID

 ### 3.6 查看角色权限（菜单 + 接口）

 - 方法：`GET`
 - 路径：`/api/v1/role/authorized`
 - 查询参数：
   - `id`: int 角色 ID
 - 响应：
   - 角色信息及其关联的菜单与 API 列表（`m2m=True`）

 ### 3.7 更新角色权限

 - 方法：`POST`
 - 路径：`/api/v1/role/authorized`
 - 请求体（RoleUpdateMenusApis）：
   - `id`: int 角色 ID
   - `menu_ids`: int[] 菜单 ID 列表
   - `api_infos`: 接口信息列表（通常包含 path + method）

 ## 四、菜单管理接口（/api/v1/menu）

 路由文件：[/app/api/v1/menus/menus.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/menus/menus.py#L14-L63)

 ### 4.1 获取菜单树列表

 - 方法：`GET`
 - 路径：`/api/v1/menu/list`
 - 查询参数：
   - `page`, `page_size`：分页参数（但实际返回的是完整树，仅 total 为根菜单数量）
 - 说明：
   - 后端通过递归函数 `get_menu_with_children` 构造树形结构

 ### 4.2 查看单个菜单

 - 方法：`GET`
 - 路径：`/api/v1/menu/get`
 - 查询参数：
   - `menu_id`: int 菜单 ID

 ### 4.3 创建菜单

 - 方法：`POST`
 - 路径：`/api/v1/menu/create`
 - 请求体（MenuCreate）：
   - 包含名称、路径、图标、组件路径、父 ID、排序等字段

 ### 4.4 更新菜单

 - 方法：`POST`
 - 路径：`/api/v1/menu/update`
 - 请求体（MenuUpdate）

 ### 4.5 删除菜单

 - 方法：`DELETE`
 - 路径：`/api/v1/menu/delete`
 - 查询参数：
   - `id`: int 菜单 ID
 - 业务规则：
   - 若该菜单存在子菜单，则返回 `Fail(msg="Cannot delete a menu with child menus")`

 ## 五、API 元数据管理接口（/api/v1/api）

 路由文件：[/app/api/v1/apis/apis.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/apis/apis.py#L11-L66)

 ### 5.1 分页查询 API 列表

 - 方法：`GET`
 - 路径：`/api/v1/api/list`
 - 查询参数：
   - `page`, `page_size`
   - `path`: string 路径模糊匹配
   - `summary`: string 接口简介模糊匹配
   - `tags`: string 所属模块模糊匹配

 ### 5.2 查看单个 API

 - 方法：`GET`
 - 路径：`/api/v1/api/get`
 - 查询参数：
   - `id`: int API ID

 ### 5.3 创建 API

 - 方法：`POST`
 - 路径：`/api/v1/api/create`
 - 请求体（ApiCreate）：
   - `path`, `method`, `summary`, `tags` 等

 ### 5.4 更新 API

 - 方法：`POST`
 - 路径：`/api/v1/api/update`
 - 请求体（ApiUpdate）

 ### 5.5 删除 API

 - 方法：`DELETE`
 - 路径：`/api/v1/api/delete`
 - 查询参数：
   - `api_id`: int API ID

 ### 5.6 刷新 API 列表

 - 方法：`POST`
 - 路径：`/api/v1/api/refresh`
 - 描述：
   - 从 FastAPI 应用路由中扫描所有接口，刷新 `api` 表数据

 ## 六、部门管理接口（/api/v1/dept）

 路由文件：[/app/api/v1/depts/depts.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/depts/depts.py#L10-L47)

 ### 6.1 查询部门树

 - 方法：`GET`
 - 路径：`/api/v1/dept/list`
 - 查询参数：
   - `name`: string 部门名称，模糊过滤
 - 响应：
   - 按层级组织的部门树结构

 ### 6.2 查看部门详情

 - 方法：`GET`
 - 路径：`/api/v1/dept/get`
 - 查询参数：
   - `id`: int 部门 ID

 ### 6.3 创建部门

 - 方法：`POST`
 - 路径：`/api/v1/dept/create`
 - 请求体（DeptCreate）

 ### 6.4 更新部门

 - 方法：`POST`
 - 路径：`/api/v1/dept/update`
 - 请求体（DeptUpdate）

 ### 6.5 删除部门

 - 方法：`DELETE`
 - 路径：`/api/v1/dept/delete`
 - 查询参数：
   - `dept_id`: int 部门 ID

 ## 七、审计日志接口（/api/v1/auditlog）

 路由文件：[/app/api/v1/auditlog/auditlog.py](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/app/api/v1/auditlog/auditlog.py#L12-L48)

 ### 7.1 分页查询操作日志

 - 方法：`GET`
 - 路径：`/api/v1/auditlog/list`
 - 查询参数（均为可选）：
   - `page`, `page_size`
   - `username`: string 操作人名称
   - `module`: string 功能模块
   - `method`: string 请求方法
   - `summary`: string 接口描述
   - `path`: string 请求路径
   - `status`: int 状态码
   - `start_time`: datetime 开始时间
   - `end_time`: datetime 结束时间
 - 说明：
   - 支持多条件组合过滤与时间范围查询

 ## 八、统一返回结构

 - 成功返回：
   - `Success`：包含 `code`（通常为 200）、`msg`、`data` 字段
   - `SuccessExtra`：在 `Success` 的基础上增加 `total`、`page`、`page_size` 等分页字段
 - 失败返回：
   - `Fail`：包含 `code`、`msg`，并可附加错误详情

 ## 九、数据库设计说明

 - 详细表结构、字段设计与约束请参考现有文档：
   - [DatabaseDesign.md](file:///d:/AI-agent-testing-platform/vue-fastapi-admin/DatabaseDesign.md)
 - 接口与数据表之间的关系：
   - 用户、角色、菜单、API、部门、审计日志等模块，均映射到对应 ORM 模型，并由上层控制器与路由进行组合使用。

