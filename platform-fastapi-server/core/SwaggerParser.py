"""
Swagger/OpenAPI 解析器
支持 OpenAPI 2.0 (Swagger) 和 3.0 规范

优化重构版本 - 更清晰的结构和更友好的参数处理
"""
import json
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from enum import Enum

import httpx
from core.logger import get_logger

logger = get_logger(__name__)


class ParamLocation(Enum):
    """参数位置枚举"""
    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    FORM_DATA = "formData"
    BODY = "body"


@dataclass
class ParamInfo:
    """参数信息数据类"""
    name: str
    type: str = "string"
    required: bool = False
    description: str = ""
    default: Any = ""
    enum: Optional[List[Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，排除None值的enum"""
        return {
            'name': self.name,
            'type': self.type,
            'required': self.required,
            'description': self.description,
            'default': self.default,
            'enum': self.enum
        }


@dataclass
class ApiResult:
    """API解析结果数据类"""
    name: str
    method: str
    url: str
    request_params: List[ParamInfo] = field(default_factory=list)
    request_headers: List[ParamInfo] = field(default_factory=list)
    request_form_datas: List[ParamInfo] = field(default_factory=list)
    request_www_form_datas: List[ParamInfo] = field(default_factory=list)
    requests_json_data: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为API存储格式"""
        result = {
            'name': self.name,
            'method': self.method,
            'url': self.url,
        }
        
        # 转换参数列表为JSON字符串
        if self.request_params:
            result['request_params'] = json.dumps(
                [p.to_dict() for p in self.request_params], 
                ensure_ascii=False
            )
        else:
            result['request_params'] = None
            
        if self.request_headers:
            result['request_headers'] = json.dumps(
                [p.to_dict() for p in self.request_headers], 
                ensure_ascii=False
            )
        else:
            result['request_headers'] = None
            
        if self.request_form_datas:
            result['request_form_datas'] = json.dumps(
                [p.to_dict() for p in self.request_form_datas], 
                ensure_ascii=False
            )
        else:
            result['request_form_datas'] = None
            
        if self.request_www_form_datas:
            result['request_www_form_datas'] = json.dumps(
                [p.to_dict() for p in self.request_www_form_datas], 
                ensure_ascii=False
            )
        else:
            result['request_www_form_datas'] = None
            
        if self.requests_json_data:
            result['requests_json_data'] = self.requests_json_data
            
        return result


class SwaggerParser:
    """
    Swagger/OpenAPI 解析器
    
    支持特性：
    - OpenAPI 2.0 (Swagger) 和 3.0 规范
    - 路径参数自动解析并合并到URL参数中
    - 安全认证头自动提取
    - $ref 引用解析（支持循环引用检测）
    - 多种请求体格式（JSON、FormData、URLEncoded）
    """
    
    # 支持的HTTP方法
    HTTP_METHODS = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']
    
    def __init__(self, swagger_data: Dict[str, Any], source_url: str = None):
        """
        初始化解析器
        
        Args:
            swagger_data: Swagger/OpenAPI JSON数据
            source_url: Swagger文档来源URL(用于推断基础URL)
        """
        self.data = swagger_data
        self.source_url = source_url
        self.version = self._detect_version()
        self.base_url = self._build_base_url()
        
        # 缓存已解析的$ref，避免循环引用
        self._ref_cache: Dict[str, Any] = {}
        
        # 安全相关
        self.security_schemes = self._parse_security_schemes()
        self.global_security = self.data.get('security', [])
        
    # ==================== 版本检测 ====================
    
    def _detect_version(self) -> str:
        """检测OpenAPI版本"""
        if 'swagger' in self.data:
            return '2.0'
        if 'openapi' in self.data:
            version = self.data['openapi']
            return '3.0' if version.startswith('3.') else 'unknown'
        return 'unknown'
    
    # ==================== URL构建 ====================
    
    def _build_base_url(self) -> str:
        """构建基础URL"""
        if self.version == '2.0':
            return self._build_base_url_v2()
        elif self.version == '3.0':
            return self._build_base_url_v3()
        return ''
    
    def _build_base_url_v2(self) -> str:
        """OpenAPI 2.0: schemes + host + basePath"""
        schemes = self.data.get('schemes', ['http'])
        host = self.data.get('host', '')
        base_path = self.data.get('basePath', '')
        
        if host:
            return f"{schemes[0]}://{host}{base_path}"
        return base_path
    
    def _build_base_url_v3(self) -> str:
        """OpenAPI 3.0: servers[0].url"""
        servers = self.data.get('servers', [])
        if not servers:
            return ''
            
        server_url = servers[0].get('url', '')
        
        # 完整URL直接返回
        if server_url.startswith(('http://', 'https://')):
            return server_url
            
        # 相对路径需要从source_url推断
        if self.source_url and server_url:
            parsed = urlparse(self.source_url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            separator = '' if server_url.startswith('/') else '/'
            return f"{base}{separator}{server_url}"
            
        return server_url
    
    def _build_full_url(self, path: str) -> str:
        """构建完整的API URL"""
        full_url = f"{self.base_url}{path}"
        
        # 相对路径且有source_url时，补全协议和主机
        if full_url.startswith('/') and self.source_url:
            parsed = urlparse(self.source_url)
            full_url = f"{parsed.scheme}://{parsed.netloc}{full_url}"
            
        return full_url
    
    # ==================== 安全认证 ====================
    
    def _parse_security_schemes(self) -> Dict[str, ParamInfo]:
        """解析安全方案定义"""
        schemes = {}
        
        if self.version == '3.0':
            security_schemes = self.data.get('components', {}).get('securitySchemes', {})
        else:  # 2.0
            security_schemes = self.data.get('securityDefinitions', {})
            
        for scheme_name, scheme in security_schemes.items():
            header_info = self._parse_single_security_scheme(scheme_name, scheme)
            if header_info:
                schemes[scheme_name] = header_info
                
        return schemes
    
    def _parse_single_security_scheme(self, name: str, scheme: Dict[str, Any]) -> Optional[ParamInfo]:
        """解析单个安全方案"""
        scheme_type = scheme.get('type', '')
        
        # API Key in Header
        if scheme_type == 'apiKey' and scheme.get('in') == 'header':
            return ParamInfo(
                name=scheme.get('name', 'Authorization'),
                type='string',
                required=False,
                description=scheme.get('description', f'{name} 认证'),
                default=''
            )
            
        # HTTP Bearer Token
        if scheme_type == 'http':
            return ParamInfo(
                name='Authorization',
                type='string',
                required=False,
                description=scheme.get('description', 'Bearer Token认证'),
                default='Bearer <token>'
            )
            
        return None
    
    def _get_auth_headers(self, operation: Dict[str, Any]) -> List[ParamInfo]:
        """
        获取接口需要的认证Header
        
        规则：
        - 接口有security配置 → 使用接口级配置
        - 接口security为空数组[] → 不需要认证
        - 否则 → 使用全局security配置
        """
        # 确定使用哪个security配置
        operation_security = operation.get('security')
        
        if operation_security is not None:
            if not operation_security:  # 空数组表示不需要认证
                return []
            security_requirements = operation_security
        else:
            if not self.global_security:
                return []
            security_requirements = self.global_security
        
        # 收集认证Header（去重）
        headers = []
        added_names = set()
        
        for requirement in security_requirements:
            if not isinstance(requirement, dict):
                continue
            for scheme_name in requirement.keys():
                if scheme_name in self.security_schemes:
                    header = self.security_schemes[scheme_name]
                    if header.name not in added_names:
                        headers.append(ParamInfo(
                            name=header.name,
                            type=header.type,
                            required=header.required,
                            description=header.description,
                            default=header.default
                        ))
                        added_names.add(header.name)
        
        return headers
    
    # ==================== 主解析逻辑 ====================
    
    def parse_apis(self) -> List[Dict[str, Any]]:
        """
        解析所有API接口
        
        Returns:
            API接口列表，每个元素为可直接存储的字典格式
        """
        apis = []
        paths = self.data.get('paths', {})
        
        for path, path_item in paths.items():
            for method in self.HTTP_METHODS:
                if method not in path_item:
                    continue
                    
                operation = path_item[method]
                api_result = self._parse_operation(path, method.upper(), operation)
                
                if api_result:
                    apis.append(api_result.to_dict())
        
        logger.info(f"解析完成，共找到 {len(apis)} 个API接口")
        return apis
    
    def _parse_operation(self, path: str, method: str, operation: Dict[str, Any]) -> Optional[ApiResult]:
        """解析单个API操作"""
        try:
            # 基本信息
            name = self._get_api_name(operation, method, path)
            full_url = self._build_full_url(path)
            
            logger.debug(f"解析API - {method} {path} -> {name}")
            
            # 创建结果对象
            result = ApiResult(name=name, method=method, url=full_url)
            
            # 解析参数（路径参数不会放入request_params，只解析query/header/body等）
            self._parse_parameters(operation.get('parameters', []), result)
            
            # 解析请求体 (OpenAPI 3.0)
            if self.version == '3.0' and 'requestBody' in operation:
                self._parse_request_body(operation['requestBody'], result)
            
            # 添加认证Header
            auth_headers = self._get_auth_headers(operation)
            self._merge_headers(result, auth_headers)
            
            return result
            
        except Exception as e:
            logger.error(f"解析API失败 {method} {path}: {e}")
            return None
    
    def _get_api_name(self, operation: Dict[str, Any], method: str, path: str) -> str:
        """获取API名称，优先级：summary > operationId > fallback"""
        summary = operation.get('summary', '').strip()
        operation_id = operation.get('operationId', '').strip()
        fallback = f"{method} {path}"
        
        return summary or operation_id or fallback
    
    # ==================== 参数解析 ====================
    
    def _parse_parameters(self, parameters: List[Dict[str, Any]], result: ApiResult) -> None:
        """
        解析参数列表
        
        注意：路径参数(path)不会放入request_params，因为它们已经体现在URL模板中
        用户需要在发送请求前手动替换URL中的{param}占位符
        """
        for param in parameters:
            param_in = param.get('in', '')
            param_info = self._create_param_info(param)
            
            if param_in == ParamLocation.QUERY.value:
                result.request_params.append(param_info)
            elif param_in == ParamLocation.HEADER.value:
                result.request_headers.append(param_info)
            elif param_in == ParamLocation.PATH.value:
                # 路径参数不放入request_params，保留在URL模板中
                pass
            elif param_in == ParamLocation.FORM_DATA.value:
                result.request_form_datas.append(param_info)
            elif param_in == ParamLocation.BODY.value:
                # Swagger 2.0 body参数
                schema = param.get('schema', {})
                result.requests_json_data = json.dumps(
                    self._generate_example(schema),
                    ensure_ascii=False,
                    indent=2
                )
    
    def _create_param_info(self, param: Dict[str, Any]) -> ParamInfo:
        """从原始参数创建ParamInfo对象"""
        # OpenAPI 3.0: 类型在schema中
        if 'schema' in param:
            schema = param['schema']
            param_type = schema.get('type', 'string')
            param_default = schema.get('default', '')
            param_enum = schema.get('enum')
        else:
            # OpenAPI 2.0: 类型直接在参数对象中
            param_type = param.get('type', 'string')
            param_default = param.get('default', '')
            param_enum = param.get('enum')
        
        return ParamInfo(
            name=param.get('name', ''),
            type=param_type,
            required=param.get('required', False),
            description=param.get('description', ''),
            default=param_default,
            enum=param_enum if param_enum else None
        )
    
    # ==================== 请求体解析 ====================
    
    def _parse_request_body(self, request_body: Dict[str, Any], result: ApiResult) -> None:
        """解析OpenAPI 3.0的requestBody"""
        content = request_body.get('content', {})
        
        # 按优先级处理不同的Content-Type
        content_handlers = [
            ('application/json', self._handle_json_body),
            ('multipart/form-data', self._handle_form_data_body),
            ('application/x-www-form-urlencoded', self._handle_urlencoded_body),
        ]
        
        for content_type, handler in content_handlers:
            if content_type in content:
                handler(content[content_type], result)
                self._add_content_type_header(result, content_type)
                break
    
    def _handle_json_body(self, content_item: Dict[str, Any], result: ApiResult) -> None:
        """处理JSON请求体"""
        schema = content_item.get('schema', {})
        result.requests_json_data = json.dumps(
            self._generate_example(schema),
            ensure_ascii=False,
            indent=2
        )
    
    def _handle_form_data_body(self, content_item: Dict[str, Any], result: ApiResult) -> None:
        """处理FormData请求体"""
        schema = content_item.get('schema', {})
        result.request_form_datas.extend(self._extract_form_fields(schema))
    
    def _handle_urlencoded_body(self, content_item: Dict[str, Any], result: ApiResult) -> None:
        """处理URLEncoded请求体"""
        schema = content_item.get('schema', {})
        result.request_www_form_datas.extend(self._extract_form_fields(schema))
    
    def _add_content_type_header(self, result: ApiResult, content_type: str) -> None:
        """添加Content-Type请求头"""
        header = ParamInfo(
            name='Content-Type',
            type='string',
            required=True,
            description='请求内容类型',
            default=content_type
        )
        result.request_headers.append(header)
    
    def _extract_form_fields(self, schema: Dict[str, Any]) -> List[ParamInfo]:
        """从schema中提取表单字段"""
        fields = []
        properties = schema.get('properties', {})
        required_fields = set(schema.get('required', []))
        
        for field_name, field_schema in properties.items():
            fields.append(ParamInfo(
                name=field_name,
                type=field_schema.get('type', 'string'),
                required=field_name in required_fields,
                description=field_schema.get('description', ''),
                default=field_schema.get('default', '')
            ))
        
        return fields
    
    def _merge_headers(self, result: ApiResult, new_headers: List[ParamInfo]) -> None:
        """合并请求头（去重）"""
        existing_names = {h.name for h in result.request_headers}
        for header in new_headers:
            if header.name not in existing_names:
                result.request_headers.append(header)
                existing_names.add(header.name)
    
    # ==================== Schema引用解析 ====================
    
    def _resolve_ref(self, ref_path: str) -> Optional[Dict[str, Any]]:
        """解析$ref引用"""
        if not ref_path.startswith('#/'):
            return None
        
        parts = ref_path[2:].split('/')
        current = self.data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current if isinstance(current, dict) else None
    
    # ==================== 示例数据生成 ====================
    
    def _generate_example(self, schema: Dict[str, Any]) -> Any:
        """
        从schema生成示例数据
        
        支持：
        - example字段
        - $ref引用（带循环检测）
        - allOf/oneOf/anyOf组合
        - 各种基础类型和格式
        """
        if not schema:
            return {}
        
        # 优先使用example
        if 'example' in schema:
            return schema['example']
        
        # 处理$ref引用
        if '$ref' in schema:
            return self._generate_example_from_ref(schema['$ref'])
        
        # 处理组合类型
        if 'allOf' in schema:
            return self._generate_example_all_of(schema['allOf'])
        if 'oneOf' in schema or 'anyOf' in schema:
            return self._generate_example_one_of(schema)
        
        # 根据类型生成
        schema_type = schema.get('type', 'object')
        return self._generate_example_by_type(schema, schema_type)
    
    def _generate_example_from_ref(self, ref_path: str) -> Any:
        """从$ref引用生成示例"""
        # 循环引用检测
        if ref_path in self._ref_cache:
            return self._ref_cache[ref_path]
        
        ref_schema = self._resolve_ref(ref_path)
        if ref_schema:
            self._ref_cache[ref_path] = {}  # 占位防循环
            result = self._generate_example(ref_schema)
            self._ref_cache[ref_path] = result
            return result
        
        # 无法解析，返回引用名称
        ref_name = ref_path.split('/')[-1]
        return f"<{ref_name}>"
    
    def _generate_example_all_of(self, schemas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """处理allOf组合"""
        result = {}
        for sub_schema in schemas:
            sub_example = self._generate_example(sub_schema)
            if isinstance(sub_example, dict):
                result.update(sub_example)
        return result
    
    def _generate_example_one_of(self, schema: Dict[str, Any]) -> Any:
        """处理oneOf/anyOf组合（取第一个）"""
        schemas = schema.get('oneOf', schema.get('anyOf', []))
        if schemas:
            return self._generate_example(schemas[0])
        return {}
    
    def _generate_example_by_type(self, schema: Dict[str, Any], schema_type: str) -> Any:
        """根据类型生成示例值"""
        generators = {
            'object': self._generate_object_example,
            'array': self._generate_array_example,
            'string': self._generate_string_example,
            'integer': self._generate_integer_example,
            'number': self._generate_number_example,
            'boolean': self._generate_boolean_example,
        }
        
        generator = generators.get(schema_type)
        return generator(schema) if generator else None
    
    def _generate_object_example(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """生成对象示例"""
        example = {}
        properties = schema.get('properties', {})
        for prop_name, prop_schema in properties.items():
            example[prop_name] = self._generate_example(prop_schema)
        return example
    
    def _generate_array_example(self, schema: Dict[str, Any]) -> List[Any]:
        """生成数组示例"""
        items = schema.get('items', {})
        return [self._generate_example(items)]
    
    def _generate_string_example(self, schema: Dict[str, Any]) -> str:
        """生成字符串示例"""
        # 枚举值
        if 'enum' in schema and schema['enum']:
            return schema['enum'][0]
        
        # 默认值
        if 'default' in schema:
            return schema['default']
        
        # 根据format生成
        format_examples = {
            'date': '2024-01-01',
            'date-time': '2024-01-01T00:00:00Z',
            'email': 'user@example.com',
            'uri': 'https://example.com',
            'uuid': '550e8400-e29b-41d4-a716-446655440000',
            'hostname': 'example.com',
            'ipv4': '192.168.1.1',
            'ipv6': '::1',
        }
        
        fmt = schema.get('format', '')
        return format_examples.get(fmt, 'string')
    
    def _generate_integer_example(self, schema: Dict[str, Any]) -> int:
        """生成整数示例"""
        if 'enum' in schema and schema['enum']:
            return schema['enum'][0]
        return schema.get('default', 0)
    
    def _generate_number_example(self, schema: Dict[str, Any]) -> float:
        """生成数字示例"""
        if 'enum' in schema and schema['enum']:
            return schema['enum'][0]
        return schema.get('default', 0.0)
    
    def _generate_boolean_example(self, schema: Dict[str, Any]) -> bool:
        """生成布尔示例"""
        return schema.get('default', False)


async def fetch_swagger_from_url(url: str) -> Dict[str, Any]:
    """
    从URL获取Swagger JSON（异步版本）
    
    Args:
        url: Swagger JSON URL
        
    Returns:
        Swagger数据字典
        
    Raises:
        ValueError: 获取失败时抛出
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.error(f"获取Swagger超时: {url}")
        raise ValueError(f"获取Swagger文档超时: {url}")
    except httpx.HTTPStatusError as e:
        logger.error(f"获取Swagger失败，HTTP状态码: {e.response.status_code}")
        raise ValueError(f"获取Swagger文档失败，HTTP状态码: {e.response.status_code}")
    except Exception as e:
        logger.error(f"获取Swagger失败: {e}")
        raise ValueError(f"无法获取Swagger文档: {e}")
