# /db - 数据库设计与操作

## 描述
数据库表设计、DDL 生成、索引优化等数据库相关操作。

## 使用方式
```
/db <操作> [参数]
```

## 操作类型

### 1. 设计表结构
```
/db design <表名> --fields "<字段定义>"
```

### 2. 生成 DDL
```
/db ddl <表名>
```

### 3. 索引分析
```
/db index <表名>
```

### 4. 数据迁移
```
/db migrate --from <旧表> --to <新表>
```

## 代码模板

参考 `@templates/code-patterns.md` 中的 Model 层规范生成代码。

### 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写下划线 | `sys_user` |
| 字段名 | 小写下划线 | `user_name` |
| 主键 | `id` | `id BIGINT` |
| 外键 | `{表}_id` | `user_id` |
| 索引 | `idx_{表}_{字段}` | `idx_user_name` |

### 必备字段
```sql
id BIGINT AUTO_INCREMENT PRIMARY KEY,
create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
update_time DATETIME ON UPDATE CURRENT_TIMESTAMP,
deleted TINYINT DEFAULT 0
```

### 字段类型
| 数据类型 | MySQL 类型 |
|----------|-----------|
| 主键 | BIGINT |
| 状态 | TINYINT |
| 短文本 | VARCHAR(n) |
| 长文本 | TEXT |
| 金额 | DECIMAL(10,2) |
| 时间 | DATETIME |

## 输出位置
- DDL 文件：`database-setup/ddl_{table}.sql`
- Model 文件：`platform-fastapi-server/apitest/model/{table}.py`

## 注意事项
- 生产环境修改需备份
- 大表添加索引注意锁表
- 字段设计考虑扩展性
