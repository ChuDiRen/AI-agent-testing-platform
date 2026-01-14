"""
API文档解析器 - 多格式API规范解析

支持格式：
- OpenAPI 3.x
- Swagger 2.0
- GraphQL Schema
- Postman Collection
"""
from typing import Any, Dict, List, Optional, Union
import json
import yaml
from pathlib import Path
from datetime import datetime

from core.models import APIEndpoint
from core.logging_config import get_logger

logger = get_logger(__name__)


class APIDocumentParser:
    """
    API文档解析器
    
    核心功能：
    - OpenAPI/Swagger解析
    - GraphQL Schema解析
    - Postman Collection解析
    - 统一数据模型转换
    """
    
    def __init__(self):
        """初始化解析器"""
        self.parser_name = "API文档解析器"
        logger.info(f"{self.parser_name} 初始化完成")
    
    async def parse_document(
        self,
        file_path: Union[str, Path],
        doc_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        解析API文档
        
        Args:
            file_path: 文档路径
            doc_type: 文档类型（openapi/swagger/graphql/postman），不提供则自动检测
        
        Returns:
            解析结果
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文档不存在: {file_path}")
        
        logger.info(f"{self.parser_name} 解析文档: {file_path}")
        
        # 读取文档内容
        content = self._read_file(file_path)
        
        # 自动检测文档类型
        if doc_type is None:
            doc_type = self._detect_document_type(content, file_path)
        
        # 根据类型解析
        if doc_type == "openapi":
            result = self._parse_openapi(content)
        elif doc_type == "swagger":
            result = self._parse_swagger(content)
        elif doc_type == "graphql":
            result = self._parse_graphql(content)
        elif doc_type == "postman":
            result = self._parse_postman(content)
        else:
            raise ValueError(f"不支持的文档类型: {doc_type}")
        
        logger.info(f"{self.parser_name} 解析完成: {len(result.get('endpoints', []))} 个端点")
        return result
    
    def _read_file(self, file_path: Path) -> Dict[str, Any]:
        """读取文件内容"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析为JSON或YAML
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            try:
                return yaml.safe_load(content)
            except yaml.YAMLError:
                # 如果是GraphQL schema，返回原始文本
                return {"raw_content": content}
    
    def _detect_document_type(self, content: Dict[str, Any], file_path: Path) -> str:
        """自动检测文档类型"""
        # 检查OpenAPI
        if "openapi" in content:
            return "openapi"
        
        # 检查Swagger
        if "swagger" in content:
            return "swagger"
        
        # 检查Postman
        if "info" in content and "item" in content:
            return "postman"
        
        # 检查GraphQL（基于文件扩展名）
        if file_path.suffix in [".graphql", ".gql"]:
            return "graphql"
        
        # 默认尝试OpenAPI
        return "openapi"
    
    def _parse_openapi(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """解析OpenAPI 3.x文档"""
        logger.info("解析OpenAPI 3.x文档")
        
        info = content.get("info", {})
        servers = content.get("servers", [])
        paths = content.get("paths", {})
        
        # 解析端点
        endpoints = []
        for path, methods in paths.items():
            for method, spec in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
                    endpoint = self._parse_openapi_endpoint(path, method.upper(), spec)
                    endpoints.append(endpoint)
        
        return {
            "doc_type": "openapi",
            "version": content.get("openapi", "3.0.0"),
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "version_info": info.get("version", ""),
            "servers": servers,
            "endpoints": endpoints,
            "total_endpoints": len(endpoints),
            "parsed_at": datetime.utcnow().isoformat()
        }
    
    def _parse_openapi_endpoint(
        self,
        path: str,
        method: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析单个OpenAPI端点"""
        # 解析参数
        parameters = []
        for param in spec.get("parameters", []):
            parameters.append({
                "name": param.get("name", ""),
                "in": param.get("in", "query"),
                "required": param.get("required", False),
                "type": param.get("schema", {}).get("type", "string"),
                "description": param.get("description", "")
            })
        
        # 解析请求体
        request_body = None
        if "requestBody" in spec:
            content = spec["requestBody"].get("content", {})
            if "application/json" in content:
                request_body = {
                    "required": spec["requestBody"].get("required", False),
                    "schema": content["application/json"].get("schema", {})
                }
        
        # 解析响应
        responses = {}
        for status_code, response_spec in spec.get("responses", {}).items():
            content = response_spec.get("content", {})
            schema = None
            if "application/json" in content:
                schema = content["application/json"].get("schema", {})
            
            responses[status_code] = {
                "description": response_spec.get("description", ""),
                "schema": schema
            }
        
        return {
            "path": path,
            "method": method,
            "summary": spec.get("summary", ""),
            "description": spec.get("description", ""),
            "operation_id": spec.get("operationId", ""),
            "tags": spec.get("tags", []),
            "parameters": parameters,
            "request_body": request_body,
            "responses": responses,
            "deprecated": spec.get("deprecated", False)
        }

    def _parse_swagger(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """解析Swagger 2.0文档"""
        logger.info("解析Swagger 2.0文档")

        info = content.get("info", {})
        base_path = content.get("basePath", "")
        paths = content.get("paths", {})

        # 解析端点
        endpoints = []
        for path, methods in paths.items():
            full_path = base_path + path
            for method, spec in methods.items():
                if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                    endpoint = self._parse_swagger_endpoint(full_path, method.upper(), spec)
                    endpoints.append(endpoint)

        return {
            "doc_type": "swagger",
            "version": content.get("swagger", "2.0"),
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "version_info": info.get("version", ""),
            "base_path": base_path,
            "endpoints": endpoints,
            "total_endpoints": len(endpoints),
            "parsed_at": datetime.utcnow().isoformat()
        }

    def _parse_swagger_endpoint(
        self,
        path: str,
        method: str,
        spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """解析单个Swagger端点"""
        # 解析参数
        parameters = []
        for param in spec.get("parameters", []):
            parameters.append({
                "name": param.get("name", ""),
                "in": param.get("in", "query"),
                "required": param.get("required", False),
                "type": param.get("type", "string"),
                "description": param.get("description", "")
            })

        # 解析响应
        responses = {}
        for status_code, response_spec in spec.get("responses", {}).items():
            responses[status_code] = {
                "description": response_spec.get("description", ""),
                "schema": response_spec.get("schema", {})
            }

        return {
            "path": path,
            "method": method,
            "summary": spec.get("summary", ""),
            "description": spec.get("description", ""),
            "operation_id": spec.get("operationId", ""),
            "tags": spec.get("tags", []),
            "parameters": parameters,
            "responses": responses,
            "deprecated": spec.get("deprecated", False)
        }

    def _parse_graphql(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """解析GraphQL Schema"""
        logger.info("解析GraphQL Schema")

        # 简化实现：提取查询和变更
        raw_content = content.get("raw_content", "")

        # 提取类型定义
        queries = self._extract_graphql_operations(raw_content, "Query")
        mutations = self._extract_graphql_operations(raw_content, "Mutation")

        # 转换为端点格式
        endpoints = []

        for query in queries:
            endpoints.append({
                "path": f"/graphql",
                "method": "POST",
                "summary": f"GraphQL Query: {query}",
                "description": f"执行GraphQL查询: {query}",
                "operation_id": query,
                "tags": ["query"],
                "parameters": [],
                "request_body": {
                    "required": True,
                    "schema": {"type": "object"}
                },
                "responses": {}
            })

        for mutation in mutations:
            endpoints.append({
                "path": f"/graphql",
                "method": "POST",
                "summary": f"GraphQL Mutation: {mutation}",
                "description": f"执行GraphQL变更: {mutation}",
                "operation_id": mutation,
                "tags": ["mutation"],
                "parameters": [],
                "request_body": {
                    "required": True,
                    "schema": {"type": "object"}
                },
                "responses": {}
            })

        return {
            "doc_type": "graphql",
            "title": "GraphQL API",
            "description": "GraphQL API Schema",
            "endpoints": endpoints,
            "total_endpoints": len(endpoints),
            "queries": queries,
            "mutations": mutations,
            "parsed_at": datetime.utcnow().isoformat()
        }

    def _extract_graphql_operations(self, schema: str, operation_type: str) -> List[str]:
        """从GraphQL Schema中提取操作"""
        operations = []

        # 简单的正则匹配（实际应使用GraphQL解析器）
        import re
        pattern = rf"type {operation_type}\s*\{{([^}}]+)\}}"
        match = re.search(pattern, schema, re.DOTALL)

        if match:
            content = match.group(1)
            # 提取字段名
            field_pattern = r"(\w+)\s*(?:\([^)]*\))?\s*:"
            operations = re.findall(field_pattern, content)

        return operations

    def _parse_postman(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """解析Postman Collection"""
        logger.info("解析Postman Collection")

        info = content.get("info", {})
        items = content.get("item", [])

        # 解析端点
        endpoints = []
        self._extract_postman_items(items, endpoints)

        return {
            "doc_type": "postman",
            "title": info.get("name", ""),
            "description": info.get("description", ""),
            "version_info": info.get("version", ""),
            "endpoints": endpoints,
            "total_endpoints": len(endpoints),
            "parsed_at": datetime.utcnow().isoformat()
        }

    def _extract_postman_items(
        self,
        items: List[Dict[str, Any]],
        endpoints: List[Dict[str, Any]],
        parent_path: str = ""
    ):
        """递归提取Postman Collection中的请求"""
        for item in items:
            # 如果是文件夹，递归处理
            if "item" in item:
                folder_name = item.get("name", "")
                self._extract_postman_items(
                    item["item"],
                    endpoints,
                    f"{parent_path}/{folder_name}" if parent_path else folder_name
                )
            # 如果是请求
            elif "request" in item:
                request = item["request"]

                # 提取URL
                url = request.get("url", {})
                if isinstance(url, str):
                    path = url
                else:
                    path = "/".join(url.get("path", []))

                # 提取方法
                method = request.get("method", "GET")

                endpoints.append({
                    "path": f"/{path}",
                    "method": method,
                    "summary": item.get("name", ""),
                    "description": request.get("description", ""),
                    "operation_id": item.get("name", "").replace(" ", "_"),
                    "tags": [parent_path] if parent_path else [],
                    "parameters": [],
                    "request_body": request.get("body", {}),
                    "responses": {}
                })

    def convert_to_api_endpoints(
        self,
        parsed_result: Dict[str, Any]
    ) -> List[APIEndpoint]:
        """将解析结果转换为APIEndpoint模型"""
        endpoints = []

        for endpoint_data in parsed_result.get("endpoints", []):
            endpoint = APIEndpoint(
                endpoint_id=endpoint_data.get("operation_id", ""),
                path=endpoint_data.get("path", ""),
                method=endpoint_data.get("method", "GET"),
                summary=endpoint_data.get("summary", ""),
                description=endpoint_data.get("description", ""),
                parameters=endpoint_data.get("parameters", []),
                request_body=endpoint_data.get("request_body"),
                responses=endpoint_data.get("responses", {}),
                tags=endpoint_data.get("tags", []),
                deprecated=endpoint_data.get("deprecated", False)
            )
            endpoints.append(endpoint)

        return endpoints

    def get_parser_info(self) -> Dict[str, Any]:
        """获取解析器信息"""
        return {
            "parser_name": self.parser_name,
            "supported_formats": [
                "OpenAPI 3.x",
                "Swagger 2.0",
                "GraphQL Schema",
                "Postman Collection"
            ],
            "capabilities": [
                "自动格式检测",
                "端点提取",
                "参数解析",
                "响应Schema解析"
            ],
            "status": "active"
        }


