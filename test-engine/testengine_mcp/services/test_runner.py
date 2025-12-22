"""
测试运行服务
执行测试用例并生成精美报告
"""
import os
import sys
import tempfile
import asyncio
import subprocess
import time
import shutil
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import yaml

from .report_service import ReportService

# mcp 模块的根目录
PROJECT_ROOT = Path(__file__).parent.parent
# test-engine 的目录（mcp 的父目录）
TEST_ENGINE_ROOT = PROJECT_ROOT.parent


class TestRunnerService:
    """测试运行服务 - 核心执行引擎"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.test_engine_root = TEST_ENGINE_ROOT
        self.reports_dir = self.test_engine_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)
        self.examples_dir = self.test_engine_root / "examples"
        
        # 报告服务
        self._report_service = ReportService(self.reports_dir)
    
    # ==================== 测试执行 ====================
    
    async def run_test_case(
        self,
        engine_type: str,
        case_content: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """运行单个测试用例"""
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=f"{engine_type}_test_")
            
            # 写入 context.yaml
            context_file = Path(temp_dir) / "context.yaml"
            context_data = context or {}
            context_data["ENGINE_TYPE"] = engine_type
            
            with open(context_file, 'w', encoding='utf-8') as f:
                yaml.dump(context_data, f, allow_unicode=True)
            
            # 写入测试用例
            case_file = Path(temp_dir) / "test_case.yaml"
            with open(case_file, 'w', encoding='utf-8') as f:
                yaml.dump(case_content, f, allow_unicode=True)
            
            # 执行测试
            result = await self._execute_test(engine_type, temp_dir, "yaml", context)
            return result
            
        except Exception as e:
            return {"success": False, "message": f"测试执行失败: {str(e)}", "error": str(e)}
        finally:
            if temp_dir and Path(temp_dir).exists():
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
    
    async def run_test_from_file(
        self,
        case_file_path: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """运行指定文件的测试用例"""
        try:
            case_path = Path(case_file_path)
            if not case_path.exists():
                return {"success": False, "message": f"用例文件不存在: {case_file_path}"}
            
            # 读取用例
            with open(case_path, 'r', encoding='utf-8') as f:
                case_content = yaml.safe_load(f)
            
            # 确定引擎类型
            cases_dir = case_path.parent
            engine_type = self._detect_engine_type(cases_dir)
            
            # 执行测试
            result = await self._execute_test(engine_type, str(cases_dir), "yaml", context)
            result["case_file"] = str(case_path)
            return result
            
        except Exception as e:
            return {"success": False, "message": f"执行失败: {str(e)}", "error": str(e)}
    
    async def run_test_directory(
        self,
        cases_dir: str,
        engine_type: Optional[str] = None,
        case_type: str = "yaml",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """运行整个目录的测试用例"""
        try:
            cases_path = Path(cases_dir)
            if not cases_path.is_absolute():
                cases_path = self.test_engine_root / cases_dir
            
            if not cases_path.exists():
                return {"success": False, "message": f"用例目录不存在: {cases_path}"}
            
            # 确定引擎类型
            if not engine_type:
                engine_type = self._detect_engine_type(cases_path)
            
            # 统计用例数量
            case_files = list(cases_path.glob("*.yaml")) + list(cases_path.glob("*.yml"))
            case_files = [f for f in case_files if f.name != "context.yaml"]
            
            result = await self._execute_test(engine_type, str(cases_path), case_type, context)
            result["cases_dir"] = str(cases_path)
            result["case_count"] = len(case_files)
            return result
            
        except Exception as e:
            return {"success": False, "message": f"执行失败: {str(e)}", "error": str(e)}
    
    async def run_test_cases_batch(
        self,
        engine_type: str,
        cases: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """批量运行测试用例"""
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(prefix=f"{engine_type}_batch_")
            
            # 写入 context.yaml
            context_file = Path(temp_dir) / "context.yaml"
            context_data = context or {}
            context_data["ENGINE_TYPE"] = engine_type
            
            with open(context_file, 'w', encoding='utf-8') as f:
                yaml.dump(context_data, f, allow_unicode=True)
            
            # 写入所有测试用例
            for i, case in enumerate(cases):
                case_file = Path(temp_dir) / f"{i+1:03d}_test_case.yaml"
                with open(case_file, 'w', encoding='utf-8') as f:
                    yaml.dump(case, f, allow_unicode=True)
            
            # 执行测试
            result = await self._execute_test(engine_type, temp_dir, "yaml", context)
            result["total_cases"] = len(cases)
            return result
            
        except Exception as e:
            return {"success": False, "message": f"批量测试执行失败: {str(e)}", "error": str(e)}
        finally:
            if temp_dir and Path(temp_dir).exists():
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
    
    def _detect_engine_type(self, cases_path: Path) -> str:
        """从目录或配置文件检测引擎类型"""
        # 从 context.yaml 读取
        context_file = cases_path / "context.yaml"
        if context_file.exists():
            with open(context_file, 'r', encoding='utf-8') as f:
                ctx = yaml.safe_load(f) or {}
                if engine_type := ctx.get("ENGINE_TYPE"):
                    return engine_type.lower()
        
        # 从目录名推断
        dir_name = cases_path.name.lower()
        if "web" in dir_name:
            return "web"
        elif "mobile" in dir_name:
            return "mobile"
        elif "perf" in dir_name:
            return "perf"
        return "api"
    
    async def _execute_test(
        self,
        engine_type: str,
        cases_dir: str,
        case_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """执行测试的核心方法"""
        start_time = time.time()
        
        # 构建命令
        cmd = [
            sys.executable, "-m", "testrun.cli",
            f"--engine-type={engine_type}",
            f"--type={case_type}",
            f"--cases={cases_dir}"
        ]
        
        # 添加引擎特定参数
        if engine_type == "web" and context:
            if "BROWSER" in context:
                cmd.append(f"--browser={context['BROWSER']}")
            if "HEADLESS" in context:
                cmd.append(f"--headless={'true' if context['HEADLESS'] else 'false'}")
        
        if engine_type == "mobile" and context:
            if "PLATFORM" in context:
                cmd.append(f"--platform={context['PLATFORM']}")
            if "SERVER" in context:
                cmd.append(f"--server={context['SERVER']}")
        
        if engine_type == "perf" and context:
            if "users" in context:
                cmd.append(f"--users={context['users']}")
            if "spawn_rate" in context:
                cmd.append(f"--spawn-rate={context['spawn_rate']}")
            if "run_time" in context:
                cmd.append(f"--run-time={context['run_time']}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.test_engine_root),
                capture_output=True,
                text=True,
                timeout=600,
                env={**os.environ, "PYTHONPATH": str(self.test_engine_root)}
            )
            
            duration = time.time() - start_time
            
            # 解析输出获取统计信息
            stdout = result.stdout or ""
            stderr = result.stderr or ""
            stats = self._parse_test_output(stdout)
            
            # 查找报告
            report_info = self._report_service.find_latest_report()
            
            return {
                "success": result.returncode == 0,
                "message": "测试执行完成" if result.returncode == 0 else "测试执行失败",
                "duration_seconds": round(duration, 2),
                "engine_type": engine_type,
                "return_code": result.returncode,
                "statistics": stats,
                "report": report_info,
                "output": {
                    "stdout": stdout[-3000:] if len(stdout) > 3000 else stdout,
                    "stderr": stderr[-1000:] if len(stderr) > 1000 else stderr
                }
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "message": "测试执行超时（超过10分钟）",
                "duration_seconds": 600,
                "error": "Timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"测试执行异常: {str(e)}",
                "duration_seconds": time.time() - start_time,
                "error": str(e)
            }
    
    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """解析测试输出获取统计信息"""
        stats = {"passed": 0, "failed": 0, "skipped": 0, "total": 0}
        
        # 尝试提取 pytest 格式的统计
        patterns = [
            (r'(\d+)\s*passed', 'passed'),
            (r'(\d+)\s*failed', 'failed'),
            (r'(\d+)\s*skipped', 'skipped'),
            (r'(\d+)\s*error', 'error'),
        ]
        
        for pattern, key in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                stats[key] = int(match.group(1))
        
        stats["total"] = stats["passed"] + stats["failed"] + stats.get("skipped", 0)
        return stats
    
    # ==================== 快速 API 测试 ====================
    
    async def run_api_test(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        expected_status: int = 200,
        expected_contains: Optional[str] = None,
        expected_json: Optional[Dict[str, Any]] = None,
        max_response_time_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """快速运行单个 API 测试（无需创建用例文件）"""
        try:
            import httpx
            
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_body
                )
            
            duration_ms = (time.time() - start_time) * 1000
            
            # 验证结果
            assertions = []
            all_passed = True
            
            # 状态码断言
            status_passed = response.status_code == expected_status
            assertions.append({
                "name": "状态码检查",
                "type": "status_code",
                "expected": expected_status,
                "actual": response.status_code,
                "passed": status_passed
            })
            if not status_passed:
                all_passed = False
            
            # 响应时间断言
            if max_response_time_ms:
                time_passed = duration_ms <= max_response_time_ms
                assertions.append({
                    "name": "响应时间检查",
                    "type": "response_time",
                    "expected": f"<= {max_response_time_ms}ms",
                    "actual": f"{duration_ms:.2f}ms",
                    "passed": time_passed
                })
                if not time_passed:
                    all_passed = False
            
            # 内容断言
            if expected_contains:
                contains_passed = expected_contains in response.text
                assertions.append({
                    "name": "响应包含检查",
                    "type": "contains",
                    "expected": expected_contains,
                    "passed": contains_passed
                })
                if not contains_passed:
                    all_passed = False
            
            # JSON 字段断言
            response_json = None
            try:
                response_json = response.json()
            except:
                pass
            
            if expected_json and response_json:
                try:
                    import jsonpath
                    for path, expected_val in expected_json.items():
                        try:
                            actual_val = jsonpath.jsonpath(response_json, path)
                            if actual_val:
                                actual_val = actual_val[0]
                            json_passed = actual_val == expected_val
                            assertions.append({
                                "name": f"JSON字段检查: {path}",
                                "type": "json_field",
                                "path": path,
                                "expected": expected_val,
                                "actual": actual_val,
                                "passed": json_passed
                            })
                            if not json_passed:
                                all_passed = False
                        except Exception as e:
                            assertions.append({
                                "name": f"JSON字段检查: {path}",
                                "type": "json_field",
                                "path": path,
                                "expected": expected_val,
                                "error": str(e),
                                "passed": False
                            })
                            all_passed = False
                except ImportError:
                    # jsonpath 库未安装，跳过 JSON 断言
                    pass
            
            return {
                "success": all_passed,
                "message": "API 测试通过" if all_passed else "API 测试失败",
                "duration_ms": round(duration_ms, 2),
                "request": {
                    "url": url,
                    "method": method.upper(),
                    "headers": headers,
                    "params": params,
                    "data": data,
                    "json": json_body
                },
                "response": {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "json": response_json,
                    "text": response.text[:2000] if len(response.text) > 2000 else response.text
                },
                "assertions": assertions,
                "summary": {
                    "total": len(assertions),
                    "passed": sum(1 for a in assertions if a["passed"]),
                    "failed": sum(1 for a in assertions if not a["passed"])
                }
            }
            
        except Exception as e:
            return {"success": False, "message": f"API 测试执行失败: {str(e)}", "error": str(e)}
    
    # ==================== 报告代理方法 ====================
    
    def get_test_report(self, report_name: Optional[str] = None) -> Dict[str, Any]:
        """获取测试报告详情"""
        return self._report_service.get_report(report_name)
    
    def list_reports(self, limit: int = 20) -> Dict[str, Any]:
        """列出所有测试报告"""
        return self._report_service.list_reports(limit)
    
    def generate_report_summary(self) -> Dict[str, Any]:
        """生成报告摘要"""
        return self._report_service.generate_summary()


# 单例实例
_test_runner_service: Optional[TestRunnerService] = None


def get_test_runner_service() -> TestRunnerService:
    """获取测试运行服务单例"""
    global _test_runner_service
    if _test_runner_service is None:
        _test_runner_service = TestRunnerService()
    return _test_runner_service
