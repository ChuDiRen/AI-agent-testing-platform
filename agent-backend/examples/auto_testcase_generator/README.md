# 自动测试用例生成器 V3

基于 LangGraph 1.0 + 多智能体协作 + middlewareV1 上下文工程

## 核心特性

- ✅ **4个专家智能体**: Analyzer(需求分析) + TestPointDesigner(测试点设计) + Writer(用例编写) + Reviewer(用例评审)
- ✅ **Supervisor协调者**: 自动调度智能体执行顺序,支持迭代优化
- ✅ **middlewareV1集成**: 消息过滤、状态同步、动态提示词注入
- ✅ **人工审核点**: 可选在关键步骤暂停等待人工确认
- ✅ **持久化存储**: 自动保存生成历史到SQLite数据库
- ✅ **LangGraph 1.0**: 使用最新 `create_agent` API
- ✅ **Python高级语法**: Type Hints、Dataclass、Async/Await

## 安装

```bash
pip install langchain langgraph langchain-openai requests python-docx pypdf
```

## 使用

### 1. 运行脚本（推荐）

```bash
cd examples/auto_testcase_generator

# 文本输入演示（默认）
python run.py

# Swagger批量生成
python run.py swagger

# 文档生成
python run.py document
```

### 2. Python API

```python
import asyncio
from auto_testcase_generator import generator

# 文本生成
async def main():
    result = await generator.generate("用户登录接口需求...")
    print(result.testcases)

# Swagger批量生成
    results = await generator.batch_generate_from_swagger(
        "https://petstore.swagger.io/v2/swagger.json",
        max_apis=10
    )
    for r in results:
        print(r.testcases)

# 文档生成
    result = await generator.generate_from_document("requirements.txt")
    print(result.testcases)

asyncio.run(main())
```

## 架构设计

### 多智能体协作流程

```
                    ┌──────────────────┐
                    │   Supervisor     │  ← 协调者
                    │  (调度执行顺序)   │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┬──────────────┐
        ↓                    ↓                    ↓              ↓
   ┌─────────┐        ┌──────────┐        ┌─────────┐    ┌──────────┐
   │Analyzer │        │TestPoint │        │ Writer  │    │Reviewer  │
   │ 需求分析 │───────▶│Designer  │───────▶│用例编写 │───▶│用例评审  │
   └─────────┘        │测试点设计│        └─────────┘    └──────────┘
                      └──────────┘              │              │
                                                │              │
                                                └──────┬───────┘
                                                       │
                                                  评审通过?
                                                   │    │
                                                  是    否
                                                   │    │
                                                  完成  ↓
                                                     重新生成
```

### middlewareV1 上下文工程

每个智能体都应用了不同的消息过滤策略:

| 智能体 | 保留消息 | 说明 |
|--------|---------|------|
| Analyzer | H=1, A=0 | 只保留最新的需求输入 |
| TestPointDesigner | H=2, A=1 | 保留需求+分析结果 |
| Writer | H=2, A=2 | 保留测试点+历史用例 |
| Reviewer | H=3, A=3 | 保留完整上下文 |

**中间件功能:**
- 🔹 **MessageFilter**: 过滤消息历史,减少token消耗
- 🔹 **StateSync**: 自动同步AI输出到状态
- 🔹 **DynamicPrompt**: 动态注入上下文到系统提示词
- 🔹 **HumanInTheLoop**: 人工审核中间件

## 文件结构

```
auto_testcase_generator/
├── __init__.py              # 模块导出
├── run.py                   # 演示脚本
├── config.py                # 配置管理
├── models.py                # 数据模型 (TestCaseState)
├── database.py              # SQLite持久化
├── generator.py             # 核心生成器 (V3版本)
├── supervisor.py            # Supervisor协调者
├── agents/                  # 4个专家智能体
│   ├── analyzer_agent.py           # 需求分析智能体
│   ├── test_point_designer_agent.py # 测试点设计智能体
│   ├── writer_agent.py             # 用例编写智能体
│   └── reviewer_agent.py           # 用例评审智能体
├── middleware/              # middlewareV1实现
│   ├── config.py                   # 过滤配置
│   ├── message_filter.py           # 消息过滤
│   ├── state_sync.py               # 状态同步
│   ├── context_manager.py          # 上下文管理器
│   └── adapters.py                 # 中间件适配器
└── prompts/                 # 提示词模板
    ├── TESTCASE_READER_SYSTEM_MESSAGE.txt
    ├── TESTCASE_TEST_POINT_DESIGNER_SYSTEM_MESSAGE.txt
    ├── TESTCASE_WRITER_SYSTEM_MESSAGE_ORIGINAL.txt
    └── TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt
```

## 配置选项

### 环境变量

```bash
export SILICONFLOW_API_KEY=sk-your-key
```

### 生成器配置

```python
from auto_testcase_generator import TestCaseGeneratorV3

generator = TestCaseGeneratorV3(
    enable_middleware=True,      # 启用 middlewareV1 (推荐)
    enable_human_review=False,   # 启用人工审核 (可选)
    enable_persistence=True,     # 启用持久化存储 (推荐)
)
```

## 数据库

生成历史自动保存到 `testcases.db` (SQLite):

```sql
CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY,
    thread_id TEXT,
    requirement TEXT,
    test_type TEXT,
    analysis TEXT,
    testcases TEXT,
    review TEXT,
    iteration INTEGER,
    created_at TIMESTAMP
);
```

查询历史记录:

```python
from auto_testcase_generator.database import TestCaseDB
from pathlib import Path

db = TestCaseDB(Path("testcases.db"))
recent = db.list_recent(limit=10)  # 最近10条记录
```

