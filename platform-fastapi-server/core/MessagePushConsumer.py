"""
消息推送消费者
从RabbitMQ队列中消费消息推送任务，发送到各个机器人平台
"""
import json
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MessagePushConsumer:
    """消息推送消费者"""
    
    def __init__(self):
        from core.RabbitMQManager import rabbitmq_manager
        from config.dev_settings import settings
        
        self.rabbitmq = rabbitmq_manager
        self.retry_count = settings.ROBOT_RETRY_COUNT
        self.timeout = settings.ROBOT_TIMEOUT
    
    def send_message(self, robot_id: int, message: str, retry: int = 0) -> bool:
        """
        发送消息到机器人
        
        Args:
            robot_id: 机器人ID
            message: 消息内容
            retry: 当前重试次数
        
        Returns:
            是否发送成功
        """
        try:
            # TODO: 从数据库获取机器人配置
            # robot = get_robot_config(robot_id)
            
            # 临时模拟发送
            logger.info(f"Sending message to robot {robot_id}: {message[:50]}...")
            time.sleep(1)  # 模拟网络延迟
            
            # 模拟90%成功率
            import random
            if random.random() > 0.1:
                logger.info(f"Message sent successfully to robot {robot_id}")
                return True
            else:
                raise Exception("模拟发送失败")
                
        except Exception as e:
            logger.error(f"Failed to send message to robot {robot_id}: {e}")
            
            # 重试逻辑
            if retry < self.retry_count:
                wait_time = 2 ** retry  # 指数退避: 1s, 2s, 4s
                logger.info(f"Retrying in {wait_time}s... (attempt {retry + 1}/{self.retry_count})")
                time.sleep(wait_time)
                return self.send_message(robot_id, message, retry + 1)
            else:
                logger.error(f"Failed to send message after {self.retry_count} retries")
                return False
    
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
            robot_id = data.get('robot_id')
            message = data.get('message')
            
            logger.info(f"Received message push task for robot {robot_id}")
            
            # 发送消息
            success = self.send_message(robot_id, message)
            
            if success:
                # 确认消息
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # 发送失败，拒绝消息（不重新入队，避免无限循环）
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                
        except Exception as e:
            logger.error(f"Error processing message push: {e}")
            # 拒绝消息并重新入队（可能是临时错误）
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start(self):
        """启动消费者"""
        logger.info("Starting message push consumer...")
        self.rabbitmq.start_message_push_consumer(self.callback)


# 全局消息推送消费者实例
message_push_consumer = MessagePushConsumer()
