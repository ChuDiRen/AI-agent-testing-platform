# AI 大模型集成技能

## 触发条件
- 关键词：AI、大模型、LLM、ChatGPT、Claude、LangChain、LangGraph、RAG
- 场景：当用户需要集成 AI 大模型功能时

## 核心规范

### 规范1：本项目 AI 技术栈

- **框架**: LangGraph (Python)
- **流式输出**: SSE (Server-Sent Events)
- **服务**: `core/AiStreamService.py`
- **配置**: `config/dev_settings.py`

### 规范2：项目 AI 模块结构

```
agent_langgraph/
├── __init__.py
├── checkpointer.py           # 检查点管理
├── LangGraphCheckpointModel.py
├── core/                     # 核心组件
├── graphs/                   # LangGraph 图定义
├── services/                 # AI 服务
└── tasks/                    # 任务定义

aiassistant/
├── api/                      # AI 助手 API
├── langgraph/                # LangGraph 集成
├── model/                    # 数据模型
├── schemas/                  # 请求/响应模式
└── services/                 # 业务服务
```

### 规范3：流式对话服务

```python
# core/AiStreamService.py
from sse_starlette.sse import EventSourceResponse
import httpx

class AiStreamService:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def stream_chat(self, messages: list, model: str = "gpt-3.5-turbo"):
        """流式对话"""
        async def generate():
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True
                    }
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            yield {"data": line[6:]}
        
        return EventSourceResponse(generate())
```

### 规范4：LangGraph 工作流定义

```python
# agent_langgraph/graphs/example_graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from operator import add

class AgentState(TypedDict):
    messages: Annotated[list, add]
    next_step: str

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("respond", respond_node)
    
    # 设置入口
    workflow.set_entry_point("analyze")
    
    # 添加边
    workflow.add_conditional_edges(
        "analyze",
        route_decision,
        {
            "execute": "execute",
            "respond": "respond"
        }
    )
    workflow.add_edge("execute", "respond")
    workflow.add_edge("respond", END)
    
    return workflow.compile()

def analyze_node(state: AgentState):
    # 分析逻辑
    return {"next_step": "execute"}

def execute_node(state: AgentState):
    # 执行逻辑
    return {"messages": ["执行完成"]}

def respond_node(state: AgentState):
    # 响应逻辑
    return {"messages": ["任务完成"]}

def route_decision(state: AgentState):
    return state["next_step"]
```

### 规范5：API 接口定义

```python
# aiassistant/api/chat_controller.py
from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

router = APIRouter(prefix="/ai", tags=["AI助手"])

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """流式对话接口"""
    async def generate():
        async for chunk in ai_service.stream_response(request.messages):
            yield {"data": chunk}
    
    return EventSourceResponse(generate())

@router.post("/chat/completion")
async def chat_completion(request: ChatRequest):
    """非流式对话接口"""
    response = await ai_service.get_completion(request.messages)
    return respModel.ok_resp(obj=response)
```

### 规范6：前端流式接收

```javascript
// 使用 EventSource 接收 SSE
const eventSource = new EventSource('/api/ai/chat/stream')

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    // 处理流式数据
    appendMessage(data.content)
}

eventSource.onerror = (error) => {
    console.error('SSE Error:', error)
    eventSource.close()
}

// 或使用 fetch + ReadableStream
async function streamChat(messages) {
    const response = await fetch('/api/ai/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages })
    })
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const chunk = decoder.decode(value)
        // 处理数据块
    }
}
```

## 禁止事项
- ❌ 在代码中硬编码 API Key
- ❌ 不处理流式响应的错误
- ❌ 不设置请求超时
- ❌ 不做 Token 限制检查

## 检查清单
- [ ] API Key 是否从配置读取
- [ ] 是否有错误处理
- [ ] 是否支持流式输出
- [ ] 是否有超时设置
