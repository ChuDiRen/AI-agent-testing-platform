"""
k6 脚本生成器
"""
import json
from typing import Dict, Any, List


class K6ScriptGenerator:
    """k6 JavaScript 脚本生成器"""
    
    def generate(self, case: Dict[str, Any]) -> str:
        """根据 YAML 配置生成 k6 脚本"""
        config = case.get("config", {})
        scenarios = case.get("scenarios", [])
        context = case.get("context", {})
        
        imports = self._generate_imports()
        options = self._generate_options(config)
        variables = self._generate_variables(context)
        default_func = self._generate_default_function(scenarios, context)
        
        script = f"""{imports}

{variables}

{options}

{default_func}
"""
        return script
    
    def _generate_imports(self) -> str:
        return """import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const requestDuration = new Trend('request_duration');"""
    
    def _generate_variables(self, context: Dict[str, Any]) -> str:
        if not context:
            return "// 无全局变量"
        
        lines = ["// 全局变量"]
        for key, value in context.items():
            if isinstance(value, str):
                lines.append(f"const {key} = '{value}';")
            elif isinstance(value, (int, float)):
                lines.append(f"const {key} = {value};")
            elif isinstance(value, bool):
                lines.append(f"const {key} = {str(value).lower()};")
            else:
                lines.append(f"const {key} = {json.dumps(value)};")
        return "\n".join(lines)
    
    def _generate_options(self, config: Dict[str, Any]) -> str:
        options = {}
        if "stages" in config:
            options["stages"] = config["stages"]
        if "thresholds" in config:
            options["thresholds"] = config["thresholds"]
        if "vus" in config:
            options["vus"] = config["vus"]
        if "duration" in config:
            options["duration"] = config["duration"]
        if "iterations" in config:
            options["iterations"] = config["iterations"]
        
        if not options:
            options = {"vus": 1, "duration": "30s"}
        
        return f"export const options = {json.dumps(options, indent=2)};"
    
    def _generate_default_function(self, scenarios: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        if not scenarios:
            return """export default function () {
  console.log('No scenarios defined');
}"""
        
        lines = ["export default function () {"]
        
        for i, scenario in enumerate(scenarios):
            name = scenario.get("name", f"场景{i+1}")
            method = scenario.get("method", "GET").upper()
            url = scenario.get("url", "")
            headers = scenario.get("headers", {})
            body = scenario.get("body", None)
            checks = scenario.get("checks", [])
            sleep_time = scenario.get("sleep", "1")
            
            url = self._process_template(url, context)
            
            lines.append(f"  group('{name}', function () {{")
            
            params_json = json.dumps({"headers": headers}) if headers else "{}"
            
            if method == "GET":
                lines.append(f"    const res = http.get(`{url}`, {params_json});")
            elif method == "POST":
                body_json = json.dumps(body) if body else "null"
                lines.append(f"    const res = http.post(`{url}`, JSON.stringify({body_json}), {params_json});")
            elif method == "PUT":
                body_json = json.dumps(body) if body else "null"
                lines.append(f"    const res = http.put(`{url}`, JSON.stringify({body_json}), {params_json});")
            elif method == "DELETE":
                lines.append(f"    const res = http.del(`{url}`, null, {params_json});")
            else:
                lines.append(f"    const res = http.request('{method}', `{url}`, null, {params_json});")
            
            if checks:
                lines.append("    check(res, {")
                for check in checks:
                    check_name, check_expr = self._parse_check(check)
                    lines.append(f"      '{check_name}': (r) => {check_expr},")
                lines.append("    });")
            else:
                lines.append("    check(res, { 'status is 200': (r) => r.status === 200 });")
            
            lines.append("    errorRate.add(res.status !== 200);")
            lines.append("    requestDuration.add(res.timings.duration);")
            lines.append("  });")
            
            if sleep_time:
                sleep_val = sleep_time.replace("s", "") if isinstance(sleep_time, str) else sleep_time
                lines.append(f"  sleep({sleep_val});")
            lines.append("")
        
        lines.append("}")
        return "\n".join(lines)
    
    def _process_template(self, template: str, context: Dict[str, Any]) -> str:
        import re
        result = template
        for match in re.finditer(r'\{\{(\w+)\}\}', template):
            var_name = match.group(1)
            result = result.replace(match.group(0), f"${{{var_name}}}")
        return result
    
    def _parse_check(self, check: str) -> tuple:
        check = check.strip()
        if check.startswith("status"):
            parts = check.split()
            if len(parts) >= 3:
                op = parts[1]
                value = parts[2]
                return (f"status {op} {value}", f"r.status {op} {value}")
        if "body.contains" in check:
            import re
            match = re.search(r'body\.contains\(["\'](.+?)["\']\)', check)
            if match:
                text = match.group(1)
                return (f"body contains {text}", f"r.body.includes('{text}')")
        return (check, "r.status === 200")
