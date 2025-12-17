# LangGraph 模块架构说明

## 目录结构

```
langgraph/
├── core/                    # 核心抽象层
│   ├── __init__.py
│   ├── base_state.py        # 统一State基类和工具函数
│   ├── base_graph.py        # Graph构建器基类
│   ├── model_factory.py     # 模型工厂（统一管理LLM实例）
│   └── node_registry.py     # 节点注册器（支持装饰器注册）
│
├── tasks/                   # 任务实现
│   ├── __init__.py
│   ├── base_task.py         # 任务基类
│   ├── registry.py          # 任务注册表
│   ├── text2case/           # 测试用例生成（多智能体协作）
│   │   ├── __init__.py
│   │   ├── multi_agent_state.py   # 状态定义
│   │   ├── multi_agent_graph.py   # Graph构建器
│   │   ├── multi_agent_task.py    # Task执行类
│   │   ├── prompts/         # 提示词模板
│   │   │   ├── __init__.py  # 提示词加载器
│   │   │   ├── supervisor.txt
│   │   │   ├── analyzer.txt
│   │   │   ├── designer.txt
│   │   │   ├── writer.txt
│   │   │   └── reviewer.txt
│   │   └── agents/          # 智能体实现
│   │       ├── base.py      # 智能体基类（含重试、回调、Token统计）
│   │       ├── supervisor.py # 协调者
│   │       ├── analyzer.py  # 需求分析专家
│   │       ├── designer.py  # 测试点设计专家
│   │       ├── writer.py    # 用例编写专家
│   │       └── reviewer.py  # 用例评审专家
│   ├── text2sql/            # SQL生成
│   │   └── ...
│   └── text2api/            # API请求生成
│       └── ...
│
├── graphs/                  # Graph导出（供langgraph dev使用）
├── services/                # 服务层
└── checkpointer.py          # 检查点管理
```

## 快速使用

### 方式1：使用Task类（推荐）

```python
from agent_langgraph import Text2CaseTask, Text2SQLTask, Text2APITask

# Text2Case - 多智能体协作生成测试用例
task = Text2CaseTask()
result = await task.arun(
    requirement="用户登录功能，支持手机号和邮箱登录，需要验证码校验",
    test_type="API",
    max_iterations=3  # 最多迭代3次优化
)

# 查看结果
print(result.state["test_cases"])
print(f"质量评分: {result.state['quality_score']}")
print(f"执行历史: {result.state['agent_history']}")

# Text2SQL
task = Text2SQLTask()
result = task.run(
    question="查询所有订单金额大于1000的用户",
    schema="users(id, name), orders(id, user_id, amount)",
    dialect="mysql"
)
print(result.state["sql"])

# Text2API
task = Text2APITask()
result = task.run(
    description="获取用户列表，支持分页",
    base_url="https://api.example.com"
)
print(result.state["curl"])
```

### 方式2：带回调的执行

```python
from agent_langgraph import Text2CaseTask

task = Text2CaseTask()

# 定义回调函数
def on_agent_start(agent_name, message, progress):
    print(f"[{agent_name}] {message} ({progress}%)")

def on_agent_error(agent_name, message, exception):
    print(f"[{agent_name}] ERROR: {message}")

# 带回调执行
result = await task.arun_with_callback(
    requirement="用户登录功能",
    on_agent_start=on_agent_start,
    on_agent_end=lambda n, s: print(f"[{n}] 完成"),
)

# 流式执行
async for agent_name, state in task.astream(requirement="用户登录功能"):
    print(f"[{agent_name}] 当前状态: {state.get('next_agent')}")
```

### 方式3：直接使用Graph

```python
from agent_langgraph import get_graph, text2sql_graph

# 通过注册表获取
graph = get_graph("text2sql")

# 或直接使用导出的graph
result = text2sql_graph.invoke({
    "question": "查询所有用户",
    "dialect": "mysql"
})
```

### 方式4：流式执行

```python
task = Text2SQLTask()
for node_name, state in task.stream(question="查询所有用户"):
    print(f"[{node_name}] completed")
```

## 多智能体协作架构

### 架构图

```
                    ┌─────────────────┐
                    │   Supervisor    │
                    │   (协调者)       │
                    └────────┬────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Analyzer │      │ Designer │      │  Writer  │
    │(需求分析) │      │(测试设计) │      │(用例编写) │
    └──────────┘      └──────────┘      └──────────┘
                             │
                             ▼
                      ┌──────────┐
                      │ Reviewer │
                      │(用例评审) │
                      └──────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
                    ▼                 ▼
              [通过: FINISH]    [不通过: Writer重写]
```

### 执行流程

1. **Supervisor** 分析当前状态，决定下一步
2. **Analyzer** 分析需求，提取测试要素
3. **Supervisor** 决定下一步 → Designer
4. **Designer** 设计测试点覆盖方案
5. **Supervisor** 决定下一步 → Writer
6. **Writer** 编写详细测试用例
7. **Supervisor** 决定下一步 → Reviewer
8. **Reviewer** 评审用例质量（0-100分）
9. **Supervisor** 根据评分决定：
   - 分数 ≥ 80：FINISH
   - 分数 < 80 且未达最大迭代：返回 Writer 重写
   - 达到最大迭代：FINISH

### 智能体职责

| 智能体 | 职责 | 输出 |
|--------|------|------|
| **Supervisor** | 协调决策 | next_agent |
| **Analyzer** | 需求分析 | analysis |
| **Designer** | 测试点设计 | test_points |
| **Writer** | 用例编写 | test_cases (JSON) |
| **Reviewer** | 质量评审 | quality_score, suggestions |

## 扩展新任务类型

### 步骤1：创建任务目录

```
tasks/
└── text2xxx/
    ├── __init__.py
    ├── state.py
    ├── nodes.py
    ├── graph.py
    └── task.py
```

### 步骤2：定义State

```python
# state.py
from typing import TypedDict, List, Optional, Dict, Any

class Text2XXXState(TypedDict, total=False):
    messages: List[Dict[str, Any]]
    completed: bool
    error: Optional[str]
    # 添加任务特有字段
    input_field: str
    output_field: Optional[str]

def create_initial_state(**kwargs) -> Text2XXXState:
    return Text2XXXState(
        messages=[],
        completed=False,
        error=None,
        **kwargs
    )
```

### 步骤3：实现节点函数

```python
# nodes.py
from .state import Text2XXXState
from ...core import ModelFactory

def process_input(state: Text2XXXState) -> Text2XXXState:
    model = ModelFactory.get_model(temperature=0.3)
    # 处理逻辑
    return {**state, "output_field": "result"}
```

### 步骤4：构建Graph

```python
# graph.py
from ...core import BaseGraphBuilder
from ..registry import TaskRegistry
from .state import Text2XXXState
from .nodes import process_input

class Text2XXXGraphBuilder(BaseGraphBuilder[Text2XXXState]):
    task_type = "text2xxx"
    
    def get_state_class(self):
        return Text2XXXState
    
    def get_nodes(self):
        return {"process_input": process_input}
    
    def get_edges(self):
        return [
            ("START", "process_input"),
            ("process_input", "END"),
        ]

# 注册任务
TaskRegistry.register("text2xxx", Text2XXXGraphBuilder)

# 导出graph
graph = Text2XXXGraphBuilder().build()
```

### 步骤5：创建Task类

```python
# task.py
from ..base_task import BaseTask
from .state import Text2XXXState, create_initial_state
from .graph import Text2XXXGraphBuilder

class Text2XXXTask(BaseTask[Text2XXXState]):
    task_type = "text2xxx"
    
    def get_graph(self):
        return Text2XXXGraphBuilder().build()
    
    def create_initial_state(self, **kwargs):
        return create_initial_state(**kwargs)
```

## 核心组件说明

### ModelFactory

统一管理LLM模型实例，支持缓存和多provider：

```python
from agent_langgraph import ModelFactory, ModelConfig

# 设置默认配置
ModelFactory.set_default_config(ModelConfig(
    provider="siliconflow",
    model_name="deepseek-ai/DeepSeek-V3",
    api_key="your-api-key"
))

# 获取模型
model = ModelFactory.get_model(temperature=0.3)
```

### TaskRegistry

任务注册表，支持动态获取Graph：

```python
from agent_langgraph import TaskRegistry, get_graph

# 列出所有任务
print(TaskRegistry.list_tasks())  # ['text2case', 'text2sql', 'text2api']

# 获取Graph
graph = get_graph("text2sql")
```

### BaseGraphBuilder

Graph构建器基类，简化Graph定义：

```python
from agent_langgraph import BaseGraphBuilder

class MyGraphBuilder(BaseGraphBuilder[MyState]):
    def get_state_class(self): ...
    def get_nodes(self): ...
    def get_edges(self): ...
    def get_conditional_edges(self): ...  # 可选
```

## 提示词管理

提示词存放在 `tasks/text2case/prompts/` 目录下，支持：
- **文件加载**：从 `.txt` 文件加载
- **数据库加载**：优先从数据库加载（需传入 `db_session`）

```python
# 智能体自动加载提示词
from agent_langgraph import AnalyzerAgent

agent = AnalyzerAgent(
    db_session=session,  # 可选，传入后优先从数据库加载
    test_type="API"
)
# 提示词通过 agent.system_prompt 访问
```

### 自定义提示词

修改 `prompts/` 目录下的 `.txt` 文件即可自定义提示词：
- `supervisor.txt` - 协调者提示词
- `analyzer.txt` - 需求分析提示词
- `designer.txt` - 测试点设计提示词
- `writer.txt` - 用例编写提示词
- `reviewer.txt` - 用例评审提示词
