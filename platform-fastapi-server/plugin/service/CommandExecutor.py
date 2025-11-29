"""
命令行执行器
用于调用插件命令行的执行器
"""
import subprocess
import asyncio
import uuid
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from core.minio_client import minio_client

logger = logging.getLogger(__name__)


class CommandExecutor:
    """命令行执行器"""
    
    def __init__(self, command: str, work_dir: str, storage_path: Optional[str] = None):
        """
        初始化命令行执行器
        
        Args:
            command: 执行命令（如: python -m webrun.cli）
            work_dir: 工作目录（逻辑工作目录，实际执行目录可能为从 MinIO 同步后的临时目录）
            storage_path: 插件在 MinIO 中的存储路径（bucket/object_name）
        """
        self.command = command
        self.work_dir = work_dir
        self.storage_path = storage_path
        self._running_tasks: Dict[str, subprocess.Popen] = {}
    
    async def execute_test(
        self,
        test_case_content: str,
        test_case_id: int,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行测试
        
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

            # 准备实际执行目录: 如果配置了 storage_path, 则从 MinIO 下载 latest.zip 并解压到本地临时目录
            # 否则仍然使用初始化传入的 work_dir
            effective_work_dir = await self._prepare_work_dir_from_minio(task_id)

            # 创建临时用例文件
            temp_dir = Path(effective_work_dir) / "temp" / task_id
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            case_file = temp_dir / f"test_case_{test_case_id}.yaml"
            case_file.write_text(test_case_content, encoding='utf-8')
            
            # 构建命令行参数
            cmd_args = self.command.split()
            cmd_args.extend([
                "--type=yaml",
                f"--cases={case_file.parent}",
            ])
            
            # 添加配置参数
            if config:
                if "browser" in config:
                    cmd_args.append(f"--browser={config['browser']}")
                if "headless" in config:
                    cmd_args.append(f"--headless={str(config['headless']).lower()}")
            
            logger.info(f"Executing command: {' '.join(cmd_args)}")
            logger.info(f"Working directory: {effective_work_dir}")
            
            # 异步执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd_args,
                cwd=str(effective_work_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 保存进程引用
            self._running_tasks[task_id] = process
            
            # 启动后台任务等待完成
            asyncio.create_task(self._wait_for_completion(task_id, process, temp_dir))
            
            return {
                "success": True,
                "task_id": task_id,
                "status": "running",
                "message": "Test execution started",
                "case_file": str(case_file),
                "temp_dir": str(temp_dir)
            }
        
        except Exception as e:
            logger.error(f"Execute test failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def _prepare_work_dir_from_minio(self, task_id: str) -> Path:
        """根据 storage_path 从 MinIO 同步插件到本地, 返回实际执行目录

        - 如果未配置 storage_path, 直接返回 self.work_dir 对应的 Path
        - 当前实现假设 storage_path 格式为 "<bucket>/<object_name>",
          其中 object_name 为 plugins/{plugin_code}/latest.zip
        """
        base_work_dir = Path(self.work_dir)

        # 未启用 MinIO 同步, 直接使用现有工作目录
        if not self.storage_path:
            return base_work_dir

        try:
            bucket, object_name = self.storage_path.split("/", 1)
        except ValueError:
            logger.warning(f"Invalid storage_path format: {self.storage_path}, fallback to local work_dir")
            return base_work_dir

        # 本地临时插件目录: <work_dir>/.__plugins__/<plugin_code>
        plugin_code = object_name.split("/")[1] if "/" in object_name else "plugin"
        local_plugins_root = base_work_dir / ".__plugins__"
        local_plugins_root.mkdir(parents=True, exist_ok=True)
        local_plugin_dir = local_plugins_root / plugin_code

        # 下载 ZIP 到临时文件
        temp_zip_path = local_plugins_root / f"{plugin_code}_{task_id}.zip"
        try:
            logger.info(f"Downloading plugin from MinIO: {self.storage_path} -> {temp_zip_path}")
            minio_client.client.fget_object(bucket, object_name, str(temp_zip_path))

            # 清理旧目录
            if local_plugin_dir.exists():
                for child in local_plugin_dir.iterdir():
                    if child.is_file():
                        child.unlink()
                    else:
                        # 简单递归删除
                        for root, dirs, files in os.walk(child, topdown=False):
                            for name in files:
                                os.remove(os.path.join(root, name))
                            for name in dirs:
                                os.rmdir(os.path.join(root, name))
                        child.rmdir()
            else:
                local_plugin_dir.mkdir(parents=True, exist_ok=True)

            # 解压到本地插件目录
            import zipfile
            with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                zip_ref.extractall(local_plugin_dir)

            logger.info(f"Plugin extracted to: {local_plugin_dir}")

        except Exception as e:
            logger.error(f"Failed to sync plugin from MinIO: {e}", exc_info=True)
            # 失败时退回原始 work_dir
            return base_work_dir
        finally:
            # 删除临时 ZIP
            try:
                if temp_zip_path.exists():
                    temp_zip_path.unlink()
            except Exception:
                pass

        # 如果 ZIP 内部还有一层目录, 可以根据需要再探测一层, 暂时直接使用解压目录
        return local_plugin_dir
    
    async def _wait_for_completion(self, task_id: str, process, temp_dir: Path):
        """等待测试完成"""
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
                process = self._running_tasks[task_id]
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
