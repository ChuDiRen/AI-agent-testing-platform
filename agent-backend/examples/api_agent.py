"""
Text2API Agent - 将自然语言转换为API调用
基于 LangChain Agent 框架，参考 SQL Agent 的实现模式

示例 API: https://petstore.swagger.io/
OpenAPI 规范: https://petstore.swagger.io/v2/swagger.json
"""

import json
import os
import sys
from typing import Optional, Dict, Any

import requests
from langchain.agents import create_agent

# 添加父目录到路径，以便导入自定义工具
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_chat_model  # 使用自定义的init_chat_model（支持硅基流动）
from langchain_core.tools import tool


class APIClient:
    """API 客户端，用于管理 OpenAPI 规范和执行 API 调用"""
    
    def __init__(self, openapi_url: str):
        """
        初始化 API 客户端
        
        Args:
            openapi_url: OpenAPI/Swagger 规范的 URL
        """
        self.openapi_url = openapi_url
        self.spec = None
        self.base_url = None
        self._load_spec()
    
    def _load_spec(self):
        """加载 OpenAPI 规范"""
        try:
            response = requests.get(self.openapi_url)
            response.raise_for_status()
            self.spec = response.json()
            
            # 获取基础 URL
            if "servers" in self.spec and self.spec["servers"]:
                self.base_url = self.spec["servers"][0]["url"]
            else:
                # Swagger 2.0 格式
                schemes = self.spec.get("schemes", ["https"])
                host = self.spec.get("host", "")
                base_path = self.spec.get("basePath", "")
                self.base_url = f"{schemes[0]}://{host}{base_path}"
            
            print(f"✅ 成功加载 API 规范: {self.base_url}")
        except Exception as e:
            raise Exception(f"加载 OpenAPI 规范失败: {e}")
    
    def get_endpoints_list(self) -> str:
        """获取所有可用的 API 端点列表"""
        if not self.spec:
            return "错误: API 规范未加载"
        
        endpoints = []
        paths = self.spec.get("paths", {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    summary = details.get("summary", details.get("operationId", ""))
                    endpoints.append(f"{method.upper()} {path} - {summary}")
        
        return "\n".join(endpoints)
    
    def get_endpoint_schema(self, path: str, method: str = "GET") -> str:
        """
        获取特定端点的详细信息
        
        Args:
            path: API 路径 (例如: /pet/{petId})
            method: HTTP 方法 (例如: GET, POST)
        """
        if not self.spec:
            return "错误: API 规范未加载"
        
        method = method.upper()
        paths = self.spec.get("paths", {})
        
        if path not in paths or method.lower() not in paths[path]:
            return f"错误: 未找到端点 {method} {path}"
        
        endpoint = paths[path][method.lower()]
        
        # 构建详细信息
        info = {
            "endpoint": f"{method} {path}",
            "summary": endpoint.get("summary", ""),
            "description": endpoint.get("description", ""),
            "parameters": endpoint.get("parameters", []),
            "requestBody": endpoint.get("requestBody", {}),
            "responses": endpoint.get("responses", {}),
        }
        
        return json.dumps(info, indent=2, ensure_ascii=False)
    
    def execute_api_call(
        self, 
        path: str, 
        method: str = "GET",
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        执行 API 调用
        
        Args:
            path: API 路径
            method: HTTP 方法
            path_params: 路径参数
            query_params: 查询参数
            body: 请求体
            headers: 请求头
        """
        try:
            # 替换路径参数
            if path_params:
                for key, value in path_params.items():
                    path = path.replace(f"{{{key}}}", str(value))
            
            # 构建完整 URL
            url = f"{self.base_url}{path}"
            
            # 默认请求头
            default_headers = {"Content-Type": "application/json"}
            if headers:
                default_headers.update(headers)
            
            # 执行请求
            response = requests.request(
                method=method.upper(),
                url=url,
                params=query_params,
                json=body,
                headers=default_headers,
                timeout=10,
            )
            
            # 返回结果
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response.text,
            }
            
            # 尝试解析 JSON
            try:
                result["body"] = response.json()
            except:
                pass
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "message": "API 调用失败"
            }, indent=2, ensure_ascii=False)


# 初始化 API 客户端（使用 Petstore 示例 API）
api_client = APIClient("https://petstore.swagger.io/v2/swagger.json")


# 创建工具
@tool
def api_list_endpoints() -> str:
    """
    列出所有可用的 API 端点
    
    输入: 空字符串
    输出: 所有可用 API 端点的列表，包括方法、路径和描述
    
    使用场景: 
    - 开始任何 API 调用之前，先查看有哪些端点可用
    - 了解 API 的整体功能
    """
    return api_client.get_endpoints_list()


@tool
def api_get_schema(path: str, method: str = "GET") -> str:
    """
    获取特定 API 端点的详细信息（参数、请求体、响应等）
    
    输入: 
    - path: API 路径 (例如: /pet/{petId})
    - method: HTTP 方法 (例如: GET, POST, PUT, DELETE)
    
    输出: 端点的详细信息，包括参数、请求体格式、响应格式等
    
    使用场景:
    - 在调用 API 之前，了解需要传递哪些参数
    - 确认请求体的格式
    - 查看可能的响应
    
    注意: 在调用 api_execute 之前，务必先调用此工具了解端点详情！
    """
    return api_client.get_endpoint_schema(path, method)


@tool
def api_execute(
    path: str,
    method: str = "GET",
    path_params: Optional[str] = None,
    query_params: Optional[str] = None,
    body: Optional[str] = None,
) -> str:
    """
    执行 API 调用
    
    输入:
    - path: API 路径 (例如: /pet/{petId})
    - method: HTTP 方法 (例如: GET, POST, PUT, DELETE)
    - path_params: 路径参数的 JSON 字符串 (例如: '{"petId": "1"}')
    - query_params: 查询参数的 JSON 字符串 (例如: '{"status": "available"}')
    - body: 请求体的 JSON 字符串 (例如: '{"name": "doggie", "status": "available"}')
    
    输出: API 响应，包括状态码、响应头和响应体
    
    使用场景:
    - 实际执行 API 调用
    - 获取数据或执行操作
    
    重要提示:
    1. 执行前必须先调用 api_get_schema 了解端点详情
    2. 确保所有必需的参数都已提供
    3. 如果遇到错误，检查参数格式和值是否正确
    """
    # 解析 JSON 参数
    path_params_dict = json.loads(path_params) if path_params else None
    query_params_dict = json.loads(query_params) if query_params else None
    body_dict = json.loads(body) if body else None
    
    return api_client.execute_api_call(
        path=path,
        method=method,
        path_params=path_params_dict,
        query_params=query_params_dict,
        body=body_dict,
    )


@tool
def api_call_checker(
    path: str,
    method: str,
    path_params: Optional[str] = None,
    query_params: Optional[str] = None,
    body: Optional[str] = None,
) -> str:
    """
    在执行 API 调用之前检查调用是否正确
    
    输入: 与 api_execute 相同的参数
    输出: 检查结果和建议
    
    使用场景:
    - 在实际执行 API 调用前验证参数
    - 避免错误的 API 调用
    
    重要: 在执行 api_execute 之前，务必先使用此工具检查！
    """
    issues = []
    
    # 检查路径参数
    if "{" in path and "}" in path:
        if not path_params:
            issues.append("路径中包含参数占位符，但未提供 path_params")
        else:
            try:
                params = json.loads(path_params)
                # 检查所有占位符是否都有对应的参数
                import re
                placeholders = re.findall(r'\{(\w+)\}', path)
                for placeholder in placeholders:
                    if placeholder not in params:
                        issues.append(f"缺少路径参数: {placeholder}")
            except json.JSONDecodeError:
                issues.append("path_params 不是有效的 JSON 格式")
    
    # 检查请求体
    if method.upper() in ["POST", "PUT", "PATCH"]:
        if not body:
            issues.append(f"{method} 请求通常需要 body 参数")
        else:
            try:
                json.loads(body)
            except json.JSONDecodeError:
                issues.append("body 不是有效的 JSON 格式")
    
    # 检查查询参数
    if query_params:
        try:
            json.loads(query_params)
        except json.JSONDecodeError:
            issues.append("query_params 不是有效的 JSON 格式")
    
    if issues:
        return "发现问题:\n" + "\n".join(f"- {issue}" for issue in issues)
    else:
        return "✅ API 调用参数检查通过，可以执行"


# 创建工具列表
tools = [
    api_list_endpoints,
    api_get_schema,
    api_call_checker,
    api_execute,
]


# 初始化 LLM
os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
model = init_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")

# 注意：checkpointer 和 store 由 langgraph.json 配置，LangGraph 服务器自动注入


# 系统提示词
system_prompt = """
你是一个专门用于与 RESTful API 交互的智能代理。
你可以理解用户的自然语言请求，并将其转换为正确的 API 调用。

工作流程:
1. 首先使用 api_list_endpoints 查看所有可用的 API 端点
2. 根据用户请求，确定需要调用哪个端点
3. 使用 api_get_schema 获取该端点的详细信息（参数、请求体格式等）
4. 使用 api_call_checker 检查即将执行的 API 调用是否正确
5. 使用 api_execute 执行 API 调用
6. 如果遇到错误，分析错误信息，调整参数后重试
7. 将 API 响应转换为易于理解的自然语言答案

重要规则:
- 不要跳过步骤 1，始终先查看可用的端点
- 在执行 API 调用前，必须先调用 api_get_schema 了解详情
- 在执行 API 调用前，必须使用 api_call_checker 检查参数
- 不要执行任何可能修改数据的操作（POST, PUT, DELETE）除非用户明确要求
- 如果 API 调用失败，分析错误并尝试修复

当前 API: Pet Store API (https://petstore.swagger.io/)
这是一个宠物商店管理 API，可以管理宠物、订单和用户信息。

请根据用户的自然语言请求,智能地调用相应的 API 并返回结果。
"""

# Agent 缓存（延迟初始化）
_agent_auto = None

async def get_agent_auto():
    """获取自动模式agent
    
    注意：checkpointer 和 store 由 langgraph.json 配置，LangGraph 服务器自动注入
    """
    global _agent_auto
    if _agent_auto is None:
        _agent_auto = create_agent(
            model,
            tools,
            system_prompt=system_prompt,
        )
    return _agent_auto

# 导出给 langgraph.json 使用
async def agent_auto():
    """Agent工厂函数，返回API agent"""
    return await get_agent_auto()
