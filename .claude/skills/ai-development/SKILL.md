# AI开发综合技能

## 触发条件
- 关键词：AI、LLM、Agent、智能体、LangChain、LangGraph、RAG、Prompt、提示词、大模型
- 场景：当用户需要开发AI应用、设计智能体或优化提示词时

## 核心规范

### 规范1：AI Agent架构设计

```
┌─────────────────────────────────────────┐
│              User Interface              │
├─────────────────────────────────────────┤
│           Agent Orchestrator             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │ Planner │ │ Memory  │ │ Tools   │   │
│  └─────────┘ └─────────┘ └─────────┘   │
├─────────────────────────────────────────┤
│              LLM Provider                │
│  (OpenAI / Claude / Local Models)        │
└─────────────────────────────────────────┘
```

### 规范2：LangGraph状态机设计

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    current_step: str
    context: dict
    final_answer: str

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("review", review_node)
    
    # 添加边
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "plan")
    workflow.add_edge("plan", "execute")
    workflow.add_conditional_edges(
        "execute",
        should_continue,
        {"continue": "execute", "review": "review"}
    )
    workflow.add_edge("review", END)
    
    return workflow.compile()
```

### 规范3：Tool定义规范

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")
    max_results: int = Field(default=10, description="最大结果数")

@tool(args_schema=SearchInput)
def search_database(query: str, max_results: int = 10) -> str:
    """
    在数据库中搜索相关内容。
    
    Args:
        query: 搜索关键词
        max_results: 返回的最大结果数
        
    Returns:
        搜索结果的 JSON 字符串
    """
    # 实现搜索逻辑
    results = db.search(query, limit=max_results)
    return json.dumps(results, ensure_ascii=False)
```

### 规范4：Memory管理

```python
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.vectorstores import FAISS

# 短期记忆 - 对话历史
short_term_memory = ConversationBufferWindowMemory(
    k=10,  # 保留最近10轮对话
    return_messages=True
)

# 长期记忆 - 向量存储
long_term_memory = FAISS.from_texts(
    texts=documents,
    embedding=embeddings
)

# 检索相关记忆
def retrieve_memory(query: str, k: int = 5):
    return long_term_memory.similarity_search(query, k=k)
```

### 规范5：Prompt工程标准

#### 5.1 Prompt结构框架

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

#### 5.2 常用Prompt技巧

| 技巧 | 说明 | 示例 |
|------|------|------|
| **角色扮演** | 赋予AI特定身份 | "你是一位资深Python开发者" |
| **Few-shot** | 提供示例引导 | "示例1: ... 示例2: ..." |
| **CoT** | 链式思考 | "让我们一步一步思考" |
| **Self-consistency** | 多次生成取最优 | 生成多个答案后投票 |
| **ReAct** | 推理+行动 | "思考->行动->观察->思考" |

#### 5.3 Few-shot示例设计

```python
FEW_SHOT_PROMPT = """
请将用户的自然语言转换为SQL查询。

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

#### 5.4 结构化输出控制

```python
STRUCTURED_OUTPUT_PROMPT = """
请分析用户反馈并提取关键信息。

用户反馈: {feedback}

请严格按以下JSON格式输出，不要添加任何其他内容：
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

# 使用Pydantic强制结构化
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

### 规范6：RAG系统设计

```python
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings

# 文档分块策略
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# 向量存储
embeddings = OpenAIEmbeddings()
vector_store = FAISS.from_documents(
    documents=split_docs,
    embedding=embeddings
)

# 检索增强生成
def rag_query(question: str, k: int = 3):
    # 检索相关文档
    docs = vector_store.similarity_search(question, k=k)
    
    # 构建prompt
    context = "\n".join([doc.page_content for doc in docs])
    prompt = f"""
基于以下上下文回答问题：
上下文: {context}
问题: {question}
请基于上下文信息回答，如果上下文中没有相关信息，请说明。
"""
    
    return llm.invoke(prompt)
```

### 规范7：错误处理与重试

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_llm_with_retry(messages: list):
    try:
        response = await llm.ainvoke(messages)
        return response
    except RateLimitError:
        logger.warning("Rate limit hit, retrying...")
        raise
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise
```

### 规范8：流式输出

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

async def stream_agent_response(query: str):
    async for chunk in agent.astream({"input": query}):
        if "output" in chunk:
            yield f"data: {json.dumps({'content': chunk['output']})}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(
        stream_agent_response(request.query),
        media_type="text/event-stream"
    )
```

### 规范9：Token优化策略

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """计算token数量"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def optimize_context(context: str, max_tokens: int = 3000) -> str:
    """优化上下文长度"""
    if count_tokens(context) <= max_tokens:
        return context
    
    # 按句子分割，保留重要内容
    sentences = context.split('。')
    optimized = []
    current_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence + '。')
        if current_tokens + sentence_tokens <= max_tokens:
            optimized.append(sentence + '。')
            current_tokens += sentence_tokens
        else:
            break
    
    return ''.join(optimized)
```

## 应用场景

### 场景1: AI Agent开发
- 设计智能体架构
- 实现状态机逻辑
- 集成外部工具
- 管理对话记忆

### 场景2: RAG系统构建
- 文档向量化
- 检索策略设计
- 生成质量优化

### 场景3: Prompt工程
- System Prompt设计
- Few-shot示例构建
- 输出格式控制
- 性能测试评估

## 禁止事项
- ❌ 在Prompt中硬编码敏感信息
- ❌ 不限制Token使用量
- ❌ 忽略LLM调用的错误处理
- ❌ 不记录Agent执行日志
- ❌ 直接暴露内部工具给用户
- ❌ 提示词过于模糊笼统
- ❌ 缺少输出格式说明
- ❌ 不测试就上线

## 检查清单
- [ ] 是否有完善的状态管理
- [ ] 是否有合理的Memory策略
- [ ] 是否有错误处理和重试机制
- [ ] 是否有Token使用监控
- [ ] 是否有执行日志记录
- [ ] 是否支持流式输出
- [ ] 是否明确定义了角色
- [ ] 是否提供了足够的上下文
- [ ] 是否指定了输出格式
- [ ] 是否包含示例（Few-shot）
- [ ] 是否进行了测试验证
