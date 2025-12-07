"""
Swagger/OpenAPI 解析器
支持 OpenAPI 2.0 (Swagger) 和 3.0 规范
"""
import json
from typing import Dict, List, Any, Optional

import httpx
from core.logger import get_logger

logger = get_logger(__name__)


class SwaggerParser:
    """Swagger/OpenAPI 解析器"""
    
    def __init__(self, swagger_data: Dict[str, Any], source_url: str = None):
        """
        初始化解析器
        :param swagger_data: Swagger/OpenAPI JSON数据
        :param source_url: Swagger文档来源URL(用于推断基础URL)
        """
        self.data = swagger_data
        self.version = self._detect_version()
        self.source_url = source_url
        self.base_url = self._get_base_url()
        # 缓存已解析的$ref,避免循环引用
        self._ref_cache = {}
        # 提取安全方案定义（用于后续判断接口是否需要认证）
        self.security_schemes = self._extract_security_schemes()
        # 检查是否有全局security配置
        self.global_security = self.data.get('security', [])
        
    def _detect_version(self) -> str:
        """检测OpenAPI版本"""
        if 'swagger' in self.data:
            return '2.0'
        elif 'openapi' in self.data:
            version = self.data['openapi']
            if version.startswith('3.'):
                return '3.0'
        return 'unknown'
    
    def _extract_security_schemes(self) -> Dict[str, Dict[str, Any]]:
        """
        提取安全方案定义
        :return: 安全方案字典 {scheme_name: header_info}
        """
        schemes = {}
        
        # OpenAPI 3.0: components.securitySchemes
        if self.version == '3.0':
            security_schemes = self.data.get('components', {}).get('securitySchemes', {})
            for scheme_name, scheme in security_schemes.items():
                if scheme.get('type') == 'apiKey' and scheme.get('in') == 'header':
                    schemes[scheme_name] = {
                        'name': scheme.get('name', 'Authorization'),
                        'type': 'string',
                        'required': False,
                        'description': scheme.get('description', f'{scheme_name} 认证'),
                        'default': '',
                        'enum': None
                    }
                elif scheme.get('type') == 'http':
                    # Bearer Token
                    schemes[scheme_name] = {
                        'name': 'Authorization',
                        'type': 'string',
                        'required': False,
                        'description': scheme.get('description', 'Bearer Token认证'),
                        'default': 'Bearer <token>',
                        'enum': None
                    }
        
        # OpenAPI 2.0: securityDefinitions
        elif self.version == '2.0':
            security_defs = self.data.get('securityDefinitions', {})
            for scheme_name, scheme in security_defs.items():
                if scheme.get('type') == 'apiKey' and scheme.get('in') == 'header':
                    schemes[scheme_name] = {
                        'name': scheme.get('name', 'Authorization'),
                        'type': 'string',
                        'required': False,
                        'description': scheme.get('description', f'{scheme_name} 认证'),
                        'default': '',
                        'enum': None
                    }
        
        return schemes
    
    def _get_operation_auth_headers(self, operation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        获取接口需要的认证Header
        根据OpenAPI规范：
        - 如果接口有security配置，使用接口级配置
        - 如果接口security为空数组[]，表示不需要认证
        - 否则使用全局security配置
        :param operation: 接口操作定义
        :return: 认证Header列表
        """
        headers = []
        
        # 确定使用哪个security配置
        operation_security = operation.get('security')
        if operation_security is not None:
            # 接口有自己的security配置
            if not operation_security:  # 空数组表示不需要认证
                return []
            security_requirements = operation_security
        else:
            # 使用全局security配置
            if not self.global_security:  # 没有全局security配置
                return []
            security_requirements = self.global_security
        
        # 根据security requirements添加对应的header
        added_headers = set()
        for requirement in security_requirements:
            if isinstance(requirement, dict):
                for scheme_name in requirement.keys():
                    if scheme_name in self.security_schemes:
                        header_info = self.security_schemes[scheme_name]
                        header_name = header_info['name']
                        if header_name not in added_headers:
                            headers.append(header_info.copy())
                            added_headers.add(header_name)
        
        return headers
    
    def _generate_api_name_from_path(self, path: str) -> str:
        """
        从路径生成接口名
        :param path: API路径,如 /user/login 或 /GenTable/update 或 /user/roles/{user_id}
        :return: 接口名,如 user_login 或 GenTable_update 或 user_roles
        """
        # 移除开头的 /
        path = path.lstrip('/')
        
        # 移除路径参数 {xxx}
        import re
        path = re.sub(r'\{[^}]+\}', '', path)
        
        # 移除多余的斜杠
        path = re.sub(r'/+', '/', path).strip('/')
        
        # 替换 / 为 _
        api_name = path.replace('/', '_')
        
        return api_name if api_name else 'root'
    
    def _get_base_url(self) -> str:
        """获取基础URL"""
        if self.version == '2.0':
            # Swagger 2.0: schemes + host + basePath
            schemes = self.data.get('schemes', ['http'])
            host = self.data.get('host', '')
            base_path = self.data.get('basePath', '')
            if host:
                return f"{schemes[0]}://{host}{base_path}"
            return base_path
        elif self.version == '3.0':
            # OpenAPI 3.0: servers[0].url
            servers = self.data.get('servers', [])
            if servers:
                server_url = servers[0].get('url', '')
                # 如果是完整URL(包含http/https),直接返回
                if server_url.startswith('http://') or server_url.startswith('https://'):
                    return server_url
                # 如果是相对路径,尝试从source_url推断
                if self.source_url and server_url:
                    # 从source_url提取基础URL: http://localhost:5000/openapi.json -> http://localhost:5000
                    from urllib.parse import urlparse
                    parsed = urlparse(self.source_url)
                    base = f"{parsed.scheme}://{parsed.netloc}"
                    # 如果server_url是/开头,直接拼接
                    if server_url.startswith('/'):
                        return f"{base}{server_url}"
                    else:
                        return f"{base}/{server_url}"
                return server_url if server_url else ''
        return ''
    
    def parse_apis(self) -> List[Dict[str, Any]]:
        """
        解析所有API接口
        :return: API接口列表
        """
        apis = []
        paths = self.data.get('paths', {})
        
        for path, path_item in paths.items():
            # 遍历每个HTTP方法
            for method in ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                if method in path_item:
                    operation = path_item[method]
                    api_info = self._parse_operation(path, method.upper(), operation)
                    if api_info:
                        apis.append(api_info)
        
        logger.info(f"解析完成,共找到 {len(apis)} 个API接口")
        return apis
    
    def _parse_operation(self, path: str, method: str, operation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析单个API操作
        :param path: 路径
        :param method: HTTP方法
        :param operation: 操作定义
        :return: API信息字典
        """
        try:
            # 构建完整URL
            full_url = f"{self.base_url}{path}"
            # 如果是相对路径且没有基础URL,从source_url推断
            if full_url.startswith('/') and self.source_url:
                from urllib.parse import urlparse
                parsed = urlparse(self.source_url)
                full_url = f"{parsed.scheme}://{parsed.netloc}{full_url}"
            
            # 基本信息 - 只返回ApiInfo模型支持的字段
            api_info = {
                'api_name': operation.get('summary', operation.get('operationId', f"{method} {path}")),
                'request_method': method,
                'request_url': full_url
            }
            
            # 解析参数
            parameters = self._parse_parameters(operation.get('parameters', []))
            api_info.update(parameters)
            
            # 解析请求体 (OpenAPI 3.0)
            if self.version == '3.0' and 'requestBody' in operation:
                request_body = self._parse_request_body_v3(operation['requestBody'])
                # 合并请求头
                if 'request_headers' in request_body and 'request_headers' in api_info:
                    # 合并两个Header列表
                    existing_headers = json.loads(api_info['request_headers']) if api_info['request_headers'] else []
                    new_headers = json.loads(request_body['request_headers'])
                    existing_headers.extend(new_headers)
                    request_body['request_headers'] = json.dumps(existing_headers, ensure_ascii=False)
                api_info.update(request_body)
            
            # 根据接口的security配置添加认证Header
            auth_headers = self._get_operation_auth_headers(operation)
            if auth_headers:
                existing_headers = json.loads(api_info.get('request_headers', 'null') or '[]')
                if not isinstance(existing_headers, list):
                    existing_headers = []
                # 避免重复添加(检查header name)
                existing_names = {h.get('name') for h in existing_headers if isinstance(h, dict)}
                for auth_header in auth_headers:
                    if auth_header['name'] not in existing_names:
                        existing_headers.append(auth_header)
                api_info['request_headers'] = json.dumps(existing_headers, ensure_ascii=False) if existing_headers else None
            
            return api_info
            
        except Exception as e:
            logger.error(f"解析API失败 {method} {path}: {e}")
            return None
    
    def _parse_parameters(self, parameters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        解析参数列表 (支持OpenAPI 2.0和3.0)
        :param parameters: 参数列表
        :return: 解析后的参数字典
        """
        result = {
            'request_params': [],  # query参数
            'request_headers': [],  # header参数
            'path_params': [],  # path参数
            'request_form_datas': [],  # formData参数
        }
        
        for param in parameters:
            param_in = param.get('in', '')
            
            # OpenAPI 3.0: 参数类型在schema中
            if 'schema' in param:
                schema = param.get('schema', {})
                param_type = schema.get('type', 'string')
                param_default = schema.get('default', '')
                param_enum = schema.get('enum', [])
            else:
                # OpenAPI 2.0: 参数类型直接在参数对象中
                param_type = param.get('type', 'string')
                param_default = param.get('default', '')
                param_enum = param.get('enum', [])
            
            param_info = {
                'name': param.get('name', ''),
                'type': param_type,
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'default': param_default,
                'enum': param_enum if param_enum else None
            }
            
            if param_in == 'query':
                result['request_params'].append(param_info)
            elif param_in == 'header':
                result['request_headers'].append(param_info)
            elif param_in == 'path':
                result['path_params'].append(param_info)
            elif param_in == 'formData':
                result['request_form_datas'].append(param_info)
            elif param_in == 'body':
                # Swagger 2.0 body参数
                schema = param.get('schema', {})
                result['requests_json_data'] = json.dumps(self._generate_example_from_schema(schema), ensure_ascii=False, indent=2)
        
        # 转换为JSON字符串
        result['request_params'] = json.dumps(result['request_params'], ensure_ascii=False) if result['request_params'] else None
        result['request_headers'] = json.dumps(result['request_headers'], ensure_ascii=False) if result['request_headers'] else None
        result['request_form_datas'] = json.dumps(result['request_form_datas'], ensure_ascii=False) if result['request_form_datas'] else None
        
        # 移除path_params,因为ApiInfo模型不支持
        result.pop('path_params', None)
        
        return result
    
    def _parse_request_body_v3(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析OpenAPI 3.0的requestBody
        :param request_body: requestBody定义
        :return: 请求体信息
        """
        result = {}
        content = request_body.get('content', {})
        content_type = None
        
        # 优先处理JSON
        if 'application/json' in content:
            content_type = 'application/json'
            schema = content['application/json'].get('schema', {})
            result['requests_json_data'] = json.dumps(
                self._generate_example_from_schema(schema), 
                ensure_ascii=False, 
                indent=2
            )
        # 处理form-data
        elif 'multipart/form-data' in content:
            content_type = 'multipart/form-data'
            schema = content['multipart/form-data'].get('schema', {})
            form_fields = self._extract_form_fields(schema)
            result['request_form_datas'] = json.dumps(form_fields, ensure_ascii=False)
        # 处理x-www-form-urlencoded
        elif 'application/x-www-form-urlencoded' in content:
            content_type = 'application/x-www-form-urlencoded'
            schema = content['application/x-www-form-urlencoded'].get('schema', {})
            form_fields = self._extract_form_fields(schema)
            result['request_www_form_datas'] = json.dumps(form_fields, ensure_ascii=False)
        
        # 添加Content-Type到请求头
        if content_type:
            content_type_header = {
                'name': 'Content-Type',
                'type': 'string',
                'required': True,
                'description': '请求内容类型',
                'default': content_type,
                'enum': None
            }
            result['request_headers'] = json.dumps([content_type_header], ensure_ascii=False)
        
        return result
    
    def _resolve_ref(self, ref_path: str) -> Optional[Dict[str, Any]]:
        """
        解析$ref引用
        :param ref_path: 引用路径,如 #/components/schemas/Pet
        :return: 引用的schema
        """
        if not ref_path.startswith('#/'):
            return None
        
        # 移除 # 并按 / 分割
        parts = ref_path[2:].split('/')
        
        # 从根数据开始导航
        current = self.data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current if isinstance(current, dict) else None
    
    def _extract_form_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从schema中提取表单字段"""
        fields = []
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        for field_name, field_schema in properties.items():
            fields.append({
                'name': field_name,
                'type': field_schema.get('type', 'string'),
                'required': field_name in required,
                'description': field_schema.get('description', ''),
                'default': field_schema.get('default', '')
            })
        
        return fields
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Any:
        """
        从schema生成示例数据 (参考openapi-to-postman实现)
        :param schema: JSON Schema
        :return: 示例数据
        """
        if not schema:
            return {}
        
        # 优先使用example字段
        if 'example' in schema:
            return schema['example']
        
        # 处理$ref引用
        if '$ref' in schema:
            ref_path = schema['$ref']
            # 避免循环引用
            if ref_path in self._ref_cache:
                return self._ref_cache[ref_path]
            
            # 解析引用: #/components/schemas/Pet 或 #/definitions/Pet
            ref_schema = self._resolve_ref(ref_path)
            if ref_schema:
                # 标记为正在解析,避免循环
                self._ref_cache[ref_path] = {}
                result = self._generate_example_from_schema(ref_schema)
                self._ref_cache[ref_path] = result
                return result
            else:
                # 无法解析,返回引用名称
                ref_name = ref_path.split('/')[-1]
                return f"<{ref_name}>"
        
        # 处理allOf, oneOf, anyOf
        if 'allOf' in schema:
            result = {}
            for sub_schema in schema['allOf']:
                result.update(self._generate_example_from_schema(sub_schema))
            return result
        
        if 'oneOf' in schema or 'anyOf' in schema:
            schemas = schema.get('oneOf', schema.get('anyOf', []))
            if schemas:
                return self._generate_example_from_schema(schemas[0])
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            example = {}
            properties = schema.get('properties', {})
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_example_from_schema(prop_schema)
            return example if example else {}
        
        elif schema_type == 'array':
            items = schema.get('items', {})
            return [self._generate_example_from_schema(items)]
        
        elif schema_type == 'string':
            # 根据format生成更合适的示例
            fmt = schema.get('format', '')
            if fmt == 'date':
                return '2024-01-01'
            elif fmt == 'date-time':
                return '2024-01-01T00:00:00Z'
            elif fmt == 'email':
                return 'user@example.com'
            elif fmt == 'uri':
                return 'https://example.com'
            elif 'enum' in schema:
                return schema['enum'][0] if schema['enum'] else 'string'
            return schema.get('default', 'string')
        
        elif schema_type == 'integer':
            if 'enum' in schema:
                return schema['enum'][0] if schema['enum'] else 0
            return schema.get('default', 0)
        
        elif schema_type == 'number':
            if 'enum' in schema:
                return schema['enum'][0] if schema['enum'] else 0.0
            return schema.get('default', 0.0)
        
        elif schema_type == 'boolean':
            return schema.get('default', False)
        
        else:
            return None


async def fetch_swagger_from_url(url: str) -> Dict[str, Any]:
    """
    从URL获取Swagger JSON (异步版本，避免自请求死锁)
    :param url: Swagger JSON URL
    :return: Swagger数据
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"获取Swagger失败: {e}")
        raise ValueError(f"无法获取Swagger文档: {e}")
