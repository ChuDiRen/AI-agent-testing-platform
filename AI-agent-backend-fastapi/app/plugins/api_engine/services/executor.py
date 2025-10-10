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
        import traceback
        from datetime import datetime

        execution_result = {
            "status": "running",
            "logs": "",
            "error_message": None,
            "response_data": None,
            "context": {},
            "execution_time": None,
            "step_results": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None
        }

        try:
            # 设置全局变量
            from ..engine.core.globalContext import g_context
            g_context().clear()  # 清空之前的上下文
            g_context().set_by_dict(context)

            # 验证YAML格式
            try:
                caseinfo = yaml.safe_load(yaml_content)
                if not caseinfo:
                    raise ValueError("YAML内容为空或格式不正确")
            except yaml.YAMLError as e:
                raise ValueError(f"YAML格式错误: {str(e)}")

            # 预处理：检查必要字段
            if not isinstance(caseinfo, dict):
                raise ValueError("YAML根节点必须是字典")

            # 初始化日志捕获
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            # 记录开始时间
            start_time = datetime.now()

            # 执行用例
            from ..engine.core.ApiTestRunner import TestRunner
            runner = TestRunner()

            print(f"===== 开始执行用例 =====")
            print(f"用例描述: {caseinfo.get('desc', 'N/A')}")
            print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"========================")

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                try:
                    runner.test_case_execute(caseinfo)
                    execution_result["status"] = "success"
                    execution_result["error_message"] = None
                except Exception as e:
                    execution_result["status"] = "failed"
                    execution_result["error_message"] = str(e)
                    # 添加异常堆栈信息到日志
                    print(f"\n===== 执行异常 =====")
                    print(f"异常类型: {type(e).__name__}")
                    print(f"异常信息: {str(e)}")
                    print(f"异常堆栈:")
                    traceback.print_exc()
                    print(f"==================")

            # 记录结束时间
            end_time = datetime.now()
            execution_result["end_time"] = end_time.isoformat()
            execution_result["execution_time"] = (end_time - start_time).total_seconds()

            # 获取输出日志
            logs = stdout_capture.getvalue() + stderr_capture.getvalue()
            execution_result["logs"] = logs

            # 解析响应数据
            response_data = self._parse_response_data(logs)
            execution_result["response_data"] = response_data

            # 获取最终上下文
            execution_result["context"] = g_context().show_dict()

            # 解析步骤结果
            execution_result["step_results"] = self._parse_step_results(logs)

            print(f"===== 执行完成 =====")
            print(f"状态: {execution_result['status']}")
            print(f"执行时间: {execution_result['execution_time']:.2f}s")
            print(f"==================")

            return execution_result

        except Exception as e:
            # 系统级错误（不是用例执行失败）
            end_time = datetime.now()
            execution_result.update({
                "status": "error",
                "error_message": str(e),
                "end_time": end_time.isoformat(),
                "execution_time": (end_time - datetime.fromisoformat(execution_result["start_time"])).total_seconds(),
                "logs": f"系统错误: {str(e)}\n{traceback.format_exc()}"
            })

            return execution_result
    
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

    def _parse_step_results(self, logs: str) -> List[Dict[str, Any]]:
        """
        从日志中解析步骤执行结果

        Args:
            logs: 执行日志

        Returns:
            步骤结果列表
        """
        step_results = []
        try:
            # 查找步骤执行标记
            step_pattern = r'开始执行步骤：(.*?)\n(.*?)(?=\n开始执行步骤：|\n========执行完毕========|\n=====|$)'
            matches = re.findall(step_pattern, logs, re.DOTALL)

            for i, (step_name, step_output) in enumerate(matches, 1):
                # 解析步骤状态
                status = "success"
                error_message = None

                if "❌" in step_output or "ERROR" in step_output or "异常" in step_output:
                    status = "failed"
                    # 尝试提取错误信息
                    error_lines = [line for line in step_output.split('\n') if '❌' in line or 'ERROR' in line]
                    if error_lines:
                        error_message = error_lines[0].strip()

                # 解析响应数据（如果有）
                response_data = None
                response_pattern = r'-----------current_response_data------------\n(.*?)\n----------end current_response_data-------------'
                response_match = re.search(response_pattern, step_output, re.DOTALL)
                if response_match:
                    try:
                        import ast
                        response_data = ast.literal_eval(response_match.group(1))
                    except:
                        pass

                step_results.append({
                    "step_number": i,
                    "step_name": step_name.strip(),
                    "status": status,
                    "output": step_output.strip(),
                    "error_message": error_message,
                    "response_data": response_data
                })

        except Exception as e:
            # 如果解析失败，至少记录执行过步骤
            step_count = logs.count("开始执行步骤：")
            for i in range(1, step_count + 1):
                step_results.append({
                    "step_number": i,
                    "step_name": f"步骤 {i}",
                    "status": "unknown",
                    "output": "解析失败",
                    "error_message": f"日志解析异常: {str(e)}",
                    "response_data": None
                })

        return step_results

