"""
用例 YAML 构建器
负责将数据库用例转换为执行器可识别的 YAML 格式
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
            context_vars: 上下文变量
            
        Returns:
            {"yaml_data": dict, "yaml_content": str, "case_name": str}
        """
        case_info = self.session.get(ApiInfoCase, case_id)
        if not case_info:
            raise ValueError(f"用例不存在: {case_id}")
        
        steps = self._get_case_steps(case_id)
        if not steps:
            raise ValueError(f"用例没有步骤: {case_id}")
        
        yaml_data = self._build_yaml_data(case_info.case_name, steps, context_vars)
        yaml_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        return {
            "yaml_data": yaml_data,
            "yaml_content": yaml_content,
            "case_name": case_info.case_name,
            "project_id": case_info.project_id
        }
    
    def build_plan_cases(self, plan_id: int) -> Dict[str, Any]:
        """
        构建计划中所有用例的 YAML 数据（支持 DDT 展开）
        
        Args:
            plan_id: 计划ID
            
        Returns:
            {
                "cases": [{"yaml_data": dict, "case_name": str}, ...],
                "combined_yaml": str,
                "plan_name": str,
                "project_id": int
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
                
                # 构建 YAML，合并 DDT 数据
                yaml_data = self._build_yaml_data_with_ddt(case_name, steps, ddt_item)
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
            "project_id": plan.project_id or 0
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
        ddt_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建带 DDT 数据合并的 YAML"""
        yaml_data = {'desc': case_name, 'steps': []}
        
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
        
        return yaml_data
    
    def _parse_step_data(self, step_data_str: Optional[str]) -> Dict[str, Any]:
        """解析步骤数据 JSON"""
        if not step_data_str:
            return {}
        try:
            return json.loads(step_data_str)
        except json.JSONDecodeError:
            return {}
    
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
            'DATA': 'json',  # JSON 数据用 json 参数
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
        
        # 转换参数
        for key, value in step_data.items():
            new_key = param_map.get(key, key.lower())
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
