# 提示词工程技能

## 触发条件
- 关键词：Prompt、提示词、提示工程、System Prompt、Few-shot、CoT
- 场景：当用户需要设计或优化 LLM 提示词时

## 核心规范

### 规范1：Prompt 结构框架

```markdown
# System Prompt 标准结构

## 1. 角色定义 (Role)
你是一个 [角色名称]，专注于 [专业领域]。

## 2. 背景信息 (Context)
[提供必要的背景知识和约束条件]

## 3. 任务说明 (Task)
你需要完成以下任务：
1. [具体任务1]
2. [具体任务2]

## 4. 输出格式 (Format)
请按以下格式输出：
```
[期望的输出格式]
```

## 5. 示例 (Examples)
输入：[示例输入]
输出：[示例输出]

## 6. 约束条件 (Constraints)
- 约束1
- 约束2
```

### 规范2：常用 Prompt 技巧

| 技巧 | 说明 | 示例 |
|------|------|------|
| **角色扮演** | 赋予 AI 特定身份 | "你是一位资深 Python 开发者" |
| **Few-shot** | 提供示例引导 | "示例1: ... 示例2: ..." |
| **CoT** | 链式思考 | "让我们一步一步思考" |
| **Self-consistency** | 多次生成取最优 | 生成多个答案后投票 |
| **ReAct** | 推理+行动 | "思考->行动->观察->思考" |

### 规范3：Few-shot 示例设计

```python
FEW_SHOT_PROMPT = """
请将用户的自然语言转换为 SQL 查询。

示例1:
用户: 查询所有状态为激活的用户
SQL: SELECT * FROM users WHERE status = 'active';

示例2:
用户: 统计每个部门的员工数量
SQL: SELECT department, COUNT(*) as count FROM employees GROUP BY department;

示例3:
用户: 找出订单金额超过1000的客户
SQL: SELECT DISTINCT customer_id FROM orders WHERE amount > 1000;

现在请处理:
用户: {user_input}
SQL:
"""
```

### 规范4：Chain of Thought (CoT)

```python
COT_PROMPT = """
请分析以下问题，并一步一步给出推理过程。

问题: {question}

请按以下步骤思考：
1. 理解问题：明确问题要求什么
2. 分析条件：列出已知条件和约束
3. 制定方案：思考解决方法
4. 逐步推理：详细展示每一步
5. 得出结论：给出最终答案

让我们开始一步一步思考：
"""
```

### 规范5：结构化输出控制

```python
STRUCTURED_OUTPUT_PROMPT = """
请分析用户反馈并提取关键信息。

用户反馈: {feedback}

请严格按以下 JSON 格式输出，不要添加任何其他内容：
```json
{
  "sentiment": "positive|negative|neutral",
  "category": "bug|feature|question|other",
  "priority": "high|medium|low",
  "summary": "一句话总结",
  "action_items": ["建议的行动项"]
}
```
"""

# 使用 Pydantic 强制结构化
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class FeedbackAnalysis(BaseModel):
    sentiment: str
    category: str
    priority: str
    summary: str
    action_items: list[str]

parser = PydanticOutputParser(pydantic_object=FeedbackAnalysis)
```

### 规范6：Prompt 优化技巧

```markdown
## 优化前
"帮我写一段代码"

## 优化后
"请用 Python 编写一个函数，实现以下功能：
1. 输入：用户列表 (List[dict])，每个用户包含 name, age, email
2. 输出：按年龄排序后的用户列表
3. 要求：
   - 使用类型注解
   - 添加 docstring
   - 处理空列表情况
4. 示例：
   输入: [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
   输出: [{'name': 'Bob', 'age': 25}, {'name': 'Alice', 'age': 30}]"
```

### 规范7：多轮对话 Prompt

```python
CONVERSATION_PROMPT = """
你是一个智能客服助手。

## 对话历史
{chat_history}

## 当前用户消息
{user_message}

## 回复要求
1. 基于对话历史理解上下文
2. 回答要简洁专业
3. 如果信息不足，礼貌询问
4. 涉及敏感操作需确认

请回复：
"""
```

### 规范8：Prompt 测试与评估

```python
# Prompt 测试用例
TEST_CASES = [
    {
        "input": "查询最近7天的订单",
        "expected_contains": ["SELECT", "orders", "7"],
        "expected_not_contains": ["DELETE", "DROP"]
    },
    {
        "input": "删除所有数据",
        "expected_response": "拒绝执行危险操作"
    }
]

def evaluate_prompt(prompt_template, test_cases):
    results = []
    for case in test_cases:
        response = llm.invoke(prompt_template.format(**case["input"]))
        passed = all(
            keyword in response for keyword in case.get("expected_contains", [])
        )
        results.append({"case": case, "response": response, "passed": passed})
    return results
```

## 禁止事项
- ❌ 提示词过于模糊笼统
- ❌ 缺少输出格式说明
- ❌ 没有处理边界情况
- ❌ 提示词中包含注入风险
- ❌ 不测试就上线

## 检查清单
- [ ] 是否明确定义了角色
- [ ] 是否提供了足够的上下文
- [ ] 是否指定了输出格式
- [ ] 是否包含示例（Few-shot）
- [ ] 是否考虑了边界情况
- [ ] 是否进行了测试验证
