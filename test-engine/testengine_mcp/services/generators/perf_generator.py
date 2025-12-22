"""
性能测试用例生成器
"""
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import BaseGenerator


class PerfCaseGenerator(BaseGenerator):
    """性能测试用例生成器"""
    
    def generate(
        self,
        name: str,
        description: str,
        host: str,
        scenarios: List[Dict[str, Any]],
        users: int = 10,
        spawn_rate: float = 1,
        run_time: str = "60s",
        think_time: Optional[Dict[str, Any]] = None,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        生成性能测试用例
        
        场景类型 (scenarios):
        - GET 请求: {"method": "get", "url": "/api/users", "name": "获取用户列表"}
        - POST 请求: {"method": "post", "url": "/api/login", "name": "登录", "json": {...}}
        
        断言类型:
        - check_status: 状态码检查
        - check_response_time: 响应时间检查
        - check_contains: 响应包含检查
        - validate_json: JSON 验证
        """
        steps = []
        
        # 构建每个场景的步骤
        for i, scenario in enumerate(scenarios):
            method = scenario.get("method", "get").lower()
            url = scenario.get("url", "/")
            req_name = scenario.get("name", f"请求_{i+1}")
            
            # 构建请求步骤
            request_step = {
                "关键字": method,
                "url": url,
                "name": req_name
            }
            
            # 添加请求参数
            if "params" in scenario:
                request_step["params"] = scenario["params"]
            if "json" in scenario:
                request_step["json"] = scenario["json"]
            if "data" in scenario:
                request_step["data"] = scenario["data"]
            if "headers" in scenario:
                request_step["headers"] = scenario["headers"]
            
            steps.append({req_name: request_step})
            
            # 添加断言
            self._add_assertions(steps, scenario, i)
            
            # 添加思考时间
            if think_time:
                self._add_think_time(steps, think_time, i)
        
        # 构建完整用例
        case = {
            "desc": description or name,
            "host": host,
            "context": {
                "users": users,
                "spawn_rate": spawn_rate,
                "run_time": run_time
            },
            "steps": steps
        }
        
        # 保存用例
        save_file = self._get_save_path(save_path, name, "perf-cases_yaml")
        self._save_case(save_file, case)
        
        return self._build_result(
            case, save_file, "perf", "性能测试用例已生成",
            perf_config={
                "host": host,
                "users": users,
                "spawn_rate": spawn_rate,
                "run_time": run_time
            }
        )
    
    def _add_assertions(self, steps: List[Dict], scenario: Dict[str, Any], index: int) -> None:
        """添加断言步骤"""
        if "check_status" in scenario:
            steps.append({f"检查状态码_{index+1}": {
                "关键字": "check_status",
                "expected": scenario["check_status"].get("expected", 200)
            }})
        
        if "check_response_time" in scenario:
            steps.append({f"检查响应时间_{index+1}": {
                "关键字": "check_response_time",
                "max_ms": scenario["check_response_time"].get("max_ms", 1000)
            }})
        
        if "check_contains" in scenario:
            steps.append({f"检查响应内容_{index+1}": {
                "关键字": "check_contains",
                "text": scenario["check_contains"].get("text", "")
            }})
        
        if "validate_json" in scenario:
            steps.append({f"验证JSON_{index+1}": {
                "关键字": "validate_json",
                "path": scenario["validate_json"].get("path", "$"),
                "expected": scenario["validate_json"].get("expected", "")
            }})
    
    def _add_think_time(self, steps: List[Dict], think_time: Dict[str, Any], index: int) -> None:
        """添加思考时间"""
        if "seconds" in think_time:
            steps.append({f"思考时间_{index+1}": {
                "关键字": "think_time",
                "seconds": think_time["seconds"]
            }})
        elif "min" in think_time and "max" in think_time:
            steps.append({f"随机等待_{index+1}": {
                "关键字": "think_time",
                "min": think_time["min"],
                "max": think_time["max"]
            }})
