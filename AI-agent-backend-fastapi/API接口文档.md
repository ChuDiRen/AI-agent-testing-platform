# FastAPI RBAC 权限系统 - API 接口文档

**版本**: v1.0.0  
**基础URL**: `http://localhost:8000/api/v1`  
**参考设计**: [RBAC表结构设计 - BNTang](https://www.cnblogs.com/BNTang/articles/17024549.html)

---

## 📋 目录

- [1. 认证接口](#1-认证接口)
- [2. 用户管理](#2-用户管理)
- [3. 角色管理](#3-角色管理)
- [4. 菜单管理](#4-菜单管理)
- [5. 部门管理](#5-部门管理)
- [6. 用户角色关联](#6-用户角色关联)
- [7. 角色菜单关联](#7-角色菜单关联)
- [8. 文件上传](#8-文件上传)
- [9. 通用说明](#9-通用说明)

---

## 1. 认证接口

### 1.1 用户注册

**接口地址**: `POST /api/v1/auth/register`

**请求示例**:
```json
{
  "username": "newuser",
  "password": "password123",
  "email": "user@example.com",
  "mobile": "13800138000",
  "dept_id": 1,
  "ssex": "0"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user_id": 2,
    "username": "newuser",
    "email": "user@example.com",
    "status": "1"
  }
}
```

### 1.2 用户登录

**接口地址**: `POST /api/v1/auth/login`

**请求示例**:
```json
{
  "username": "BNTang",
  "password": "1234qwer"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

---

## 2. 用户管理

### 2.1 获取当前用户信息

**接口地址**: `GET /api/v1/users/me`

**请求头**:
```
Authorization: Bearer {access_token}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "username": "BNTang",
    "email": "303158131@qq.com",
    "mobile": "17788888888",
    "dept_id": 1,
    "status": "1",
    "ssex": "0",
    "avatar": "default.jpg",
    "description": "我是帅比作者。",
    "create_time": "2019-06-14T20:39:22",
    "last_login_time": "2019-08-02T15:57:00"
  }
}
```

### 2.2 获取用户列表（分页）

**接口地址**: `GET /api/v1/users/`

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20，最大100）
- `keyword`: 搜索关键词（可选）
- `is_active`: 是否激活（可选）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "user_id": 1,
        "username": "BNTang",
        "email": "303158131@qq.com",
        "status": "1"
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20,
    "pages": 1
  }
}
```

### 2.3 获取用户详情

**接口地址**: `GET /api/v1/users/{user_id}`

### 2.4 更新用户信息

**接口地址**: `PUT /api/v1/users/{user_id}`

**请求示例**:
```json
{
  "email": "newemail@example.com",
  "mobile": "13900139000",
  "description": "更新的个人描述"
}
```

### 2.5 删除用户

**接口地址**: `DELETE /api/v1/users/{user_id}`

### 2.6 导出用户数据（CSV）

**接口地址**: `GET /api/v1/users/export/csv`

### 2.7 导出用户数据（JSON）

**接口地址**: `GET /api/v1/users/export/json`

---

## 3. 角色管理

### 3.1 创建角色

**接口地址**: `POST /api/v1/roles/`

**请求示例**:
```json
{
  "role_name": "产品经理",
  "remark": "负责产品设计和规划"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "角色创建成功",
  "data": {
    "role_id": 2,
    "role_name": "产品经理",
    "remark": "负责产品设计和规划",
    "create_time": "2025-01-04T10:00:00"
  }
}
```

### 3.2 获取角色列表

**接口地址**: `GET /api/v1/roles/`

**查询参数**:
- `skip`: 跳过数量（默认0）
- `limit`: 限制数量（默认100）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "role_id": 1,
      "role_name": "管理员",
      "remark": "管理员",
      "create_time": "2017-12-27T16:23:11",
      "menus": [
        {
          "menu_id": 1,
          "menu_name": "系统管理",
          "perms": null
        },
        {
          "menu_id": 2,
          "menu_name": "用户管理",
          "perms": "user:view"
        }
      ]
    }
  ]
}
```

### 3.3 获取角色详情

**接口地址**: `GET /api/v1/roles/{role_id}`

### 3.4 更新角色

**接口地址**: `PUT /api/v1/roles/{role_id}`

### 3.5 删除角色

**接口地址**: `DELETE /api/v1/roles/{role_id}`

---

## 4. 菜单管理

### 4.1 创建菜单

**接口地址**: `POST /api/v1/menus/`

**创建菜单示例**:
```json
{
  "parent_id": 0,
  "menu_name": "系统管理",
  "path": "/system",
  "component": "Layout",
  "perms": null,
  "icon": "el-icon-set-up",
  "type": "0",
  "order_num": 1
}
```

**创建按钮示例**:
```json
{
  "parent_id": 2,
  "menu_name": "新增用户",
  "path": "",
  "component": "",
  "perms": "user:add",
  "icon": null,
  "type": "1",
  "order_num": null
}
```

**字段说明**:
- `parent_id`: 上级菜单ID，0表示顶级菜单
- `menu_name`: 菜单/按钮名称
- `path`: 路由路径（仅菜单需要）
- `component`: 组件路径（仅菜单需要）
- `perms`: 权限标识，格式为 `资源:操作`，如 `user:view`、`user:add`
- `icon`: 图标
- `type`: 类型，`0`=菜单，`1`=按钮
- `order_num`: 排序号

**响应示例**:
```json
{
  "success": true,
  "message": "菜单创建成功",
  "data": {
    "menu_id": 1,
    "parent_id": 0,
    "menu_name": "系统管理",
    "path": "/system",
    "component": "Layout",
    "type": "0",
    "create_time": "2025-01-04T10:00:00"
  }
}
```

### 4.2 获取菜单列表

**接口地址**: `GET /api/v1/menus/`

### 4.3 获取菜单树结构

**接口地址**: `GET /api/v1/menus/tree`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "menu_id": 1,
      "parent_id": 0,
      "menu_name": "系统管理",
      "path": "/system",
      "type": "0",
      "children": [
        {
          "menu_id": 2,
          "parent_id": 1,
          "menu_name": "用户管理",
          "path": "/system/user",
          "perms": "user:view",
          "type": "0",
          "children": [
            {
              "menu_id": 3,
              "parent_id": 2,
              "menu_name": "新增用户",
              "perms": "user:add",
              "type": "1",
              "children": []
            },
            {
              "menu_id": 4,
              "parent_id": 2,
              "menu_name": "修改用户",
              "perms": "user:update",
              "type": "1",
              "children": []
            },
            {
              "menu_id": 5,
              "parent_id": 2,
              "menu_name": "删除用户",
              "perms": "user:delete",
              "type": "1",
              "children": []
            }
          ]
        }
      ]
    }
  ]
}
```

### 4.4 获取用户菜单

**接口地址**: `GET /api/v1/menus/user/{user_id}`

**说明**: 根据用户的角色获取该用户拥有的所有菜单和按钮权限

### 4.5 获取菜单详情

**接口地址**: `GET /api/v1/menus/{menu_id}`

### 4.6 更新菜单

**接口地址**: `PUT /api/v1/menus/{menu_id}`

### 4.7 删除菜单

**接口地址**: `DELETE /api/v1/menus/{menu_id}`

---

## 5. 部门管理

### 5.1 创建部门

**接口地址**: `POST /api/v1/departments/`

**请求示例**:
```json
{
  "parent_id": 0,
  "dept_name": "开发部",
  "order_num": 1
}
```

**字段说明**:
- `parent_id`: 上级部门ID，0表示顶级部门
- `dept_name`: 部门名称
- `order_num`: 排序号

### 5.2 获取部门列表

**接口地址**: `GET /api/v1/departments/`

### 5.3 获取部门详情

**接口地址**: `GET /api/v1/departments/{dept_id}`

### 5.4 更新部门

**接口地址**: `PUT /api/v1/departments/{dept_id}`

### 5.5 删除部门

**接口地址**: `DELETE /api/v1/departments/{dept_id}`

---

## 6. 用户角色关联

### 6.1 为用户分配角色

**接口地址**: `POST /api/v1/user-roles/assign`

**请求示例**:
```json
{
  "user_id": 1,
  "role_ids": [1, 2]
}
```

**说明**: 为用户分配多个角色，会先删除用户现有的所有角色关联，然后建立新的关联关系

### 6.2 获取用户的角色列表

**接口地址**: `GET /api/v1/user-roles/{user_id}/roles`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "role_id": 1,
      "role_name": "管理员",
      "remark": "系统管理员"
    }
  ]
}
```

### 6.3 移除用户角色

**接口地址**: `DELETE /api/v1/user-roles/{user_id}/roles/{role_id}`

---

## 7. 角色菜单关联

### 7.1 为角色分配菜单权限

**接口地址**: `POST /api/v1/role-menus/assign`

**请求示例**:
```json
{
  "role_id": 1,
  "menu_ids": [1, 2, 3, 4, 5]
}
```

**说明**: 为角色分配菜单权限，会先删除角色现有的所有菜单关联，然后建立新的关联关系

### 7.2 获取角色的菜单列表

**接口地址**: `GET /api/v1/role-menus/{role_id}/menus`

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "menu_id": 1,
      "menu_name": "系统管理",
      "type": "0",
      "perms": null
    },
    {
      "menu_id": 2,
      "menu_name": "用户管理",
      "type": "0",
      "perms": "user:view"
    },
    {
      "menu_id": 3,
      "menu_name": "新增用户",
      "type": "1",
      "perms": "user:add"
    },
    {
      "menu_id": 4,
      "menu_name": "修改用户",
      "type": "1",
      "perms": "user:update"
    },
    {
      "menu_id": 5,
      "menu_name": "删除用户",
      "type": "1",
      "perms": "user:delete"
    }
  ]
}
```

### 7.3 移除角色菜单权限

**接口地址**: `DELETE /api/v1/role-menus/{role_id}/menus/{menu_id}`

---

## 8. 文件上传

### 8.1 上传头像

**接口地址**: `POST /api/v1/upload/avatar`

**请求格式**: `multipart/form-data`

**请求参数**:
- `file`: 图片文件（必需）

**响应示例**:
```json
{
  "success": true,
  "data": {
    "filename": "avatar_1234567890.jpg",
    "url": "/uploads/avatars/avatar_1234567890.jpg",
    "size": 102400
  }
}
```

### 8.2 上传文件

**接口地址**: `POST /api/v1/upload/file`

**请求格式**: `multipart/form-data`

**请求参数**:
- `file`: 文件（必需）

### 8.3 删除文件

**接口地址**: `DELETE /api/v1/upload/file`

**查询参数**:
- `filename`: 文件名（必需）

---

## 9. 通用说明

### 9.1 统一响应格式

所有接口都使用统一的响应格式：

**成功响应**:
```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

**失败响应**:
```json
{
  "success": false,
  "message": "错误信息",
  "error_code": "ERROR_CODE",
  "data": null
}
```

### 9.2 认证方式

除了注册和登录接口外，其他所有接口都需要在请求头中携带 JWT Token：

```
Authorization: Bearer {access_token}
```

### 9.3 HTTP 状态码

| 状态码 | 说明 |
|-------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（未登录或Token过期） |
| 403 | 禁止访问（无权限） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 9.4 分页参数

支持分页的接口统一使用以下参数：

| 参数 | 类型 | 说明 |
|-----|------|------|
| page | integer | 页码（从1开始） |
| page_size | integer | 每页数量（默认20，最大100） |

**分页响应格式**:
```json
{
  "items": [],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### 9.5 权限标识规范

权限标识采用 `资源:操作` 的格式：

| 资源 | 操作 | 权限标识 | 说明 |
|-----|------|---------|------|
| user | view | user:view | 查看用户 |
| user | add | user:add | 新增用户 |
| user | update | user:update | 修改用户 |
| user | delete | user:delete | 删除用户 |
| role | manage | role:manage | 管理角色 |
| menu | manage | menu:manage | 管理菜单 |

---

## 10. RBAC 权限验证流程

根据博客 [RBAC表结构设计](https://www.cnblogs.com/BNTang/articles/17024549.html) 的设计，权限验证流程如下：

### 场景：用户 BNTang 访问"删除用户"功能

**步骤1**: 用户登录
```
POST /api/v1/auth/login
→ 获取 access_token
```

**步骤2**: 系统内部权限验证流程
```
1. 从 t_user 表查询用户 BNTang
   → user_id = 1

2. 从 t_user_role 表查询用户角色
   → role_id = 1 (管理员)

3. 从 t_role_menu 表查询角色菜单
   → menu_id = 1, 2, 3, 4, 5

4. 从 t_menu 表查询菜单权限
   → menu_id = 5, perms = 'user:delete'

5. 验证通过，允许访问
```

**步骤3**: 前端展示
- 根据用户菜单显示可访问的页面
- 根据按钮权限控制按钮显示/隐藏

---

## 11. 快速开始

### 11.1 初始化数据库

```bash
python init_data.py
```

初始化后的测试数据：
- **用户**: BNTang / 1234qwer
- **角色**: 管理员
- **菜单**: 5个（系统管理、用户管理、新增/修改/删除用户）
- **部门**: 开发部

### 11.2 启动服务

```bash
python run.py
```

### 11.3 访问 API 文档

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 11.4 测试流程

**1. 登录获取 Token**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"BNTang","password":"1234qwer"}'
```

**2. 使用 Token 访问接口**
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer {access_token}"
```

**3. 获取用户菜单**
```bash
curl -X GET "http://localhost:8000/api/v1/menus/user/1" \
  -H "Authorization: Bearer {access_token}"
```

**4. 获取菜单树**
```bash
curl -X GET "http://localhost:8000/api/v1/menus/tree" \
  -H "Authorization: Bearer {access_token}"
```

---

## 12. 数据库表结构

完整的数据库表结构请参考博客文章：[RBAC表结构设计 - BNTang](https://www.cnblogs.com/BNTang/articles/17024549.html)

**核心表**:
- `t_user` - 用户表（13个字段）
- `t_role` - 角色表（5个字段）
- `t_menu` - 菜单表（11个字段）
- `t_user_role` - 用户角色关联表（2个字段）
- `t_role_menu` - 角色菜单关联表（2个字段）
- `t_dept` - 部门表（6个字段）

---

**文档版本**: v1.0.0  
**最后更新**: 2025-10-02  
**参考设计**: https://www.cnblogs.com/BNTang/articles/17024549.html  
**在线文档**: http://localhost:8000/docs
