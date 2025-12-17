"""
Text2API Node Functions

API请求生成任务的节点函数
"""
import json
import re
import logging
from typing import Dict, Any

from agent_langgraph.tasks.text2api.state import Text2APIState
from agent_langgraph.core import ModelFactory

logger = logging.getLogger(__name__)


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


def understand_description(state: Text2APIState) -> Text2APIState:
    """
    理解描述节点
    
    解析用户输入，提取API请求意图
    """
    logger.info("Understanding description...")
    
    description = extract_description(state)
    
    if not description:
        return {**state, "error": "请输入API请求描述"}
    
    messages = list(state.get("messages", []))
    messages.append({"role": "ai", "content": "正在理解您的API请求描述..."})
    
    return {
        **state,
        "description": description,
        "messages": messages,
    }


def generate_api_request(state: Text2APIState) -> Text2APIState:
    """
    生成API请求节点
    
    根据描述生成HTTP请求
    """
    logger.info("Generating API request...")
    
    if state.get("error"):
        return state
    
    model = ModelFactory.get_model(temperature=0.2)
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
        
        messages = list(state.get("messages", []))
        messages.append({
            "role": "ai",
            "content": f"API请求生成完成:\n```\n{curl}\n```"
        })
        
        return {
            **state,
            "request": request,
            "curl": curl,
            "explanation": result.get("explanation", ""),
            "completed": True,
            "messages": messages,
        }
    except Exception as e:
        logger.error(f"API request generation failed: {e}")
        return {**state, "error": str(e)}
