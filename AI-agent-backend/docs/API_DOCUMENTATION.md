# AI-Agent-Backend API 接口文档

## 概述

AI-Agent-Backend 是一个基于 FastAPI 的企业级 RBAC 权限管理系统，提供完整的用户、角色、菜单、部门管理功能。

### 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 通用响应格式

所有API接口都遵循统一的响应格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未认证或Token过期 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

### 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "data": null,
  "error_code": "ERROR_CODE",
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

## 认证接口

### 用户登录

**接口描述**: 用户登录获取访问令牌

- **URL**: `POST /users/login`
- **认证**: 无需认证
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "username": "admin",
  "password": "123456"
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**成功响应**:

```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_info": {
      "user_id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "mobile": "17788888888",
      "dept_id": 1,
      "status": "1",
      "ssex": "0",
      "avatar": "default.jpg",
      "description": "系统管理员",
      "create_time": "2025-08-24T10:00:00",
      "modify_time": "2025-08-24T10:00:00",
      "last_login_time": "2025-08-24T13:00:00"
    },
    "permissions": ["user:view", "user:add", "user:update", "user:delete"]
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

**错误响应**:

```json
{
  "success": false,
  "message": "用户名或密码错误",
  "data": null,
  "error_code": "INVALID_CREDENTIALS",
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

## 用户管理接口

### 创建用户

**接口描述**: 创建新用户

- **URL**: `POST /users/`
- **认证**: 需要Bearer Token
- **权限**: 需要用户创建权限
- **Content-Type**: `application/json`

**请求头**:

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**请求参数**:

```json
{
  "username": "testuser",
  "password": "123456",
  "email": "test@example.com",
  "mobile": "13800138000",
  "dept_id": 1,
  "ssex": "0",
  "avatar": "default.jpg",
  "description": "测试用户"
}
```

| 参数名 | 类型 | 必填 | 说明 | 限制 |
|--------|------|------|------|------|
| username | string | 是 | 用户名 | 3-50个字符 |
| password | string | 是 | 密码 | 6-20个字符 |
| email | string | 否 | 邮箱 | 最大128个字符 |
| mobile | string | 否 | 手机号 | 最大20个字符 |
| dept_id | integer | 否 | 部门ID | - |
| ssex | string | 否 | 性别 | 0:男, 1:女, 2:保密 |
| avatar | string | 否 | 头像 | 最大100个字符 |
| description | string | 否 | 描述 | 最大100个字符 |

**成功响应**:

```json
{
  "success": true,
  "message": "用户创建成功",
  "data": {
    "user_id": 2,
    "username": "testuser",
    "email": "test@example.com",
    "mobile": "13800138000",
    "dept_id": 1,
    "status": "1",
    "ssex": "0",
    "avatar": "default.jpg",
    "description": "测试用户",
    "create_time": "2025-08-24T13:00:00",
    "modify_time": "2025-08-24T13:00:00",
    "last_login_time": null
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取用户列表

**接口描述**: 获取所有用户列表

- **URL**: `GET /users/`
- **认证**: 需要Bearer Token
- **权限**: 需要用户查看权限

**请求头**:

```
Authorization: Bearer <access_token>
```

**成功响应**:

```json
{
  "success": true,
  "message": "获取用户列表成功",
  "data": {
    "users": [
      {
        "user_id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "mobile": "17788888888",
        "dept_id": 1,
        "status": "1",
        "ssex": "0",
        "avatar": "default.jpg",
        "description": "系统管理员",
        "create_time": "2025-08-24T10:00:00",
        "modify_time": "2025-08-24T10:00:00",
        "last_login_time": "2025-08-24T13:00:00"
      }
    ]
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取用户详情

**接口描述**: 根据用户ID获取用户详细信息

- **URL**: `GET /users/{user_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要用户查看权限

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |

**请求头**:

```
Authorization: Bearer <access_token>
```

**成功响应**: 同创建用户响应格式

### 更新用户信息

**接口描述**: 更新用户信息

- **URL**: `PUT /users/{user_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要用户更新权限
- **Content-Type**: `application/json`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |

**请求参数**:

```json
{
  "email": "newemail@example.com",
  "mobile": "13900139000",
  "ssex": "1",
  "avatar": "new_avatar.jpg",
  "description": "更新后的描述"
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| email | string | 否 | 新邮箱 |
| mobile | string | 否 | 新手机号 |
| ssex | string | 否 | 新性别 |
| avatar | string | 否 | 新头像 |
| description | string | 否 | 新描述 |

**成功响应**: 同创建用户响应格式

### 删除用户

**接口描述**: 删除指定用户

- **URL**: `DELETE /users/{user_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要用户删除权限

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |

**成功响应**:

```json
{
  "success": true,
  "message": "用户删除成功",
  "data": true,
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 修改用户密码

**接口描述**: 修改用户密码

- **URL**: `PUT /users/{user_id}/password`
- **认证**: 需要Bearer Token
- **权限**: 需要密码修改权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "old_password": "123456",
  "new_password": "newpassword123"
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码 |

### 分配用户角色

**接口描述**: 为用户分配角色

- **URL**: `POST /users/{user_id}/roles`
- **认证**: 需要Bearer Token
- **权限**: 需要角色分配权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "role_ids": [1, 2, 3]
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| role_ids | array | 是 | 角色ID列表 |

### 获取用户角色

**接口描述**: 获取用户的角色信息

- **URL**: `GET /users/{user_id}/roles`
- **认证**: 需要Bearer Token
- **权限**: 需要角色查看权限

**成功响应**:

```json
{
  "success": true,
  "message": "获取用户角色成功",
  "data": {
    "user_id": 1,
    "username": "admin",
    "roles": [
      {
        "role_id": 1,
        "role_name": "管理员",
        "remark": "系统管理员"
      }
    ]
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

## 角色管理接口

### 创建角色

**接口描述**: 创建新角色

- **URL**: `POST /roles/`
- **认证**: 需要Bearer Token
- **权限**: 需要角色创建权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "role_name": "测试角色",
  "remark": "测试角色描述"
}
```

| 参数名 | 类型 | 必填 | 说明 | 限制 |
|--------|------|------|------|------|
| role_name | string | 是 | 角色名称 | 1-10个字符 |
| remark | string | 否 | 角色描述 | 最大100个字符 |

**成功响应**:

```json
{
  "success": true,
  "message": "角色创建成功",
  "data": {
    "role_id": 2,
    "role_name": "测试角色",
    "remark": "测试角色描述",
    "create_time": "2025-08-24T13:00:00",
    "modify_time": "2025-08-24T13:00:00"
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取角色列表

**接口描述**: 分页获取角色列表

- **URL**: `GET /roles/`
- **认证**: 需要Bearer Token
- **权限**: 需要角色查看权限

**查询参数**:

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，最小值1 |
| size | integer | 否 | 10 | 每页大小，1-100 |

**成功响应**:

```json
{
  "success": true,
  "message": "获取角色列表成功",
  "data": {
    "roles": [
      {
        "role_id": 1,
        "role_name": "管理员",
        "remark": "系统管理员角色",
        "create_time": "2025-08-24T10:00:00",
        "modify_time": "2025-08-24T10:00:00"
      }
    ],
    "total": 1,
    "page": 1,
    "size": 10,
    "pages": 1
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取角色详情

**接口描述**: 根据角色ID获取角色详细信息

- **URL**: `GET /roles/{role_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要角色查看权限

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| role_id | integer | 是 | 角色ID |

**成功响应**: 同创建角色响应格式

### 更新角色信息

**接口描述**: 更新角色信息

- **URL**: `PUT /roles/{role_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要角色更新权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "role_name": "新角色名称",
  "remark": "新的角色描述"
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| role_name | string | 否 | 新角色名称 |
| remark | string | 否 | 新角色描述 |

### 删除角色

**接口描述**: 删除指定角色

- **URL**: `DELETE /roles/{role_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要角色删除权限

**成功响应**:

```json
{
  "success": true,
  "message": "角色删除成功",
  "data": true,
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 分配菜单权限

**接口描述**: 为角色分配菜单权限

- **URL**: `POST /roles/{role_id}/menus`
- **认证**: 需要Bearer Token
- **权限**: 需要权限分配权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "menu_ids": [1, 2, 3, 4, 5]
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| menu_ids | array | 是 | 菜单ID列表 |

### 获取角色权限

**接口描述**: 获取角色的权限信息

- **URL**: `GET /roles/{role_id}/permissions`
- **认证**: 需要Bearer Token
- **权限**: 需要权限查看权限

**成功响应**:

```json
{
  "success": true,
  "message": "获取角色权限成功",
  "data": {
    "role_id": 1,
    "role_name": "管理员",
    "permissions": ["user:view", "user:add", "user:update", "user:delete"],
    "menu_ids": [1, 2, 3, 4, 5]
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

## 菜单管理接口

### 创建菜单

**接口描述**: 创建新菜单或按钮

- **URL**: `POST /menus/`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单创建权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "parent_id": 0,
  "menu_name": "系统管理",
  "menu_type": "0",
  "path": "/system",
  "component": "Layout",
  "perms": null,
  "icon": "el-icon-set-up",
  "order_num": 1
}
```

| 参数名 | 类型 | 必填 | 说明 | 限制 |
|--------|------|------|------|------|
| parent_id | integer | 是 | 上级菜单ID | 0表示顶级菜单 |
| menu_name | string | 是 | 菜单/按钮名称 | 1-50个字符 |
| menu_type | string | 是 | 类型 | 0:菜单, 1:按钮 |
| path | string | 否 | 路由路径 | 最大255个字符 |
| component | string | 否 | 路由组件 | 最大255个字符 |
| perms | string | 否 | 权限标识 | 最大50个字符 |
| icon | string | 否 | 图标 | 最大50个字符 |
| order_num | number | 否 | 排序号 | - |

**成功响应**:

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
    "perms": null,
    "icon": "el-icon-set-up",
    "menu_type": "0",
    "order_num": 1,
    "create_time": "2025-08-24T13:00:00",
    "modify_time": "2025-08-24T13:00:00"
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取菜单树

**接口描述**: 获取完整的菜单树结构

- **URL**: `GET /menus/tree`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单查看权限

**成功响应**:

```json
{
  "success": true,
  "message": "获取菜单树成功",
  "data": [
    {
      "menu_id": 1,
      "parent_id": 0,
      "menu_name": "系统管理",
      "path": "/system",
      "component": "Layout",
      "perms": null,
      "icon": "el-icon-set-up",
      "menu_type": "0",
      "order_num": 1,
      "children": [
        {
          "menu_id": 2,
          "parent_id": 1,
          "menu_name": "用户管理",
          "path": "/system/user",
          "component": "system/user/Index",
          "perms": "user:view",
          "icon": "el-icon-user",
          "menu_type": "0",
          "order_num": 1,
          "children": []
        }
      ]
    }
  ],
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取菜单详情

**接口描述**: 根据菜单ID获取菜单详细信息

- **URL**: `GET /menus/{menu_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单查看权限

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| menu_id | integer | 是 | 菜单ID |

**成功响应**: 同创建菜单响应格式

### 更新菜单信息

**接口描述**: 更新菜单信息

- **URL**: `PUT /menus/{menu_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单更新权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "menu_name": "新菜单名称",
  "path": "/new-path",
  "component": "NewComponent",
  "perms": "new:permission",
  "icon": "new-icon",
  "order_num": 2
}
```

### 删除菜单

**接口描述**: 删除指定菜单

- **URL**: `DELETE /menus/{menu_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单删除权限

### 获取用户菜单

**接口描述**: 获取指定用户的菜单树和权限

- **URL**: `GET /menus/user/{user_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单查看权限

**成功响应**:

```json
{
  "success": true,
  "message": "获取用户菜单成功",
  "data": {
    "menus": [
      {
        "menu_id": 1,
        "parent_id": 0,
        "menu_name": "系统管理",
        "path": "/system",
        "component": "Layout",
        "perms": null,
        "icon": "el-icon-set-up",
        "menu_type": "0",
        "order_num": 1,
        "children": []
      }
    ],
    "permissions": ["user:view", "user:add", "user:update"]
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

## 部门管理接口

### 创建部门

**接口描述**: 创建新部门

- **URL**: `POST /departments/`
- **认证**: 需要Bearer Token
- **权限**: 需要部门创建权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "parent_id": 0,
  "dept_name": "开发部",
  "order_num": 1
}
```

| 参数名 | 类型 | 必填 | 说明 | 限制 |
|--------|------|------|------|------|
| parent_id | integer | 是 | 上级部门ID | 0表示顶级部门 |
| dept_name | string | 是 | 部门名称 | 1-100个字符 |
| order_num | number | 否 | 排序号 | - |

**成功响应**:

```json
{
  "success": true,
  "message": "部门创建成功",
  "data": {
    "dept_id": 1,
    "parent_id": 0,
    "dept_name": "开发部",
    "order_num": 1,
    "create_time": "2025-08-24T13:00:00",
    "modify_time": "2025-08-24T13:00:00"
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取部门树

**接口描述**: 获取完整的部门树结构

- **URL**: `GET /departments/tree`
- **认证**: 需要Bearer Token
- **权限**: 需要部门查看权限

**成功响应**:

```json
{
  "success": true,
  "message": "获取部门树成功",
  "data": [
    {
      "dept_id": 1,
      "parent_id": 0,
      "dept_name": "技术部",
      "order_num": 1,
      "create_time": "2025-08-24T10:00:00",
      "modify_time": "2025-08-24T10:00:00",
      "children": [
        {
          "dept_id": 2,
          "parent_id": 1,
          "dept_name": "开发组",
          "order_num": 1.1,
          "create_time": "2025-08-24T10:00:00",
          "modify_time": "2025-08-24T10:00:00",
          "children": []
        }
      ]
    }
  ],
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取部门列表

**接口描述**: 获取所有部门列表

- **URL**: `GET /departments/`
- **认证**: 需要Bearer Token
- **权限**: 需要部门查看权限

**成功响应**:

```json
{
  "success": true,
  "message": "获取部门列表成功",
  "data": {
    "departments": [
      {
        "dept_id": 1,
        "parent_id": 0,
        "dept_name": "技术部",
        "order_num": 1,
        "create_time": "2025-08-24T10:00:00",
        "modify_time": "2025-08-24T10:00:00"
      }
    ]
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

### 获取部门详情

**接口描述**: 根据部门ID获取部门详细信息

- **URL**: `GET /departments/{dept_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要部门查看权限

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| dept_id | integer | 是 | 部门ID |

### 更新部门信息

**接口描述**: 更新部门信息

- **URL**: `PUT /departments/{dept_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要部门更新权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "dept_name": "新部门名称",
  "order_num": 2
}
```

### 删除部门

**接口描述**: 删除指定部门

- **URL**: `DELETE /departments/{dept_id}`
- **认证**: 需要Bearer Token
- **权限**: 需要部门删除权限

### 获取部门状态

**接口描述**: 获取部门状态信息（是否有子部门、用户等）

- **URL**: `GET /departments/{dept_id}/status`
- **认证**: 需要Bearer Token
- **权限**: 需要部门查看权限

**成功响应**:

```json
{
  "success": true,
  "message": "获取部门状态成功",
  "data": {
    "dept_id": 1,
    "dept_name": "技术部",
    "has_children": true,
    "has_users": false,
    "can_delete": false
  },
  "error_code": null,
  "timestamp": "2025-08-24T13:00:00.000Z"
}
```

## 权限管理接口

### 获取用户权限列表

**接口描述**: 获取指定用户的权限列表

- **URL**: `GET /permission/user/{user_id}/permissions`
- **认证**: 需要Bearer Token
- **权限**: 需要权限查看权限（查看他人权限需要管理员权限）

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| user_id | integer | 是 | 用户ID |

**成功响应**:

```json
{
  "code": 200,
  "message": "获取用户权限成功",
  "data": {
    "user_id": 1,
    "permissions": ["user:view", "user:add", "user:update", "user:delete"]
  }
}
```

### 获取用户菜单树

**接口描述**: 获取指定用户的菜单树

- **URL**: `GET /permission/user/{user_id}/menus`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单查看权限（查看他人菜单需要管理员权限）

**成功响应**:

```json
{
  "code": 200,
  "message": "获取用户菜单成功",
  "data": {
    "user_id": 1,
    "menus": [
      {
        "menu_id": 1,
        "menu_name": "系统管理",
        "path": "/system",
        "children": []
      }
    ]
  }
}
```

### 获取角色权限列表

**接口描述**: 获取指定角色的权限列表

- **URL**: `GET /permission/role/{role_id}/permissions`
- **认证**: 需要Bearer Token
- **权限**: 需要角色权限查看权限

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| role_id | integer | 是 | 角色ID |

### 获取完整菜单树

**接口描述**: 获取完整菜单树结构

- **URL**: `GET /permission/menus/tree`
- **认证**: 需要Bearer Token
- **权限**: 需要菜单查看权限

### 获取缓存统计信息

**接口描述**: 获取缓存系统的统计信息

- **URL**: `GET /permission/cache/stats`
- **认证**: 需要Bearer Token
- **权限**: 需要缓存查看权限

**成功响应**:

```json
{
  "code": 200,
  "message": "获取缓存统计成功",
  "data": {
    "total_keys": 150,
    "memory_usage": "2.5MB",
    "hit_rate": "85.6%",
    "cache_type": "memory"
  }
}
```

### 获取缓存配置

**接口描述**: 获取缓存系统的配置信息

- **URL**: `GET /permission/cache/config`
- **认证**: 需要Bearer Token
- **权限**: 需要缓存配置查看权限

**成功响应**:

```json
{
  "code": 200,
  "message": "获取缓存配置成功",
  "data": {
    "cache_type": "memory",
    "default_ttl": 3600,
    "max_memory": "100MB",
    "eviction_policy": "allkeys-lru"
  }
}
```

### 刷新缓存

**接口描述**: 刷新权限缓存

- **URL**: `POST /permission/cache/refresh`
- **认证**: 需要Bearer Token
- **权限**: 需要缓存刷新权限

**成功响应**:

```json
{
  "code": 200,
  "message": "缓存刷新成功",
  "data": true
}
```

### 设置缓存配置

**接口描述**: 设置缓存系统配置

- **URL**: `POST /permission/cache/config`
- **认证**: 需要Bearer Token
- **权限**: 需要缓存配置更新权限
- **Content-Type**: `application/json`

**请求参数**:

```json
{
  "cache_type": "redis",
  "ttl": 7200,
  "enabled": true
}
```

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| cache_type | string | 否 | 缓存类型 |
| ttl | integer | 否 | 缓存过期时间（秒） |
| enabled | boolean | 否 | 是否启用缓存 |

## 系统信息接口

### 获取系统信息

**接口描述**: 获取系统基本信息

- **URL**: `GET /`
- **认证**: 无需认证

**成功响应**:

```json
{
  "message": "Welcome to AI-Agent-Backend",
  "version": "1.0.0",
  "description": "AI Agent Backend - 企业级五层架构FastAPI应用",
  "docs_url": "/docs",
  "environment": "development"
}
```

## 错误码说明

### 通用错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| VALIDATION_ERROR | 422 | 数据验证失败 |
| BUSINESS_ERROR | 400 | 业务逻辑错误 |
| AUTHENTICATION_ERROR | 401 | 认证失败 |
| AUTHORIZATION_ERROR | 403 | 权限不足 |
| NOT_FOUND_ERROR | 404 | 资源不存在 |
| CONFLICT_ERROR | 409 | 资源冲突 |
| RATE_LIMIT_ERROR | 429 | 请求频率限制 |
| INTERNAL_SERVER_ERROR | 500 | 服务器内部错误 |
| SERVICE_UNAVAILABLE_ERROR | 503 | 服务不可用 |

### 用户相关错误码

| 错误码 | 说明 |
|--------|------|
| USER_NOT_FOUND | 用户不存在 |
| USER_ALREADY_EXISTS | 用户已存在 |
| INVALID_CREDENTIALS | 用户名或密码错误 |
| TOKEN_EXPIRED | 令牌已过期 |
| INVALID_TOKEN | 无效令牌 |

### 权限相关错误码

| 错误码 | 说明 |
|--------|------|
| PERMISSION_DENIED | 权限被拒绝 |
| ROLE_NOT_FOUND | 角色不存在 |
| MENU_NOT_FOUND | 菜单不存在 |
| DEPARTMENT_NOT_FOUND | 部门不存在 |

## 使用示例

### JavaScript/TypeScript 示例

```javascript
// 登录
const login = async (username, password) => {
  const response = await fetch('http://localhost:8000/api/v1/users/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });

  const result = await response.json();
  if (result.success) {
    localStorage.setItem('token', result.data.access_token);
    return result.data;
  } else {
    throw new Error(result.message);
  }
};

// 获取用户列表
const getUsers = async () => {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:8000/api/v1/users/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  const result = await response.json();
  if (result.success) {
    return result.data.users;
  } else {
    throw new Error(result.message);
  }
};

// 创建用户
const createUser = async (userData) => {
  const token = localStorage.getItem('token');
  const response = await fetch('http://localhost:8000/api/v1/users/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(userData)
  });

  const result = await response.json();
  if (result.success) {
    return result.data;
  } else {
    throw new Error(result.message);
  }
};
```

### Python 示例

```python
import requests
import json

class AIAgentAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token = None

    def login(self, username, password):
        """用户登录"""
        url = f"{self.base_url}/users/login"
        data = {"username": username, "password": password}

        response = requests.post(url, json=data)
        result = response.json()

        if result["success"]:
            self.token = result["data"]["access_token"]
            return result["data"]
        else:
            raise Exception(result["message"])

    def get_headers(self):
        """获取请求头"""
        if not self.token:
            raise Exception("请先登录")
        return {"Authorization": f"Bearer {self.token}"}

    def get_users(self):
        """获取用户列表"""
        url = f"{self.base_url}/users/"
        response = requests.get(url, headers=self.get_headers())
        result = response.json()

        if result["success"]:
            return result["data"]["users"]
        else:
            raise Exception(result["message"])

    def create_user(self, user_data):
        """创建用户"""
        url = f"{self.base_url}/users/"
        response = requests.post(url, json=user_data, headers=self.get_headers())
        result = response.json()

        if result["success"]:
            return result["data"]
        else:
            raise Exception(result["message"])

# 使用示例
api = AIAgentAPI()
api.login("admin", "123456")
users = api.get_users()
print(f"用户数量: {len(users)}")
```

## 注意事项

1. **认证**: 除了登录接口和系统信息接口外，所有接口都需要在请求头中携带有效的Bearer Token
2. **权限**: 不同的接口需要不同的权限，请确保当前用户具有相应的权限
3. **数据格式**: 所有请求和响应都使用JSON格式
4. **错误处理**: 请根据响应中的`success`字段判断请求是否成功，并处理相应的错误信息
5. **令牌过期**: 访问令牌有效期为30分钟，过期后需要重新登录
6. **缓存**: 系统支持Redis缓存，在没有Redis的情况下会自动降级为内存缓存

## 更新日志

- **v1.0.0** (2025-08-24): 初始版本，包含完整的RBAC权限管理功能
