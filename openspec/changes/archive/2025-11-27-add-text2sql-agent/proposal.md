# Change: Add Intelligent Text-to-SQL Agent System

## Why
项目需要一个智能的自然语言到SQL转换系统，使用户能够通过自然语言查询数据库，无需编写SQL语句。该系统基于LangGraph的多代理架构实现，具备智能分析、自动生成、多层验证、安全执行和自愈能力。

## What Changes
- **新增** `agent-backend/text2sql/` 目录，包含完整的Text-to-SQL代理系统
- **新增** 监督代理 (Supervisor Agent) - 协调整个工作流程
- **新增** Schema分析代理 (Schema Agent) - 分析用户查询和数据库模式
- **新增** SQL生成代理 (SQL Generator Agent) - 生成高质量SQL语句
- **新增** SQL验证代理 (SQL Validator Agent) - 验证SQL的正确性和安全性
- **新增** SQL执行代理 (SQL Executor Agent) - 安全执行SQL
- **新增** 错误恢复代理 (Error Recovery Agent) - 智能错误分析和自动修复
- **新增** 图表生成代理 (Chart Generator Agent) - 调用mcp-server-chart生成数据可视化图表
- **新增** 数据库管理器 - 支持多种数据库类型的统一接口
- **新增** 图工作流 (Graph Workflow) - 基于LangGraph的状态机
- **新增** 短期记忆 (Checkpointer) - 基于SqliteSaver的会话上下文管理
- **新增** 长期记忆 (Store) - 基于SqliteStore的知识存储
- **新增** 上下文管理器 - 消息裁剪和历史压缩，防止上下文爆炸
- **新增** 流式查询 - 支持SSE实时输出
- **新增** 分页处理 - 大数据集分页展示
- **新增** 并发控制 - 限流、连接池、请求队列
- **新增** 提示词管理 - 外部化Markdown文件管理
- **配置** 动态模型 - 支持运行时切换模型和提供商

## Impact
- Affected specs: `text2sql-core`, `text2sql-agents`, `text2sql-database`, `text2sql-memory`, `text2sql-streaming`
- Affected code: `agent-backend/text2sql/`
- Dependencies: langgraph, langgraph-supervisor, langgraph-checkpoint-sqlite, langchain, langchain-openai, SQLAlchemy, 各数据库驱动
- LLM: 硅基流动 DeepSeek-V3.2-Exp (https://api.siliconflow.cn/v1)
