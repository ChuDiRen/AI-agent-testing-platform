"""
命令行执行器
用于调用插件命令行的执行器
"""
import subprocess
import asyncio
import uuid
import os
import sys
import json
import yaml
import logging
import re
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from core.temp_manager import get_temp_subdir

logger = logging.getLogger(__name__)

# 创建线程池用于执行子进程（解决 Windows 上 asyncio 子进程的兼容性问题）
_executor = ThreadPoolExecutor(max_workers=10)


def parse_test_output(stdout: str) -> Dict[str, Any]:
    """
    解析测试输出，提取关键结果信息
    
    Args:
        stdout: 原始标准输出
    
    Returns:
        解析后的结构化结果
    """
    result = {
        "test_cases": [],
        "summary": {},
        "response_data": None,
    }
    
    # 提取 response_data（支持多种格式）
    # 格式1: -----------current_response_data------------
    # 格式2: -+current_response_data-+
    response_match = re.search(
        r'-+\s*current_response_data\s*-+\s*\n(.+?)\n\s*-+\s*end\s*current_response_data\s*-+',
        stdout, re.DOTALL | re.IGNORECASE
    )
    if response_match:
        try:
            # 尝试解析为字典
            response_str = response_match.group(1).strip()
            result["response_data"] = eval(response_str)  # 因为是 Python dict 格式
        except Exception as e:
            # 如果 eval 失败，尝试用 ast.literal_eval
            try:
                import ast
                result["response_data"] = ast.literal_eval(response_str)
            except:
                result["response_data"] = response_str
    
    # 提取测试用例结果 (格式: test_case_execute[用例名] ... PASSED/FAILED)
    case_pattern = re.compile(r'test_case_execute\[(.+?)\].*?(PASSED|FAILED)', re.DOTALL)
    for match in case_pattern.finditer(stdout):
        result["test_cases"].append({
            "name": match.group(1),
            "status": match.group(2)
        })
    
    # 提取汇总 (格式: 1 passed, 2 failed 等)
    summary_match = re.search(r'=+ (\d+ passed.*?) =+', stdout)
    if summary_match:
        result["summary"]["text"] = summary_match.group(1)
        # 解析数字
        passed = re.search(r'(\d+) passed', stdout)
        failed = re.search(r'(\d+) failed', stdout)
        result["summary"]["passed"] = int(passed.group(1)) if passed else 0
        result["summary"]["failed"] = int(failed.group(1)) if failed else 0
    
    return result


class CommandExecutor:
    """命令行执行器"""
    
    def __init__(self, command: str):
        """
        初始化命令行执行器
        
        Args:
            command: 执行命令（如: webrun, apirun）
        """
        self.command = command
        self._running_tasks: Dict[str, subprocess.Popen] = {}
    
    async def execute_test(
        self,
        test_case_content: str,
        test_case_id: int,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        同步执行测试（等待测试完成后返回结果）
        
        Args:
            test_case_content: 测试用例内容（YAML格式）
            test_case_id: 测试用例ID
            config: 执行配置
        
        Returns:
            执行结果
        """
        try:
            # 生成任务ID
            task_id = str(uuid.uuid4())

            # 使用项目 temp 目录下的 executor 子目录
            temp_dir = get_temp_subdir("executor") / task_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # 文件名需要以数字开头，符合 YamlCaseParser 的命名规范
            case_file = temp_dir / f"1_test_case_{test_case_id}.yaml"
            
            # 检测并转换内容格式：如果是 JSON 则转为 YAML
            yaml_content = test_case_content
            if test_case_content.strip().startswith('{'):
                try:
                    data = json.loads(test_case_content)
                    yaml_content = yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)
                    logger.info(f"Task {task_id}: 已将 JSON 转换为 YAML 格式")
                except json.JSONDecodeError:
                    pass  # 不是有效 JSON，保持原样
            
            case_file.write_text(yaml_content, encoding='utf-8')
            
            # 构建命令行参数（使用绝对路径避免路径解析问题）
            cmd_args = self.command.split()
            cmd_args.extend([
                "--type=yaml",
                f"--cases={case_file.parent.resolve()}",
            ])
            
            # 动态添加配置参数（支持所有自定义参数）
            if config:
                for key, value in config.items():
                    # 跳过内部配置项（不传递给命令行）
                    if key in ("timeout", "work_dir", "_internal"):
                        continue
                    
                    # 跳过已经通过固定参数传递的
                    if key in ("type", "cases"):
                        continue
                    
                    # 转换参数名：下划线转连字符（engine_type -> engine-type）
                    param_name = key.replace("_", "-")
                    
                    # 处理布尔值
                    if isinstance(value, bool):
                        cmd_args.append(f"--{param_name}={str(value).lower()}")
                    # 处理 None 值（跳过）
                    elif value is None:
                        continue
                    # 处理其他值
                    else:
                        cmd_args.append(f"--{param_name}={value}")
            
            # 设置工作目录（默认使用临时目录）
            effective_work_dir = temp_dir
            
            logger.info(f"Executing command: {' '.join(cmd_args)}")
            logger.info(f"Working directory: {effective_work_dir}")
            
            # 获取超时时间
            timeout = config.get("timeout", 120) if config else 120
            
            # 使用临时文件捕获输出（避免 Windows 下 PIPE 缓冲区死锁）
            stdout_file = temp_dir / "stdout.log"
            stderr_file = temp_dir / "stderr.log"
            
            # 定义阻塞执行函数（在线程池中运行，避免阻塞事件循环）
            def _run_subprocess():
                with open(stdout_file, 'w', encoding='utf-8') as f_out, \
                     open(stderr_file, 'w', encoding='utf-8') as f_err:
                    proc = subprocess.Popen(
                        cmd_args,
                        cwd=str(effective_work_dir),
                        stdout=f_out,
                        stderr=f_err,
                        stdin=subprocess.DEVNULL
                    )
                    try:
                        proc.wait(timeout=timeout)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                        logger.warning(f"Task {task_id} timed out after {timeout} seconds")
                    return proc.returncode
            
            # 在线程池中执行阻塞操作，避免阻塞 FastAPI 事件循环
            loop = asyncio.get_event_loop()
            returncode = await loop.run_in_executor(None, _run_subprocess)
            process = type('Process', (), {'returncode': returncode})()
            
            # 读取输出文件
            stdout = stdout_file.read_bytes() if stdout_file.exists() else b''
            stderr = stderr_file.read_bytes() if stderr_file.exists() else b''
            
            stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else ""
            stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else ""
            
            # 调试日志：记录命令输出
            if stderr_str:
                logger.warning(f"Task {task_id} stderr: {stderr_str[:1000]}")
            if not stdout_str and process.returncode != 0:
                logger.error(f"Task {task_id} failed with no output, returncode={process.returncode}")
            
            # 解析测试输出，提取关键结果
            parsed_output = parse_test_output(stdout_str)
            
            # 构建完整执行结果（保存到文件）
            full_result_data = {
                "task_id": task_id,
                "status": "completed" if process.returncode == 0 else "failed",
                "returncode": process.returncode,
                "test_cases": parsed_output["test_cases"],
                "summary": parsed_output["summary"],
                "response_data": parsed_output["response_data"],
                "stderr": stderr_str if stderr_str else None,
                "completed_at": datetime.now().isoformat(),
                "raw_stdout": stdout_str
            }
            
            # 保存完整结果到文件（供后续查询）
            result_file = temp_dir / "result.json"
            result_file.write_text(json.dumps(full_result_data, ensure_ascii=False, indent=2), encoding='utf-8')
            
            logger.info(f"Task {task_id} completed with return code {process.returncode}")
            
            # 复制报告文件到 temp 目录
            try:
                cmd_name = self.command.split()[0]
                executor_base = get_temp_subdir("executor")
                
                # 查找报告文件的可能路径
                report_patterns = []
                
                # 1. 从 temp/executor/executor_install_{cmd_name}/ 目录查找（用户上传的插件）
                for install_dir in executor_base.glob(f"executor_install_*"):
                    # 查找安装目录下的 reports 目录
                    for reports_dir in install_dir.rglob("reports"):
                        report_file = reports_dir / "complete.html"
                        if report_file.exists():
                            report_patterns.append(report_file)
                
                # 2. 从命令名对应的目录查找
                report_patterns.append(executor_base / f"executor_install_{cmd_name}" / "reports" / "complete.html")
                report_patterns.append(executor_base / f"executor_install_{cmd_name.replace('-', '_')}" / "reports" / "complete.html")
                
                # 3. 从系统安装的插件模块路径查找（pip install -e 安装的插件）
                try:
                    # 根据命令名推断模块名（huace-apirun -> apirun）
                    module_name = cmd_name.replace('huace-', '').replace('-', '_')
                    import importlib
                    module = importlib.import_module(module_name)
                    module_root = Path(module.__file__).parent.parent
                    report_patterns.append(module_root / "reports" / "complete.html")
                except Exception:
                    pass
                
                for report_src in report_patterns:
                    if report_src.exists():
                        report_dst = temp_dir / "complete.html"
                        shutil.copy2(report_src, report_dst)
                        logger.info(f"Task {task_id}: 报告已复制到 {report_dst}")
                        break
            except Exception as copy_err:
                logger.warning(f"Task {task_id}: 复制报告失败 {copy_err}")
            
            # 构建简洁的返回结果（给前端展示）
            response_data = parsed_output.get("response_data") or {}
            
            # 解析请求体（可能是 b'...' 格式的字符串）
            request_body = response_data.get("body", "")
            if isinstance(request_body, str) and request_body.startswith("b'"):
                try:
                    # 去掉 b'...' 包装，解析实际内容
                    request_body = eval(request_body).decode('utf-8') if request_body else ""
                except Exception:
                    pass
            
            # 尝试解析为 JSON 格式（更易读）
            try:
                if request_body:
                    request_body = json.loads(request_body)
            except Exception:
                pass
            
            # 解析响应体
            response_body = response_data.get("response", "")
            if response_body:
                try:
                    response_body = json.loads(response_body)
                except Exception:
                    pass
            
            simple_result = {
                "task_id": task_id,
                "status": "completed" if process.returncode == 0 else "failed",
                "test_cases": parsed_output["test_cases"],
                "summary": {
                    "total": parsed_output["summary"].get("passed", 0) + parsed_output["summary"].get("failed", 0),
                    "passed": parsed_output["summary"].get("passed", 0),
                    "failed": parsed_output["summary"].get("failed", 0),
                    "duration": parsed_output["summary"].get("text", "")
                },
                "request": {
                    "url": response_data.get("url", ""),
                    "method": response_data.get("method", ""),
                    "headers": response_data.get("headers", {}),
                    "params": response_data.get("params", {}),
                    "body": request_body
                },
                "response": {
                    "status_code": response_data.get("status_code"),
                    "headers": response_data.get("response_headers", {}),
                    "body": response_body if response_body else None
                },
                "error": stderr_str if stderr_str and process.returncode != 0 else None
            }
            
            # 构建返回结果
            result = {
                "success": True,
                "task_id": task_id,
                "status": simple_result["status"],
                "data": simple_result,
                "case_file": str(case_file),
                "temp_dir": str(temp_dir)
            }
            
            # 注意：不再清理临时目录，保留报告文件供前端查看
            # 如需清理，可通过 /Plugin/cleanupTempFiles 接口定期清理过期报告
            
            return result
        
        except Exception as e:
            import traceback
            error_detail = f"{type(e).__name__}: {str(e)}"
            logger.error(f"Execute test failed: {error_detail}", exc_info=True)
            return {
                "success": False,
                "error": error_detail,
                "traceback": traceback.format_exc()
            }

    def _get_work_dir(self) -> Path:
        """获取工作目录（临时文件存放目录）"""
        # 使用项目 temp 目录下的 executor 子目录
        return get_temp_subdir("executor")
    
    def _wait_and_save_result(self, task_id: str, process: subprocess.Popen, temp_dir: Path, timeout: int = 60):
        """在后台线程中等待测试完成并保存结果"""
        try:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                logger.warning(f"Task {task_id} timed out after {timeout} seconds")
            
            stdout_str = stdout.decode('utf-8', errors='ignore') if stdout else ""
            stderr_str = stderr.decode('utf-8', errors='ignore') if stderr else ""
            
            # 解析测试输出，提取关键结果
            parsed_output = parse_test_output(stdout_str)
            
            # 构建执行结果
            result_data = {
                "task_id": task_id,
                "status": "completed" if process.returncode == 0 else "failed",
                "returncode": process.returncode,
                "test_cases": parsed_output["test_cases"],
                "summary": parsed_output["summary"],
                "response_data": parsed_output["response_data"],
                "stderr": stderr_str if stderr_str else None,
                "completed_at": datetime.now().isoformat()
            }
            
            # 保存完整结果到文件
            full_result = {**result_data, "raw_stdout": stdout_str}
            result_file = temp_dir / "result.json"
            result_file.write_text(json.dumps(full_result, ensure_ascii=False, indent=2), encoding='utf-8')
            
            logger.info(f"Task {task_id} completed with return code {process.returncode}")
            
            # 从运行任务中移除
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
        
        except Exception as e:
            logger.error(f"Wait for completion failed: {str(e)}", exc_info=True)
    
    async def _wait_for_completion(self, task_id: str, process, temp_dir: Path):
        """等待测试完成（异步版本，保留兼容性）"""
        try:
            stdout, stderr = await process.communicate()
            
            # 保存执行结果
            result_file = temp_dir / "result.json"
            result_data = {
                "task_id": task_id,
                "status": "completed" if process.returncode == 0 else "failed",
                "returncode": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "completed_at": datetime.now().isoformat()
            }
            
            result_file.write_text(json.dumps(result_data, ensure_ascii=False, indent=2), encoding='utf-8')
            
            logger.info(f"Task {task_id} completed with return code {process.returncode}")
            
            # 从运行任务中移除
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
        
        except Exception as e:
            logger.error(f"Wait for completion failed: {str(e)}", exc_info=True)
    
    async def get_task_status(self, task_id: str, temp_dir: str) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            task_id: 任务ID
            temp_dir: 临时目录
        
        Returns:
            任务状态
        """
        try:
            temp_path = Path(temp_dir)
            result_file = temp_path / "result.json"
            
            # 检查是否完成
            if result_file.exists():
                result_data = json.loads(result_file.read_text(encoding='utf-8'))
                return {
                    "success": True,
                    "data": result_data
                }
            
            # 检查是否还在运行
            if task_id in self._running_tasks:
                task_info = self._running_tasks[task_id]
                process = task_info["process"]
                if process.poll() is None:
                    return {
                        "success": True,
                        "data": {
                            "task_id": task_id,
                            "status": "running",
                            "message": "Test is still running"
                        }
                    }
            
            return {
                "success": False,
                "error": "Task not found or status unavailable"
            }
        
        except Exception as e:
            logger.error(f"Get task status failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            task_id: 任务ID
        
        Returns:
            取消结果
        """
        try:
            if task_id in self._running_tasks:
                process = self._running_tasks[task_id]
                process.terminate()
                
                # 等待进程结束
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()

                del self._running_tasks[task_id]

                return {
                    "success": True,
                    "message": "Task cancelled"
                }

            return {
                "success": False,
                "error": "Task not found or already completed"
            }

        except Exception as e:
            logger.error(f"Cancel task failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
