# Technical Design: Intelligent Text-to-SQL Agent System

## Context

本系统旨在提供一个基于LangGraph的智能自然语言到SQL转换和执行平台。系统采用多代理协作架构，每个代理专注于特定任务，通过监督代理协调整体工作流程。

### Stakeholders
- 数据分析师：需要通过自然语言查询数据库
- 业务用户：无SQL编写能力但需要数据查询
- 开发人员：需要集成和扩展系统

### Constraints
- 必须支持多种主流数据库（MySQL、PostgreSQL、SQLite等）
- 必须防止SQL注入和其他安全风险
- 查询响应时间需在可接受范围内
- 需要提供详细的执行日志和监控

## Goals / Non-Goals

### Goals
- 提供准确的自然语言到SQL转换
- 实现多层安全验证机制
- 支持错误自动检测和恢复
- 提供可扩展的代理架构
- 支持多种数据库类型

### Non-Goals
- 不处理数据库管理任务（DDL操作）
- 不提供图形化查询构建器
- 不处理超大规模数据导出（但支持分页）

## Decisions

### Decision 1: 动态模型与提示词管理

**选择**: 支持动态模型切换和提示词外部化管理

**动态模型配置**:
```python
# config.py - 支持动态切换模型
from dataclasses import dataclass
from typing import Optional

@dataclass
class LLMConfig:
    provider: str = "siliconflow"  # siliconflow, openai, anthropic
    model_name: str = "deepseek-ai/DeepSeek-V3.2-Exp"
    api_url: str = "https://api.siliconflow.cn/v1"
    api_key: Optional[str] = None  # 从环境变量读取
    temperature: float = 0.0
    max_tokens: int = 4096
    streaming: bool = True  # 启用流式输出

def get_model(config: LLMConfig = None):
    """动态获取模型实例"""
    config = config or LLMConfig()
    return init_chat_model(
        f"{config.provider}:{config.model_name}",
        api_key=config.api_key or os.getenv("SILICONFLOW_API_KEY"),
        base_url=config.api_url,
        streaming=config.streaming
    )
```

**提示词外部化管理**:
```
agent-backend/text2sql/
└── prompts/
    ├── __init__.py
    ├── supervisor.md        # 监督代理提示词
    ├── schema_agent.md      # Schema分析提示词
    ├── sql_generator.md     # SQL生成提示词
    ├── sql_validator.md     # SQL验证提示词
    ├── sql_executor.md      # SQL执行提示词
    ├── error_recovery.md    # 错误恢复提示词
    └── chart_generator.md   # 图表生成提示词

# prompts/loader.py - 提示词加载器
from pathlib import Path
from functools import lru_cache

PROMPTS_DIR = Path(__file__).parent / "prompts"

@lru_cache(maxsize=32)
def load_prompt(name: str, **kwargs) -> str:
    """动态加载并格式化提示词"""
    prompt_file = PROMPTS_DIR / f"{name}.md"
    template = prompt_file.read_text(encoding="utf-8")
    return template.format(**kwargs) if kwargs else template
```

**理由**:
- 动态模型支持运行时切换不同提供商
- 提示词Markdown文件便于维护和版本控制
- LRU缓存避免重复读取文件
- 支持变量替换实现动态提示词

**实现参考**: `agent-backend/examples/utils.py` 中的 `init_chat_model` 函数

### Decision 2: 采用LangGraph多代理架构

**选择**: 使用LangGraph最新版本的`create_react_agent`和`langgraph-supervisor`实现多代理系统

**核心API** (参考 https://docs.langchain.com/oss/python/langgraph/overview):
```python
# 安装依赖
pip install langgraph langgraph-supervisor langgraph-checkpoint-sqlite

# 创建ReAct代理
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model

# 创建专门化代理
schema_agent = create_react_agent(
    model=model,
    tools=[get_schema, get_tables],
    name="schema_expert",
    prompt="You are a database schema expert..."
)

sql_agent = create_react_agent(
    model=model,
    tools=[generate_sql, validate_sql],
    name="sql_expert",
    prompt="You are a SQL generation expert..."
)

# 创建Supervisor协调多代理
workflow = create_supervisor(
    agents=[schema_agent, sql_agent, executor_agent, chart_agent],
    model=model,
    prompt="You are a supervisor coordinating SQL query workflow..."
)

app = workflow.compile(checkpointer=checkpointer, store=store)
```

**理由**:
- LangGraph提供成熟的状态管理和流程控制
- `create_supervisor`支持自动handoff工具生成
- 支持条件路由和错误恢复
- 代理间通信机制清晰
- 易于扩展和测试

**Alternatives considered**:
- 单一大型代理：灵活性不足，难以维护
- 传统规则引擎：无法处理复杂自然语言
- 纯LangChain链式调用：状态管理复杂

### Decision 3: 七代理分工模式

**选择**: 将系统分为7个专门化代理

| 代理 | 职责 |
|------|------|
| Supervisor | 工作流协调、路由决策 |
| Schema | 查询分析、模式检索 |
| SQL Generator | SQL生成、查询优化 |
| SQL Validator | 语法检查、安全扫描 |
| SQL Executor | 安全执行、结果处理 |
| Error Recovery | 错误分析、自动修复 |
| Chart Generator | 数据可视化、图表生成（MCP） |

**理由**:
- 单一职责原则，便于测试和维护
- 可独立优化和扩展各代理
- 故障隔离，一个代理失败不影响其他代理

### Decision 4: 状态驱动的工作流

**选择**: 使用`SQLMessageState`管理整个查询生命周期状态

```python
class SQLMessageState(MessagesState):
    connection_id: int
    query_analysis: Optional[Dict[str, Any]]
    schema_info: Optional[SchemaInfo]
    generated_sql: Optional[str]
    validation_result: Optional[SQLValidationResult]
    execution_result: Optional[SQLExecutionResult]
    chart_result: Optional[ChartResult]  # 图表生成结果
    retry_count: int
    current_stage: Literal[...]
    error_history: List[Dict[str, Any]]
```

**理由**:
- 清晰的状态追踪
- 支持重试和恢复
- 便于调试和日志记录

### Decision 5: 双层记忆系统

**选择**: 实现短期记忆 + 长期记忆的双层架构

```python
# 短期记忆 - 会话上下文 (LangGraph最新API)
from langgraph.checkpoint.sqlite import SqliteSaver

# 使用from_conn_string创建（推荐）
checkpointer = SqliteSaver.from_conn_string("agent-backend/data/agent_memory.db")
# 首次使用需要setup
checkpointer.setup()

# 长期记忆 - 知识存储
from langgraph.store.memory import InMemoryStore
# 生产环境可使用PostgresStore
from langgraph.store.postgres import PostgresStore

store = InMemoryStore()  # 或 PostgresStore.from_conn_string(DB_URI)

# 编译图时传入checkpointer和store
app = workflow.compile(
    checkpointer=checkpointer,
    store=store
)

# 调用时指定thread_id和user_id
config = {
    "configurable": {
        "thread_id": "conversation-1",
        "user_id": "user-123"
    }
}
result = app.invoke({"messages": [...]}, config)
```

**短期记忆 (Checkpointer)**:
- 存储当前会话的对话历史
- 支持中断恢复和回滚 (time-travel debugging)
- 按thread_id隔离不同会话
- 支持`get_state_history`获取历史状态

**长期记忆 (Store)**:
- 存储Schema信息缓存
- 保存常用查询模式
- 维护用户偏好设置
- 支持语义搜索 `store.search(namespace, query=...)`

**数据库路径**: `agent-backend/data/agent_memory.db`

**理由**:
- 短期记忆保证对话连贯性
- 长期记忆避免重复查询Schema
- SQLite轻量级，无需额外服务
- 生产环境可无缝切换到PostgreSQL

### Decision 6: 多数据库统一接口

**选择**: 使用DatabaseManager封装所有数据库操作

**支持的数据库**:
- MySQL / MariaDB
- PostgreSQL
- SQLite
- Oracle
- Snowflake
- BigQuery
- ClickHouse
- DuckDB

**理由**:
- 抽象层隐藏数据库差异
- 统一的连接池管理
- 便于添加新数据库支持

### Decision 7: 实时流式查询与分页

**选择**: 支持流式输出和大数据集分页展示

**流式查询实现**:
```python
# 使用LangGraph stream_mode实现流式输出
async def stream_sql_query(user_query: str, config: dict):
    """流式处理SQL查询，实时返回结果"""
    async for chunk in app.astream(
        {"messages": [{"role": "user", "content": user_query}]},
        config,
        stream_mode="messages"  # 或 "values", "updates"
    ):
        yield chunk

# FastAPI流式响应
from fastapi.responses import StreamingResponse

@app.post("/query/stream")
async def stream_query(request: QueryRequest):
    async def generate():
        async for chunk in stream_sql_query(request.query, config):
            yield f"data: {json.dumps(chunk)}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
```

**分页查询实现**:
```python
@dataclass
class PaginationConfig:
    page: int = 1
    page_size: int = 100
    max_page_size: int = 1000

class SQLExecutionResult:
    data: List[Dict]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

# SQL自动添加分页
def add_pagination(sql: str, pagination: PaginationConfig) -> str:
    offset = (pagination.page - 1) * pagination.page_size
    return f"{sql} LIMIT {pagination.page_size} OFFSET {offset}"
```

**理由**:
- 流式输出提升用户体验，无需等待完整响应
- 分页避免一次性加载大量数据导致内存溢出
- 支持SSE(Server-Sent Events)实现前端实时更新

### Decision 8: 上下文管理与防爆策略

**选择**: 实现多层上下文压缩和管理机制

**上下文爆炸问题解决方案**:
```python
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import trim_messages

# 策略1: 消息裁剪 - 保留最近N条
def trim_context(messages: List, max_messages: int = 20):
    """保留最近的消息，防止上下文过长"""
    return trim_messages(
        messages,
        max_tokens=8000,  # 根据模型上下文窗口设置
        strategy="last",  # 保留最后的消息
        token_counter=len,  # 或使用tiktoken精确计数
        include_system=True,
        allow_partial=False
    )

# 策略2: 对话摘要 - 压缩历史
class ContextManager:
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.summary_model = get_model()
    
    async def compress_history(self, messages: List) -> List:
        """当上下文过长时，压缩历史消息为摘要"""
        if self._count_tokens(messages) > self.max_tokens:
            # 保留最近5条，其余压缩为摘要
            recent = messages[-5:]
            old = messages[:-5]
            summary = await self._summarize(old)
            return [{"role": "system", "content": f"历史摘要: {summary}"}] + recent
        return messages

# 策略3: Schema信息压缩
def compress_schema_info(schema: SchemaInfo, query_context: str) -> str:
    """只保留与查询相关的表和列信息"""
    relevant_tables = extract_relevant_tables(query_context, schema)
    return format_compressed_schema(relevant_tables)

# 策略4: 结果集压缩
def compress_results(results: List[Dict], max_rows: int = 50) -> str:
    """压缩大结果集，只保留样本和统计信息"""
    if len(results) > max_rows:
        return {
            "sample": results[:10],
            "total_count": len(results),
            "summary": f"共{len(results)}条记录，显示前10条"
        }
    return results
```

**理由**:
- 多层压缩策略适应不同场景
- 保留关键信息同时控制token用量
- Schema压缩减少无关表信息干扰

### Decision 9: 基于LangGraph API服务部署

**选择**: 使用LangGraph API服务进行部署，支持二次开发扩展

**参考文档**: https://docs.langchain.com/oss/python/langgraph/local-server

**langgraph.json配置**:
```json
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": ["."],
  "graphs": {
    "text2sql_agent": "./text2sql/chat_graph.py:app",
    "text2sql_stream": "./text2sql/chat_graph.py:stream_app"
  },
  "env": ".env",
  "python_version": "3.11"
}
```

**启动服务**:
```bash
# 开发模式 (支持热重载)
cd agent-backend
langgraph dev --port 2024

# 生产模式
langgraph up --port 8123
```

**API端点**:
```bash
# 流式查询
curl -s --request POST \
  --url "http://localhost:2024/runs/stream" \
  --header 'Content-Type: application/json' \
  --data '{
    "assistant_id": "text2sql_agent",
    "input": {
      "messages": [{"role": "human", "content": "查询所有客户"}]
    },
    "stream_mode": "messages-tuple"
  }'

# Python SDK调用
from langgraph_sdk import get_sync_client

client = get_sync_client(url="http://localhost:2024")
for chunk in client.runs.stream(
    None,  # Threadless run
    "text2sql_agent",
    input={"messages": [{"role": "human", "content": "查询所有客户"}]},
    stream_mode="messages-tuple",
):
    print(chunk.data)
```

**二次开发扩展**:
```python
# text2sql/server.py - 自定义服务扩展
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from langgraph_sdk import get_client

app = FastAPI(title="Text2SQL API")

# 集成LangGraph客户端
lg_client = get_client(url="http://localhost:2024")

@app.post("/api/v1/query")
async def query(request: Request):
    """自定义查询接口，封装LangGraph API"""
    data = await request.json()
    
    # 添加分页、鉴权等自定义逻辑
    pagination = data.get("pagination", {"page": 1, "page_size": 100})
    
    async def generate():
        async for chunk in lg_client.runs.stream(
            data.get("thread_id"),
            "text2sql_agent",
            input={"messages": data["messages"], "pagination": pagination},
            stream_mode="messages-tuple",
            config={"configurable": data.get("config", {})}
        ):
            yield f"data: {json.dumps(chunk.data)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/v1/query/sync")
async def query_sync(request: Request):
    """同步查询接口，返回完整结果"""
    data = await request.json()
    result = await lg_client.runs.wait(
        data.get("thread_id"),
        "text2sql_agent",
        input={"messages": data["messages"]}
    )
    return result
```

**理由**:
- LangGraph API提供标准化的服务端点
- 支持开发模式热重载
- 可通过二次开发添加自定义功能
- 支持LangGraph Studio调试

### Decision 10: 高并发架构

**选择**: 采用异步架构 + 连接池 + 限流机制

**并发控制实现**:
```python
import asyncio
from asyncio import Semaphore
from contextlib import asynccontextmanager

# 1. 全局并发限制
class ConcurrencyManager:
    def __init__(self, max_concurrent: int = 100):
        self.semaphore = Semaphore(max_concurrent)
        self.active_requests = 0
    
    @asynccontextmanager
    async def acquire(self):
        async with self.semaphore:
            self.active_requests += 1
            try:
                yield
            finally:
                self.active_requests -= 1

# 2. 数据库连接池
from sqlalchemy.pool import QueuePool

class DatabaseManager:
    def __init__(self, pool_size: int = 20, max_overflow: int = 10):
        self.engine = create_engine(
            db_url,
            poolclass=QueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_timeout=30,
            pool_recycle=3600
        )

# 3. LLM请求限流
from aiolimiter import AsyncLimiter

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.limiter = AsyncLimiter(requests_per_minute, 60)
    
    async def acquire(self):
        await self.limiter.acquire()

# 4. 请求队列（可选，用于峰值削峰）
from asyncio import Queue

class RequestQueue:
    def __init__(self, max_size: int = 1000):
        self.queue = Queue(maxsize=max_size)
        self.workers = []
    
    async def start_workers(self, num_workers: int = 10):
        for _ in range(num_workers):
            worker = asyncio.create_task(self._worker())
            self.workers.append(worker)
```

**架构图**:
```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐          ┌─────────┐          ┌─────────┐
   │ Worker1 │          │ Worker2 │          │ Worker3 │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────┴────────┐
                    │ Connection Pool │
                    │   (20 + 10)     │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │    Database     │
                    └─────────────────┘
```

**理由**:
- 异步架构充分利用IO等待时间
- 连接池复用减少连接开销
- 限流保护下游服务和API配额
- 支持水平扩展

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Input (Natural Language)            │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                         │
│              (Workflow Coordination & Routing)              │
└─────────────────────────────────────────────────────────────┘
        │           │           │           │           │
        ▼           ▼           ▼           ▼           ▼
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │ Schema  │ │   SQL   │ │   SQL   │ │   SQL   │ │  Error  │ │  Chart  │
   │  Agent  │ │Generator│ │Validator│ │Executor │ │Recovery │ │Generator│
   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
        │           │           │           │           │
        └───────────┴───────────┴───────────┴───────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database Manager                          │
│         (Multi-DB Support: MySQL, PostgreSQL, etc.)          │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Stages

```
START
  │
  ▼
┌──────────────────┐
│  schema_analysis │ ◄──────────────────────┐
└──────────────────┘                        │
  │                                         │
  ▼                                         │
┌──────────────────┐                        │
│  sql_generation  │                        │
└──────────────────┘                        │
  │                                         │
  ▼                                         │
┌──────────────────┐     validation_failed  │
│  sql_validation  │ ──────────────────────►│
└──────────────────┘                        │
  │ validation_passed                       │
  ▼                                         │
┌──────────────────┐     execution_failed   │
│  sql_execution   │ ──────────────────────►│
└──────────────────┘                        │
  │ execution_success                       │
  ▼                                         │
┌──────────────────┐                        │
│   error_recovery │ ◄──────────────────────┘
└──────────────────┘  (if retry_count < max)
  │
  ▼
 END
```

## Risks / Trade-offs

### Risk 1: LLM响应质量不稳定
- **风险**: 大语言模型可能生成错误或低效的SQL
- **缓解**: 多层验证机制 + 自动重试 + 错误恢复代理

### Risk 2: 数据库连接性能
- **风险**: 频繁连接可能影响性能
- **缓解**: 连接池管理 + 查询超时控制

### Risk 3: 安全性风险
- **风险**: SQL注入、未授权访问
- **缓解**: 多层安全验证 + 关键字过滤 + 权限控制

### Risk 4: 复杂查询准确性
- **风险**: 多表关联、嵌套子查询可能不准确
- **缓解**: Schema信息增强 + 示例学习 + 用户确认机制

### Risk 5: 上下文爆炸
- **风险**: 长对话导致token超限，影响模型质量
- **缓解**: 多层压缩策略 + 消息裁剪 + Schema信息筛选

### Risk 6: 高并发性能瓶颈
- **风险**: 大量并发请求导致系统过载
- **缓解**: 连接池 + 限流 + 异步架构 + 请求队列

## File Structure

```
agent-backend/text2sql/
├── __init__.py
├── config.py                  # LLM和系统配置（动态模型）
├── chat_graph.py              # 主图工作流
├── state.py                   # 状态定义
├── prompts/                   # 提示词文件（外部化管理）
│   ├── __init__.py
│   ├── loader.py              # 提示词加载器
│   ├── supervisor.md          # 监督代理提示词
│   ├── schema_agent.md        # Schema分析提示词
│   ├── sql_generator.md       # SQL生成提示词
│   ├── sql_validator.md       # SQL验证提示词
│   ├── sql_executor.md        # SQL执行提示词
│   ├── error_recovery.md      # 错误恢复提示词
│   └── chart_generator.md     # 图表生成提示词
├── memory/
│   ├── __init__.py
│   ├── checkpointer.py        # 短期记忆 (SqliteSaver)
│   ├── store.py               # 长期记忆 (SqliteStore)
│   └── manager.py             # 记忆统一管理器
├── context/                   # 上下文管理
│   ├── __init__.py
│   ├── trimmer.py             # 消息裁剪器
│   ├── compressor.py          # 上下文压缩器
│   └── manager.py             # 上下文管理器
├── concurrency/               # 并发控制
│   ├── __init__.py
│   ├── limiter.py             # 限流器
│   ├── pool.py                # 连接池管理
│   └── queue.py               # 请求队列
├── agents/
│   ├── __init__.py
│   ├── supervisor_agent.py    # 监督代理
│   ├── schema_agent.py        # Schema分析代理
│   ├── sql_generator_agent.py # SQL生成代理
│   ├── sql_validator_agent.py # SQL验证代理
│   ├── sql_executor_agent.py  # SQL执行代理
│   ├── error_recovery_agent.py# 错误恢复代理
│   └── chart_generator_agent.py # 图表生成代理 (MCP)
├── database/
│   ├── __init__.py
│   ├── db_manager.py          # 数据库管理器
│   └── pagination.py          # 分页处理
├── streaming/                 # 流式处理
│   ├── __init__.py
│   ├── handler.py             # 流式响应处理
│   └── sse.py                 # SSE事件流
├── tools/
│   ├── __init__.py
│   ├── schema_tools.py        # Schema相关工具
│   ├── sql_tools.py           # SQL相关工具
│   ├── validation_tools.py    # 验证工具
│   └── chart_tools.py         # 图表生成工具 (mcp-server-chart)
├── models/
│   ├── __init__.py
│   ├── schema_models.py       # Schema数据模型
│   ├── result_models.py       # 结果数据模型
│   └── pagination_models.py   # 分页数据模型
├── api/                       # API层（二次开发）
│   ├── __init__.py
│   ├── routes.py              # API路由
│   ├── schemas.py             # 请求/响应模型
│   └── server.py              # 自定义FastAPI服务器
└── tests/
    ├── __init__.py
    ├── test_agents.py
    ├── test_graph.py
    ├── test_streaming.py
    ├── test_concurrency.py
    └── demo_intelligent_sql.py
```

## Migration Plan

### Phase 1: 基础架构 (Week 1)
1. 创建项目目录结构
2. 实现状态管理类
3. 实现数据库管理器

### Phase 2: 代理实现 (Week 2)
1. 实现各个专门化代理
2. 创建代理工具函数
3. 单元测试

### Phase 3: 工作流集成 (Week 3)
1. 实现图工作流
2. 集成所有代理
3. 端到端测试

### Phase 4: 优化与文档 (Week 4)
1. 性能优化
2. 安全加固
3. 文档完善

## Open Questions

1. **查询结果缓存策略**: 是否需要实现查询结果缓存？缓存过期策略如何设计？
2. **用户确认机制**: 对于高风险操作（如UPDATE/DELETE），是否需要用户二次确认？
3. **多语言支持**: 自然语言查询是否需要支持英语以外的语言？
4. **并发控制**: 如何处理同一连接的并发查询请求？
