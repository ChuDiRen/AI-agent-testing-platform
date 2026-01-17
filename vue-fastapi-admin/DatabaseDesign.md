# vue-fastapi-admin 数据库设计文档

> 基于 FastAPI + Vue3 + Naive UI 的现代化轻量管理平台

## 技术栈

- **ORM**: Tortoise ORM
- **数据库**: MySQL / PostgreSQL
- **认证**: JWT

---

## 表结构总览

| 表名 | 说明 | 核心字段 |
|------|------|----------|
| `user` | 用户表 | username, email, password, roles |
| `role` | 角色表 | name, desc, menus, apis |
| `api` | API接口表 | path, method, summary, tags |
| `menu` | 菜单表 | name, path, menu_type, parent_id |
| `dept` | 部门表 | name, desc, parent_id |
| `dept_closure` | 部门闭包表 | ancestor, descendant, level |
| `audit_log` | 审计日志表 | user_id, module, method, path |

---

## 详细表设计

### 1. user 用户表

```sql
-- 用户表
CREATE TABLE `user` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username` VARCHAR(20) NOT NULL COMMENT '用户名称',
    `alias` VARCHAR(30) COMMENT '姓名',
    `email` VARCHAR(255) NOT NULL COMMENT '邮箱',
    `phone` VARCHAR(20) COMMENT '电话',
    `password` VARCHAR(128) COMMENT '密码',
    `is_active` TINYINT DEFAULT 1 COMMENT '是否激活',
    `is_superuser` TINYINT DEFAULT 0 COMMENT '是否为超级管理员',
    `last_login` DATETIME COMMENT '最后登录时间',
    `dept_id` BIGINT COMMENT '部门ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_user_username` (`username`),
    KEY `idx_user_email` (`email`),
    KEY `idx_user_is_active` (`is_active`),
    KEY `idx_user_is_superuser` (`is_superuser`),
    KEY `idx_user_last_login` (`last_login`),
    KEY `idx_user_dept_id` (`dept_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';
```

**关联关系**:
- `user` ↔ `role`: 多对多 (user_role)
- `user` ↔ `dept`: 多对一

---

### 2. role 角色表

```sql
-- 角色表
CREATE TABLE `role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(20) NOT NULL COMMENT '角色名称',
    `desc` VARCHAR(500) COMMENT '角色描述',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_role_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';
```

**关联关系**:
- `role` ↔ `user`: 多对多 (user_role)
- `role` ↔ `menu`: 多对多 (role_menu)
- `role` ↔ `api`: 多对多 (role_api)

---

### 3. api API接口表

```sql
-- API接口表
CREATE TABLE `api` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `path` VARCHAR(100) NOT NULL COMMENT 'API路径',
    `method` VARCHAR(10) NOT NULL COMMENT '请求方法',
    `summary` VARCHAR(500) COMMENT '请求简介',
    `tags` VARCHAR(100) COMMENT 'API标签',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_api_path` (`path`),
    KEY `idx_api_method` (`method`),
    KEY `idx_api_tags` (`tags`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API接口表';
```

**MethodType 枚举**:
| 值 | 说明 |
|----|------|
| GET | GET 请求 |
| POST | POST 请求 |
| PUT | PUT 请求 |
| DELETE | DELETE 请求 |
| PATCH | PATCH 请求 |

---

### 4. menu 菜单表

```sql
-- 菜单表
CREATE TABLE `menu` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(20) NOT NULL COMMENT '菜单名称',
    `remark` JSON COMMENT '保留字段',
    `menu_type` VARCHAR(20) COMMENT '菜单类型',
    `icon` VARCHAR(100) COMMENT '菜单图标',
    `path` VARCHAR(100) NOT NULL COMMENT '菜单路径',
    `order` INT DEFAULT 0 COMMENT '排序',
    `parent_id` INT DEFAULT 0 COMMENT '父菜单ID',
    `is_hidden` TINYINT DEFAULT 0 COMMENT '是否隐藏',
    `component` VARCHAR(100) NOT NULL COMMENT '组件',
    `keepalive` TINYINT DEFAULT 1 COMMENT '存活',
    `redirect` VARCHAR(100) COMMENT '重定向',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_menu_name` (`name`),
    KEY `idx_menu_path` (`path`),
    KEY `idx_menu_order` (`order`),
    KEY `idx_menu_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='菜单表';
```

**MenuType 枚举**:
| 值 | 说明 |
|----|------|
| catalog | 目录 |
| menu | 菜单 |

---

### 5. dept 部门表

```sql
-- 部门表
CREATE TABLE `dept` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `name` VARCHAR(20) NOT NULL COMMENT '部门名称',
    `desc` VARCHAR(500) COMMENT '备注',
    `is_deleted` TINYINT DEFAULT 0 COMMENT '软删除标记',
    `order` INT DEFAULT 0 COMMENT '排序',
    `parent_id` INT DEFAULT 0 COMMENT '父部门ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_dept_name` (`name`),
    KEY `idx_dept_is_deleted` (`is_deleted`),
    KEY `idx_dept_order` (`order`),
    KEY `idx_dept_parent_id` (`parent_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门表';
```

---

### 6. dept_closure 部门闭包表

```sql
-- 部门闭包表（用于树形结构查询）
CREATE TABLE `dept_closure` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `ancestor` INT NOT NULL COMMENT '父代',
    `descendant` INT NOT NULL COMMENT '子代',
    `level` INT DEFAULT 0 COMMENT '深度',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_dept_closure_ancestor` (`ancestor`),
    KEY `idx_dept_closure_descendant` (`descendant`),
    KEY `idx_dept_closure_level` (`level`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='部门闭包表';
```

> 使用闭包表模式实现部门树形结构，支持高效的祖先/后代查询

---

### 7. audit_log 审计日志表

```sql
-- 审计日志表
CREATE TABLE `audit_log` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `username` VARCHAR(64) DEFAULT '' COMMENT '用户名称',
    `module` VARCHAR(64) DEFAULT '' COMMENT '功能模块',
    `summary` VARCHAR(128) DEFAULT '' COMMENT '请求描述',
    `method` VARCHAR(10) DEFAULT '' COMMENT '请求方法',
    `path` VARCHAR(255) DEFAULT '' COMMENT '请求路径',
    `status` INT DEFAULT -1 COMMENT '状态码',
    `response_time` INT DEFAULT 0 COMMENT '响应时间(单位ms)',
    `request_args` JSON COMMENT '请求参数',
    `response_body` JSON COMMENT '返回数据',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_audit_log_user_id` (`user_id`),
    KEY `idx_audit_log_username` (`username`),
    KEY `idx_audit_log_module` (`module`),
    KEY `idx_audit_log_method` (`method`),
    KEY `idx_audit_log_path` (`path`),
    KEY `idx_audit_log_status` (`status`),
    KEY `idx_audit_log_response_time` (`response_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';
```

---

## 多对多关联表

### user_role 用户角色关联表

```sql
-- user_role 用户角色关联表
CREATE TABLE `user_role` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_role_user_id_role_id` (`user_id`, `role_id`),
    KEY `idx_user_role_user_id` (`user_id`),
    KEY `idx_user_role_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户角色关联表';
```

### role_menu 角色菜单关联表

```sql
-- role_menu 角色菜单关联表
CREATE TABLE `role_menu` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `menu_id` BIGINT NOT NULL COMMENT '菜单ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_menu_role_id_menu_id` (`role_id`, `menu_id`),
    KEY `idx_role_menu_role_id` (`role_id`),
    KEY `idx_role_menu_menu_id` (`menu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色菜单关联表';
```

### role_api 角色API关联表

```sql
-- role_api 角色API关联表
CREATE TABLE `role_api` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `api_id` BIGINT NOT NULL COMMENT 'API ID',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_role_api_role_id_api_id` (`role_id`, `api_id`),
    KEY `idx_role_api_role_id` (`role_id`),
    KEY `idx_role_api_api_id` (`api_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色API关联表';
```

---

## ER 图

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    user     │──────────│  user_role  │──────────│    role     │
│             │         └─────────────┘         │             │
│  username   │                                   │    name     │
│  email      │         ┌─────────────┐         │    desc     │
│  password   │──────────│  role_menu  │──────────│             │
│  is_active  │         └─────────────┘         └──────┬──────┘
│  is_superuser│                                    │
└─────────────┘         ┌─────────────┐         ┌──────▼──────┐
                        │  role_api   │         │    menu     │
                        └─────────────┘         │             │
                                               │    name     │
┌─────────────┐         ┌─────────────┐         │    path     │
│    dept     │──────────│dept_closure│         │ menu_type   │
│             │         │  (closure)  │         │  parent_id  │
│    name     │         └─────────────┘         │  component  │
│  parent_id  │                               └───────────────┘
└─────────────┘
                                               ┌─────────────┐
                                               │     api     │
                                               │             │
                                               │    path     │
                                               │   method    │
                                               │   summary   │
                                               └─────────────┘

┌─────────────┐
│ audit_log   │
│             │
│   user_id   │
│   module    │
│   method    │
│    path     │
│   status    │
└─────────────┘
```

---

## 索引设计原则

| 索引类型 | 字段 | 说明 |
|----------|------|------|
| 主键 | id | 自增主键 |
| 唯一索引 | username | 用户名唯一 |
| 唯一索引 | email | 邮箱唯一 |
| 唯一索引 | name (role/dept) | 名称唯一 |
| 普通索引 | status | 状态过滤 |
| 普通索引 | parent_id | 树形结构 |
| 普通索引 | created_at | 时间排序 |

---

## 权限模型

### RBAC (Role-Based Access Control)

1. **用户 (User)**: 系统操作主体
2. **角色 (Role)**: 权限集合，一个用户可拥有多个角色
3. **菜单 (Menu)**: 前端路由权限
4. **API (Api)**: 后端接口权限

### 权限控制流程

```
用户登录 → 获取角色 → 获取菜单列表 → 获取API权限
         ↓
      JWT Token → 每次请求携带 Token
                  ↓
            验证 Token → 检查菜单权限 → 检查 API 权限
```

---

## 基础字段规范

所有表包含以下系统字段:

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | BIGINT | 主键ID |
| `created_at` | DATETIME | 创建时间 |
| `updated_at` | DATETIME | 更新时间 |

---

## 快速开始

### 初始化数据库

```python
from tortoise import Tortoise

async def init_db():
    await Tortoise.init(
        db_url="mysql://root:password@localhost:3306/vue_fastapi_admin",
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()
```

### 创建初始用户

```python
from app.models.admin import User, Role

# 创建超级管理员角色
admin_role = await Role.create(name="超级管理员", desc="拥有所有权限")

# 创建管理员用户
admin_user = await User.create(
    username="admin",
    email="admin@qq.com",
    password="123456",
    is_superuser=True,
)
await admin_user.roles.add(admin_role)
```
