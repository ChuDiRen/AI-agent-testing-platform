"""
Text2API Graph - 自然语言生成API请求

用于 langgraph dev 服务器的图定义
"""
import os
import json
import re
import logging
from typing import TypedDict, List, Optional, Dict, Any

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


# ==================== State Definition ====================

class Text2APIState(TypedDict):
    """Text2API状态定义"""
    messages: List[dict]
    description: str
    api_spec: Optional[str]
    base_url: Optional[str]
    auth_type: str
    request: Optional[Dict[str, Any]]
    curl: Optional[str]
    explanation: Optional[str]
    completed: bool
    error: Optional[str]


# ==================== Helper Functions ====================

def get_model():
    """获取模型实例"""
    api_key = os.getenv("SILICONFLOW_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1")
    model_name = os.getenv("SILICONFLOW_MODEL", "deepseek-ai/DeepSeek-V3")
    
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.2,
    )


def extract_description(state: Text2APIState) -> str:
    """从状态中提取描述"""
    if state.get("description"):
        return state["description"]
    
    messages = state.get("messages", [])
    for msg in reversed(messages):
        if isinstance(msg, dict):
            role = msg.get("role") or msg.get("type")
            if role in ("human", "user"):
                return msg.get("content", "")
    
    return ""


def generate_curl(request: Dict[str, Any]) -> str:
    """生成cURL命令"""
    method = request.get("method", "GET")
    url = request.get("url", "")
    headers = request.get("headers", {})
    body = request.get("body", {})
    params = request.get("params", {})
    
    if params:
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"{url}?{param_str}"
    
    curl_parts = [f"curl -X {method}"]
    
    for key, value in headers.items():
        curl_parts.append(f"-H '{key}: {value}'")
    
    if body and method in ("POST", "PUT", "PATCH"):
        body_str = json.dumps(body, ensure_ascii=False)
        curl_parts.append(f"-d '{body_str}'")
    
    curl_parts.append(f"'{url}'")
    
    return " \\\n  ".join(curl_parts)


# ==================== Node Functions ====================

def understand_description(state: Text2APIState) -> Text2APIState:
    """理解描述"""
    logger.info("Understanding description...")
    
    description = extract_description(state)
    
    if not description:
        return {**state, "error": "请输入API请求描述"}
    
    return {
        **state,
        "description": description,
        "messages": state.get("messages", []) + [{"role": "ai", "content": "正在理解您的API请求描述..."}]
    }


def generate_api_request(state: Text2APIState) -> Text2APIState:
    """生成API请求"""
    logger.info("Generating API request...")
    
    if state.get("error"):
        return state
    
    model = get_model()
    description = state.get("description", "")
    api_spec = state.get("api_spec", "")
    base_url = state.get("base_url", "")
    auth_type = state.get("auth_type", "none")
    
    spec_text = f"\nAPI规范:\n{api_spec}" if api_spec else ""
    base_url_text = f"\n基础URL: {base_url}" if base_url else ""
    
    prompt = f"""你是一个专业的API开发专家，请根据以下描述生成HTTP API请求。

描述: {description}
{base_url_text}
{spec_text}
认证类型: {auth_type}

请输出JSON格式：
```json
{{
  "request": {{
    "method": "GET/POST/PUT/DELETE",
    "url": "完整URL或路径",
    "headers": {{
      "Content-Type": "application/json"
    }},
    "params": {{}},
    "body": {{}}
  }},
  "explanation": "请求说明"
}}
```

注意：
1. 根据描述选择合适的HTTP方法
2. 正确设置Content-Type
3. 如果需要认证，添加相应的认证头（使用占位符）
"""
    
    try:
        response = model.invoke(prompt)
        content = response.content
        
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            result = json.loads(json_match.group())
        else:
            result = {
                "request": {
                    "method": "GET",
                    "url": base_url or "/api/unknown",
                    "headers": {},
                    "params": {},
                    "body": {}
                },
                "explanation": content
            }
        
        request = result.get("request", {})
        curl = generate_curl(request)
        
        return {
            **state,
            "request": request,
            "curl": curl,
            "explanation": result.get("explanation", ""),
            "completed": True,
            "messages": state.get("messages", []) + [{"role": "ai", "content": f"API请求生成完成:\n```\n{curl}\n```"}]
        }
    except Exception as e:
        logger.error(f"API request generation failed: {e}")
        return {**state, "error": str(e)}


# ==================== Build Graph ====================

def build_graph():
    """构建LangGraph图"""
    workflow = StateGraph(Text2APIState)
    
    workflow.add_node("understand_description", understand_description)
    workflow.add_node("generate_api_request", generate_api_request)
    
    workflow.add_edge(START, "understand_description")
    workflow.add_edge("understand_description", "generate_api_request")
    workflow.add_edge("generate_api_request", END)
    
    return workflow.compile()


# 导出graph实例供langgraph dev使用
graph = build_graph()
