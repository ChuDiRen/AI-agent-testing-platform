"""
API文档解析器

支持多种API文档格式：
- OpenAPI/Swagger
- GraphQL
- REST API
- Postman Collection

核心功能：
1. 解析API文档结构
2. 提取接口信息
3. 生成测试规范
4. 识别依赖关系
"""
import asyncio
import json
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import re

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class APIEndpoint(BaseModel):
    """API端点信息"""
    path: str = Field(description="API路径")
    method: str = Field(description="HTTP方法")
    description: str = Field(default="", description="接口描述")
    parameters: List[Dict[str, Any]] = Field(default_factory=list, description="参数列表")
    request_body: Optional[Dict[str, Any]] = Field(default=None, description="请求体")
    responses: Dict[str, Any] = Field(default_factory=dict, description="响应定义")
    security: List[Dict[str, Any]] = Field(default_factory=list, description="安全配置")
    tags: List[str] = Field(default_factory=list, description="标签")


class APISpec(BaseModel):
    """API规范信息"""
    title: str = Field(description="API标题")
    version: str = Field(description="API版本")
    description: str = Field(default="", description="API描述")
    servers: List[Dict[str, str]] = Field(default_factory=list, description="服务器列表")
    endpoints: List[APIEndpoint] = Field(default_factory=list, description="端点列表")
    schemas: Dict[str, Any] = Field(default_factory=dict, description="数据模式")
    security_definitions: Dict[str, Any] = Field(default_factory=dict, description="安全定义")


class APIDocumentParser:
    """API文档解析器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.3,
            base_url="https://api.deepseek.com/v1",
            api_key="sk-f79fae69b11a4fce88e04805bd6314b7"
        )
        
        # 支持的文档格式
        self.supported_formats = {
            'openapi': self._parse_openapi,
            'swagger': self._parse_swagger,
            'graphql': self._parse_graphql,
            'rest': self._parse_rest,
            'postman': self._parse_postman
        }
    
    async def parse_document(self, doc_content: str, doc_type: str = "openapi") -> APISpec:
        """解析API文档"""
        if doc_type not in self.supported_formats:
            raise ValueError(f"不支持的文档类型: {doc_type}")
        
        parser = self.supported_formats[doc_type]
        api_spec = await parser(doc_content)
        
        return api_spec
    
    async def _parse_openapi(self, doc_content: str) -> APISpec:
        """解析OpenAPI/Swagger文档"""
        try:
            # 尝试解析YAML
            if doc_content.strip().startswith('openapi:') or doc_content.strip().startswith('swagger:'):
                spec_data = yaml.safe_load(doc_content)
            else:
                # 尝试解析JSON
                spec_data = json.loads(doc_content)
        except:
            # 如果解析失败，使用LLM分析
            spec_data = await self._analyze_with_llm(doc_content, "openapi")
        
        # 提取基本信息
        openapi_version = spec_data.get('openapi', spec_data.get('swagger', '3.0.0'))
        info = spec_data.get('info', {})
        
        api_spec = APISpec(
            title=info.get('title', 'API'),
            version=info.get('version', '1.0.0'),
            description=info.get('description', ''),
            servers=spec_data.get('servers', []),
            schemas=spec_data.get('components', {}).get('schemas', spec_data.get('definitions', {}))
        )
        
        # 提取端点信息
        paths = spec_data.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    endpoint = APIEndpoint(
                        path=path,
                        method=method.upper(),
                        description=details.get('summary', details.get('description', '')),
                        parameters=details.get('parameters', []),
                        request_body=details.get('requestBody'),
                        responses=details.get('responses', {}),
                        security=details.get('security', []),
                        tags=details.get('tags', [])
                    )
                    api_spec.endpoints.append(endpoint)
        
        # 提取安全定义
        security_definitions = spec_data.get('components', {}).get('securitySchemes', spec_data.get('securityDefinitions', {}))
        api_spec.security_definitions = security_definitions
        
        return api_spec
    
    async def _parse_swagger(self, doc_content: str) -> APISpec:
        """解析Swagger文档"""
        # Swagger 2.0解析逻辑
        try:
            spec_data = yaml.safe_load(doc_content)
        except:
            spec_data = json.loads(doc_content)
        
        info = spec_data.get('info', {})
        
        api_spec = APISpec(
            title=info.get('title', 'API'),
            version=info.get('version', '1.0.0'),
            description=info.get('description', ''),
            servers=spec_data.get('host', ''),
            schemas=spec_data.get('definitions', {})
        )
        
        # 提取端点信息
        paths = spec_data.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    endpoint = APIEndpoint(
                        path=path,
                        method=method.upper(),
                        description=details.get('summary', details.get('description', '')),
                        parameters=details.get('parameters', []),
                        request_body=details.get('body'),
                        responses=details.get('responses', {}),
                        security=details.get('security', [])
                    )
                    api_spec.endpoints.append(endpoint)
        
        return api_spec
    
    async def _parse_graphql(self, doc_content: str) -> APISpec:
        """解析GraphQL文档"""
        # GraphQL schema解析
        schema_lines = doc_content.split('\n')
        
        api_spec = APISpec(
            title="GraphQL API",
            version="1.0.0",
            description="GraphQL Schema"
        )
        
        # 提取类型定义
        current_type = None
        for line in schema_lines:
            line = line.strip()
            if line.startswith('type '):
                current_type = line.split()[1]
                api_spec.endpoints.append(APIEndpoint(
                    path=f"/graphql/{current_type}",
                    method="POST",
                    description=f"GraphQL {current_type} operations"
                ))
            elif line.startswith('input '):
                current_input = line.split()[1]
                # 处理输入类型
                pass
        
        return api_spec
    
    async def _parse_rest(self, doc_content: str) -> APISpec:
        """解析REST API文档"""
        # REST API文档解析（Markdown格式）
        api_spec = APISpec(
            title="REST API",
            version="1.0.0",
            description="REST API Documentation"
        )
        
        # 使用LLM分析REST API文档
        analysis = await self._analyze_with_llm(doc_content, "rest")
        
        # 提取端点信息
        for endpoint_info in analysis.get('endpoints', []):
            endpoint = APIEndpoint(
                path=endpoint_info.get('path', '/'),
                method=endpoint_info.get('method', 'GET'),
                description=endpoint_info.get('description', ''),
                parameters=endpoint_info.get('parameters', [])
            )
            api_spec.endpoints.append(endpoint)
        
        return api_spec
    
    async def _parse_postman(self, doc_content: str) -> APISpec:
        """解析Postman Collection"""
        try:
            collection_data = json.loads(doc_content)
        except:
            # 如果解析失败，使用LLM分析
            collection_data = await self._analyze_with_llm(doc_content, "postman")
        
        info = collection_data.get('info', {})
        
        api_spec = APISpec(
            title=info.get('name', 'Postman Collection'),
            version=info.get('version', '1.0.0'),
            description=info.get('description', '')
        )
        
        # 提取请求信息
        for item in collection_data.get('item', []):
            if 'request' in item:
                request = item['request']
                url = request.get('url', {})
                method = request.get('method', 'GET')
                path = url.get('raw', '/')
                
                endpoint = APIEndpoint(
                    path=path,
                    method=method.upper(),
                    description=item.get('name', ''),
                    parameters=url.get('query', [])
                )
                api_spec.endpoints.append(endpoint)
        
        return api_spec
    
    async def _analyze_with_llm(self, doc_content: str, doc_type: str) -> Dict[str, Any]:
        """使用LLM分析文档内容"""
        prompt = f"""
        分析以下{doc_type} API文档，提取结构化信息：
        
        文档内容：
        {doc_content[:2000]}  # 限制长度
        
        请提取以下信息并返回JSON格式：
        {{
            "title": "API标题",
            "version": "API版本", 
            "description": "API描述",
            "endpoints": [
                {{
                    "path": "/api/endpoint",
                    "method": "GET",
                    "description": "接口描述",
                    "parameters": []
                }}
            ]
        }}
        """
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            data = json.loads(response.content)
            return data
        except:
            # 如果解析失败，返回基本结构
            return {
                "title": f"{doc_type.upper()} API",
                "version": "1.0.0",
                "description": "API Documentation",
                "endpoints": []
            }
    
    async def extract_test_scenarios(self, api_spec: APISpec) -> List[Dict[str, Any]]:
        """提取测试场景"""
        test_scenarios = []
        
        for endpoint in api_spec.endpoints:
            # 功能测试场景
            functional_scenario = {
                "type": "functional",
                "endpoint": endpoint.path,
                "method": endpoint.method,
                "scenario": f"测试{endpoint.description}的基本功能",
                "test_cases": [
                    f"验证{endpoint.path}的正常响应",
                    f"测试{endpoint.method}方法的参数验证"
                ]
            }
            test_scenarios.append(functional_scenario)
            
            # 安全测试场景
            if endpoint.security:
                security_scenario = {
                    "type": "security",
                    "endpoint": endpoint.path,
                    "method": endpoint.method,
                    "scenario": f"测试{endpoint.path}的安全认证",
                    "test_cases": [
                        "验证认证头",
                        "测试权限控制",
                        "检查敏感信息泄露"
                    ]
                }
                test_scenarios.append(security_scenario)
            
            # 边界条件测试
            boundary_scenario = {
                "type": "boundary",
                "endpoint": endpoint.path,
                "method": endpoint.method,
                "scenario": f"测试{endpoint.path}的边界条件",
                "test_cases": [
                    "测试参数边界值",
                    "验证异常输入处理",
                    "检查响应格式"
                ]
            }
            test_scenarios.append(boundary_scenario)
        
        return test_scenarios
    
    async def identify_dependencies(self, api_spec: APISpec) -> List[Dict[str, Any]]:
        """识别API依赖关系"""
        dependencies = []
        
        # 分析端点之间的依赖关系
        for i, endpoint in enumerate(api_spec.endpoints):
            for j, other_endpoint in enumerate(api_spec.endpoints):
                if i != j:
                    # 检查路径依赖
                    if endpoint.path in other_endpoint.path or other_endpoint.path in endpoint.path:
                        dependencies.append({
                            "source": endpoint.path,
                            "target": other_endpoint.path,
                            "relationship": "depends_on",
                            "type": "path_dependency"
                        })
                    
                    # 检查参数依赖
                    source_params = set(p.get('name', '') for p in endpoint.parameters)
                    target_params = set(p.get('name', '') for p in other_endpoint.parameters)
                    
                    if source_params & target_params:
                        dependencies.append({
                            "source": endpoint.path,
                            "target": other_endpoint.path,
                            "relationship": "shares_parameters",
                            "type": "parameter_dependency"
                        })
        
        return dependencies
    
    async def generate_api_summary(self, api_spec: APISpec) -> Dict[str, Any]:
        """生成API摘要"""
        summary = {
            "basic_info": {
                "title": api_spec.title,
                "version": api_spec.version,
                "description": api_spec.description,
                "endpoints_count": len(api_spec.endpoints)
            },
            "endpoint_analysis": {
                "methods": {},
                "tags": {},
                "security": {}
            },
            "complexity_metrics": {
                "avg_parameters_per_endpoint": 0,
                "complexity_score": 0,
                "security_coverage": 0
            }
        }
        
        # 分析端点方法分布
        for endpoint in api_spec.endpoints:
            method = endpoint.method
            summary["endpoint_analysis"]["methods"][method] = summary["endpoint_analysis"]["methods"].get(method, 0) + 1
            
            # 分析标签分布
            for tag in endpoint.tags:
                summary["endpoint_analysis"]["tags"][tag] = summary["endpoint_analysis"]["tags"].get(tag, 0) + 1
            
            # 分析安全配置
            if endpoint.security:
                summary["endpoint_analysis"]["security"]["secured_endpoints"] = summary["endpoint_analysis"]["security"].get("secured_endpoints", 0) + 1
        
        # 计算复杂度指标
        if api_spec.endpoints:
            total_params = sum(len(ep.parameters) for ep in api_spec.endpoints)
            summary["complexity_metrics"]["avg_parameters_per_endpoint"] = total_params / len(api_spec.endpoints)
            summary["complexity_metrics"]["complexity_score"] = len(api_spec.endpoints) * (total_params / max(len(api_spec.endpoints), 1))
        
        return summary
