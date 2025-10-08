# Copyright (c) 2025 左岚. All rights reserved.
"""
API引擎执行器服务
"""
import yaml
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional
import re


class ApiEngineExecutor:
    """API引擎执行器"""
    
    def __init__(self):
        pass
    
    def execute_case(self, yaml_content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行测试用例
        
        Args:
            yaml_content: YAML格式的用例内容
            context: 执行上下文(全局变量)
        
        Returns:
            执行结果字典
        """
        try:
            # 设置全局变量
            from ..engine.core.globalContext import g_context
            g_context().set_by_dict(context)
            
            # 解析YAML内容
            caseinfo = yaml.safe_load(yaml_content)
            
            # 捕获输出
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # 执行用例
            from ..engine.core.ApiTestRunner import TestRunner
            runner = TestRunner()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                try:
                    runner.test_case_execute(caseinfo)
                    status = "success"
                    error_message = None
                except Exception as e:
                    status = "failed"
                    error_message = str(e)
            
            # 获取输出日志
            logs = stdout_capture.getvalue() + stderr_capture.getvalue()
            
            # 解析响应数据
            response_data = self._parse_response_data(logs)
            
            return {
                "status": status,
                "logs": logs,
                "error_message": error_message,
                "response_data": response_data,
                "context": g_context().show_dict()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "logs": "",
                "error_message": str(e),
                "response_data": None,
                "context": {}
            }
    
    def form_to_yaml(self, config_data: Dict[str, Any]) -> str:
        """
        将表单配置转换为YAML格式
        
        Args:
            config_data: 表单配置数据
        
        Returns:
            YAML字符串
        """
        yaml_obj = {
            'desc': config_data.get('desc', ''),
            'pre_script': config_data.get('pre_script', []),
            'steps': [],
            'post_script': config_data.get('post_script', []),
        }
        
        # 处理步骤
        for step in config_data.get('steps', []):
            step_name = step.get('name', '')
            step_params = step.get('params', {})
            yaml_obj['steps'].append({step_name: step_params})
        
        # 处理DDT数据
        if 'ddts' in config_data and config_data['ddts']:
            yaml_obj['ddts'] = config_data['ddts']
        
        # 处理context
        if 'context' in config_data and config_data['context']:
            yaml_obj['context'] = config_data['context']
        
        return yaml.dump(yaml_obj, allow_unicode=True, default_flow_style=False)
    
    def _parse_response_data(self, logs: str) -> Optional[Dict[str, Any]]:
        """
        从日志中解析响应数据
        
        Args:
            logs: 执行日志
        
        Returns:
            响应数据字典或None
        """
        try:
            # 查找特殊标记之间的内容
            pattern = r'-----------current_response_data------------\n(.*?)\n----------end current_response_data-------------'
            match = re.search(pattern, logs, re.DOTALL)
            
            if match:
                response_str = match.group(1)
                # 尝试解析为字典
                import ast
                return ast.literal_eval(response_str)
            
            return None
        except Exception:
            return None

