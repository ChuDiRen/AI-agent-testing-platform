# AI Agent 开发技能

## 触发条件
- 关键词：AI Agent、智能体、LangChain、LangGraph、Agent、RAG、LLM 应用
- 场景：当用户需要开发 AI 智能体或 LLM 应用时

## 核心规范

### 规范1：Agent 架构设计

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

### 规范2：LangGraph 状态机设计

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

### 规范3：Tool 定义规范

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

### 规范4：Memory 管理

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

### 规范5：Prompt 模板设计

```python
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_PROMPT = """你是一个专业的 AI 助手。

## 角色定位
{role_description}

## 可用工具
{tools_description}

## 约束条件
1. 始终基于事实回答
2. 不确定时主动询问
3. 复杂任务分步执行
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
```

### 规范6：错误处理与重试

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

### 规范7：流式输出

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

## 禁止事项
- ❌ 在 Prompt 中硬编码敏感信息
- ❌ 不限制 Token 使用量
- ❌ 忽略 LLM 调用的错误处理
- ❌ 不记录 Agent 执行日志
- ❌ 直接暴露内部工具给用户

## 检查清单
- [ ] 是否有完善的状态管理
- [ ] 是否有合理的 Memory 策略
- [ ] 是否有错误处理和重试机制
- [ ] 是否有 Token 使用监控
- [ ] 是否有执行日志记录
- [ ] 是否支持流式输出
