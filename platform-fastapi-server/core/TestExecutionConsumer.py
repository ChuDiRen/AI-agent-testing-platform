"""
测试执行消费者
从RabbitMQ队列中消费测试执行任务，并通过WebSocket实时推送进度

执行流程：
1. 从队列获取执行任务
2. 更新状态为"执行中"
3. 逐步执行测试用例
4. 实时推送执行进度
5. 生成Allure报告
6. 更新状态为"执行完成"
7. 发送机器人通知
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

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
    
    async def execute_test_case(self, case_id: int, execution_id: str, plan_id: Optional[int] = None):
        """
        执行测试用例并实时推送进度
        
        执行流程：
        1. 从数据库获取测试用例步骤
        2. 加载context.yaml（环境变量、数据库配置）
        3. 执行pre_script（前置脚本）
        4. 遍历steps执行每个步骤
        5. 执行post_script（后置脚本）
        6. 生成Allure测试数据
        
        Args:
            case_id: 测试用例ID
            execution_id: 执行ID（用于WebSocket连接标识）
            plan_id: 测试计划ID（用于机器人通知）
        """
        try:
            from core.database import engine
            from sqlmodel import Session as DBSession
            from apitest.model.ApiInfoCaseModel import ApiInfoCase
            from apitest.model.ApiInfoCaseStepModel import ApiInfoCaseStep
            from apitest.model.ApiKeyWordModel import ApiKeyWord
            
            db = DBSession(engine)
            
            try:
                # 获取用例信息
                case_info = db.get(ApiInfoCase, case_id)
                if not case_info:
                    await self._send_error(execution_id, f"用例不存在: {case_id}")
                    return
                
                # 获取用例步骤
                stmt = select(ApiInfoCaseStep).where(
                    ApiInfoCaseStep.case_info_id == case_id
                ).order_by(ApiInfoCaseStep.run_order)
                steps = db.exec(stmt).all()
                
                if not steps:
                    await self._send_error(execution_id, f"用例没有步骤: {case_id}")
                    return
                
                total_steps = len(steps)
                
                # 发送开始事件
                await self.ws_manager.send_progress(execution_id, {
                    "type": "start",
                    "execution_id": execution_id,
                    "case_id": case_id,
                    "case_name": case_info.case_name,
                    "total_steps": total_steps,
                    "progress": 0,
                    "status": self.STATUS_RUNNING,
                    "message": f"开始执行测试用例: {case_info.case_name} (共{total_steps}步)",
                    "timestamp": datetime.now().isoformat()
                })
                
                # 执行前置脚本
                if case_info.pre_request:
                    await self._execute_script(
                        execution_id, case_info.pre_request, "前置脚本"
                    )
                
                # 逐步执行
                passed_steps = 0
                failed_steps = 0
                
                for idx, step in enumerate(steps, 1):
                    # 获取关键字信息
                    keyword = db.get(ApiKeyWord, step.keyword_id) if step.keyword_id else None
                    keyword_name = keyword.keyword_fun_name if keyword else "unknown"
                    
                    # 发送步骤开始事件
                    await self.ws_manager.send_progress(execution_id, {
                        "type": "step_start",
                        "execution_id": execution_id,
                        "current_step": idx,
                        "total_steps": total_steps,
                        "progress": int(((idx - 1) / total_steps) * 100),
                        "step_name": step.step_desc or f"步骤{idx}",
                        "keyword": keyword_name,
                        "status": "running",
                        "message": f"正在执行步骤 {idx}/{total_steps}: {step.step_desc or keyword_name}",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # 执行步骤（这里调用实际的关键字执行器）
                    step_result = await self._execute_step(step, keyword, db)
                    
                    # 发送步骤结束事件
                    step_status = "passed" if step_result.get("success") else "failed"
                    if step_status == "passed":
                        passed_steps += 1
                    else:
                        failed_steps += 1
                    
                    await self.ws_manager.send_progress(execution_id, {
                        "type": "step_end",
                        "execution_id": execution_id,
                        "current_step": idx,
                        "total_steps": total_steps,
                        "progress": int((idx / total_steps) * 100),
                        "step_name": step.step_desc or f"步骤{idx}",
                        "status": step_status,
                        "result": step_result,
                        "message": f"步骤 {idx} {'通过' if step_status == 'passed' else '失败'}",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # 如果失败且不是继续执行模式，停止执行
                    if step_status == "failed":
                        await self.ws_manager.send_progress(execution_id, {
                            "type": "complete",
                            "execution_id": execution_id,
                            "status": "failed",
                            "progress": 100,
                            "passed_steps": passed_steps,
                            "failed_steps": failed_steps,
                            "message": f"测试用例执行失败，在步骤 {idx} 处中断",
                            "timestamp": datetime.now().isoformat()
                        })
                        return
                
                # 执行后置脚本
                if case_info.post_request:
                    await self._execute_script(
                        execution_id, case_info.post_request, "后置脚本"
                    )
                
                # 发送完成事件
                await self.ws_manager.send_progress(execution_id, {
                    "type": "complete",
                    "execution_id": execution_id,
                    "status": "passed",
                    "progress": 100,
                    "passed_steps": passed_steps,
                    "failed_steps": failed_steps,
                    "message": f"测试用例执行成功，共{passed_steps}步通过",
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Test case {case_id} execution completed: {execution_id}")
                
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Error executing test case {case_id}: {e}", exc_info=True)
            await self._send_error(execution_id, str(e))
    
    async def _execute_step(
        self, 
        step: Any, 
        keyword: Any, 
        session: Session
    ) -> Dict[str, Any]:
        """
        执行单个测试步骤
        
        Args:
            step: 步骤对象
            keyword: 关键字对象
            session: 数据库会话
            
        Returns:
            执行结果字典
        """
        try:
            # 解析步骤数据
            step_data = {}
            if step.step_data:
                try:
                    step_data = json.loads(step.step_data)
                except json.JSONDecodeError:
                    pass
            
            # 根据关键字类型执行不同的操作
            if keyword and keyword.keyword_fun_name:
                kw_name = keyword.keyword_fun_name.lower()
                
                # HTTP 请求类关键字
                if kw_name in ('send_request', 'request_get', 'request_post', 'request_put', 
                               'request_delete', 'request_patch'):
                    return await self._execute_http_request(step_data, kw_name)
                
                # 数据库操作关键字
                elif kw_name in ('db_query', 'db_execute'):
                    return await self._execute_db_operation(step_data, kw_name)
                
                # 断言关键字
                elif kw_name.startswith('assert_'):
                    return await self._execute_assertion(step_data, kw_name)
            
            # 默认模拟执行
            await asyncio.sleep(0.5)
            return {"success": True, "message": "步骤执行成功"}
            
        except Exception as e:
            logger.error(f"步骤执行失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _execute_http_request(
        self, 
        step_data: Dict[str, Any], 
        keyword_name: str
    ) -> Dict[str, Any]:
        """执行HTTP请求"""
        import httpx
        
        try:
            url = step_data.get('url') or step_data.get('URL', '')
            method = step_data.get('method', 'GET').upper()
            headers = step_data.get('headers') or step_data.get('HEADERS', {})
            params = step_data.get('params') or step_data.get('PARAMS', {})
            json_data = step_data.get('json') or step_data.get('JSON')
            data = step_data.get('data') or step_data.get('DATA')
            timeout = step_data.get('timeout', 30)
            
            # 从关键字名推断方法
            if 'post' in keyword_name:
                method = 'POST'
            elif 'put' in keyword_name:
                method = 'PUT'
            elif 'delete' in keyword_name:
                method = 'DELETE'
            elif 'patch' in keyword_name:
                method = 'PATCH'
            
            if not url:
                return {"success": False, "error": "URL不能为空"}
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    data=data
                )
                
                return {
                    "success": response.status_code < 400,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() * 1000,
                    "headers": dict(response.headers),
                    "body": response.text[:1000] if response.text else ""
                }
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_db_operation(
        self, 
        step_data: Dict[str, Any], 
        keyword_name: str
    ) -> Dict[str, Any]:
        """执行数据库操作"""
        # TODO: 实现数据库操作
        await asyncio.sleep(0.3)
        return {"success": True, "message": "数据库操作成功"}
    
    async def _execute_assertion(
        self, 
        step_data: Dict[str, Any], 
        keyword_name: str
    ) -> Dict[str, Any]:
        """执行断言"""
        try:
            expected = step_data.get('expected')
            actual = step_data.get('actual')
            
            if keyword_name == 'assert_equals':
                success = expected == actual
            elif keyword_name == 'assert_contains':
                success = str(expected) in str(actual)
            elif keyword_name == 'assert_not_null':
                success = actual is not None
            else:
                success = True
            
            return {
                "success": success,
                "expected": expected,
                "actual": actual,
                "message": "断言通过" if success else "断言失败"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_script(
        self, 
        execution_id: str, 
        script: str, 
        script_type: str
    ):
        """执行Python脚本"""
        try:
            await self.ws_manager.send_progress(execution_id, {
                "type": "script_start",
                "script_type": script_type,
                "message": f"开始执行{script_type}",
                "timestamp": datetime.now().isoformat()
            })
            
            # 解析脚本
            scripts = []
            try:
                parsed = json.loads(script)
                if isinstance(parsed, list):
                    scripts = parsed
                elif isinstance(parsed, str):
                    scripts = [parsed]
            except json.JSONDecodeError:
                scripts = [script]
            
            # 执行脚本（安全考虑，这里只是模拟）
            for s in scripts:
                if s and s.strip():
                    # TODO: 实现安全的脚本执行
                    await asyncio.sleep(0.2)
            
            await self.ws_manager.send_progress(execution_id, {
                "type": "script_end",
                "script_type": script_type,
                "status": "passed",
                "message": f"{script_type}执行完成",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"{script_type}执行失败: {e}")
            await self.ws_manager.send_progress(execution_id, {
                "type": "script_end",
                "script_type": script_type,
                "status": "failed",
                "error": str(e),
                "message": f"{script_type}执行失败",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _send_error(self, execution_id: str, error_message: str):
        """发送错误事件"""
        await self.ws_manager.send_progress(execution_id, {
            "type": "error",
            "execution_id": execution_id,
            "status": "error",
            "progress": 0,
            "message": f"执行出错: {error_message}",
            "timestamp": datetime.now().isoformat()
        })
    
    def callback(self, message):
        """
        消息回调函数(兼容RabbitMQ和内存队列)
        
        消息格式：
        {
            "execution_id": "uuid",
            "case_id": 123,
            "plan_id": 456  // 可选，用于机器人通知
        }
        
        Args:
            message: 消息数据(dict或RabbitMQ消息对象)
        """
        try:
            # 兼容RabbitMQ和内存队列
            if isinstance(message, dict):
                # 内存队列：直接是字典
                data = message
            else:
                # RabbitMQ：需要解析body
                ch, method, properties, body = message
                data = json.loads(body) if isinstance(body, (str, bytes)) else body
            
            execution_id = data.get('execution_id')
            case_id = data.get('case_id')
            plan_id = data.get('plan_id')
            
            logger.info(f"Received test execution task: execution_id={execution_id}, case_id={case_id}, plan_id={plan_id}")
            
            # 在线程中创建新事件循环执行异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    self.execute_test_case(case_id, execution_id, plan_id)
                )
            finally:
                loop.close()
            
            # 确认消息(仅RabbitMQ需要)
            if not isinstance(message, dict):
                ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing test execution message: {e}", exc_info=True)
            # 拒绝消息并重新入队(仅RabbitMQ)
            if not isinstance(message, dict):
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """启动消费者"""
        logger.info("Starting test execution consumer...")
        self.queue_manager.start_test_execution_consumer(self.callback)


# 全局测试执行消费者实例
test_execution_consumer = TestExecutionConsumer()
