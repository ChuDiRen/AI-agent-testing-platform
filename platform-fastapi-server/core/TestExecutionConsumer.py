"""
测试执行消费者
从RabbitMQ队列中消费测试执行任务，并通过WebSocket实时推送进度

执行流程：
1. 从队列获取执行任务
2. 调用 ExecutionService 执行测试
3. 生成Allure报告
4. 更新执行状态并通过WebSocket推送结果
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from sqlmodel import Session, select

logger = logging.getLogger(__name__)


class TestExecutionConsumer:
    """测试执行消费者"""

    # 任务状态常量
    STATUS_WAITING = "等待中"
    STATUS_RUNNING = "执行中"
    STATUS_COMPLETED = "执行完成"

    def __init__(self):
        from core.QueueFactory import queue_manager
        from core.WebSocketManager import manager as ws_manager

        self.queue_manager = queue_manager
        self.ws_manager = ws_manager

    async def _send_progress(self, execution_id: str, event_data: Dict[str, Any]):
        """发送进度事件到WebSocket"""
        try:
            await self.ws_manager.send_progress(execution_id, event_data)
        except Exception as e:
            logger.error(f"WebSocket推送失败: {e}")

    async def _execute_test_via_service(
        self,
        case_id: int,
        execution_id: str,
        plan_id: Optional[int] = None,
        context_vars: Optional[Dict[str, Any]] = None
    ):
        """
        通过 ExecutionService 执行测试

        Args:
            case_id: 测试用例ID
            execution_id: 执行ID（用于WebSocket连接标识）
            plan_id: 测试计划ID
            context_vars: 上下文变量
        """
        from core.database import engine
        from sqlmodel import Session as DBSession
        from apitest.model.ApiInfoCaseModel import ApiInfoCase
        from apitest.service.execution_service import ExecutionService

        db = DBSession(engine)

        try:
            # 获取用例信息
            case_info = db.get(ApiInfoCase, case_id)
            if not case_info:
                await self._send_progress(execution_id, {
                    "type": "error",
                    "execution_id": execution_id,
                    "status": "error",
                    "message": f"用例不存在: {case_id}",
                    "timestamp": datetime.now().isoformat()
                })
                return

            # 发送开始事件
            await self._send_progress(execution_id, {
                "type": "start",
                "execution_id": execution_id,
                "case_id": case_id,
                "case_name": case_info.case_name,
                "status": self.STATUS_RUNNING,
                "message": f"开始执行测试用例: {case_info.case_name}",
                "timestamp": datetime.now().isoformat()
            })

            # 调用 ExecutionService 执行测试
            exec_service = ExecutionService(db)
            result = exec_service.execute_case(
                case_id=case_id,
                test_name=f"{case_info.case_name}_{execution_id[:8]}",
                context_vars=context_vars,
                task_execution_id=None
            )

            test_id = result.get("test_id")
            if test_id:
                # 等待执行完成（简单轮询检查状态）
                max_wait_time = 600  # 最大等待10分钟
                poll_interval = 2  # 每2秒检查一次
                waited_time = 0

                from apitest.model.ApiHistoryModel import ApiHistory

                while waited_time < max_wait_time:
                    history = db.get(ApiHistory, test_id)
                    if history and history.test_status != "running":
                        # 执行完成
                        await self._send_progress(execution_id, {
                            "type": "complete",
                            "execution_id": execution_id,
                            "status": history.test_status,
                            "test_id": test_id,
                            "report_path": history.allure_report_path,
                            "passed": history.passed_count or 0,
                            "failed": history.failed_count or 0,
                            "message": f"测试用例执行{history.test_status}",
                            "timestamp": datetime.now().isoformat()
                        })
                        return

                    # 发送进度
                    await self._send_progress(execution_id, {
                        "type": "progress",
                        "execution_id": execution_id,
                        "status": "running",
                        "message": f"正在执行... 已等待{waited_time}秒",
                        "timestamp": datetime.now().isoformat()
                    })

                    await self._wait_async(poll_interval)
                    waited_time += poll_interval

                # 超时
                await self._send_progress(execution_id, {
                    "type": "timeout",
                    "execution_id": execution_id,
                    "status": "timeout",
                    "message": f"执行超时（{max_wait_time}秒）",
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"执行测试失败: {e}", exc_info=True)
            await self._send_progress(execution_id, {
                "type": "error",
                "execution_id": execution_id,
                "status": "error",
                "message": f"执行失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
        finally:
            db.close()

    async def _wait_async(self, seconds: float):
        """异步等待"""
        import asyncio
        await asyncio.sleep(seconds)

    def callback(self, message):
        """
        消息回调函数

        消息格式：
        {
            "execution_id": "uuid",
            "case_id": 123,
            "plan_id": 456  // 可选，用于测试计划执行
        }

        Args:
            message: 消息数据(dict)
        """
        try:
            data = message if isinstance(message, dict) else json.loads(message)

            execution_id = data.get('execution_id')
            case_id = data.get('case_id')
            plan_id = data.get('plan_id')
            context_vars = data.get('context_vars')

            logger.info(f"Received test execution task: execution_id={execution_id}, case_id={case_id}, plan_id={plan_id}")

            # 在线程中创建新事件循环执行异步任务
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    self._execute_test_via_service(case_id, execution_id, plan_id, context_vars)
                )
            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Error processing test execution message: {e}", exc_info=True)

    def start(self):
        """启动消费者"""
        logger.info("Starting test execution consumer...")
        self.queue_manager.start_test_execution_consumer(self.callback)


# 全局测试执行消费者实例
test_execution_consumer = TestExecutionConsumer()
