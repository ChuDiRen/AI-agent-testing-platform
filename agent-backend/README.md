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
DATABASE_URI=sqlite:///sqlite_storage/data/langgraph_server.db
DEEPSEEK_API_KEY=your-api-key
REDIS_URI=fake
LANGGRAPH_RUNTIME_EDITION=community
```

### 3. 启动服务

```bash
python unified_server.py
```

**特点：**
- ✅ 完美支持自定义长期记忆和短期记忆
- ✅ 数据持久化到 SQLite (data/agent_memory.db)
- ✅ 启动时自动健康检查和诊断
- ✅ 不依赖 Monkey Patch，更稳定

**访问地址：**
- API Server: http://localhost:2025
- API 文档: http://localhost:2025/docs
- Studio UI: http://localhost:2025/ui

**命令参数：**
```bash
python unified_server.py          # 开发模式（默认）
python unified_server.py prod     # 生产模式
python unified_server.py --port 8080  # 自定义端口
```

#### 方式 2: 运行具体示例

```bash
# SQL Agent
python examples/sql_agent.py

# API Agent
python examples/api_agent.py

# 自动测试用例生成器 ⭐
cd examples/auto_testcase_generator
python run.py              # 文本输入演示
python run.py swagger      # Swagger批量生成
python run.py document     # 文档生成
```

---

## 📊 可用的 Agent

| Agent | 文件 | 功能 |
|-------|------|------|
| sql_agent | examples/sql_agent.py | SQL 数据库查询 |
| api_agent | examples/api_agent.py | RESTful API 调用 |
| **auto_testcase_generator** | **examples/auto_testcase_generator/** | **自动测试用例生成器（双模型协作）** ⭐ |

---

## 🌟 推荐：Auto Testcase Generator

### 特性

- ✅ **双模型协作**: Reader(分析) + Writer(生成) + Reviewer(审查)
- ✅ **Swagger 支持**: 一键解析 Swagger/OpenAPI 并批量生成
- ✅ **文档解析**: 支持 TXT/Word/PDF 需求文档
- ✅ **业务场景识别**: 自动识别 CRUD 完整流程
- ✅ **Python 高级语法**: Type Hints、Dataclass、Async/Await
- ✅ **数据持久化**: SQLite + Checkpoint 双重存储

### 快速开始

```python
import asyncio
from examples.auto_testcase_generator import generator

# 文本生成
async def main():
    result = await generator.generate("用户登录接口需求...")
    print(result.testcases)
    
    # Swagger批量生成
    results = await generator.batch_generate_from_swagger(
        "https://petstore.swagger.io/v2/swagger.json",
        max_apis=10
    )
    
    # 文档生成
    result = await generator.generate_from_document("requirements.txt")

asyncio.run(main())
```

### 核心逻辑（参考 AutoGenTestCase）

```
需求输入
   ↓
1. Reader 分析需求 (deepseek-chat)
   ↓
2. Writer 生成用例 (deepseek-reasoner)
   ↓
3. Reviewer 审查质量 (deepseek-chat)
   ↓
   判断：需要改进? → 返回步骤2
   ↓
输出最终测试用例
```

详细说明：[examples/auto_testcase_generator/README.md](examples/auto_testcase_generator/README.md)

---

## 📝 配置文件

### langgraph.json

```json
{
  "graphs": {
    "sql_agent": "./examples/sql_agent.py:agent_old",
    "api_agent": "./examples/api_agent.py:agent_auto",
    "testcase_generator": "./examples/testcase_generator.py:create_testcase_generator_graph"
  },
  "env": ".env"
}
```

---

## 🗄️ 持久化说明

| 运行方式 | 持久化 | 数据库文件 |
|---------|--------|-----------|
| `python agent-backend_run.py` ⭐ | **SQLite 完全持久化** | `sqlite_storage/data/` |
| `python examples/xxx.py` | SQLite | `sqlite_storage/data/hitl_checkpoints.db` |
| `auto_testcase_generator` | SQLite + Store | `checkpoints.db` + InMemoryStore |

**重要说明**：
- ✅ `agent-backend_run.py` 使用社区版 `langgraph dev` 命令
- ✅ 无需 Docker、PostgreSQL、Redis、License Key
- ✅ 数据完全持久化到 SQLite

详细配置说明：[README_NEW_STARTUP.md](README_NEW_STARTUP.md)

---

## ✅ 推荐用法

- **API 服务器（持久化）**：`python agent-backend_run.py` ⭐
- **测试用例生成**：使用 Python API 调用 `generator.generate()`
- **直接运行示例**：`python examples/sql_agent.py`

---

## 🔗 相关文档

- [LangChain Tools 文档](https://docs.langchain.com/oss/python/langchain/tools)
- [LangGraph 文档](https://docs.langgraph.com)
- [Auto Testcase Generator 详细文档](examples/auto_testcase_generator/README.md)

---
