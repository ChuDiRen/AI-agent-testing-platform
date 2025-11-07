# Agent Backend - LangGraph

基于 LangGraph 的 AI Agent 后端服务。

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

`.env` 文件已配置：
```bash
LANGGRAPH_SQLITE_URI=sqlite:///checkpoints.db
DEEPSEEK_API_KEY=your-api-key
```

### 3. 运行方式

#### 方式 1: 开发调试（内存持久化）

```bash
langgraph dev
```

- 访问：http://localhost:2024
- 特点：快速启动，重启后数据丢失

#### 方式 2: SQLite 持久化（推荐测试）

```bash
# 运行 SQL Agent
python examples/sql_agent.py

# 运行 API Agent  
python examples/api_agent.py
```

- 特点：数据永久保存到 `examples/checkpoints.db`

---

## 📊 可用的 Agent

| Agent | 文件 | 功能 |
|-------|------|------|
| sql_agent | examples/sql_agent.py | SQL 数据库查询 |
| sql_agent_graph | examples/sql_agent_graph.py | SQL Agent（Graph 版） |
| api_agent | examples/api_agent.py | RESTful API 调用 |

---

## 📝 配置文件

### langgraph.json
```json
{
  "graphs": {
    "sql_agent": "./examples/sql_agent.py:agent_old",
    "sql_agent_graph": "./examples/sql_agent_graph.py:agent_old",
    "api_agent": "./examples/api_agent.py:agent_auto"
  },
  "env": ".env"
}
```

---

## 🗄️ 持久化说明

| 运行方式 | 持久化 | 数据库文件 |
|---------|--------|-----------|
| `langgraph dev` | 内存 | 无（重启丢失） |
| `python examples/xxx.py` | SQLite | `examples/checkpoints.db` |

---

## ✅ 推荐用法

- **快速测试 UI**：`langgraph dev`
- **测试持久化**：`python examples/sql_agent.py`
