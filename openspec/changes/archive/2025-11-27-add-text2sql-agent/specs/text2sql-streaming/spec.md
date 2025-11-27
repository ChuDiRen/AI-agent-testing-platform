# Text-to-SQL Streaming and Concurrency Capability

## ADDED Requirements

### Requirement: Real-time Streaming Query
系统 SHALL 支持实时流式查询，使用SSE(Server-Sent Events)向客户端推送结果。

#### Scenario: Stream mode activation
- **WHEN** 客户端请求流式查询
- **THEN** 系统使用`stream_mode="messages"`处理请求
- **AND** 实时推送每个处理步骤的结果

#### Scenario: SSE event format
- **WHEN** 有新的处理结果
- **THEN** 以SSE格式发送数据 `data: {json}\n\n`
- **AND** 包含事件类型标识

#### Scenario: Stream completion
- **WHEN** 查询处理完成
- **THEN** 发送结束事件标识
- **AND** 关闭流连接

#### Scenario: Stream error handling
- **WHEN** 流式处理过程中发生错误
- **THEN** 发送错误事件给客户端
- **AND** 安全关闭流连接

### Requirement: Pagination Support
系统 SHALL 支持大数据集的分页查询和展示。

#### Scenario: Automatic pagination
- **WHEN** 查询结果超过默认限制（100条）
- **THEN** 自动添加LIMIT和OFFSET子句
- **AND** 返回分页元数据（总数、当前页、总页数）

#### Scenario: Custom page size
- **WHEN** 用户指定每页数量
- **THEN** 使用指定的page_size（最大1000）
- **AND** 验证参数有效性

#### Scenario: Pagination navigation
- **WHEN** 请求特定页码
- **THEN** 返回对应页的数据
- **AND** 包含has_next和has_prev标识

#### Scenario: Total count query
- **WHEN** 需要获取总记录数
- **THEN** 执行COUNT(*)查询获取总数
- **AND** 缓存结果避免重复查询

### Requirement: Dynamic Model Configuration
系统 SHALL 支持动态模型切换和配置。

#### Scenario: Runtime model switch
- **WHEN** 请求指定使用特定模型
- **THEN** 动态加载对应的模型实例
- **AND** 保持会话一致性

#### Scenario: Multi-provider support
- **WHEN** 配置不同的模型提供商（siliconflow/openai/anthropic）
- **THEN** 使用对应的API端点和认证
- **AND** 统一调用接口

#### Scenario: Streaming output
- **WHEN** 模型配置启用streaming
- **THEN** 模型响应以流式方式返回
- **AND** 支持逐token输出

### Requirement: External Prompt Management
系统 SHALL 支持提示词外部化管理。

#### Scenario: Prompt file loading
- **WHEN** 代理初始化
- **THEN** 从`prompts/`目录加载对应的Markdown文件
- **AND** 使用LRU缓存避免重复读取

#### Scenario: Dynamic prompt formatting
- **WHEN** 提示词包含变量占位符
- **THEN** 运行时替换为实际值
- **AND** 支持{dialect}、{top_k}等变量

#### Scenario: Prompt hot reload
- **WHEN** 提示词文件被修改
- **THEN** 支持清除缓存重新加载
- **AND** 无需重启服务

### Requirement: Context Explosion Prevention
系统 SHALL 实现多层上下文管理机制，防止token超限。

#### Scenario: Message trimming
- **WHEN** 消息历史超过max_tokens限制
- **THEN** 按策略裁剪旧消息
- **AND** 保留系统消息和最近N条

#### Scenario: History summarization
- **WHEN** 需要压缩大量历史消息
- **THEN** 将旧消息压缩为摘要
- **AND** 保留关键上下文信息

#### Scenario: Schema compression
- **WHEN** 数据库Schema信息过大
- **THEN** 只保留与查询相关的表和列
- **AND** 减少无关信息干扰

#### Scenario: Result set compression
- **WHEN** 查询结果集过大
- **THEN** 只保留样本数据和统计摘要
- **AND** 提示用户完整数据需分页查看

### Requirement: High Concurrency Support
系统 SHALL 支持高并发访问，实现限流和资源池化。

#### Scenario: Request rate limiting
- **WHEN** 请求速率超过配置限制
- **THEN** 延迟处理或返回429错误
- **AND** 保护下游服务

#### Scenario: Connection pooling
- **WHEN** 需要数据库连接
- **THEN** 从连接池获取可用连接
- **AND** 使用完毕归还连接池

#### Scenario: Concurrent request limiting
- **WHEN** 并发请求数超过最大限制
- **THEN** 新请求等待信号量
- **AND** 防止系统过载

#### Scenario: Request queuing
- **WHEN** 瞬时流量超过处理能力
- **THEN** 请求进入队列等待处理
- **AND** 支持优先级排序

#### Scenario: Async processing
- **WHEN** 处理SQL查询请求
- **THEN** 使用异步方式执行
- **AND** 充分利用IO等待时间

### Requirement: LangGraph API Service Deployment
系统 SHALL 支持通过LangGraph API服务进行部署和访问。

#### Scenario: LangGraph dev mode
- **WHEN** 执行`langgraph dev`命令
- **THEN** 启动开发服务器于端口2024
- **AND** 支持代码热重载

#### Scenario: Graph export
- **WHEN** 配置langgraph.json
- **THEN** 导出text2sql_agent和stream_app图
- **AND** 可通过LangGraph API访问

#### Scenario: REST API streaming
- **WHEN** 调用`/runs/stream`端点
- **THEN** 以SSE格式返回流式响应
- **AND** 支持messages-tuple流模式

#### Scenario: Python SDK integration
- **WHEN** 使用langgraph_sdk调用服务
- **THEN** 支持同步和异步客户端
- **AND** 支持thread管理和状态持久化

#### Scenario: LangGraph Studio debugging
- **WHEN** 连接LangGraph Studio
- **THEN** 支持可视化调试
- **AND** 可查看代理执行流程

### Requirement: Secondary Development Extension
系统 SHALL 支持二次开发扩展，封装LangGraph API提供自定义接口。

#### Scenario: Custom FastAPI server
- **WHEN** 需要自定义业务逻辑
- **THEN** 通过FastAPI服务封装LangGraph API
- **AND** 添加鉴权、限流等中间件

#### Scenario: LangGraph SDK client integration
- **WHEN** 自定义服务调用LangGraph
- **THEN** 使用langgraph_sdk客户端
- **AND** 支持流式和同步调用

#### Scenario: Custom query endpoint
- **WHEN** 调用自定义`/api/v1/query`端点
- **THEN** 封装分页、鉴权等逻辑
- **AND** 转发到LangGraph API处理
