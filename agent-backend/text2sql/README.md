# Text2SQL - 智能自然语言到SQL转换系统

基于LangGraph的多代理架构实现，支持自然语言查询转SQL、多数据库、流式输出和图表可视化。

## 特性

- 🤖 **多代理架构**: 7个专门化代理协作处理查询
- 🗄️ **多数据库支持**: MySQL, PostgreSQL, SQLite, Oracle等
- 💾 **双层记忆系统**: 短期会话记忆 + 长期知识存储
- 🔄 **流式输出**: SSE实时响应
- 📊 **图表生成**: 自动数据可视化
- 🛡️ **安全验证**: 多层SQL安全检查
- 🔧 **自动修复**: 智能错误恢复

## 快速开始

### 安装依赖

```bash
pip install -r text2sql/requirements.txt
```

### 启动LangGraph开发服务

```bash
cd agent-backend
langgraph dev --port 2024
```

### 启动自定义API服务

```bash
python -m text2sql.api.server
```

## 使用方法

### 1. Python SDK

```python
from text2sql.chat_graph import process_sql_query

# 同步查询
result = await process_sql_query(
    query="查询所有用户",
    connection_id=0,
    thread_id="session-1"
)

# 流式查询
async for chunk in stream_sql_query("统计每个部门人数"):
    print(chunk)
```

### 2. REST API

```bash
# 执行查询
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "查询所有用户", "connection_id": 0}'

# 流式查询
curl -X POST http://localhost:8000/api/v1/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "查询所有用户", "stream": true}'
```

### 3. LangGraph API

```bash
# 使用LangGraph SDK
curl -s --request POST \
  --url "http://localhost:2024/runs/stream" \
  --header 'Content-Type: application/json' \
  --data '{
    "assistant_id": "text2sql_agent",
    "input": {
      "messages": [{"role": "human", "content": "查询所有用户"}]
    },
    "stream_mode": "messages-tuple"
  }'
```

## 项目结构

```
text2sql/
├── __init__.py
├── config.py              # 配置管理
├── state.py               # 状态定义
├── chat_graph.py          # 主图工作流
├── prompts/               # 提示词文件
├── memory/                # 记忆系统
├── context/               # 上下文管理
├── agents/                # 代理实现
├── database/              # 数据库管理
├── tools/                 # 工具函数
├── streaming/             # 流式处理
├── concurrency/           # 并发控制
├── api/                   # API层
└── tests/                 # 测试
```

## 配置

### 环境变量

```bash
# LLM配置
SILICONFLOW_API_KEY=your_api_key

# 数据库
DATABASE_URL=mysql://user:pass@localhost/db
```

### LLM配置

```python
from text2sql.config import LLMConfig, get_model

config = LLMConfig(
    provider="siliconflow",
    model_name="deepseek-ai/DeepSeek-V3",
    streaming=True
)

model = get_model(config)
```

## 代理架构

| 代理 | 职责 |
|------|------|
| Supervisor | 工作流协调、路由决策 |
| Schema Agent | 查询分析、Schema检索 |
| SQL Generator | SQL生成、查询优化 |
| SQL Validator | 语法检查、安全扫描 |
| SQL Executor | 安全执行、结果处理 |
| Error Recovery | 错误分析、自动修复 |
| Chart Generator | 数据可视化 |

## 测试

```bash
# 运行演示
python -m text2sql.tests.demo_intelligent_sql

# 运行测试
pytest text2sql/tests/ -v
```

## License

MIT
