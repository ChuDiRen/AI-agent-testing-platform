"""
执行服务
负责编排执行流程：验证 → 准备 → 执行 → 收集结果

统一执行流程：
1. 所有用例统一写入 workspace 目录
2. CommandExecutor 只负责执行命令
3. ResultCollector 负责解析和持久化
"""
import uuid
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from sqlmodel import Session, select

from core.temp_manager import get_temp_subdir
from plugin.model.PluginModel import Plugin
from plugin.service.TaskScheduler import task_scheduler

from ..model.ApiHistoryModel import ApiHistory
from .case_yaml_builder import CaseYamlBuilder
from .result_collector import ResultCollector

logger = logging.getLogger(__name__)

# 后台任务线程池
_bg_executor = ThreadPoolExecutor(max_workers=5, thread_name_prefix="exec_")


def shutdown_executor(wait: bool = True):
    """关闭后台执行线程池（应用退出时调用）"""
    _bg_executor.shutdown(wait=wait)
    logger.info("执行线程池已关闭")


class ExecutionService:
    """执行服务 - 统一入口"""
    
    def __init__(self, session: Session):
        self.session = session
        self.yaml_builder = CaseYamlBuilder(session)
    
    # ==================== 公开方法 ====================
    
    def validate_executor(self, executor_code: str) -> Plugin:
        """验证执行器插件"""
        plugin = self.session.exec(
            select(Plugin).where(Plugin.plugin_code == executor_code)
        ).first()
        
        if not plugin:
            raise ValueError(f"执行器插件不存在: {executor_code}")
        if plugin.is_enabled != 1:
            raise ValueError(f"执行器插件未启用: {executor_code}")
        if plugin.plugin_type != "executor":
            raise ValueError(f"插件类型错误: {plugin.plugin_type}")
        
        return plugin
    
    def execute_case(
        self,
        case_id: int,
        executor_code: str,
        test_name: Optional[str] = None,
        context_vars: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行单个用例（异步提交）
        
        Returns:
            {"test_id": int, "status": "running"}
        """
        # 1. 构建 YAML
        build_result = self.yaml_builder.build_single_case(case_id, context_vars)
        
        # 2. 创建 workspace 并写入文件
        workspace = self._create_workspace(f"case_{case_id}")
        self.yaml_builder.save_cases_to_dir(
            [{"yaml_data": None, "yaml_content": build_result["yaml_content"], 
              "case_name": build_result["case_name"]}],
            workspace
        )
        
        # 3. 创建历史记录
        history = self._create_history(
            test_name=test_name or f"{build_result['case_name']}_测试",
            case_id=case_id,
            project_id=build_result.get("project_id") or 0,
            yaml_content=build_result["yaml_content"],
            workspace=workspace
        )
        
        # 4. 提交后台执行
        self._submit_execution(
            test_id=history.id,
            executor_code=executor_code,
            workspace=workspace,
            case_names=[build_result["case_name"]]
        )
        
        return {"test_id": history.id, "status": "running"}
    
    def execute_plan(
        self,
        plan_id: int,
        executor_code: str,
        test_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行测试计划（异步提交）
        
        Returns:
            {"test_id": int, "execution_uuid": str, "status": "running", "total_cases": int}
        """
        # 1. 构建所有用例 YAML
        build_result = self.yaml_builder.build_plan_cases(plan_id)
        
        # 2. 创建 workspace 并写入文件
        execution_uuid = str(uuid.uuid4())
        workspace = get_temp_subdir("executor") / execution_uuid
        workspace.mkdir(parents=True, exist_ok=True)
        self.yaml_builder.save_cases_to_dir(build_result["cases"], workspace)
        
        case_names = [c["case_name"] for c in build_result["cases"]]
        
        # 3. 创建历史记录
        history = self._create_history(
            test_name=test_name or f"{build_result['plan_name']}_测试",
            plan_id=plan_id,
            project_id=build_result.get("project_id") or 0,
            yaml_content=build_result["combined_yaml"],
            workspace=workspace,
            execution_uuid=execution_uuid
        )
        
        # 4. 提交后台执行
        self._submit_execution(
            test_id=history.id,
            executor_code=executor_code,
            workspace=workspace,
            case_names=case_names
        )
        
        logger.info(f"计划已提交: workspace={workspace}, 用例数={len(case_names)}")
        
        return {
            "test_id": history.id,
            "execution_uuid": execution_uuid,
            "status": "running",
            "total_cases": len(case_names),
            "plan_id": plan_id
        }
    
    # ==================== 私有方法 ====================
    
    def _create_workspace(self, prefix: str) -> Path:
        """创建工作目录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        workspace = get_temp_subdir("executor") / f"{prefix}_{timestamp}_{uuid.uuid4().hex[:8]}"
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace
    
    def _create_history(
        self,
        test_name: str,
        yaml_content: str,
        workspace: Path,
        case_id: int = 0,
        plan_id: int = None,
        project_id: int = 0,
        execution_uuid: str = None
    ) -> ApiHistory:
        """创建执行历史记录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        history = ApiHistory(
            api_info_id=0,
            case_info_id=case_id,
            project_id=project_id or 0,
            plan_id=plan_id,
            execution_uuid=execution_uuid,
            test_name=f"{test_name}_{timestamp}",
            test_status="running",
            yaml_content=yaml_content,
            allure_report_path=str(workspace),
            create_time=datetime.now(),
            modify_time=datetime.now()
        )
        self.session.add(history)
        self.session.commit()
        self.session.refresh(history)
        return history
    
    def _submit_execution(
        self,
        test_id: int,
        executor_code: str,
        workspace: Path,
        case_names: list
    ):
        """提交后台执行任务"""
        _bg_executor.submit(
            _run_execution,
            test_id=test_id,
            executor_code=executor_code,
            workspace=str(workspace),
            case_names=case_names
        )


# ==================== 后台执行函数（模块级，避免闭包问题） ====================

def _run_execution(
    test_id: int,
    executor_code: str,
    workspace: str,
    case_names: list
):
    """
    后台执行测试（在线程池中运行）
    统一处理单用例和计划执行
    """
    from core.database import engine
    from sqlmodel import Session as DBSession
    
    db = DBSession(engine)
    try:
        logger.info(f"开始执行: test_id={test_id}, workspace={workspace}, 用例数={len(case_names)}")
        
        # 执行测试
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                task_scheduler.execute_test(
                    session=db,
                    plugin_code=executor_code,
                    test_case_id=test_id,
                    test_case_content=workspace,
                    config={"is_directory": True}
                )
            )
        finally:
            loop.close()
        
        # 更新结果
        collector = ResultCollector(db)
        if len(case_names) == 1:
            collector.update_single_case_result(test_id, result)
        else:
            collector.update_plan_result(test_id, result, case_names, len(case_names))
        
        logger.info(f"执行完成: test_id={test_id}, success={result.get('success')}")
        
    except Exception as e:
        logger.error(f"执行失败: test_id={test_id}, 错误: {e}", exc_info=True)
        try:
            collector = ResultCollector(db)
            collector.mark_failed(test_id, str(e))
        except:
            pass
    finally:
        db.close()
