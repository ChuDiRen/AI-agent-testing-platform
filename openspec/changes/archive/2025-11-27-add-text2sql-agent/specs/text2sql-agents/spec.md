# Text-to-SQL Agent System Capability

## ADDED Requirements

### Requirement: Supervisor Agent Coordination
监督代理 SHALL 协调所有子代理的工作流程，实现智能路由决策。

#### Scenario: Normal workflow routing
- **WHEN** 接收用户查询请求
- **THEN** 按顺序调度Schema分析→SQL生成→SQL验证→SQL执行
- **AND** 在每个阶段检查执行结果

#### Scenario: Error routing decision
- **WHEN** 子代理返回错误状态
- **THEN** 根据错误类型决定是重试、跳转到错误恢复还是直接失败
- **AND** 确保retry_count不超过max_retries（默认3次）

#### Scenario: Workflow completion
- **WHEN** 查询成功执行或达到最大重试次数
- **THEN** 汇总所有处理结果返回给用户
- **AND** 清理临时状态

### Requirement: Schema Analysis
Schema分析代理 SHALL 分析用户查询意图并获取相关数据库模式信息。

#### Scenario: Query intent recognition
- **WHEN** 接收自然语言查询
- **THEN** 识别查询类型（SELECT/聚合/排序等）
- **AND** 提取关键实体和字段需求

#### Scenario: Schema information retrieval
- **WHEN** 确定查询涉及的表
- **THEN** 获取表结构、列信息和关联关系
- **AND** 缓存Schema信息以供后续使用

#### Scenario: Value mapping
- **WHEN** 查询包含具体值（如"中国客户"）
- **THEN** 识别可能的列和匹配值
- **AND** 提供模糊匹配建议

### Requirement: SQL Generation
SQL生成代理 SHALL 根据Schema信息生成高质量的SQL语句。

#### Scenario: Basic SQL generation
- **WHEN** 接收查询分析结果和Schema信息
- **THEN** 生成语法正确的SQL语句
- **AND** 包含适当的别名和格式化

#### Scenario: Query optimization suggestions
- **WHEN** 生成SQL语句
- **THEN** 分析可能的性能问题
- **AND** 提供索引使用和查询优化建议

#### Scenario: LIMIT clause handling
- **WHEN** 查询未指定结果限制
- **THEN** 自动添加LIMIT子句（默认100）
- **AND** 提示用户可调整限制

### Requirement: SQL Validation
SQL验证代理 SHALL 验证SQL语句的正确性、安全性和性能。

#### Scenario: Syntax validation
- **WHEN** 接收生成的SQL语句
- **THEN** 验证SQL语法是否正确
- **AND** 返回详细的语法错误信息

#### Scenario: Security scanning
- **WHEN** 验证SQL语句
- **THEN** 检测SQL注入风险
- **AND** 扫描危险关键字（DROP、DELETE、TRUNCATE等）
- **AND** 对高风险操作返回警告

#### Scenario: Performance analysis
- **WHEN** 验证SQL语句
- **THEN** 分析查询复杂度
- **AND** 检查是否缺少索引
- **AND** 评估可能的全表扫描风险

### Requirement: SQL Execution
SQL执行代理 SHALL 安全执行验证通过的SQL语句并处理结果。

#### Scenario: Safe query execution
- **WHEN** 接收验证通过的SQL语句
- **THEN** 通过数据库连接执行查询
- **AND** 应用超时控制和资源限制

#### Scenario: Result formatting
- **WHEN** 查询执行成功
- **THEN** 将结果转换为结构化格式
- **AND** 包含行数、列信息和执行时间

#### Scenario: Error handling
- **WHEN** 查询执行失败
- **THEN** 捕获数据库异常
- **AND** 返回详细错误信息供错误恢复代理处理

### Requirement: Error Recovery
错误恢复代理 SHALL 智能分析错误并尝试自动修复。

#### Scenario: Error pattern recognition
- **WHEN** 接收查询错误
- **THEN** 识别错误类型（语法错误、表不存在、权限不足等）
- **AND** 匹配已知的错误模式

#### Scenario: Automatic fix generation
- **WHEN** 识别到可修复的错误
- **THEN** 生成修复策略
- **AND** 返回修正后的SQL或查询参数

#### Scenario: Recovery failure handling
- **WHEN** 无法自动修复错误
- **THEN** 返回详细的错误分析
- **AND** 提供用户可操作的建议

### Requirement: Chart Generation via MCP
图表生成代理 SHALL 调用mcp-server-chart生成数据可视化图表。

#### Scenario: Auto chart type selection
- **WHEN** 接收SQL执行结果数据
- **THEN** 分析数据类型和结构
- **AND** 自动选择合适的图表类型（柱状图、折线图、饼图等）

#### Scenario: MCP chart generation
- **WHEN** 确定图表类型和数据
- **THEN** 调用mcp-server-chart的相应工具
- **AND** 生成图表配置或图片

#### Scenario: Chart customization
- **WHEN** 用户指定图表要求（如"用饼图显示"）
- **THEN** 按用户要求生成指定类型图表
- **AND** 应用默认样式和颜色方案

#### Scenario: Aggregation data visualization
- **WHEN** 查询结果包含聚合数据（COUNT、SUM、AVG等）
- **THEN** 自动识别为可视化候选
- **AND** 推荐适合的图表类型
