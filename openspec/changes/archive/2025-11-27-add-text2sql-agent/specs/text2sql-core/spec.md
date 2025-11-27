# Text-to-SQL Core Capability

## ADDED Requirements

### Requirement: Natural Language Query Processing
系统 SHALL 接收用户的自然语言查询并将其转换为可执行的SQL语句。

#### Scenario: Basic query conversion
- **WHEN** 用户输入 "查询所有客户的姓名和邮箱"
- **THEN** 系统生成对应的SELECT语句
- **AND** 返回格式化的查询结果

#### Scenario: Complex query with aggregation
- **WHEN** 用户输入 "哪种音乐类型的曲目平均时长最长"
- **THEN** 系统生成包含JOIN、GROUP BY和聚合函数的SQL语句
- **AND** 按平均时长降序返回结果

#### Scenario: Multi-table join query
- **WHEN** 用户输入 "显示销售额最高的前5个艺术家"
- **THEN** 系统生成多表关联查询
- **AND** 正确处理Artist、Album、Track和InvoiceLine的关联关系

### Requirement: Query Result Formatting
系统 SHALL 将SQL执行结果格式化为易于理解的输出格式。

#### Scenario: Tabular result display
- **WHEN** 查询返回多行数据
- **THEN** 结果以表格形式呈现
- **AND** 包含列名和数据类型信息

#### Scenario: Empty result handling
- **WHEN** 查询未返回任何数据
- **THEN** 返回明确的"无结果"提示
- **AND** 建议可能的查询修改

#### Scenario: Large result set handling
- **WHEN** 查询结果超过默认限制（100行）
- **THEN** 自动添加LIMIT子句
- **AND** 提示用户完整结果集大小

### Requirement: Query Execution Monitoring
系统 SHALL 监控查询执行过程并提供性能指标。

#### Scenario: Execution time tracking
- **WHEN** 执行任何SQL查询
- **THEN** 记录并返回执行时间
- **AND** 时间精度至少到毫秒

#### Scenario: Query timeout handling
- **WHEN** 查询执行时间超过配置的超时时间（默认30秒）
- **THEN** 中断查询执行
- **AND** 返回超时错误信息和优化建议

### Requirement: State Management
系统 SHALL 维护查询处理的完整生命周期状态。

#### Scenario: State initialization
- **WHEN** 接收新的查询请求
- **THEN** 初始化SQLMessageState
- **AND** 设置connection_id和初始stage

#### Scenario: State transition tracking
- **WHEN** 查询处理从一个阶段进入下一阶段
- **THEN** 更新current_stage字段
- **AND** 保留之前阶段的处理结果

#### Scenario: Error history preservation
- **WHEN** 查询处理过程中发生错误
- **THEN** 将错误信息追加到error_history
- **AND** 增加retry_count计数器
