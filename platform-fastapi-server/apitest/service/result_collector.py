"""
执行结果收集器
负责解析执行结果、更新历史记录、持久化报告
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from sqlmodel import Session

from ..model.ApiHistoryModel import ApiHistory
from ..model.TestTaskModel import TestTask, TestTaskExecution

logger = logging.getLogger(__name__)


class ResultCollector:
    """执行结果收集器"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def update_single_case_result(
        self,
        test_id: int,
        execute_result: Dict[str, Any]
    ) -> ApiHistory:
        """
        更新单用例执行结果
        
        Args:
            test_id: 测试历史ID
            execute_result: 执行器返回的结果
            
        Returns:
            更新后的历史记录
        """
        history = self.session.get(ApiHistory, test_id)
        if not history:
            raise ValueError(f"测试记录不存在: {test_id}")
        
        if execute_result.get("success"):
            # 保存执行结果数据
            result_data = execute_result.get("result")
            if result_data:
                history.response_data = json.dumps(result_data, ensure_ascii=False)
                
                # 检查 test_cases 中是否有非通过的用例
                test_cases = result_data.get("test_cases", [])
                # Allure 状态: PASSED(通过), FAILED(失败), BROKEN(故障), SKIPPED(跳过), UNKNOWN(未知)
                # 只有 PASSED 才算成功，其他状态都算失败
                if test_cases:
                    has_failed = any(tc.get("status") != "PASSED" for tc in test_cases)
                    history.test_status = "failed" if has_failed else "success"
                else:
                    # test_cases 为空时，检查 returncode 或 stdout 中的失败信息
                    returncode = result_data.get("returncode", 0)
                    stdout = result_data.get("stdout", "")
                    if returncode != 0 or "FAILED" in stdout or "failed" in stdout.lower():
                        history.test_status = "failed"
                    else:
                        history.test_status = "success"
            else:
                history.test_status = "success"
            
            # 更新报告路径
            temp_dir = execute_result.get("temp_dir")
            if temp_dir:
                history.allure_report_path = temp_dir
                logger.info(f"报告路径已更新: {temp_dir}")
        else:
            history.test_status = "failed"
            history.error_message = execute_result.get("error")
        
        history.finish_time = datetime.now()
        history.modify_time = datetime.now()
        self.session.commit()
        
        logger.info(f"用例测试完成: {test_id}, 状态: {history.test_status}")
        return history
    
    def update_plan_result(
        self,
        test_id: int,
        execute_result: Dict[str, Any],
        case_names: List[str],
        total_cases: int
    ) -> ApiHistory:
        """
        更新计划批量执行结果
        
        Args:
            test_id: 测试历史ID
            execute_result: 执行器返回的结果
            case_names: 用例名称列表
            total_cases: 总用例数
            
        Returns:
            更新后的历史记录
        """
        history = self.session.get(ApiHistory, test_id)
        if not history:
            raise ValueError(f"测试记录不存在: {test_id}")
        
        if execute_result.get("success"):
            exec_data = execute_result.get("result", {}) or {}
            test_cases = exec_data.get("test_cases", [])
            
            # 构建用例结果列表
            case_results, passed_count, failed_count = self._build_case_results(
                case_names, test_cases
            )
            
            # 更新报告路径
            temp_dir = execute_result.get("temp_dir")
            report_path = temp_dir if temp_dir else history.allure_report_path
            
            overall_status = "success" if failed_count == 0 else "failed"
            history.test_status = overall_status
            history.response_data = json.dumps({
                "total": total_cases,
                "passed": passed_count,
                "failed": failed_count,
                "cases": case_results,
                "report_path": report_path
            }, ensure_ascii=False)
            
            if temp_dir:
                history.allure_report_path = temp_dir
        else:
            history.test_status = "failed"
            history.error_message = execute_result.get("error")
        
        history.finish_time = datetime.now()
        history.modify_time = datetime.now()
        self.session.commit()
        
        logger.info(f"计划批量执行完成: {test_id}, 状态: {history.test_status}")
        return history
    
    def mark_failed(self, test_id: int, error_message: str) -> Optional[ApiHistory]:
        """标记执行失败"""
        history = self.session.get(ApiHistory, test_id)
        if history:
            history.test_status = "failed"
            history.error_message = error_message
            history.finish_time = datetime.now()
            history.modify_time = datetime.now()
            self.session.commit()
        return history
    
    def update_task_execution(
        self,
        execution_id: int,
        status: str,
        passed_cases: int = 0,
        failed_cases: int = 0,
        report_path: str = None,
        error_message: str = None
    ) -> Optional[TestTaskExecution]:
        """
        更新测试任务执行记录状态
        
        Args:
            execution_id: 执行记录ID
            status: 执行状态 (completed/failed)
            passed_cases: 通过用例数
            failed_cases: 失败用例数
            report_path: 报告路径
            error_message: 错误信息
        """
        execution = self.session.get(TestTaskExecution, execution_id)
        if not execution:
            logger.warning(f"执行记录不存在: {execution_id}")
            return None
        
        execution.status = status
        execution.passed_cases = passed_cases
        execution.failed_cases = failed_cases
        execution.end_time = datetime.now()
        
        # 计算执行耗时
        if execution.start_time:
            duration = (execution.end_time - execution.start_time).total_seconds()
            execution.duration = int(duration)
        
        if report_path:
            execution.report_path = report_path
        if error_message:
            execution.error_message = error_message
        
        # 同时更新关联的 TestTask 状态
        task = self.session.get(TestTask, execution.task_id)
        if task:
            task.task_status = 'pending'  # 执行完成后恢复为待执行状态
            if status == 'completed' and failed_cases == 0:
                task.success_count += 1
            else:
                task.fail_count += 1
            task.modify_time = datetime.now()
        
        self.session.commit()
        logger.info(f"任务执行记录已更新: execution_id={execution_id}, status={status}")
        return execution
    
    # ==================== 私有方法 ====================
    
    def _build_case_results(
        self,
        case_names: List[str],
        test_cases: List[Dict]
    ) -> tuple:
        """
        构建用例结果列表
        
        Returns:
            (case_results, passed_count, failed_count)
        """
        case_results = []
        passed_count = 0
        failed_count = 0
        
        for idx, case_name in enumerate(case_names):
            case_status = "success"
            
            # 从执行结果中匹配用例状态
            for tc in test_cases:
                tc_name = tc.get("name", "")
                if case_name in tc_name or tc_name in case_name:
                    # Allure 状态: PASSED(通过), FAILED(失败), BROKEN(故障), SKIPPED(跳过), UNKNOWN(未知)
                    # 只有 PASSED 才算成功
                    case_status = "success" if tc.get("status") == "PASSED" else "failed"
                    break
            
            if case_status == "success":
                passed_count += 1
            else:
                failed_count += 1
            
            case_results.append({
                "index": idx,
                "case_name": case_name,
                "success": case_status == "success",
                "status": case_status
            })
        
        return case_results, passed_count, failed_count
