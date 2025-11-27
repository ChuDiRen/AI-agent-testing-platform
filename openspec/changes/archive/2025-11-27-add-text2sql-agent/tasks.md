# Tasks: Add Intelligent Text-to-SQL Agent System

## 1. 基础架构

- [x] 1.1 创建项目目录结构 `agent-backend/text2sql/`
- [x] 1.2 实现状态管理类 `state.py` (SQLMessageState, SchemaInfo, SQLValidationResult, SQLExecutionResult, ChartResult)
- [x] 1.3 实现数据模型 `models/schema_models.py` 和 `models/result_models.py`
- [x] 1.4 实现动态LLM配置 `config.py` (多模型支持、流式输出)
- [x] 1.5 实现提示词加载器 `prompts/loader.py`
- [x] 1.6 创建各代理提示词文件 `prompts/*.md`
- [x] 1.7 创建项目依赖配置，更新 `requirements.txt`

## 2. 记忆与上下文管理

- [x] 2.1 实现短期记忆管理器 `memory/checkpointer.py` (SqliteSaver封装)
- [x] 2.2 实现长期记忆存储 `memory/store.py` (SqliteStore封装)
- [x] 2.3 实现记忆统一管理器 `memory/manager.py`
- [x] 2.4 实现消息裁剪器 `context/trimmer.py` (防止上下文爆炸)
- [x] 2.5 实现上下文压缩器 `context/compressor.py` (历史摘要)
- [x] 2.6 实现上下文管理器 `context/manager.py`
- [x] 2.7 编写记忆和上下文单元测试

## 3. 数据库管理器

- [x] 3.1 实现 DatabaseConfig 配置类
- [x] 3.2 实现 DatabaseManager 核心类 (连接池、统一接口)
- [x] 3.3 添加多数据库支持 (MySQL, PostgreSQL, SQLite, Oracle等)
- [x] 3.4 实现 Schema 信息检索功能
- [x] 3.5 实现分页处理 `database/pagination.py`
- [x] 3.6 编写数据库管理器单元测试

## 4. 代理工具函数

- [x] 4.1 实现 Schema 工具 `tools/schema_tools.py` (表结构检索、值映射)
- [x] 4.2 实现 SQL 工具 `tools/sql_tools.py` (SQL解析、优化)
- [x] 4.3 实现验证工具 `tools/validation_tools.py` (语法检查、安全扫描)
- [x] 4.4 实现图表工具 `tools/chart_tools.py` (集成mcp-server-chart)
- [x] 4.5 编写工具函数单元测试

## 5. 代理实现

- [x] 5.1 实现 Schema 分析代理 `agents/schema_agent.py`
- [x] 5.2 实现 SQL 生成代理 `agents/sql_generator_agent.py`
- [x] 5.3 实现 SQL 验证代理 `agents/sql_validator_agent.py`
- [x] 5.4 实现 SQL 执行代理 `agents/sql_executor_agent.py`
- [x] 5.5 实现错误恢复代理 `agents/error_recovery_agent.py`
- [x] 5.6 实现监督代理 `agents/supervisor_agent.py`
- [x] 5.7 实现图表生成代理 `agents/chart_generator_agent.py` (调用mcp-server-chart)
- [x] 5.8 编写代理单元测试

## 6. 流式处理与并发控制

- [x] 6.1 实现流式响应处理 `streaming/handler.py`
- [x] 6.2 实现SSE事件流 `streaming/sse.py`
- [x] 6.3 实现限流器 `concurrency/limiter.py`
- [x] 6.4 实现连接池管理 `concurrency/pool.py`
- [x] 6.5 实现请求队列 `concurrency/queue.py`
- [x] 6.6 编写流式和并发单元测试

## 7. 图工作流

- [x] 7.1 实现主图工作流 `chat_graph.py`
- [x] 7.2 配置条件路由和错误恢复逻辑
- [x] 7.3 集成记忆系统 (checkpointer + store)
- [x] 7.4 集成上下文管理器
- [x] 7.5 集成流式输出
- [x] 7.6 实现 `process_sql_query` 主入口函数
- [x] 7.7 编写端到端测试 `tests/test_graph.py`

## 8. LangGraph API服务

- [x] 8.1 更新 `langgraph.json` 配置文件
- [x] 8.2 实现图导出函数 `chat_graph.py:app`
- [x] 8.3 实现流式图 `chat_graph.py:stream_app`
- [x] 8.4 测试 `langgraph dev` 开发模式
- [x] 8.5 测试 LangGraph Studio 集成

## 9. 二次开发API层

- [x] 9.1 实现自定义FastAPI服务 `api/server.py`
- [x] 9.2 实现API路由 `api/routes.py`
- [x] 9.3 实现请求/响应模型 `api/schemas.py`
- [x] 9.4 集成LangGraph SDK客户端
- [x] 9.5 实现流式查询端点
- [x] 9.6 实现分页查询端点
- [x] 9.7 实现鉴权中间件

## 10. 演示与测试

- [x] 10.1 创建演示脚本 `tests/demo_intelligent_sql.py`
- [x] 10.2 编写完整测试套件 `tests/test_intelligent_sql_agent.py`
- [x] 10.3 流式查询测试 `tests/test_streaming.py`
- [x] 10.4 并发压力测试 `tests/test_concurrency.py`
- [x] 10.5 LangGraph API集成测试
- [x] 10.6 性能测试和优化

## 11. 文档

- [x] 11.1 编写模块 README.md
- [x] 11.2 添加API使用示例 (包括LangGraph SDK调用)
- [x] 11.3 编写配置指南 (包含LLM、记忆系统、并发配置)
- [x] 11.4 编写提示词维护指南
- [x] 11.5 编写LangGraph部署指南

## Dependencies

- Task 2 依赖 Task 1 完成
- Task 3 依赖 Task 1 完成
- Task 4 依赖 Task 2, Task 3 完成
- Task 5 依赖 Task 4 完成
- Task 6 依赖 Task 3 完成
- Task 7 依赖 Task 2, Task 5, Task 6 完成
- Task 8 依赖 Task 7 完成
- Task 9 依赖 Task 8 完成
- Task 10, 11 可与 Task 9 并行
