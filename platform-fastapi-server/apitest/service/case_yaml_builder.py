"""
用例 YAML 构建器
负责将数据库用例转换为执行器可识别的 YAML 格式

支持的YAML格式：
- desc: 用例名称
- pre_script: 前置Python脚本列表
- steps: 测试步骤列表
- post_script: 后置Python脚本列表
- ddts: 数据驱动数据
"""
import json
import copy
from typing import List, Dict, Any, Optional
from pathlib import Path

import yaml
from sqlmodel import Session, select

from ..model.ApiInfoCaseModel import ApiInfoCase
from ..model.ApiInfoCaseStepModel import ApiInfoCaseStep
from ..model.ApiKeyWordModel import ApiKeyWord
from ..model.ApiCollectionInfoModel import ApiCollectionInfo
from ..model.ApiCollectionDetailModel import ApiCollectionDetail
from ..model.ApiDbBaseModel import ApiDbBase


class CaseYamlBuilder:
    """用例 YAML 构建器"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def build_single_case(
        self,
        case_id: int,
        context_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        构建单个用例的 YAML 数据
        
        Args:
            case_id: 用例ID
            context_vars: 上下文变量（会与用例自身的 ddts 合并）
            
        Returns:
            {"yaml_data": dict, "yaml_content": str, "case_name": str, "project_id": int}
        """
        case_info = self.session.get(ApiInfoCase, case_id)
        if not case_info:
            raise ValueError(f"用例不存在: {case_id}")
        
        steps = self._get_case_steps(case_id)
        if not steps:
            raise ValueError(f"用例没有步骤: {case_id}")
        
        # 加载用例自身的 ddts 数据
        case_ddts = self._parse_ddts(case_info.ddts)
        
        # 加载用例的全局配置
        case_context = self._parse_context_config(case_info.context_config)
        
        # 构建 YAML 数据，包含 ddts、全局配置、前置/后置脚本
        yaml_data = self._build_yaml_data_with_ddts(
            case_name=case_info.case_name,
            steps=steps,
            case_ddts=case_ddts,
            context_vars=context_vars,
            case_context=case_context,
            pre_request=case_info.pre_request,
            post_request=case_info.post_request
        )
        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        return {
            "yaml_data": yaml_data,
            "yaml_content": yaml_content,
            "case_name": case_info.case_name,
            "project_id": case_info.project_id
        }
    
    def build_context_yaml(self, project_id: int, plan_env: Optional[str] = None) -> str:
        """
        构建 context.yaml 文件内容
        包含环境变量和数据库配置
        
        Args:
            project_id: 项目ID
            plan_env: 测试计划的全局环境变量（JSON字符串）
            
        Returns:
            context.yaml 内容字符串
        """
        context_data = {}
        
        # 1. 加载测试计划的全局环境变量
        if plan_env:
            try:
                env_list = json.loads(plan_env)
                if isinstance(env_list, list):
                    for item in env_list:
                        if isinstance(item, dict):
                            for key, value in item.items():
                                if key != 'desc':
                                    context_data[key] = value
                elif isinstance(env_list, dict):
                    context_data.update(env_list)
            except json.JSONDecodeError:
                pass
        
        # 2. 加载项目的数据库配置
        db_configs = self._get_db_configs(project_id)
        if db_configs:
            context_data['databases'] = db_configs
        
        if not context_data:
            return ""
        
        return yaml.dump(context_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    def _get_db_configs(self, project_id: int) -> Dict[str, Any]:
        """获取项目的数据库配置"""
        stmt = select(ApiDbBase).where(
            ApiDbBase.project_id == project_id,
            ApiDbBase.is_enabled == '1'
        )
        db_list = self.session.exec(stmt).all()
        
        configs = {}
        for db in db_list:
            try:
                db_info = json.loads(db.db_info) if db.db_info else {}
                configs[db.ref_name] = {
                    'type': db.db_type,
                    'name': db.name,
                    **db_info
                }
            except json.JSONDecodeError:
                configs[db.ref_name] = {
                    'type': db.db_type,
                    'name': db.name,
                    'connection': db.db_info
                }
        
        return configs
    
    def _parse_ddts(self, ddts_str: Optional[str]) -> List[Dict[str, Any]]:
        """解析用例的 ddts 字段"""
        if not ddts_str:
            return []
        try:
            data = json.loads(ddts_str)
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            return []
    
    def _parse_context_config(self, config_str: Optional[str]) -> Dict[str, Any]:
        """解析用例的全局配置"""
        if not config_str:
            return {}
        try:
            return json.loads(config_str)
        except json.JSONDecodeError:
            return {}
    
    def _build_yaml_data_with_ddts(
        self,
        case_name: str,
        steps: List[ApiInfoCaseStep],
        case_ddts: List[Dict[str, Any]],
        context_vars: Optional[Dict[str, Any]] = None,
        case_context: Optional[Dict[str, Any]] = None,
        pre_request: Optional[str] = None,
        post_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """构建包含 ddts、全局配置和前置/后置脚本的 YAML 数据"""
        yaml_data = {'desc': case_name}
        
        # 添加全局配置（放在最前面）
        if case_context:
            for key, value in case_context.items():
                yaml_data[key] = value
        
        # 添加前置脚本
        if pre_request:
            pre_scripts = self._parse_script(pre_request)
            if pre_scripts:
                yaml_data['pre_script'] = pre_scripts
        
        yaml_data['steps'] = []
        
        # 收集 ddts 中使用的变量名，这些变量不应该被预先替换
        ddts_var_names = set()
        for ddt_item in case_ddts:
            if isinstance(ddt_item, dict):
                ddts_var_names.update(k for k in ddt_item.keys() if k != 'desc')
        
        for step in steps:
            step_data = self._parse_step_data(step.step_data)
            keyword_name = self._get_keyword_name(step.keyword_id)
            
            # 预先替换全局配置变量，但跳过 ddts 中定义的变量（让执行器在运行时替换）
            if case_context:
                # 过滤掉 ddts 中定义的变量
                context_to_replace = {k: v for k, v in case_context.items() if k not in ddts_var_names}
                if context_to_replace:
                    step_data = self._replace_context_vars(step_data, context_to_replace)
            
            # 只对 HTTP 请求类关键字进行转换，其他关键字保持原样
            final_keyword, final_data = self._normalize_step(keyword_name, step_data)
            
            step_item = {
                step.step_desc or f"步骤{step.run_order}": {
                    '关键字': final_keyword,
                    **final_data
                }
            }
            yaml_data['steps'].append(step_item)
        
        # 添加后置脚本
        if post_request:
            post_scripts = self._parse_script(post_request)
            if post_scripts:
                yaml_data['post_script'] = post_scripts
        
        # 添加 ddts 数据
        if case_ddts:
            yaml_data['ddts'] = case_ddts
        elif context_vars:
            yaml_data['ddts'] = [{'desc': f'{case_name}_数据', **context_vars}]
        
        return yaml_data
    
    def _parse_script(self, script_str: Optional[str]) -> List[str]:
        """解析脚本字符串为脚本列表"""
        if not script_str:
            return []
        
        # 尝试解析为JSON数组
        try:
            scripts = json.loads(script_str)
            if isinstance(scripts, list):
                return [s for s in scripts if s and isinstance(s, str)]
            elif isinstance(scripts, str):
                return [scripts] if scripts.strip() else []
        except json.JSONDecodeError:
            pass
        
        # 如果不是JSON，直接作为单个脚本
        script_str = script_str.strip()
        if script_str:
            return [script_str]
        return []
    
    def _replace_context_vars(self, data: Any, context: Dict[str, Any]) -> Any:
        """递归替换数据中的全局配置变量 {{VAR}}"""
        if isinstance(data, dict):
            return {k: self._replace_context_vars(v, context) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._replace_context_vars(item, context) for item in data]
        elif isinstance(data, str):
            result = data
            for key, value in context.items():
                placeholder = '{{' + key + '}}'
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
            return result
        else:
            return data
    
    def build_plan_cases(self, plan_id: int) -> Dict[str, Any]:
        """
        构建计划中所有用例的 YAML 数据（支持 DDT 展开）
        
        Args:
            plan_id: 计划ID
            
        Returns:
            {
                "cases": [{"yaml_data": dict, "case_name": str, "yaml_content": str}, ...],
                "combined_yaml": str,
                "plan_name": str,
                "project_id": int,
                "context_yaml": str  # context.yaml 内容
            }
        """
        plan = self.session.get(ApiCollectionInfo, plan_id)
        if not plan:
            raise ValueError(f"测试计划不存在: {plan_id}")
        
        # 查询计划中的所有用例
        stmt = select(ApiCollectionDetail).where(
            ApiCollectionDetail.collection_info_id == plan_id
        ).order_by(ApiCollectionDetail.run_order)
        plan_cases = self.session.exec(stmt).all()
        
        if not plan_cases:
            raise ValueError(f"测试计划中没有用例: {plan_id}")
        
        # 构建 context.yaml（包含环境变量和数据库配置）
        context_yaml = self.build_context_yaml(
            project_id=plan.project_id or 0,
            plan_env=plan.collection_env
        )
        
        all_cases = []
        combined_parts = []
        
        for plan_case in plan_cases:
            case_info = self.session.get(ApiInfoCase, plan_case.case_info_id)
            if not case_info:
                continue
            
            steps = self._get_case_steps(plan_case.case_info_id)
            if not steps:
                continue
            
            # 解析 DDT 数据
            ddt_list = self._parse_ddt_data(plan_case.ddt_data)
            
            # 为每组 DDT 数据生成一个用例
            for ddt_idx, ddt_item in enumerate(ddt_list):
                ddt_desc = ddt_item.get('desc', f'数据{ddt_idx + 1}') if isinstance(ddt_item, dict) else f'数据{ddt_idx + 1}'
                case_name = f"{case_info.case_name}_{ddt_desc}" if len(ddt_list) > 1 else case_info.case_name
                
                # 构建 YAML，合并 DDT 数据和前置/后置脚本
                yaml_data = self._build_yaml_data_with_ddt(
                    case_name=case_name,
                    steps=steps,
                    ddt_item=ddt_item,
                    pre_request=case_info.pre_request,
                    post_request=case_info.post_request
                )
                yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
                
                all_cases.append({
                    "yaml_data": yaml_data,
                    "yaml_content": yaml_content,
                    "case_name": case_name
                })
                combined_parts.append(f"# 用例: {case_name}\n{yaml_content}")
        
        if not all_cases:
            raise ValueError("没有有效的测试用例")
        
        return {
            "cases": all_cases,
            "combined_yaml": "---\n".join(combined_parts),
            "plan_name": plan.plan_name,
            "project_id": plan.project_id or 0,
            "context_yaml": context_yaml
        }
    
    def save_cases_to_dir(self, cases: List[Dict], target_dir: Path) -> List[str]:
        """
        将用例保存到目录
        
        Args:
            cases: 用例列表 [{"yaml_data": dict, "case_name": str}, ...]
            target_dir: 目标目录
            
        Returns:
            保存的文件名列表
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        filenames = []
        
        for idx, case in enumerate(cases):
            case_name = case["case_name"]
            yaml_content = case.get("yaml_content") or yaml.dump(
                case["yaml_data"], allow_unicode=True, default_flow_style=False, sort_keys=False
            )
            filename = f"{idx + 1}_{case_name}.yaml"
            (target_dir / filename).write_text(yaml_content, encoding='utf-8')
            filenames.append(filename)
        
        return filenames
    
    # ==================== 私有方法 ====================
    
    def _get_case_steps(self, case_id: int) -> List[ApiInfoCaseStep]:
        """获取用例步骤"""
        stmt = select(ApiInfoCaseStep).where(
            ApiInfoCaseStep.case_info_id == case_id
        ).order_by(ApiInfoCaseStep.run_order)
        return list(self.session.exec(stmt).all())
    
    def _build_yaml_data(
        self,
        case_name: str,
        steps: List[ApiInfoCaseStep],
        context_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """构建 YAML 数据结构"""
        yaml_data = {'desc': case_name, 'steps': []}
        
        for step in steps:
            step_data = self._parse_step_data(step.step_data)
            keyword_name = self._get_keyword_name(step.keyword_id)
            
            # 只对 HTTP 请求类关键字进行转换，其他关键字保持原样
            final_keyword, final_data = self._normalize_step(keyword_name, step_data)
            
            step_item = {
                step.step_desc or f"步骤{step.run_order}": {
                    '关键字': final_keyword,
                    **final_data
                }
            }
            yaml_data['steps'].append(step_item)
        
        if context_vars:
            yaml_data['ddts'] = [{'desc': f'{case_name}_数据', **context_vars}]
        
        return yaml_data
    
    def _build_yaml_data_with_ddt(
        self,
        case_name: str,
        steps: List[ApiInfoCaseStep],
        ddt_item: Dict[str, Any],
        pre_request: Optional[str] = None,
        post_request: Optional[str] = None
    ) -> Dict[str, Any]:
        """构建带 DDT 数据合并和前置/后置脚本的 YAML"""
        yaml_data = {'desc': case_name}
        
        # 添加前置脚本
        if pre_request:
            pre_scripts = self._parse_script(pre_request)
            if pre_scripts:
                yaml_data['pre_script'] = pre_scripts
        
        yaml_data['steps'] = []
        
        for step in steps:
            step_data = self._parse_step_data(step.step_data)
            
            # 合并 DDT 数据到步骤
            if ddt_item and isinstance(ddt_item, dict):
                step_data = self._deep_merge_ddt(step_data, ddt_item)
            
            keyword_name = self._get_keyword_name(step.keyword_id)
            
            # 只对 HTTP 请求类关键字进行转换，其他关键字保持原样
            final_keyword, final_data = self._normalize_step(keyword_name, step_data)
            
            step_item = {
                step.step_desc or f"步骤{step.run_order}": {
                    '关键字': final_keyword,
                    **final_data
                }
            }
            yaml_data['steps'].append(step_item)
        
        # 添加后置脚本
        if post_request:
            post_scripts = self._parse_script(post_request)
            if post_scripts:
                yaml_data['post_script'] = post_scripts
        
        return yaml_data
    
    def _parse_step_data(self, step_data_str: Optional[str]) -> Dict[str, Any]:
        """解析步骤数据 JSON，并递归解析嵌套的 JSON 字符串"""
        if not step_data_str:
            return {}
        try:
            data = json.loads(step_data_str)
            # 递归解析嵌套的 JSON 字符串
            return self._deep_parse_json_strings(data)
        except json.JSONDecodeError:
            return {}
    
    def _deep_parse_json_strings(self, obj: Any) -> Any:
        """递归解析对象中的 JSON 字符串"""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                result[key] = self._deep_parse_json_strings(value)
            return result
        elif isinstance(obj, list):
            return [self._deep_parse_json_strings(item) for item in obj]
        elif isinstance(obj, str):
            # 尝试解析看起来像 JSON 的字符串
            stripped = obj.strip()
            if stripped.startswith('{') or stripped.startswith('['):
                try:
                    parsed = json.loads(obj)
                    return self._deep_parse_json_strings(parsed)
                except json.JSONDecodeError:
                    pass
            return obj
        else:
            return obj
    
    def _get_keyword_name(self, keyword_id: Optional[int]) -> str:
        """获取关键字名称"""
        if not keyword_id:
            return "send_request"
        keyword = self.session.get(ApiKeyWord, keyword_id)
        return keyword.keyword_fun_name if keyword else "send_request"
    
    # HTTP 请求类关键字（需要转换为 send_request 格式）
    _HTTP_REQUEST_KEYWORDS = {
        'request_get', 'request_post', 'request_put', 'request_delete', 'request_patch',
        'request_post_json', 'request_post_form', 'request_post_form_data',
        'request_post_form_urlencoded', 'request_post_row_json'
    }
    
    def _normalize_step(self, keyword_name: str, step_data: Dict[str, Any]) -> tuple:
        """
        标准化步骤数据
        
        Returns:
            (final_keyword, final_data) - 最终关键字名和参数数据
        """
        kw_lower = keyword_name.lower()
        
        # 只有 HTTP 请求类关键字才需要转换
        if kw_lower in self._HTTP_REQUEST_KEYWORDS or kw_lower.startswith('request_'):
            return 'send_request', self._convert_to_send_request(step_data, keyword_name)
        
        # 其他关键字（如 assert_text_comparators）保持原样
        return keyword_name, step_data
    
    # send_request 支持的有效参数
    _VALID_REQUEST_PARAMS = {'url', 'method', 'params', 'data', 'json', 'headers', 'files', 'timeout', 'cookies', 'auth'}
    
    def _convert_to_send_request(self, step_data: Dict[str, Any], keyword_name: str) -> Dict[str, Any]:
        """
        将旧格式 HTTP 请求参数转换为 send_request 统一格式
        
        旧格式: URL, HEADERS, DATA (大写)
        新格式: url, headers, json, method (小写)
        """
        result = {}
        
        # 参数名映射：大写 → 小写
        param_map = {
            'URL': 'url',
            'PARAMS': 'params',
            'HEADERS': 'headers',
            'DATA': 'data',
            'JSON': 'json',
            'FILES': 'files'
        }
        
        # 从关键字名推断 HTTP 方法
        method = 'GET'
        kw_lower = keyword_name.lower()
        if 'post' in kw_lower:
            method = 'POST'
        elif 'put' in kw_lower:
            method = 'PUT'
        elif 'delete' in kw_lower:
            method = 'DELETE'
        elif 'patch' in kw_lower:
            method = 'PATCH'
        
        result['method'] = method
        
        # 转换参数，过滤空值和无效参数
        for key, value in step_data.items():
            # 跳过空值
            if value is None or value == '' or value == {}:
                continue
            
            new_key = param_map.get(key, key.lower())
            
            # 只保留有效的请求参数
            if new_key in self._VALID_REQUEST_PARAMS:
                result[new_key] = value
        
        return result
    
    def _parse_ddt_data(self, ddt_data_str: Optional[str]) -> List[Dict[str, Any]]:
        """解析 DDT 数据"""
        if not ddt_data_str:
            return [{}]
        try:
            data = json.loads(ddt_data_str)
            if isinstance(data, list):
                return data if data else [{}]
            return [data]
        except json.JSONDecodeError:
            return [{}]
    
    def _deep_merge_ddt(self, target: Dict, ddt_data: Dict) -> Dict:
        """递归合并 DDT 数据到目标字典"""
        result = copy.deepcopy(target)
        for key, value in ddt_data.items():
            if key == 'desc':
                continue
            self._replace_value_recursive(result, key, value)
        return result
    
    def _replace_value_recursive(self, obj: Any, target_key: str, new_value: Any):
        """递归查找并替换同名 key"""
        if isinstance(obj, dict):
            for k in list(obj.keys()):
                if k.lower() == target_key.lower():
                    obj[k] = new_value
                elif isinstance(obj[k], (dict, list)):
                    self._replace_value_recursive(obj[k], target_key, new_value)
        elif isinstance(obj, list):
            for item in obj:
                self._replace_value_recursive(item, target_key, new_value)
