# Text-to-SQL Memory Management Capability

## ADDED Requirements

### Requirement: Short-term Memory Management
系统 SHALL 使用SqliteSaver实现短期记忆，管理会话上下文和对话历史。

#### Scenario: Session context preservation
- **WHEN** 用户在同一会话中发送多个查询
- **THEN** 系统保持对话上下文
- **AND** 后续查询可以引用之前的结果

#### Scenario: Thread isolation
- **WHEN** 不同用户或不同会话发起查询
- **THEN** 按thread_id隔离各自的对话历史
- **AND** 不同会话之间数据互不干扰

#### Scenario: Interrupt and resume
- **WHEN** 查询处理被中断（如超时或错误）
- **THEN** 系统可以从中断点恢复
- **AND** 保留中断前的所有状态

#### Scenario: State rollback
- **WHEN** 需要回滚到之前的状态
- **THEN** 系统支持状态回滚操作
- **AND** 恢复到指定的checkpoint

### Requirement: Long-term Memory Storage
系统 SHALL 使用SqliteStore实现长期记忆，存储持久化知识和用户偏好。

#### Scenario: Schema caching
- **WHEN** 首次查询某个数据库的Schema信息
- **THEN** 将Schema信息存储到长期记忆
- **AND** 后续查询直接从缓存读取

#### Scenario: Query pattern learning
- **WHEN** 用户重复执行类似查询
- **THEN** 系统记录常用查询模式
- **AND** 为后续相似查询提供优化建议

#### Scenario: User preference storage
- **WHEN** 用户指定查询偏好（如默认限制、排序方式）
- **THEN** 将偏好存储到长期记忆
- **AND** 后续查询自动应用用户偏好

#### Scenario: Cross-session knowledge sharing
- **WHEN** 用户在新会话中查询相同数据库
- **THEN** 系统可以访问之前会话存储的知识
- **AND** 减少重复的Schema检索操作

### Requirement: Memory Unified Management
系统 SHALL 提供统一的记忆管理器，协调短期和长期记忆的使用。

#### Scenario: Memory initialization
- **WHEN** 系统启动或首次处理查询
- **THEN** 初始化短期记忆(checkpointer)和长期记忆(store)
- **AND** 确保data目录和数据库文件存在

#### Scenario: Lazy loading
- **WHEN** 记忆组件未被使用
- **THEN** 延迟初始化以节省资源
- **AND** 首次访问时自动创建连接

#### Scenario: Connection reuse
- **WHEN** 多次访问记忆系统
- **THEN** 复用已建立的数据库连接
- **AND** 使用缓存避免重复初始化

#### Scenario: Memory cleanup
- **WHEN** 会话结束或记忆数据过期
- **THEN** 提供清理机制释放资源
- **AND** 保留重要的长期记忆数据

### Requirement: Memory Database Configuration
系统 SHALL 提供灵活的记忆数据库配置。

#### Scenario: Default path configuration
- **WHEN** 未指定自定义路径
- **THEN** 使用默认路径 `agent-backend/data/agent_memory.db`
- **AND** 自动创建必要的目录结构

#### Scenario: Custom path support
- **WHEN** 配置自定义数据库路径
- **THEN** 使用指定路径存储记忆数据
- **AND** 验证路径可写

#### Scenario: Thread-safe access
- **WHEN** 多个线程同时访问记忆数据库
- **THEN** 使用 `check_same_thread=False` 配置
- **AND** 确保并发安全
