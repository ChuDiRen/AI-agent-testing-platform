"""YAML测试用例生成服务"""
import yaml
import json
from typing import Dict, List, Optional, Any
from apitest.model.ApiInfoModel import ApiInfo

class YamlGeneratorService:
    """将接口信息转换为api-engine支持的YAML格式"""
    
    @staticmethod
    def generate_yaml(
        api_info: ApiInfo,
        test_name: str,
        context_vars: Optional[Dict[str, Any]] = None,
        pre_script: Optional[List[str]] = None,
        post_script: Optional[List[str]] = None,
        variable_extracts: Optional[List[Dict]] = None,
        assertions: Optional[List[Dict]] = None
    ) -> str:
        """
        生成YAML测试用例
        
        Args:
            api_info: 接口信息对象
            test_name: 测试用例名称
            context_vars: 上下文变量字典
            pre_script: 前置脚本列表
            post_script: 后置脚本列表
            variable_extracts: 变量提取配置列表
            assertions: 断言配置列表
            
        Returns:
            YAML格式的测试用例字符串
        """
        # 构建测试用例结构
        test_case = {
            'desc': test_name or f'{api_info.api_name}_测试',
            'steps': []
        }
        
        # 构建主请求步骤
        request_step = YamlGeneratorService._build_request_step(api_info, context_vars)
        test_case['steps'].append(request_step)
        
        # 添加变量提取步骤
        if variable_extracts:
            for extract in variable_extracts:
                extract_step = YamlGeneratorService._build_extract_step(extract)
                test_case['steps'].append(extract_step)
        
        # 添加断言步骤
        if assertions:
            for assertion in assertions:
                assert_step = YamlGeneratorService._build_assertion_step(assertion)
                test_case['steps'].append(assert_step)
        
        # 添加前置脚本
        if pre_script and len(pre_script) > 0:
            test_case['pre_script'] = pre_script
        
        # 添加后置脚本
        if post_script and len(post_script) > 0:
            test_case['post_script'] = post_script
        
        # 添加数据驱动（如果需要）
        if context_vars:
            test_case['ddts'] = [{
                'desc': f'{test_name}_数据',
                **context_vars
            }]
        
        # 转换为YAML格式
        yaml_content = yaml.dump(test_case, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return yaml_content
    
    @staticmethod
    def _build_request_step(api_info: ApiInfo, context_vars: Optional[Dict[str, Any]] = None) -> Dict:
        """构建请求步骤"""
        step_name = api_info.api_name or '发送请求'
        step_data = {
            '关键字': 'send_request',
            'method': api_info.request_method or 'GET',
            'url': api_info.request_url or ''
        }
        
        # 添加URL参数
        if api_info.request_params:
            try:
                params = json.loads(api_info.request_params) if isinstance(api_info.request_params, str) else api_info.request_params
                step_data['params'] = params
            except:
                pass
        
        # 添加请求头
        if api_info.request_headers:
            try:
                headers = json.loads(api_info.request_headers) if isinstance(api_info.request_headers, str) else api_info.request_headers
                step_data['headers'] = headers
            except:
                pass
        
        # 根据请求方法添加请求体
        if api_info.request_method in ['POST', 'PUT', 'PATCH']:
            # form-data
            if api_info.request_form_datas:
                try:
                    form_data = json.loads(api_info.request_form_datas) if isinstance(api_info.request_form_datas, str) else api_info.request_form_datas
                    step_data['data'] = form_data
                except:
                    pass
            
            # x-www-form-urlencoded
            elif api_info.request_www_form_datas:
                try:
                    www_form_data = json.loads(api_info.request_www_form_datas) if isinstance(api_info.request_www_form_datas, str) else api_info.request_www_form_datas
                    step_data['data'] = www_form_data
                except:
                    pass
            
            # json数据
            elif api_info.requests_json_data:
                try:
                    json_data = json.loads(api_info.requests_json_data) if isinstance(api_info.requests_json_data, str) else api_info.requests_json_data
                    step_data['json'] = json_data
                except:
                    pass
            
            # 文件上传
            if api_info.request_files:
                try:
                    files = json.loads(api_info.request_files) if isinstance(api_info.request_files, str) else api_info.request_files
                    step_data['files'] = files
                except:
                    pass
        
        return {step_name: step_data}
    
    @staticmethod
    def _build_extract_step(extract_config: Dict) -> Dict:
        """构建变量提取步骤"""
        step_name = extract_config.get('description') or f"提取_{extract_config.get('var_name')}"
        step_data = {
            '关键字': 'ex_jsonData',
            'EXVALUE': extract_config.get('extract_path', ''),
            'VARNAME': extract_config.get('var_name', ''),
            'INDEX': str(extract_config.get('index', 0))
        }
        return {step_name: step_data}
    
    @staticmethod
    def _build_assertion_step(assertion_config: Dict) -> Dict:
        """构建断言步骤"""
        step_name = assertion_config.get('description') or '断言验证'
        
        # 根据断言类型构建不同的步骤
        assert_type = assertion_config.get('type', 'assert_text_comparators')
        
        if assert_type == 'assert_text_comparators':
            # 文本比较断言
            step_data = {
                '关键字': 'assert_text_comparators',
                'VALUE': assertion_config.get('actual_value', ''),
                'EXPECTED': assertion_config.get('expected_value', ''),
                'OP_STR': assertion_config.get('operator', '==')
            }
        elif assert_type == 'assert_json_path':
            # JSONPath断言
            step_data = {
                '关键字': 'ex_jsonData',
                'EXVALUE': assertion_config.get('extract_path', ''),
                'VARNAME': f"temp_{assertion_config.get('description', 'value')}",
                'INDEX': '0'
            }
        else:
            # 默认文本比较
            step_data = {
                '关键字': 'assert_text_comparators',
                'VALUE': assertion_config.get('actual_value', ''),
                'EXPECTED': assertion_config.get('expected_value', ''),
                'OP_STR': '=='
            }
        
        return {step_name: step_data}
    
    @staticmethod
    def generate_context_yaml(context_vars: Dict[str, Any]) -> str:
        """生成上下文变量YAML文件"""
        yaml_content = yaml.dump(context_vars, allow_unicode=True, default_flow_style=False)
        return yaml_content
