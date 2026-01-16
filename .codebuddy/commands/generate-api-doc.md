---
description: 生成API接口文档的命令（按功能模块拆分）
---

# 命令：generate-api-doc

## 功能描述

根据前端API定义或后端接口代码，生成标准的OpenAPI/Swagger格式API文档，**按功能模块拆分为独立的文档文件**。

## 使用方式

```
/generate-api-doc
```

或

```
/generate-api-doc <API文件路径或目录>
```

## 参数说明

- `--format=openapi` - 生成OpenAPI 3.0格式（默认）
- `--format=swagger` - 生成Swagger 2.0格式
- `--output=docs/api-docs/` - 输出目录（默认）
- `--from-frontend` - 从前端API文件生成
- `--from-backend` - 从后端代码生成
- `--split-modules` - 按功能模块拆分文档（推荐）

## 输出文件结构

执行后会生成按功能模块拆分的API文档：

```
docs/api-docs/
├── README.md                      # API文档总览
├── common.md                      # 通用规范（认证、错误码等）
├── auth-module.md                 # 认证授权模块
├── user-module.md                 # 用户管理模块
├── role-module.md                 # 角色管理模块
├── permission-module.md           # 权限管理模块
├── profile-module.md              # 个人中心模块
├── log-module.md                  # 日志管理模块
├── dict-module.md                 # 数据字典模块
└── openapi.json                   # 完整OpenAPI规范（可选）
```

## 模块说明

### 1. 认证授权模块 (auth-module.md)

- POST `/api/v1/auth/login` - 用户登录
- POST `/api/v1/auth/logout` - 用户登出
- POST `/api/v1/auth/refresh` - 刷新Token

### 2. 用户管理模块 (user-module.md)

- GET `/api/v1/user/list` - 用户列表（分页、搜索、筛选）
- GET `/api/v1/user/{id}` - 用户详情
- POST `/api/v1/user` - 新增用户
- PUT `/api/v1/user/{id}` - 编辑用户
- DELETE `/api/v1/user/{id}` - 删除用户
- PUT `/api/v1/user/status` - 批量更新用户状态

### 3. 角色管理模块 (role-module.md)

- GET `/api/v1/role/list` - 角色列表
- GET `/api/v1/role/{id}` - 角色详情
- POST `/api/v1/role` - 新增角色
- PUT `/api/v1/role/{id}` - 编辑角色
- DELETE `/api/v1/role/{id}` - 删除角色
- GET `/api/v1/role/{id}/permissions` - 角色权限查询
- POST `/api/v1/role/{id}/permissions` - 配置角色权限

### 4. 权限管理模块 (permission-module.md)

- GET `/api/v1/permission/tree` - 权限树形结构
- GET `/api/v1/permission/list` - 权限列表（分页）
- POST `/api/v1/permission` - 新增权限
- PUT `/api/v1/permission/{id}` - 编辑权限
- DELETE `/api/v1/permission/{id}` - 删除权限

### 5. 个人中心模块 (profile-module.md)

- GET `/api/v1/user/profile` - 获取当前用户信息
- PUT `/api/v1/user/profile` - 更新个人信息
- PUT `/api/v1/user/password` - 修改密码

### 6. 日志管理模块 (log-module.md)

- GET `/api/v1/log/operation/list` - 操作日志列表
- GET `/api/v1/log/login/list` - 登录日志列表

### 7. 数据字典模块 (dict-module.md)

- GET `/api/v1/dict/roles` - 获取所有角色（下拉选择）

## 文档模板

### 模块文档模板 (auth-module.md)

```markdown
# 认证授权模块 API

## 模块概述

提供用户认证、授权、Token管理相关接口。

## 接口列表

| 接口名称 | 请求方式 | URL | 说明 |
|---------|---------|-----|------|
| 用户登录 | POST | /api/v1/auth/login | 用户登录认证 |
| 用户登出 | POST | /api/v1/auth/logout | 用户退出登录 |
| 刷新Token | POST | /api/v1/auth/refresh | 刷新访问令牌 |

---

## 1. 用户登录

### 接口描述
用户通过用户名和密码进行登录认证，成功后返回JWT Token。

### 基本信息
- **接口地址**: `/api/v1/auth/login`
- **请求方式**: POST
- **Content-Type**: application/json
- **是否需要认证**: 否

### 请求参数

#### Body参数

| 参数名 | 类型 | 必填 | 说明 | 示例值 |
|--------|------|------|------|--------|
| username | string | 是 | 用户名 | admin |
| password | string | 是 | 密码 | admin123 |

#### 请求示例

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### 响应参数

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | int | 响应码（200表示成功） |
| message | string | 响应消息 |
| data | object | 返回数据 |
| data.token | string | JWT访问令牌 |
| data.refreshToken | string | 刷新令牌 |
| data.user | object | 用户信息 |
| data.user.id | int | 用户ID |
| data.user.username | string | 用户名 |
| data.user.realName | string | 真实姓名 |
| data.user.roles | array | 角色列表 |

#### 响应示例

**成功响应（200）**：
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "realName": "管理员",
      "roles": [
        {
          "id": 1,
          "roleName": "超级管理员",
          "roleCode": "SUPER_ADMIN"
        }
      ]
    }
  }
}
```

**登录失败（401）**：
```json
{
  "code": 401,
  "message": "用户名或密码错误",
  "data": null
}
```

### 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | 用户名或密码错误 |
| 429 | 登录过于频繁（5次/分钟） |
| 500 | 服务器内部错误 |

### 业务规则

1. 密码使用BCrypt加密验证
2. JWT Token有效期2小时
3. RefreshToken有效期7天
4. 登录失败5次后锁定账户15分钟

### 注意事项

- 前端需要将Token存储在localStorage中
- 每次请求需要在Header中携带Token：`Authorization: Bearer {token}`
- Token过期时使用RefreshToken刷新

---

## 2. 用户登出

### 接口描述
用户退出登录，后端将Token加入黑名单。

### 基本信息
- **接口地址**: `/api/v1/auth/logout`
- **请求方式**: POST
- **Content-Type**: application/json
- **是否需要认证**: 是

### 请求参数

无需请求参数。

### 响应参数

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | int | 响应码（200表示成功） |
| message | string | 响应消息 |
| data | null | 无数据 |

#### 响应示例

```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

### 注意事项

- 前端需要清除localStorage中的Token
- 后端将Token加入Redis黑名单
```

### 通用规范文档模板 (common.md)

```markdown
# API接口通用规范

## 接口基础信息

### Base URL

- **开发环境**: `http://localhost:8080/api/v1`
- **测试环境**: `https://test-api.example.com/api/v1`
- **生产环境**: `https://api.example.com/api/v1`

### 认证方式

使用JWT Bearer Token认证。

**请求Header**：
```
Authorization: Bearer {token}
```

**获取Token方式**：
- 调用登录接口获取Token
- Token有效期：2小时
- RefreshToken有效期：7天

### 数据格式

- **Content-Type**: `application/json`
- **Accept**: `application/json`
- **字符编码**: UTF-8

## 统一响应格式

### 成功响应

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { }
}
```

### 失败响应

```json
{
  "code": 400,
  "message": "参数错误",
  "data": null
}
```

### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | int | 响应码 |
| message | string | 响应消息 |
| data | object/null | 响应数据 |

## 统一错误码

| 错误码 | HTTP状态码 | 说明 |
|--------|-----------|------|
| 200 | 200 | 请求成功 |
| 400 | 400 | 请求参数错误 |
| 401 | 401 | 未认证或Token过期 |
| 403 | 403 | 无权限访问 |
| 404 | 404 | 资源不存在 |
| 409 | 409 | 资源冲突（如用户名已存在） |
| 422 | 422 | 数据验证失败 |
| 429 | 429 | 请求过于频繁 |
| 500 | 500 | 服务器内部错误 |

## 分页参数规范

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | int | 否 | 1 | 当前页码 |
| pageSize | int | 否 | 10 | 每页条数 |

### 响应格式

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "list": [ ],
    "total": 100,
    "page": 1,
    "pageSize": 10,
    "totalPages": 10
  }
}
```

### 响应字段说明

| 字段名 | 类型 | 说明 |
|--------|------|------|
| list | array | 数据列表 |
| total | int | 总记录数 |
| page | int | 当前页码 |
| pageSize | int | 每页条数 |
| totalPages | int | 总页数 |

## 时间格式规范

所有时间字段统一使用ISO 8601格式：

```json
{
  "createTime": "2024-01-16T10:30:00Z",
  "updateTime": "2024-01-16T15:45:00Z"
}
```

## 接口限流规则

| 接口类型 | 限流规则 |
|---------|---------|
| 登录接口 | 5次/分钟 |
| 其他接口 | 100次/分钟 |

### 限流响应

```json
{
  "code": 429,
  "message": "请求过于频繁，请稍后重试",
  "data": null
}
```

## 参数验证规则

### 字符串长度限制

| 参数名 | 最小长度 | 最大长度 | 说明 |
|--------|---------|---------|------|
| username | 3 | 20 | 用户名 |
| password | 6 | 20 | 密码 |
| realName | 2 | 20 | 真实姓名 |
| email | 5 | 50 | 邮箱 |
| phone | 11 | 11 | 手机号 |

### 枚举值

| 字段名 | 枚举值 | 说明 |
|--------|--------|------|
| status | 0, 1 | 0-禁用，1-启用 |
| permissionType | menu, button, api | 菜单、按钮、接口 |

## 安全规范

1. **HTTPS传输**：生产环境必须使用HTTPS
2. **敏感数据加密**：密码等敏感数据必须加密传输
3. **SQL注入防护**：使用参数化查询
4. **XSS防护**：输出数据进行HTML转义
5. **CSRF防护**：关键操作需要CSRF Token
```

## 执行流程

### 阶段1：扫描和分析

1. **扫描前端API文件**：
   - 查找 `src/api/` 目录下的所有API文件
   - 解析接口定义
   - 提取接口信息

2. **分析接口模块**：
   - 按功能模块分类
   - 识别接口依赖关系
   - 确定模块划分

### 阶段2：生成文档

1. **生成总览文档** (`README.md`)：
   - 所有模块索引
   - 快速导航链接

2. **生成通用规范文档** (`common.md`)：
   - 认证规范
   - 错误码定义
   - 分页规范
   - 时间格式

3. **按模块生成文档**：
   - `auth-module.md`
   - `user-module.md`
   - `role-module.md`
   - `permission-module.md`
   - 等等

4. **生成OpenAPI规范** (`openapi.json`)：
   - 完整的JSON格式文档
   - 可用于Swagger UI

## 示例

```
/generate-api-doc --split-modules --output=docs/api-docs/
```

生成所有模块的API文档到 `docs/api-docs/` 目录。

## 相关命令

- `/split-tasks` - 拆分开发任务
- `/generate-sequence-diagram` - 生成时序图
- `/test-api` - API接口测试
- `/develop-backend` - 后端开发
