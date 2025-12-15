# 数据库设计 Skill

## 概述
本 Skill 用于数据库表结构设计，确保数据模型规范、可扩展、高性能。适用于任何关系型数据库。

## 使用场景
- 新项目数据库设计
- 功能模块数据建模
- 数据库重构优化

---

## 设计流程

```
需求分析 → 实体识别 → 关系建模 → 表结构设计 → 索引优化 → 迁移脚本
```

---

## 设计提示词模板

### 从需求生成数据库设计
```prompt
请根据需求文档 @doc/PRD.md 设计数据库表结构：

1. 识别核心实体
2. 定义实体属性
3. 建立实体关系
4. 输出表结构设计文档

要求：
- 遵循命名规范
- 包含必要索引
- 考虑数据量增长
- 支持软删除
```

---

## 命名规范

### 表名规范
| 规则 | 示例 |
|------|------|
| 使用小写下划线 | `user_role` |
| 使用单数名词 | `user` 而非 `users` |
| 关联表：两表名拼接 | `user_role`、`role_permission` |
| 前缀分类（可选） | `sys_user`、`biz_order` |

### 字段名规范
| 规则 | 示例 |
|------|------|
| 使用小写下划线 | `created_at` |
| 主键统一命名 | `id` |
| 外键：表名_id | `user_id`、`role_id` |
| 布尔字段：is_前缀 | `is_active`、`is_deleted` |
| 时间字段：_at后缀 | `created_at`、`updated_at` |

---

## 必备字段

### 基础字段
```sql
id          BIGINT PRIMARY KEY AUTO_INCREMENT,  -- 主键
created_at  DATETIME DEFAULT CURRENT_TIMESTAMP, -- 创建时间
updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, -- 更新时间
created_by  BIGINT,                             -- 创建人ID（可选）
updated_by  BIGINT                              -- 更新人ID（可选）
```

### 软删除字段
```sql
is_deleted  TINYINT DEFAULT 0,                  -- 删除标记：0未删除，1已删除
deleted_at  DATETIME                            -- 删除时间
```

---

## 数据类型选择

### 常用类型对照
| 场景 | MySQL | PostgreSQL | 说明 |
|------|-------|------------|------|
| 主键 | BIGINT | BIGSERIAL | 自增主键 |
| 短文本 | VARCHAR(N) | VARCHAR(N) | N≤255 |
| 长文本 | TEXT | TEXT | 不限长度 |
| 整数 | INT/BIGINT | INTEGER/BIGINT | 根据范围选择 |
| 小数 | DECIMAL(M,N) | NUMERIC(M,N) | 金额用此类型 |
| 布尔 | TINYINT(1) | BOOLEAN | 0/1 或 true/false |
| 日期时间 | DATETIME | TIMESTAMP | 时间戳 |
| JSON | JSON | JSONB | 结构化数据 |
| 枚举 | VARCHAR(20) | VARCHAR(20) | 避免用ENUM类型 |

### 字段长度参考
| 字段类型 | 推荐长度 |
|---------|---------|
| 用户名 | VARCHAR(50) |
| 密码哈希 | VARCHAR(255) |
| 邮箱 | VARCHAR(100) |
| 手机号 | VARCHAR(20) |
| URL | VARCHAR(500) |
| 状态/类型 | VARCHAR(20) |
| 标题 | VARCHAR(200) |
| 描述 | TEXT |

---

## 关系设计

### 一对多 (1:N)
```sql
-- 用户表
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);

-- 文章表（多方持有外键）
CREATE TABLE article (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,        -- 外键指向 user
    title VARCHAR(200) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
```

### 多对多 (N:M)
```sql
-- 用户表
CREATE TABLE user (
    id BIGINT PRIMARY KEY,
    username VARCHAR(50) NOT NULL
);

-- 角色表
CREATE TABLE role (
    id BIGINT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- 关联表
CREATE TABLE user_role (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (role_id) REFERENCES role(id)
);
```

### 自关联（树形结构）
```sql
-- 菜单表（树形结构）
CREATE TABLE menu (
    id BIGINT PRIMARY KEY,
    parent_id BIGINT DEFAULT 0,     -- 父级ID，0表示顶级
    name VARCHAR(50) NOT NULL,
    path VARCHAR(200),
    sort INT DEFAULT 0,             -- 排序
    FOREIGN KEY (parent_id) REFERENCES menu(id)
);
```

---

## 索引设计

### 索引类型
| 类型 | 用途 | 示例 |
|------|------|------|
| PRIMARY KEY | 主键 | `id` |
| UNIQUE | 唯一约束 | `username`、`email` |
| INDEX | 普通索引 | 查询条件字段 |
| COMPOSITE | 联合索引 | `(user_id, status)` |

### 索引命名规范
```sql
-- 主键
pk_表名

-- 唯一索引
uk_表名_字段名

-- 普通索引
idx_表名_字段名

-- 联合索引
idx_表名_字段1_字段2
```

### 索引设计原则
1. **WHERE 条件字段**：经常用于查询的字段
2. **外键字段**：关联查询必须有索引
3. **排序字段**：ORDER BY 的字段
4. **联合索引最左原则**：把区分度高的字段放前面
5. **避免过度索引**：索引会降低写入性能

---

## 表结构文档模板

```markdown
# 数据库设计文档

## 1. 用户表 (user)

**表说明：** 系统用户信息

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BIGINT | 是 | AUTO | 主键 |
| username | VARCHAR(50) | 是 | - | 用户名，唯一 |
| password | VARCHAR(255) | 是 | - | 密码哈希 |
| email | VARCHAR(100) | 否 | NULL | 邮箱 |
| phone | VARCHAR(20) | 否 | NULL | 手机号 |
| status | VARCHAR(20) | 是 | 'active' | 状态：active/inactive |
| is_deleted | TINYINT | 是 | 0 | 删除标记 |
| created_at | DATETIME | 是 | NOW | 创建时间 |
| updated_at | DATETIME | 是 | NOW | 更新时间 |

**索引：**
- `pk_user` (id) - 主键
- `uk_user_username` (username) - 唯一索引
- `idx_user_status` (status) - 普通索引

---

## 2. 角色表 (role)

**表说明：** 系统角色

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BIGINT | 是 | AUTO | 主键 |
| code | VARCHAR(50) | 是 | - | 角色编码，唯一 |
| name | VARCHAR(50) | 是 | - | 角色名称 |
| description | VARCHAR(200) | 否 | NULL | 描述 |
| is_deleted | TINYINT | 是 | 0 | 删除标记 |
| created_at | DATETIME | 是 | NOW | 创建时间 |
| updated_at | DATETIME | 是 | NOW | 更新时间 |

**索引：**
- `pk_role` (id) - 主键
- `uk_role_code` (code) - 唯一索引
```

---

## RBAC 权限模型示例

```sql
-- 用户表
CREATE TABLE user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    is_deleted TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_status (status)
);

-- 角色表
CREATE TABLE role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(200),
    is_deleted TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 权限表
CREATE TABLE permission (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    type VARCHAR(20) NOT NULL,          -- menu/button/api
    parent_id BIGINT DEFAULT 0,
    path VARCHAR(200),
    icon VARCHAR(50),
    sort INT DEFAULT 0,
    is_deleted TINYINT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_permission_type (type),
    INDEX idx_permission_parent (parent_id)
);

-- 用户角色关联表
CREATE TABLE user_role (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user_role_user (user_id),
    INDEX idx_user_role_role (role_id)
);

-- 角色权限关联表
CREATE TABLE role_permission (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_role_permission (role_id, permission_id),
    INDEX idx_role_permission_role (role_id),
    INDEX idx_role_permission_perm (permission_id)
);
```

---

## 输出物清单

- [ ] 实体关系图（ER图描述）
- [ ] 表结构设计文档 (`doc/database-design.md`)
- [ ] SQL 建表脚本 (`sql/schema.sql`)
- [ ] 索引设计说明
- [ ] 初始化数据脚本 (`sql/init-data.sql`)

---

## 完成标志

```
✅ 所有实体已识别
✅ 关系已正确建模
✅ 命名规范统一
✅ 索引设计合理
✅ 文档已生成
```
