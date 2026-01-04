# 数据库设计技能

## 触发条件
当用户提到：数据库、SQL、建表、MySQL、字典、DDL、索引、迁移、schema、表结构

## 设计规范

### 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写下划线，业务前缀 | `sys_user`, `api_info` |
| 字段名 | 小写下划线 | `user_name`, `create_time` |
| 主键 | `id` | `id BIGINT PRIMARY KEY` |
| 外键 | `{表名}_id` | `user_id`, `project_id` |
| 索引 | `idx_{表名}_{字段}` | `idx_user_name` |
| 唯一索引 | `uk_{表名}_{字段}` | `uk_user_email` |

### 必备字段
```sql
-- 每张表必须包含
id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
create_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
update_time DATETIME ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
create_by VARCHAR(64) DEFAULT NULL COMMENT '创建人',
update_by VARCHAR(64) DEFAULT NULL COMMENT '更新人',
deleted TINYINT DEFAULT 0 COMMENT '删除标记：0未删除 1已删除'
```

### 字段类型选择
| 数据类型 | MySQL 类型 | 说明 |
|----------|-----------|------|
| 主键/外键 | BIGINT | 8字节，范围大 |
| 状态/类型 | TINYINT | 0-255，节省空间 |
| 短文本 | VARCHAR(n) | n≤255 |
| 长文本 | TEXT | 大文本内容 |
| 金额 | DECIMAL(10,2) | 精确计算 |
| 时间 | DATETIME | 日期时间 |
| 布尔 | TINYINT(1) | 0/1 |
| JSON | JSON | MySQL 5.7+ |

## DDL 模板

### 创建表
```sql
-- {table_comment}
CREATE TABLE `{table_name}` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    -- 业务字段
    `name` VARCHAR(100) NOT NULL COMMENT '名称',
    `code` VARCHAR(50) DEFAULT NULL COMMENT '编码',
    `status` TINYINT DEFAULT 1 COMMENT '状态：1启用 0禁用',
    `sort` INT DEFAULT 0 COMMENT '排序',
    `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注',
    -- 关联字段
    `parent_id` BIGINT DEFAULT NULL COMMENT '父级ID',
    `project_id` BIGINT DEFAULT NULL COMMENT '项目ID',
    -- 系统字段
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `create_by` VARCHAR(64) DEFAULT NULL COMMENT '创建人',
    `update_by` VARCHAR(64) DEFAULT NULL COMMENT '更新人',
    `deleted` TINYINT DEFAULT 0 COMMENT '删除标记',
    PRIMARY KEY (`id`),
    KEY `idx_{table_name}_status` (`status`),
    KEY `idx_{table_name}_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='{table_comment}';
```

### 索引设计原则
```sql
-- 1. 主键索引（自动创建）
PRIMARY KEY (`id`)

-- 2. 唯一索引（业务唯一性）
UNIQUE KEY `uk_user_email` (`email`)

-- 3. 普通索引（查询优化）
KEY `idx_user_status` (`status`)

-- 4. 组合索引（遵循最左前缀）
KEY `idx_user_status_type` (`status`, `type`)

-- 5. 全文索引（搜索优化）
FULLTEXT KEY `ft_content` (`content`)
```

### 常用 ALTER 语句
```sql
-- 添加字段
ALTER TABLE `{table}` ADD COLUMN `field` VARCHAR(100) COMMENT '说明' AFTER `name`;

-- 修改字段
ALTER TABLE `{table}` MODIFY COLUMN `field` VARCHAR(200) COMMENT '新说明';

-- 删除字段
ALTER TABLE `{table}` DROP COLUMN `field`;

-- 添加索引
ALTER TABLE `{table}` ADD INDEX `idx_field` (`field`);

-- 删除索引
ALTER TABLE `{table}` DROP INDEX `idx_field`;

-- 添加外键
ALTER TABLE `{table}` ADD CONSTRAINT `fk_name` 
    FOREIGN KEY (`field_id`) REFERENCES `other_table` (`id`);
```

## SQLModel 映射

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class {Table}(SQLModel, table=True):
    """数据库表映射"""
    __tablename__ = "{table_name}"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(..., max_length=100, description="名称")
    code: Optional[str] = Field(default=None, max_length=50, description="编码")
    status: int = Field(default=1, description="状态：1启用 0禁用")
    sort: int = Field(default=0, description="排序")
    remark: Optional[str] = Field(default=None, max_length=500, description="备注")
    
    # 关联字段
    parent_id: Optional[int] = Field(default=None, foreign_key="{table_name}.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    
    # 系统字段
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(default=None)
    create_by: Optional[str] = Field(default=None, max_length=64)
    update_by: Optional[str] = Field(default=None, max_length=64)
    deleted: int = Field(default=0)
```

## 性能优化建议

### 索引优化
1. **WHERE 条件字段**建索引
2. **ORDER BY 字段**建索引
3. **JOIN 关联字段**建索引
4. **避免**在索引列上使用函数
5. **组合索引**遵循最左前缀原则

### 查询优化
```sql
-- 避免 SELECT *
SELECT id, name, status FROM user WHERE status = 1;

-- 使用 LIMIT 分页
SELECT * FROM user LIMIT 0, 20;

-- 避免 OR，使用 IN
SELECT * FROM user WHERE status IN (1, 2);

-- 使用 EXISTS 代替 IN（大数据量）
SELECT * FROM user u WHERE EXISTS (SELECT 1 FROM role r WHERE r.user_id = u.id);
```

## 注意事项
1. 生产环境修改表结构需备份
2. 大表添加索引使用 `ALGORITHM=INPLACE`
3. 字段设计考虑扩展性
4. 敏感数据需加密存储
