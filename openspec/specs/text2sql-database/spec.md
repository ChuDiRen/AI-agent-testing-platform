# text2sql-database Specification

## Purpose
TBD - created by archiving change add-text2sql-agent. Update Purpose after archive.
## Requirements
### Requirement: Multi-Database Support
数据库管理器 SHALL 提供统一接口支持多种数据库类型。

#### Scenario: MySQL connection
- **WHEN** 配置MySQL数据库连接
- **THEN** 使用mysql-connector或PyMySQL建立连接
- **AND** 支持MySQL 5.7+和MySQL 8.0+

#### Scenario: PostgreSQL connection
- **WHEN** 配置PostgreSQL数据库连接
- **THEN** 使用psycopg2或asyncpg建立连接
- **AND** 支持PostgreSQL 10+

#### Scenario: SQLite connection
- **WHEN** 配置SQLite数据库连接
- **THEN** 使用内置sqlite3模块建立连接
- **AND** 支持本地和内存数据库

#### Scenario: Additional database support
- **WHEN** 配置Oracle/Snowflake/BigQuery/ClickHouse/DuckDB连接
- **THEN** 使用对应的数据库驱动建立连接
- **AND** 提供一致的查询接口

### Requirement: Database Configuration
数据库配置类 SHALL 封装所有连接参数。

#### Scenario: Basic configuration
- **WHEN** 创建数据库配置
- **THEN** 包含db_type、host、port、database、username、password
- **AND** 验证必填参数

#### Scenario: Connection options
- **WHEN** 配置高级连接选项
- **THEN** 支持SSL/TLS、连接超时、字符集等参数
- **AND** 提供合理的默认值

### Requirement: Connection Pool Management
数据库管理器 SHALL 实现连接池以提高性能。

#### Scenario: Pool initialization
- **WHEN** 首次请求数据库连接
- **THEN** 创建连接池
- **AND** 预创建最小数量的连接

#### Scenario: Connection reuse
- **WHEN** 请求数据库连接
- **THEN** 从连接池获取可用连接
- **AND** 使用完毕后归还连接池

#### Scenario: Connection health check
- **WHEN** 从连接池获取连接
- **THEN** 验证连接是否有效
- **AND** 自动替换失效连接

### Requirement: Schema Information Retrieval
数据库管理器 SHALL 提供数据库Schema信息检索功能。

#### Scenario: Table list retrieval
- **WHEN** 请求数据库表列表
- **THEN** 返回所有可访问的表名
- **AND** 包含表类型（表/视图）

#### Scenario: Column information retrieval
- **WHEN** 请求表的列信息
- **THEN** 返回列名、数据类型、是否可空、默认值
- **AND** 标识主键和外键

#### Scenario: Relationship discovery
- **WHEN** 请求表关联信息
- **THEN** 返回外键约束定义
- **AND** 推断表之间的关联关系

#### Scenario: Index information retrieval
- **WHEN** 请求表的索引信息
- **THEN** 返回所有索引定义
- **AND** 包含索引类型和覆盖列

### Requirement: Query Execution Safety
数据库管理器 SHALL 确保查询执行的安全性。

#### Scenario: Timeout enforcement
- **WHEN** 执行SQL查询
- **THEN** 应用配置的超时限制
- **AND** 超时后自动终止查询

#### Scenario: Read-only mode
- **WHEN** 配置为只读模式
- **THEN** 拒绝执行写入操作（INSERT/UPDATE/DELETE）
- **AND** 返回明确的权限错误

#### Scenario: Row limit enforcement
- **WHEN** 查询返回大量数据
- **THEN** 应用配置的行数限制
- **AND** 提示用户结果已截断

### Requirement: Error Handling and Recovery
数据库管理器 SHALL 提供健壮的错误处理机制。

#### Scenario: Connection failure recovery
- **WHEN** 数据库连接失败
- **THEN** 自动重试连接（最多3次）
- **AND** 记录详细错误日志

#### Scenario: Query error handling
- **WHEN** SQL查询执行失败
- **THEN** 捕获并转换数据库特定异常
- **AND** 返回统一的错误格式

#### Scenario: Transaction management
- **WHEN** 执行需要事务的操作
- **THEN** 支持事务开始、提交和回滚
- **AND** 确保异常时自动回滚

