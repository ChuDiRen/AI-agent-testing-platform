# API接口规范文档

> 本文档基于vue-fastapi-admin项目的接口规范制定，用于指导后端API重构工作

## 📋 接口规范总览

### 基础规范

**接口前缀**: `/api/v1`

**响应格式**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

**分页格式**:
```json
{
  "items": [],
  "total": 100
}
```

**错误格式**:
```json
{
  "code": 400,
  "msg": "错误信息",
  "data": null
}
```

---

## 1. Base模块 (`/api/v1/base`)

### 1.1 登录接口

**接口路径**: `POST /api/v1/base/access_token`

**请求参数**:
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### 1.2 获取用户信息

**接口路径**: `GET /api/v1/base/userinfo`

**请求头**: `Authorization: Bearer {token}`

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "user_id": 1,
    "username": "admin",
    "nickname": "管理员",
    "email": "admin@example.com",
    "mobile": "13800138000",
    "avatar": "https://...",
    "dept_id": 1,
    "dept_name": "总公司",
    "roles": [
      {
        "role_id": 1,
        "role_name": "超级管理员"
      }
    ]
  }
}
```

### 1.3 获取用户菜单

**接口路径**: `GET /api/v1/base/usermenu`

**请求头**: `Authorization: Bearer {token}`

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "menu_id": 1,
      "parent_id": 0,
      "menu_name": "系统管理",
      "path": "/system",
      "component": "Layout",
      "icon": "SettingOutlined",
      "menu_type": "0",
      "order_num": 1,
      "children": [
        {
          "menu_id": 2,
          "parent_id": 1,
          "menu_name": "用户管理",
          "path": "/system/user",
          "component": "system/user/index",
          "icon": "UserOutlined",
          "menu_type": "0",
          "order_num": 1,
          "children": []
        }
      ]
    }
  ]
}
```

### 1.4 获取用户API权限

**接口路径**: `GET /api/v1/base/userapi`

**请求头**: `Authorization: Bearer {token}`

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    "user:view",
    "user:create",
    "user:update",
    "user:delete",
    "role:view",
    "role:create"
  ]
}
```

### 1.5 修改密码

**接口路径**: `POST /api/v1/base/update_password`

**请求头**: `Authorization: Bearer {token}`

**请求参数**:
```json
{
  "old_password": "123456",
  "new_password": "654321"
}
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "密码修改成功",
  "data": null
}
```

---

## 2. User模块 (`/api/v1/user`)

### 2.1 获取用户列表

**接口路径**: `GET /api/v1/user/list`

**请求参数**:
```
?page=1&page_size=10&username=admin&dept_id=1&status=1
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "items": [
      {
        "user_id": 1,
        "username": "admin",
        "nickname": "管理员",
        "email": "admin@example.com",
        "mobile": "13800138000",
        "dept_id": 1,
        "dept_name": "总公司",
        "status": 1,
        "created_at": "2024-01-01 00:00:00"
      }
    ],
    "total": 100
  }
}
```

### 2.2 获取单个用户

**接口路径**: `GET /api/v1/user/get`

**请求参数**:
```
?user_id=1
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "user_id": 1,
    "username": "admin",
    "nickname": "管理员",
    "email": "admin@example.com",
    "mobile": "13800138000",
    "dept_id": 1,
    "status": 1,
    "role_ids": [1, 2]
  }
}
```

### 2.3 创建用户

**接口路径**: `POST /api/v1/user/create`

**请求参数**:
```json
{
  "username": "test",
  "password": "123456",
  "nickname": "测试用户",
  "email": "test@example.com",
  "mobile": "13800138001",
  "dept_id": 1,
  "status": 1,
  "role_ids": [2]
}
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "创建成功",
  "data": {
    "user_id": 2
  }
}
```

### 2.4 更新用户

**接口路径**: `POST /api/v1/user/update`

**请求参数**:
```json
{
  "user_id": 2,
  "nickname": "测试用户2",
  "email": "test2@example.com",
  "mobile": "13800138002",
  "dept_id": 2,
  "status": 0,
  "role_ids": [2, 3]
}
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "更新成功",
  "data": null
}
```

### 2.5 删除用户

**接口路径**: `DELETE /api/v1/user/delete`

**请求参数**:
```
?user_id=2
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "删除成功",
  "data": null
}
```

### 2.6 重置密码

**接口路径**: `POST /api/v1/user/reset_password`

**请求参数**:
```json
{
  "user_id": 2,
  "new_password": "123456"
}
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "密码重置成功",
  "data": null
}
```

---

## 3. Role模块 (`/api/v1/role`)

### 3.1 获取角色列表

**接口路径**: `GET /api/v1/role/list`

**请求参数**:
```
?page=1&page_size=10&role_name=管理员
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "items": [
      {
        "role_id": 1,
        "role_name": "超级管理员",
        "remark": "拥有所有权限",
        "is_active": true,
        "created_at": "2024-01-01 00:00:00"
      }
    ],
    "total": 10
  }
}
```

### 3.2 创建角色

**接口路径**: `POST /api/v1/role/create`

**请求参数**:
```json
{
  "role_name": "普通用户",
  "remark": "普通用户角色",
  "is_active": true
}
```

### 3.3 更新角色

**接口路径**: `POST /api/v1/role/update`

**请求参数**:
```json
{
  "role_id": 2,
  "role_name": "普通用户2",
  "remark": "更新后的备注",
  "is_active": false
}
```

### 3.4 删除角色

**接口路径**: `DELETE /api/v1/role/delete`

**请求参数**:
```
?role_id=2
```

### 3.5 获取角色权限

**接口路径**: `GET /api/v1/role/authorized`

**请求参数**:
```
?role_id=1
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "menu_ids": [1, 2, 3],
    "api_ids": [1, 2, 3, 4, 5]
  }
}
```

### 3.6 更新角色权限

**接口路径**: `POST /api/v1/role/authorized`

**请求参数**:
```json
{
  "role_id": 2,
  "menu_ids": [1, 2, 3],
  "api_ids": [1, 2, 3, 4, 5]
}
```

---

## 4. Menu模块 (`/api/v1/menu`)

### 4.1 获取菜单列表

**接口路径**: `GET /api/v1/menu/list`

**响应数据**: 返回树形结构的菜单列表

### 4.2 创建菜单

**接口路径**: `POST /api/v1/menu/create`

### 4.3 更新菜单

**接口路径**: `POST /api/v1/menu/update`

### 4.4 删除菜单

**接口路径**: `DELETE /api/v1/menu/delete`

---

## 5. API模块 (`/api/v1/api`)

### 5.1 获取API列表

**接口路径**: `GET /api/v1/api/list`

### 5.2 创建API

**接口路径**: `POST /api/v1/api/create`

### 5.3 更新API

**接口路径**: `POST /api/v1/api/update`

### 5.4 删除API

**接口路径**: `DELETE /api/v1/api/delete`

### 5.5 刷新API

**接口路径**: `POST /api/v1/api/refresh`

---

## 6. Dept模块 (`/api/v1/dept`)

### 6.1 获取部门列表

**接口路径**: `GET /api/v1/dept/list`

### 6.2 创建部门

**接口路径**: `POST /api/v1/dept/create`

### 6.3 更新部门

**接口路径**: `POST /api/v1/dept/update`

### 6.4 删除部门

**接口路径**: `DELETE /api/v1/dept/delete`

---

## 7. AuditLog模块 (`/api/v1/auditlog`)

### 7.1 获取审计日志列表

**接口路径**: `GET /api/v1/auditlog/list`

**请求参数**:
```
?page=1&page_size=10&username=admin&action=create&start_time=2024-01-01&end_time=2024-12-31
```

**响应数据**:
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "items": [
      {
        "log_id": 1,
        "username": "admin",
        "action": "create",
        "resource_type": "user",
        "resource_id": 2,
        "ip_address": "127.0.0.1",
        "created_at": "2024-01-01 00:00:00"
      }
    ],
    "total": 100
  }
}
```

