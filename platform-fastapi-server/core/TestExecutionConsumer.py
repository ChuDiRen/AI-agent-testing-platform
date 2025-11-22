"""
测试执行消费者
从RabbitMQ队列中消费测试执行任务，并通过WebSocket实时推送进度
"""
import json
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TestExecutionConsumer:
    """测试执行消费者"""
    
    def __init__(self):
        from core.RabbitMQManager import rabbitmq_manager
        from core.WebSocketManager import manager as ws_manager
        
        self.rabbitmq = rabbitmq_manager
        self.ws_manager = ws_manager
    
    async def execute_test_case(self, case_id: int, execution_id: str):
        """
        执行测试用例并实时推送进度
        
        Args:
            case_id: 测试用例ID
            execution_id: 执行ID（用于WebSocket连接标识）
        """
        try:
            # TODO: 从数据库获取测试用例步骤
            # steps = get_test_case_steps(case_id)
            # 临时模拟数据
            steps = [
                {"id": 1, "step_desc": "初始化测试环境", "keyword": "setup"},
                {"id": 2, "step_desc": "发送登录请求", "keyword": "http_post"},
                {"id": 3, "step_desc": "验证响应状态", "keyword": "assert_status"},
                {"id": 4, "step_desc": "清理测试数据", "keyword": "teardown"},
            ]
            
            total_steps = len(steps)
            
            # 发送开始事件
            await self.ws_manager.send_progress(execution_id, {
                "type": "start",
                "execution_id": execution_id,
                "case_id": case_id,
                "total_steps": total_steps,
                "progress": 0,
                "status": "running",
                "message": f"开始执行测试用例 (共{total_steps}步)",
                "timestamp": datetime.now().isoformat()
            })
            
            # 逐步执行
            for idx, step in enumerate(steps, 1):
                # 发送步骤开始事件
                await self.ws_manager.send_progress(execution_id, {
                    "type": "step_start",
                    "execution_id": execution_id,
                    "current_step": idx,
                    "total_steps": total_steps,
                    "progress": int(((idx - 1) / total_steps) * 100),
                    "step_name": step["step_desc"],
                    "status": "running",
                    "message": f"正在执行步骤 {idx}/{total_steps}: {step['step_desc']}",
                    "timestamp": datetime.now().isoformat()
                })
                
                # 模拟步骤执行
                await asyncio.sleep(2)  # TODO: 实际执行关键字
                
                # 模拟执行结果（90%成功率）
                import random
                success = random.random() > 0.1
                
                # 发送步骤结束事件
                await self.ws_manager.send_progress(execution_id, {
                    "type": "step_end",
                    "execution_id": execution_id,
                    "current_step": idx,
                    "total_steps": total_steps,
                    "progress": int((idx / total_steps) * 100),
                    "step_name": step["step_desc"],
                    "status": "passed" if success else "failed",
                    "message": f"步骤 {idx} {'通过' if success else '失败'}",
                    "timestamp": datetime.now().isoformat()
                })
                
                # 如果失败，停止执行
                if not success:
                    await self.ws_manager.send_progress(execution_id, {
                        "type": "complete",
                        "execution_id": execution_id,
                        "status": "failed",
                        "progress": 100,
                        "message": f"测试用例执行失败，在步骤 {idx} 处中断",
                        "timestamp": datetime.now().isoformat()
                    })
                    return
            
            # 发送完成事件
            await self.ws_manager.send_progress(execution_id, {
                "type": "complete",
                "execution_id": execution_id,
                "status": "passed",
                "progress": 100,
                "message": "测试用例执行成功",
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Test case {case_id} execution completed: {execution_id}")
            
        except Exception as e:
            logger.error(f"Error executing test case {case_id}: {e}")
            # 发送错误事件
            await self.ws_manager.send_progress(execution_id, {
                "type": "error",
                "execution_id": execution_id,
                "status": "error",
                "progress": 0,
                "message": f"执行出错: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    def callback(self, ch, method, properties, body):
        """
        RabbitMQ消息回调函数
        
        Args:
            ch: 通道
            method: 方法
            properties: 属性
            body: 消息体
        """
        try:
            data = json.loads(body)
            execution_id = data.get('execution_id')
            case_id = data.get('case_id')
            
            logger.info(f"Received test execution task: execution_id={execution_id}, case_id={case_id}")
            
            # 执行测试用例（异步）
            asyncio.run(self.execute_test_case(case_id, execution_id))
            
            # 确认消息
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error(f"Error processing test execution message: {e}")
            # 拒绝消息并重新入队
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """启动消费者"""
        logger.info("Starting test execution consumer...")
        self.rabbitmq.start_test_execution_consumer(self.callback)


# 全局测试执行消费者实例
test_execution_consumer = TestExecutionConsumer()
