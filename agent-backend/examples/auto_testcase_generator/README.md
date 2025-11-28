# 自动测试用例生成器 V6

基于 LangGraph 1.0 + 智能体/工具混合架构 + 智能测试方法选择

## 🎯 架构优化

### 智能体 vs 工具

| 模块 | 类型 | 说明 | Token消耗 |
|------|------|------|----------|
| **需求分析** | 智能体 | 需要理解复杂需求 | ✅ 消耗 |
| **测试点设计** | 智能体 | 需要创造性设计 | ✅ 消耗 |
| **用例编写** | 智能体 | 核心生成任务 | ✅ 消耗 |
| **用例评审** | 智能体 | 需要质量判断 | ✅ 消耗 |
| **测试方法选择** | 工具 | 确定性逻辑 | ❌ 0消耗 |
| **数据导出** | 工具 | 纯数据处理 | ❌ 0消耗 |

### 优化效果

| 指标 | V5 | V6 | 提升 |
|------|-----|-----|------|
| LLM调用次数 | 6-8次 | 4次 | **50%↓** |
| Token消耗 | 高 | 中 | **40%↓** |
| 执行速度 | 慢 | 快 | **2-3x↑** |

## 🏗️ 核心组件

### LLM智能体 (4个)
- 🔍 **Analyzer**: 深度理解需求，提取测试要素
- 📋 **TestPointDesigner**: 设计正常/异常/边界测试点
- ✍️ **Writer**: 生成完整测试用例 (集成测试方法模板)
- 🔎 **Reviewer**: 多维度质量评审 (0-100分)

### 工具函数 (2个)
- 🛠️ **TestMethodSelector**: 根据需求特征选择测试方法
- 📊 **ToolAgent**: 导出XMind/Excel，生成统计报告

### 测试方法模板 (6种)
| 方法 | 适用场景 |
|------|---------|
| 等价类划分 | 输入验证 |
| 边界值分析 | 范围限制 |
| 判定表 | 多条件逻辑 |
| 场景法 | 业务流程 |
| 正交法 | 配置组合 |
| 因果图 | 条件约束 |

## 📦 安装

```bash
pip install langchain langgraph langchain-openai requests python-docx pypdf openpyxl pydantic beautifulsoup4
```

## 🚀 快速开始

### 1. 运行脚本（推荐）

```bash
cd examples/auto_testcase_generator

# 文本输入演示（默认）
python run.py

# 带流式进度的生成
python run.py stream -t "用户登录接口需求..."

# Swagger批量生成
python run.py swagger

# 文档生成
python run.py document
```

### 2. Python API

```python
import asyncio
from auto_testcase_generator import generator

async def main():
    # 完整流程生成
    result = await generator.generate(
        "用户登录接口需求...",
        test_type="API",
        max_iterations=3
    )
    
    # 查看结果
    print(f"测试用例:\n{result.testcases}")
    print(f"质量评分: {result.quality_score}分")
    print(f"XMind文件: {result.xmind_path}")
    print(f"Excel文件: {result.excel_path}")

asyncio.run(main())
```

## 🏗️ 架构设计

### 多智能体协作流程

```
用户输入 (需求文档URL/文本)
           │
           ▼
┌─────────────────────────┐
│      Supervisor         │  ← 识别意图与规划路径
│   (智能Token管理)        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│    需求分析专家          │  ← 深度解析需求
│  (支持URL/知识库获取)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│   测试点设计专家         │  ← 设计测试覆盖点
│  (多维度测试策略)        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  测试用例编写专家        │  ← 生成详细测试用例
│   (JSON结构化输出)       │◄──────┐
└───────────┬─────────────┘       │
            │                     │
            ▼                     │
┌─────────────────────────┐       │
│  测试用例评审专家        │       │ 质量不通过
│  (多维度评分0-100)       │───────┘ (最多3次)
└───────────┬─────────────┘
            │ 质量通过
            ▼
┌─────────────────────────┐
│    数据处理专家          │  ← 非LLM确定性任务
│  (XMind/Excel导出)       │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│      输出物打包          │
│  下载链接 + 统计报告     │
└─────────────────────────┘
```

### 质量评分体系

| 评审维度 | 满分 | 说明 |
|---------|------|------|
| 需求覆盖度 | 30分 | 是否覆盖所有需求点和测试点 |
| 用例质量 | 25分 | 步骤清晰、预期结果明确、数据合理 |
| 用例完整性 | 20分 | 格式规范、字段完整 |
| 可执行性 | 15分 | 步骤可执行、前置条件可达成 |
| 设计合理性 | 10分 | 优先级合理、无冗余重复 |
| **总分** | **100分** | **≥80分通过** |

### middlewareV1 上下文工程

每个智能体都应用了不同的消息过滤策略:

| 智能体 | 保留消息 | Temperature | 说明 |
|--------|---------|-------------|------|
| Analyzer | H=1, A=0 | 0.5 | 只保留最新的需求输入 |
| TestPointDesigner | H=2, A=1 | 0.5 | 保留需求+分析结果 |
| Writer | H=2, A=2 | 0.7 | 创造性任务，需要更高温度 |
| Reviewer | H=3, A=3 | 0.1 | 严格性任务，需要低温度 |
| Supervisor | H=5, A=5 | - | 保留决策信息，不保留工具调用 |

**中间件功能:**
- 🔹 **PreModelHook**: 执行前优化上下文，动态注入历史信息
- 🔹 **AfterModelHook**: 执行后保存结果，支持版本管理
- 🔹 **DynamicModelMiddleware**: 根据任务类型动态调整模型参数
- 🔹 **TokenManager**: 智能Token管理，降低30-50%成本

## 📁 文件结构

```
auto_testcase_generator/
├── __init__.py              # 模块导出
├── run.py                   # CLI演示脚本
├── config.py                # 配置管理
├── models.py                # 数据模型 (TestCaseState + Pydantic验证)
├── database.py              # SQLite持久化
├── generator.py             # 核心生成器
├── supervisor.py            # Supervisor协调者 (意图识别+Token管理)
├── parsers.py               # Swagger/文档解析器
├── agents/                  # 5个专家智能体
│   ├── analyzer_agent.py           # 需求分析专家
│   ├── test_point_designer_agent.py # 测试点设计专家
│   ├── writer_agent.py             # 用例编写专家
│   ├── reviewer_agent.py           # 用例评审专家 (多维度评分)
│   └── tool_agent.py               # 数据处理专家 (非LLM)
├── middleware/              # middlewareV1实现
│   ├── config.py                   # 过滤配置
│   ├── message_filter.py           # 消息过滤
│   ├── state_sync.py               # 状态同步
│   ├── context_manager.py          # 上下文管理器
│   ├── adapters.py                 # 中间件适配器
│   └── hooks.py                    # Pre/After钩子函数
├── tools/                   # 工具模块
│   └── requirement_tools.py        # 需求获取工具 (URL/知识库)
├── prompts/                 # 提示词模板
│   ├── TESTCASE_READER_SYSTEM_MESSAGE.txt
│   ├── TESTCASE_TEST_POINT_DESIGNER_SYSTEM_MESSAGE.txt
│   ├── TESTCASE_WRITER_SYSTEM_MESSAGE_ORIGINAL.txt
│   └── TESTCASE_REVIEWER_SYSTEM_MESSAGE.txt
└── output/                  # 输出目录 (XMind/Excel)
```

## ⚙️ 配置选项

### 环境变量

```bash
export SILICONFLOW_API_KEY=sk-your-key
# 或
export DEEPSEEK_API_KEY=sk-your-key
```

### 生成器配置

```python
from auto_testcase_generator import TestCaseGeneratorV3

generator = TestCaseGeneratorV3(
    enable_middleware=True,      # 启用 middlewareV1 (推荐)
    enable_human_review=False,   # 启用人工审核 (可选)
    enable_persistence=True,     # 启用持久化存储 (推荐)
    enable_data_export=True,     # 启用数据导出 (XMind/Excel)
)
```

### 意图识别

系统会自动识别用户意图，支持灵活的执行范围：

| 用户输入 | 识别意图 | 执行链路 |
|---------|---------|---------|
| "帮我分析这个需求" | 需求分析 | 需求分析专家 → 结束 |
| "设计测试点" | 测试点设计 | 需求分析 → 测试点设计 → 结束 |
| "生成测试用例" | 完整流程 | 全流程执行 |
| 仅提供URL | 完整流程 | 默认全流程执行 |

## 💾 数据库

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
    quality_score REAL,
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

## 📊 输出格式

### 测试用例 JSON 结构

```json
{
  "测试用例": [
    {
      "功能模块": "用户登录",
      "测试用例列表": [
        {
          "用例编号": "TC001",
          "用例标题": "正确用户名密码登录成功",
          "优先级": "P0",
          "前置条件": "1. 用户已注册\n2. 账号未被锁定",
          "测试步骤": [
            "1. 打开登录页面",
            "2. 输入正确的用户名：test@example.com",
            "3. 输入正确的密码：Test123!",
            "4. 点击登录按钮"
          ],
          "预期结果": [
            "1. 登录成功，显示欢迎提示",
            "2. 自动跳转到首页",
            "3. 显示用户头像和昵称"
          ],
          "测试数据": {
            "username": "test@example.com",
            "password": "Test123!"
          }
        }
      ]
    }
  ]
}
```

### 导出文件

- **XMind思维导图**: `output/testcases_YYYYMMDD_HHMMSS.xmind`
- **Excel表格**: `output/testcases_YYYYMMDD_HHMMSS.xlsx`
- **统计报告**: 包含用例数量、模块分布、优先级分布

## 🔧 技术亮点

### 1. 智能Token管理
- Supervisor的Token消耗降低40-50%
- 子智能体的Token消耗降低20-30%
- 上下文仍然保持连贯性和完整性

### 2. 状态持久化与版本管理
- 每个阶段的输出都会保存到state
- 支持历史追踪和版本回溯
- 如果智能体中断，可以从上次状态继续执行

### 3. Pydantic数据验证
- 确保输出数据格式正确
- 发现缺失或错误的字段
- 统计测试用例数量和分布

### 4. 异步并发处理
- 需求分析和测试点设计并行执行
- XMind和Excel并行导出
- 文档生成时间降低约50%

## 📝 更新日志

### V4.0 (2024-11)
- ✨ 新增数据处理专家 (Tool Agent)
- ✨ 新增智能Token管理
- ✨ 新增意图识别功能
- ✨ 新增完成标志机制
- ✨ 新增多维度质量评分
- ✨ 新增版本管理和评审历史
- ✨ 新增XMind/Excel导出
- ✨ 新增需求获取工具 (URL/知识库)
- 🔧 优化中间件架构 (Pre/After Hook)
- 🔧 优化评审专家评分解析

