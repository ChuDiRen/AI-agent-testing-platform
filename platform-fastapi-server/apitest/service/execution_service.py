"""
执行服务
负责编排执行流程：准备 → 执行 → 收集结果

统一执行流程：
1. 所有用例统一写入 workspace 目录
2. 使用 pytest + allure 执行测试
3. ResultCollector 负责解析和持久化
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from sqlmodel import Session

from core.temp_manager import get_temp_subdir

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

    def execute_case(
        self,
        case_id: int,
        test_name: Optional[str] = None,
        context_vars: Optional[Dict[str, Any]] = None,
        task_execution_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行单个用例（异步提交）

        Args:
            case_id: 用例ID
            test_name: 测试名称
            context_vars: 上下文变量

        Returns:
            {"test_id": int, "status": "running", "executor": str}
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
            workspace=workspace,
            case_names=[build_result["case_name"]],
            task_execution_id=task_execution_id
        )

        return {"test_id": history.id, "status": "running", "executor": "api_engine"}
    
    def execute_plan(
        self,
        plan_id: int,
        test_name: Optional[str] = None,
        task_execution_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行测试计划（异步提交）

        执行流程：
        1. 生成测试用例YAML文件
           - context.yaml（环境变量、数据库配置）
           - {order}_{uuid}.yaml（测试用例）
        2. 调用执行器执行测试
        3. 生成Allure报告
        4. 保存执行记录到历史记录表

        Returns:
            {"test_id": int, "execution_uuid": str, "status": "running", "total_cases": int}
        """
        # 1. 构建所有用例 YAML
        build_result = self.yaml_builder.build_plan_cases(plan_id)

        # 2. 创建 workspace 并写入文件
        execution_uuid = str(uuid.uuid4())
        workspace = get_temp_subdir("executor") / execution_uuid
        workspace.mkdir(parents=True, exist_ok=True)

        # 写入 context.yaml（环境变量、数据库配置）
        context_yaml = build_result.get("context_yaml")
        if context_yaml:
            (workspace / "context.yaml").write_text(context_yaml, encoding='utf-8')

        # 写入测试用例文件
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
            workspace=workspace,
            case_names=case_names,
            task_execution_id=task_execution_id,
            plan_id=plan_id
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
            update_time=datetime.now()
        )
        self.session.add(history)
        self.session.commit()
        self.session.refresh(history)
        return history
    
    def _submit_execution(
        self,
        test_id: int,
        workspace: Path,
        case_names: list,
        task_execution_id: Optional[int] = None,
        plan_id: Optional[int] = None
    ):
        """提交后台执行任务"""
        _bg_executor.submit(
            _run_execution,
            test_id=test_id,
            workspace=str(workspace),
            case_names=case_names,
            task_execution_id=task_execution_id,
            plan_id=plan_id
        )


# ==================== 后台执行函数（模块级，避免闭包问题） ====================

def _run_execution(
    test_id: int,
    workspace: str,
    case_names: list,
    task_execution_id: int = None,
    plan_id: int = None
):
    """
    后台执行测试（在线程池中运行）
    统一处理单用例和计划执行

    执行流程：
    1. 直接调用执行引擎的 run() 方法
    2. 生成Allure报告
    3. 保存执行记录
    """
    from core.database import engine
    from sqlmodel import Session as DBSession

    db = DBSession(engine)
    passed_count = 0
    failed_count = 0
    success = False
    try:
        logger.info(f"开始执行: test_id={test_id}, workspace={workspace}, 用例数={len(case_names)}")

        # 准备执行环境
        workspace_path = Path(workspace)

        # 设置执行引擎环境
        import sys
        import os

        # 添加执行引擎到 Python 路径
        engine_path = Path(__file__).parent.parent.parent / "engine" / "api-engine"
        if str(engine_path) not in sys.path:
            sys.path.insert(0, str(engine_path))

        # 保存原始 sys.argv
        original_argv = sys.argv.copy()
        original_cwd = os.getcwd()

        try:
            # 模拟命令行调用：设置 sys.argv
            sys.argv = [
                "cli.py",
                "--type=yaml",
                f"--cases={workspace_path}",
                f"--reports={workspace_path}"
            ]

            logger.info(f"模拟命令行调用执行引擎，workspace={workspace_path}")

            # 直接调用 run()，参数通过 sys.argv 传递
            from apirun.cli import run
            exit_code = run()

            success = exit_code == 0

            # 解析 allure-results 获取通过/失败数
            passed_count = 0
            failed_count = 0
            allure_results_dir = workspace_path / "allure-results"
            if allure_results_dir.exists():
                import json
                for result_file in allure_results_dir.glob("*-result.json"):
                    try:
                        with open(result_file, 'r', encoding='utf-8') as f:
                            result_data = json.load(f)
                            # allure 结果中包含步骤信息
                            for step in result_data.get('steps', []):
                                if 'status' in step:
                                    if step['status'] == 'passed':
                                        passed_count += 1
                                    elif step['status'] == 'failed':
                                        failed_count += 1
                            # 如果没有步骤，检查用例本身的状态
                            if not result_data.get('steps') and 'status' in result_data:
                                if result_data['status'] == 'passed':
                                    passed_count += 1
                                elif result_data['status'] == 'failed':
                                    failed_count += 1
                    except Exception as e:
                        logger.warning(f"解析 allure 结果文件失败: {e}")

            # 构建结果字典
            result_dict = {
                "success": success,
                "returncode": exit_code,
                "passed": passed_count,
                "failed": failed_count
            }

            # 更新结果
            collector = ResultCollector(db)
            if len(case_names) == 1:
                history = collector.update_single_case_result(test_id, result_dict)
            else:
                history = collector.update_plan_result(
                    test_id, result_dict, case_names, len(case_names), plan_id=plan_id
                )

            # 更新 TestTaskExecution 记录（如果有）
            if task_execution_id:
                exec_status = 'completed' if success else 'failed'
                collector.update_task_execution(
                    execution_id=task_execution_id,
                    status=exec_status,
                    passed_cases=passed_count,
                    failed_cases=failed_count,
                    report_path=workspace
                )

            logger.info(f"执行完成: test_id={test_id}, success={success}, passed={passed_count}, failed={failed_count}")

        finally:
            # 恢复 sys.argv 和工作目录
            sys.argv = original_argv
            os.chdir(original_cwd)

    except Exception as e:
        logger.error(f"执行失败: test_id={test_id}, 错误: {e}", exc_info=True)
        success = False
        try:
            collector = ResultCollector(db)
            collector.mark_failed(test_id, str(e))
            # 更新 TestTaskExecution 记录为失败
            if task_execution_id:
                collector.update_task_execution(
                    execution_id=task_execution_id,
                    status='failed',
                    failed_cases=len(case_names),
                    error_message=str(e)
                )
        except:
            pass
    finally:
        db.close()
