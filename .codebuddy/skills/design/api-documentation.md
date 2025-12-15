# API 文档生成 Skill

## 概述
本 Skill 用于生成和维护 API 接口文档，确保前后端开发的接口规范统一。适用于任何后端技术栈。

## 使用场景
- 前端开发完成后，生成 API 文档供后端参考
- 后端开发完成后，更新 API 文档供前端对接
- 前后端联调时的接口规范确认

---

## API 文档生成提示词

### 从前端代码生成 API 文档
```prompt
@api 根据当前文件下所有的 API 文件生成接口文档，放到 doc 目录中，遵循以下格式：

• 接口名称
• 功能描述: 详细描述接口的功能和用途
• 入参: 参数类型和说明
  - param1: type - 参数1说明
  - param2: type - 参数2说明
• 返回参数: 返回值类型和说明
  - field1: type - 字段1说明
  - field2: type - 字段2说明
• url地址: /api/endpoint
• 请求方式: GET/POST/PUT/DELETE
```

### 从后端代码生成 API 文档
```prompt
@controller 根据当前控制器文件生成接口文档，包含：
- 接口名称和功能描述
- 请求方式和URL
- 请求参数（Query/Body/Path）
- 响应参数结构
- 错误码说明
- 示例请求和响应
```

---

## API 文档格式标准

### 基本信息
```markdown
## 接口名称

**接口名称：** 简短描述接口功能
**功能描述：** 详细描述接口的业务用途
**接口地址：** /api/v1/endpoint
**请求方式：** GET/POST/PUT/DELETE
**Content-Type：** application/json
```

### 请求参数
```markdown
### 请求参数

**请求示例：**
```json
{
  "page": 1,
  "pageSize": 10,
  "status": "active",
  "keyword": "搜索关键词"
}
```

**参数说明：**

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|-----|------|--------|
| page | int | 否 | 页码（默认1） | 2 |
| pageSize | int | 否 | 每页数量（默认10，最大100） | 20 |
| status | string | 否 | 状态过滤 | active |
| keyword | string | 否 | 搜索关键词 | 测试 |
```

### 响应参数
```markdown
### 响应参数

**成功响应示例：**
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "status": "active",
        "createdAt": "2025-01-21 10:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```

**参数说明：**

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|-----|------|--------|
| code | int | 是 | 状态码，200表示成功 | 200 |
| message | string | 是 | 响应消息 | 获取成功 |
| data | object | 是 | 响应数据 | |
| data.items | array | 是 | 数据列表 | |
| data.total | int | 是 | 总数量 | 100 |
| data.page | int | 是 | 当前页码 | 1 |
| data.pageSize | int | 是 | 每页数量 | 10 |
```

### 错误响应
```markdown
### 错误响应

**错误响应示例：**
```json
{
  "code": 400,
  "message": "用户名已存在",
  "data": null
}
```

**错误码说明：**

| 错误码 | 说明 |
|-------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未登录 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |
```

---

## 完整 API 文档模板

```markdown
# 用户管理 API 文档

## 1. 获取用户列表

**接口名称：** 获取用户列表
**功能描述：** 分页获取系统用户列表，支持按用户名、状态筛选
**接口地址：** /api/v1/users
**请求方式：** GET
**Content-Type：** application/json

### 请求参数

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|-----|------|--------|
| page | int | 否 | 页码（默认1） | 1 |
| pageSize | int | 否 | 每页数量（默认10） | 10 |
| username | string | 否 | 用户名筛选（模糊匹配） | admin |
| status | string | 否 | 状态筛选 | active |

### 响应参数

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "status": "active",
        "createdAt": "2025-01-21 10:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```

---

## 2. 创建用户

**接口名称：** 创建用户
**功能描述：** 创建新的系统用户
**接口地址：** /api/v1/users
**请求方式：** POST
**Content-Type：** application/json

### 请求参数

```json
{
  "username": "newuser",
  "password": "123456",
  "email": "newuser@example.com",
  "phone": "13800138000"
}
```

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|-------|------|-----|------|--------|
| username | string | 是 | 用户名（3-50位） | newuser |
| password | string | 是 | 密码（6-20位） | 123456 |
| email | string | 否 | 邮箱 | newuser@example.com |
| phone | string | 否 | 手机号 | 13800138000 |

### 响应参数

```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 2,
    "username": "newuser"
  }
}
```

---

## 3. 更新用户

**接口名称：** 更新用户信息
**功能描述：** 更新指定用户的信息
**接口地址：** /api/v1/users/{id}
**请求方式：** PUT
**Content-Type：** application/json

### 请求参数

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| id | int | 是 | 用户ID |

**请求体：**

```json
{
  "email": "updated@example.com",
  "phone": "13900139000",
  "status": "inactive"
}
```

### 响应参数

```json
{
  "code": 200,
  "message": "更新成功",
  "data": null
}
```

---

## 4. 删除用户

**接口名称：** 删除用户
**功能描述：** 删除指定用户
**接口地址：** /api/v1/users/{id}
**请求方式：** DELETE

### 请求参数

**路径参数：**

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| id | int | 是 | 用户ID |

### 响应参数

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```
```

---

## 文档同步要求

### 必须同步更新的情况
- 入参结构变更
- 返回参数变更
- URL 地址变更
- 请求方式变更
- 新增接口
- 删除接口

### 文档存放位置
- 项目文档目录: `doc/api/` 或 `docs/api/`

### 文档命名规范
- 按模块命名: `{模块名}-api.md`
- 示例: `user-api.md`, `order-api.md`, `product-api.md`

---

## 接口规范约束

### 请求方式规范
| 方法 | 用途 |
|-----|------|
| GET | 获取资源 |
| POST | 创建资源 |
| PUT | 更新资源 |
| DELETE | 删除资源 |

### 响应格式统一
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

### 分页响应格式
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "pageSize": 10
  }
}
```
