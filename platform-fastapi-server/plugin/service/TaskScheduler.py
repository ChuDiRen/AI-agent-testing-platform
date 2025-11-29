"""
测试任务调度器（命令行调用版本）
负责接收测试任务、选择合适的执行器插件并通过命令行调度执行
"""
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime
import logging

from ..model.PluginModel import Plugin
from .CommandExecutor import CommandExecutor

logger = logging.getLogger(__name__)


class TaskScheduler:
    """测试任务调度器（命令行版本）"""
    
    def __init__(self):
        """初始化调度器"""
        self._executors: Dict[str, CommandExecutor] = {}
    
    def _get_executor(self, command: str, work_dir: str, storage_path: Optional[str] = None) -> CommandExecutor:
        """
        获取或创建命令行执行器
        
        Args:
            command: 执行命令
            work_dir: 工作目录
            storage_path: 插件在 MinIO 中的存储路径
        
        Returns:
            CommandExecutor实例
        """
        key = f"{work_dir}:{command}:{storage_path or ''}"
        if key not in self._executors:
            self._executors[key] = CommandExecutor(command, work_dir, storage_path=storage_path)
        
        return self._executors[key]
    
    async def execute_test(
        self,
        session: Session,
        plugin_code: str,
        test_case_id: int,
        test_case_content: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行测试任务
        
        Args:
            session: 数据库会话
            plugin_code: 插件代码标识
            test_case_id: 测试用例ID
            test_case_content: 测试用例内容（YAML格式）
            config: 执行配置
        
        Returns:
            执行结果
        """
        try:
            # 1. 查询插件
            plugin = session.exec(
                select(Plugin).where(Plugin.plugin_code == plugin_code)
            ).first()
            
            if not plugin:
                return {
                    "success": False,
                    "error": f"Plugin '{plugin_code}' not found"
                }
            
            # 2. 检查插件是否启用
            if plugin.is_enabled != 1:
                return {
                    "success": False,
                    "error": f"Plugin '{plugin_code}' is disabled"
                }
            
            # 3. 检查插件类型
            if plugin.plugin_type != "executor":
                return {
                    "success": False,
                    "error": f"Plugin '{plugin_code}' is not an executor type"
                }
            
            # 4. 获取命令行执行器
            logger.info(f"Executing test on plugin: {plugin_code}")
            executor = self._get_executor(plugin.command, plugin.work_dir, plugin.storage_path)
            
            # 5. 执行测试
            execute_result = await executor.execute_test(
                test_case_content=test_case_content,
                test_case_id=test_case_id,
                config=config
            )
            
            if not execute_result.get("success"):
                return {
                    "success": False,
                    "error": f"Plugin execution failed: {execute_result.get('error')}"
                }
            
            # 6. 返回成功结果
            return {
                "success": True,
                "task_id": execute_result.get("task_id"),
                "plugin_code": plugin_code,
                "plugin_name": plugin.plugin_name,
                "status": execute_result.get("status", "running"),
                "message": execute_result.get("message", "Test execution started"),
                "temp_dir": execute_result.get("temp_dir")
            }
        
        except Exception as e:
            logger.error(f"Task scheduling failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"Task scheduling error: {str(e)}"
            }
    
    async def get_task_status(
        self,
        session: Session,
        plugin_code: str,
        task_id: str,
        temp_dir: str
    ) -> Dict[str, Any]:
        """
        查询任务状态
        
        Args:
            session: 数据库会话
            plugin_code: 插件代码
            task_id: 任务ID
            temp_dir: 临时目录
        
        Returns:
            任务状态
        """
        try:
            # 查询插件
            plugin = session.exec(
                select(Plugin).where(Plugin.plugin_code == plugin_code)
            ).first()
            
            if not plugin:
                return {
                    "success": False,
                    "error": f"Plugin '{plugin_code}' not found"
                }
            
            # 获取执行器
            executor = self._get_executor(plugin.command, plugin.work_dir, plugin.storage_path)
            
            # 查询状态
            status_result = await executor.get_task_status(task_id, temp_dir)
            
            if not status_result.get("success"):
                return {
                    "success": False,
                    "error": status_result.get("error")
                }
            
            return {
                "success": True,
                "data": status_result.get("data")
            }
        
        except Exception as e:
            logger.error(f"Get task status failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def cancel_task(
        self,
        session: Session,
        plugin_code: str,
        task_id: str
    ) -> Dict[str, Any]:
        """
        取消任务
        
        Args:
            session: 数据库会话
            plugin_code: 插件代码
            task_id: 任务ID
        
        Returns:
            取消结果
        """
        try:
            #查询插件
            plugin = session.exec(
                select(Plugin).where(Plugin.plugin_code == plugin_code)
            ).first()
            
            if not plugin:
                return {
                    "success": False,
                    "error": f"Plugin '{plugin_code}' not found"
                }
            
            # 获取执行器
            executor = self._get_executor(plugin.command, plugin.work_dir)
            
            # 取消任务
            cancel_result = await executor.cancel_task(task_id)
            
            if not cancel_result.get("success"):
                return {
                    "success": False,
                    "error": cancel_result.get("error")
                }
            
            return {
                "success": True,
                "message": "Task cancelled successfully"
            }
        
        except Exception as e:
            logger.error(f"Cancel task failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_available_executors(
        self,
        session: Session
    ) -> Dict[str, Any]:
        """
        列出所有可用的执行器插件
        
        Args:
            session: 数据库会话
        
        Returns:
            可用执行器列表
        """
        try:
            # 查询所有已启用的执行器插件
            plugins = session.exec(
                select(Plugin)
                .where(Plugin.plugin_type == "executor")
                .where(Plugin.is_enabled == 1)
            ).all()
            
            executors = []
            for plugin in plugins:
                executors.append({
                    "plugin_code": plugin.plugin_code,
                    "plugin_name": plugin.plugin_name,
                    "version": plugin.version,
                    "command": plugin.command,
                    "work_dir": plugin.work_dir,
                    "capabilities": plugin.capabilities,
                    "description": plugin.description
                })
            
            return {
                "success": True,
                "executors": executors
            }
        
        except Exception as e:
            logger.error(f"List executors failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


# 创建全局调度器实例
task_scheduler = TaskScheduler()
