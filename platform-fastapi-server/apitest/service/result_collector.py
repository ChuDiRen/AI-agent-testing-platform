"""
执行结果收集器
负责解析执行结果、更新历史记录、持久化报告、发送机器人通知
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from sqlmodel import Session, select

from ..model.ApiHistoryModel import ApiHistory
from ..model.TestTaskModel import TestTask, TestTaskExecution
from ..model.ApiPlanRobotModel import ApiPlanRobot

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
        history.update_time = datetime.now()
        self.session.commit()
        
        logger.info(f"用例测试完成: {test_id}, 状态: {history.test_status}")
        return history
    
    def update_plan_result(
        self,
        test_id: int,
        execute_result: Dict[str, Any],
        case_names: List[str],
        total_cases: int,
        plan_id: Optional[int] = None
    ) -> ApiHistory:
        """
        更新计划批量执行结果
        
        Args:
            test_id: 测试历史ID
            execute_result: 执行器返回的结果
            case_names: 用例名称列表
            total_cases: 总用例数
            plan_id: 测试计划ID（用于发送机器人通知）
            
        Returns:
            更新后的历史记录
        """
        history = self.session.get(ApiHistory, test_id)
        if not history:
            raise ValueError(f"测试记录不存在: {test_id}")
        
        passed_count = 0
        failed_count = 0
        report_path = history.allure_report_path
        
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
            failed_count = total_cases
        
        history.finish_time = datetime.now()
        history.update_time = datetime.now()
        self.session.commit()
        
        logger.info(f"计划批量执行完成: {test_id}, 状态: {history.test_status}")
        
        # 发送机器人通知
        actual_plan_id = plan_id or history.plan_id
        if actual_plan_id:
            self._send_robot_notification(
                plan_id=actual_plan_id,
                test_name=history.test_name,
                status=history.test_status,
                total=total_cases,
                passed=passed_count,
                failed=failed_count,
                report_path=report_path,
                execution_time=history.finish_time
            )
        
        return history
    
    def mark_failed(self, test_id: int, error_message: str) -> Optional[ApiHistory]:
        """标记执行失败"""
        history = self.session.get(ApiHistory, test_id)
        if history:
            history.test_status = "failed"
            history.error_message = error_message
            history.finish_time = datetime.now()
            history.update_time = datetime.now()
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
            task.update_time = datetime.now()
        
        self.session.commit()
        logger.info(f"任务执行记录已更新: execution_id={execution_id}, status={status}")
        return execution
    
    # ==================== 私有方法 ====================
    
    def _send_robot_notification(
        self,
        plan_id: int,
        test_name: str,
        status: str,
        total: int,
        passed: int,
        failed: int,
        report_path: str,
        execution_time: datetime
    ):
        """
        发送机器人通知
        
        Args:
            plan_id: 测试计划ID
            test_name: 测试名称
            status: 执行状态
            total: 总用例数
            passed: 通过数
            failed: 失败数
            report_path: 报告路径
            execution_time: 执行时间
        """
        try:
            from msgmanage.model.RobotConfigModel import RobotConfig
            
            # 查询计划关联的机器人
            stmt = select(ApiPlanRobot).where(
                ApiPlanRobot.plan_id == plan_id,
                ApiPlanRobot.is_enabled == True
            )
            plan_robots = self.session.exec(stmt).all()
            
            if not plan_robots:
                logger.debug(f"计划 {plan_id} 没有启用的机器人通知")
                return
            
            # 判断是否需要发送通知
            is_success = status == "success"
            
            for pr in plan_robots:
                # 检查通知条件
                if is_success and not pr.notify_on_success:
                    continue
                if not is_success and not pr.notify_on_failure:
                    continue
                
                # 获取机器人配置
                robot = self.session.get(RobotConfig, pr.robot_id)
                if not robot or not robot.is_enabled:
                    continue
                
                # 构建通知消息
                pass_rate = round(passed / total * 100, 2) if total > 0 else 0
                message = self._build_notification_message(
                    test_name=test_name,
                    status=status,
                    total=total,
                    passed=passed,
                    failed=failed,
                    pass_rate=pass_rate,
                    report_path=report_path,
                    execution_time=execution_time
                )
                
                # 发送通知
                self._send_to_robot(robot, message)
                
        except Exception as e:
            logger.error(f"发送机器人通知失败: {e}", exc_info=True)
    
    def _build_notification_message(
        self,
        test_name: str,
        status: str,
        total: int,
        passed: int,
        failed: int,
        pass_rate: float,
        report_path: str,
        execution_time: datetime
    ) -> Dict[str, Any]:
        """构建通知消息内容"""
        status_text = "✅ 通过" if status == "success" else "❌ 失败"
        time_str = execution_time.strftime("%Y-%m-%d %H:%M:%S") if execution_time else ""
        
        return {
            "title": f"测试执行通知 - {test_name}",
            "content": f"""
**测试计划**: {test_name}
**执行状态**: {status_text}
**执行时间**: {time_str}

**测试统计**:
- 总用例数: {total}
- 通过: {passed}
- 失败: {failed}
- 通过率: {pass_rate}%

**报告路径**: {report_path}
""".strip(),
            "status": status,
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate
        }
    
    def _send_to_robot(self, robot, message: Dict[str, Any]):
        """发送消息到机器人"""
        import httpx
        
        try:
            if robot.robot_type == "wechat":
                # 企业微信机器人
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "content": message["content"]
                    }
                }
            elif robot.robot_type == "dingtalk":
                # 钉钉机器人
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": message["title"],
                        "text": message["content"]
                    }
                }
            elif robot.robot_type == "feishu":
                # 飞书机器人
                payload = {
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {
                                "tag": "plain_text",
                                "content": message["title"]
                            },
                            "template": "green" if message["status"] == "success" else "red"
                        },
                        "elements": [
                            {
                                "tag": "markdown",
                                "content": message["content"]
                            }
                        ]
                    }
                }
            else:
                logger.warning(f"不支持的机器人类型: {robot.robot_type}")
                return
            
            # 发送请求
            with httpx.Client(timeout=10.0) as client:
                response = client.post(robot.webhook_url, json=payload)
                if response.status_code == 200:
                    logger.info(f"机器人通知发送成功: {robot.robot_name}")
                else:
                    logger.warning(f"机器人通知发送失败: {robot.robot_name}, status={response.status_code}")
                    
        except Exception as e:
            logger.error(f"发送机器人消息失败: {robot.robot_name}, error={e}")
    
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
