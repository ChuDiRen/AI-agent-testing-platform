# 自动测试用例生成器

核心逻辑参考: 
- [AutoGenTestCase](https://github.com/13429837441/AutoGenTestCase) - 双模型协作
- [LangGraph 并行执行](https://docs.langchain.com/oss/python/langgraph/workflows-agents) - 并行生成

## 特性

- ✅ 双模型协作: Reader(分析) + Writer(生成) + Reviewer(审查)
- ✅ Python高级语法: Type Hints、Dataclass、Cached Property、LRU Cache
- ✅ 并行执行: 参考LangGraph模式，多接口同时生成（asyncio.gather）
- ✅ 三种输入: 文本、Swagger、文档(TXT/Word/PDF)

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

## 架构

### 单个用例生成流程

```
需求输入
   ↓
Reader (deepseek-chat) - 快速分析需求
   ↓
Writer (deepseek-reasoner) - 深度思考生成
   ↓
Reviewer (deepseek-chat) - 快速审查
   ↓
判断是否需要改进 → 是: 返回Writer / 否: 完成
```

### 批量并行生成（Swagger）

参考 [LangGraph Parallelization](https://docs.langchain.com/oss/python/langgraph/workflows-agents#parallelization) 原理，使用 `asyncio.gather` 实现：

```python
# 类似LangGraph中从START并行启动多个节点
tasks = [generate(endpoint1), generate(endpoint2), generate(endpoint3)]

# 所有任务并行执行
results = await asyncio.gather(*tasks)
```

对应的LangGraph概念：
```
                    START
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
    endpoint1     endpoint2     endpoint3  (并行生成)
        ↓             ↓             ↓
        └─────────────┼─────────────┘
                      ↓
                 聚合结果
```

## Python高级特性

- `@dataclass(frozen=True)` - 不可变配置类
- `@cached_property` - 缓存属性（懒加载模型）
- `@lru_cache` - LRU缓存（Swagger解析）
- `@contextmanager` - 上下文管理器（数据库连接）
- Type Hints - 完整类型注解
- Async/Await - 异步编程
- List Comprehension - 列表推导式
- Generator Expression - 生成器表达式

## 文件结构

```
auto_testcase_generator/
├── __init__.py       # 模块导出
├── run.py            # 运行脚本（演示）
├── config.py         # 配置管理（cached_property）
├── models.py         # 数据模型（Dataclass）
├── parsers.py        # 解析器（lru_cache）
├── database.py       # 数据库（contextmanager）
├── generator.py      # 核心生成器（AsyncIO）
└── prompts/          # 提示词模板
    ├── TESTCASE_READER_SYSTEM_MESSAGE.txt
    ├── TESTCASE_WRITER_SYSTEM_MESSAGE.txt
    └── TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt
```

## 配置

在 `config.py` 中设置或通过环境变量:

```bash
export DEEPSEEK_API_KEY=sk-your-key
```

