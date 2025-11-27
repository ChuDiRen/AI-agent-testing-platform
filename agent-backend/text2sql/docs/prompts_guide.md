# 提示词维护指南

本文档说明如何维护和自定义Text2SQL系统的提示词。

## 提示词文件位置

所有提示词文件存储在 `text2sql/prompts/` 目录下：

```
prompts/
├── loader.py              # 提示词加载器
├── supervisor.md          # 监督代理提示词
├── schema_agent.md        # Schema分析代理
├── sql_generator.md       # SQL生成代理
├── sql_validator.md       # SQL验证代理
├── sql_executor.md        # SQL执行代理
├── error_recovery.md      # 错误恢复代理
└── chart_generator.md     # 图表生成代理
```

## 提示词格式

### 基本结构

```markdown
# Agent Name

简短描述代理的职责。

## 职责

1. 主要职责1
2. 主要职责2

## 工具

- `tool_name`: 工具描述

## 输出格式

期望的输出格式说明

## 注意事项

- 注意事项1
- 注意事项2
```

### 变量占位符

提示词支持使用 `{variable}` 格式的占位符，在加载时会被替换：

```markdown
默认返回 {top_k} 条记录
当前数据库类型: {dialect}
最大重试次数: {max_retries}
```

## 加载提示词

```python
from text2sql.prompts import load_prompt

# 加载不带变量的提示词
prompt = load_prompt("schema_agent")

# 加载并替换变量
prompt = load_prompt("sql_generator", dialect="mysql", top_k=100)
```

## 修改提示词

### 1. 直接编辑文件

编辑对应的 `.md` 文件即可。系统使用LRU缓存，修改后需要清除缓存：

```python
from text2sql.prompts import clear_cache
clear_cache()
```

### 2. 开发模式自动重载

使用 `langgraph dev` 时支持热重载。

## 最佳实践

### 1. 保持简洁

- 每个提示词专注于单一职责
- 避免过长的描述
- 使用清晰的结构

### 2. 明确输出格式

```markdown
## 输出格式

返回JSON格式:
```json
{
    "is_valid": true,
    "sql": "...",
    "errors": []
}
```

### 3. 提供示例

```markdown
## 示例

输入: "查询所有用户"
输出:
```sql
SELECT * FROM users LIMIT 100;
```

### 4. 定义边界

明确说明代理**不应该**做什么：

```markdown
## 禁止操作

- 不生成DELETE、UPDATE等修改语句
- 不访问系统表
- 不使用存储过程
```

## 自定义代理

### 添加新代理

1. 创建提示词文件 `prompts/new_agent.md`
2. 创建代理实现 `agents/new_agent.py`
3. 在代理中加载提示词

```python
from text2sql.prompts import load_prompt

def create_new_agent(model):
    prompt = load_prompt("new_agent")
    return create_react_agent(model=model, prompt=prompt, name="new_agent")
```

### 修改现有代理行为

1. 复制原提示词文件
2. 修改内容
3. 保存并清除缓存

## 调试技巧

### 查看加载的提示词

```python
from text2sql.prompts import load_prompt, get_prompt_path

# 查看文件路径
print(get_prompt_path("sql_generator"))

# 查看内容
print(load_prompt("sql_generator", dialect="mysql", top_k=100))
```

### 列出所有提示词

```python
from text2sql.prompts.loader import list_prompts
print(list_prompts())
```

## 常见问题

### Q: 提示词修改后不生效？

清除缓存：
```python
from text2sql.prompts import clear_cache
clear_cache()
```

### Q: 变量未被替换？

检查变量名是否正确，使用 `{variable}` 格式。

### Q: 如何添加多语言支持？

创建语言特定的提示词文件：
```
prompts/
├── sql_generator.md       # 默认（中文）
├── sql_generator_en.md    # 英文
└── sql_generator_ja.md    # 日文
```

加载时指定语言：
```python
prompt = load_prompt(f"sql_generator_{lang}")
```
