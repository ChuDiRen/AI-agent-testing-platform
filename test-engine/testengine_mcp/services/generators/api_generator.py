"""
API 测试用例生成器
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseGenerator


class ApiCaseGenerator(BaseGenerator):
    """API 测试用例生成器"""
    
    def generate(
        self,
        name: str,
        description: str,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        extracts: Optional[List[Dict[str, str]]] = None,
        asserts: Optional[List[Dict[str, Any]]] = None,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成 API 测试用例
        
        断言类型:
        - status_code: 状态码断言 {"type": "status_code", "expected": 200}
        - contains: 响应包含文本 {"type": "contains", "expected": "success"}
        - equals: 精确匹配 {"type": "equals", "value": "{{variable}}", "expected": "value"}
        - jsonpath: JSON 路径断言 {"type": "jsonpath", "jsonpath": "$.code", "expected": 0}
        - response_time: 响应时间断言 {"type": "response_time", "max_ms": 1000}
        - json_length: JSON 数组长度断言
        """
        steps = []
        
        # 1. 构建请求步骤
        request_step = {
            "关键字": "send_request",
            "url": url,
            "method": method.upper()
        }
        
        if headers:
            request_step["headers"] = headers
        if params:
            request_step["params"] = params
        if data:
            request_step["data"] = data
        if json_body:
            request_step["json"] = json_body
        
        steps.append({f"发送{method.upper()}请求": request_step})
        
        # 2. 添加提取步骤
        if extracts:
            for extract in extracts:
                extract_step = {
                    "关键字": "ex_jsonData",
                    "EXVALUE": extract.get("jsonpath", "$"),
                    "VARNAME": extract.get("name", "extracted_value"),
                    "INDEX": str(extract.get("index", 0))
                }
                steps.append({f"提取{extract.get('name', 'value')}": extract_step})
        
        # 3. 添加断言步骤
        if asserts:
            for i, assertion in enumerate(asserts):
                step = self._build_assert_step(assertion, i)
                if step:
                    steps.extend(step if isinstance(step, list) else [step])
        else:
            # 默认添加状态码断言
            steps.append({"断言状态码": {
                "关键字": "assert_status_code",
                "EXPECTED": 200
            }})
        
        # 构建完整用例
        case = {
            "desc": description or name,
            "steps": steps
        }
        
        # 保存用例
        save_file = self._get_save_path(save_path, name, "api-cases_yaml")
        self._save_case(save_file, case)
        
        return self._build_result(case, save_file, "api", "API 测试用例已生成")
    
    def _build_assert_step(self, assertion: Dict[str, Any], index: int) -> Optional[List[Dict]]:
        """构建断言步骤"""
        assert_type = assertion.get("type", "status_code")
        step_name = f"断言{index+1}_{assert_type}"
        
        if assert_type == "status_code":
            return [{step_name: {
                "关键字": "assert_status_code",
                "EXPECTED": assertion.get("expected", 200)
            }}]
        
        elif assert_type == "contains":
            return [{step_name: {
                "关键字": "assert_text_comparators",
                "VALUE": "{{response_text}}",
                "EXPECTED": assertion.get("expected", ""),
                "OP_STR": "contains"
            }}]
        
        elif assert_type == "equals":
            return [{step_name: {
                "关键字": "assert_text_comparators",
                "VALUE": assertion.get("value", ""),
                "EXPECTED": assertion.get("expected", ""),
                "OP_STR": "=="
            }}]
        
        elif assert_type == "not_equals":
            return [{step_name: {
                "关键字": "assert_text_comparators",
                "VALUE": assertion.get("value", ""),
                "EXPECTED": assertion.get("expected", ""),
                "OP_STR": "!="
            }}]
        
        elif assert_type == "jsonpath":
            # 先提取再断言
            var_name = f"_assert_var_{index}"
            return [
                {f"提取断言值_{index+1}": {
                    "关键字": "ex_jsonData",
                    "EXVALUE": assertion.get("jsonpath", "$"),
                    "VARNAME": var_name,
                    "INDEX": "0"
                }},
                {step_name: {
                    "关键字": "assert_text_comparators",
                    "VALUE": f"{{{{{var_name}}}}}",
                    "EXPECTED": assertion.get("expected", ""),
                    "OP_STR": assertion.get("operator", "==")
                }}
            ]
        
        elif assert_type == "response_time":
            return [{step_name: {
                "关键字": "assert_response_time",
                "MAX_MS": assertion.get("max_ms", 1000)
            }}]
        
        elif assert_type == "json_length":
            var_name = f"_len_var_{index}"
            return [
                {f"提取数组_{index+1}": {
                    "关键字": "ex_jsonData",
                    "EXVALUE": assertion.get("jsonpath", "$"),
                    "VARNAME": var_name,
                    "INDEX": "all"
                }},
                {step_name: {
                    "关键字": "assert_list_length",
                    "LIST_VAR": f"{{{{{var_name}}}}}",
                    "EXPECTED": assertion.get("expected", 0),
                    "OP_STR": assertion.get("operator", ">=")
                }}
            ]
        
        return None
