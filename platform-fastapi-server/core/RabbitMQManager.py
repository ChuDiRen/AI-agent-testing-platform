"""
RabbitMQ消息队列管理器
用于异步任务处理（测试执行、消息推送）
"""
import json
import logging
from typing import Callable, Optional

import pika

logger = logging.getLogger(__name__)


class RabbitMQManager:
    """RabbitMQ客户端管理器"""
    
    def __init__(
        self, 
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None
    ):
        """
        初始化RabbitMQ连接
        
        Args:
            host: RabbitMQ服务器地址
            port: RabbitMQ端口
            username: 用户名
            password: 密码
        """
        # 延迟加载配置
        from config.dev_settings import settings
        
        self.host = host or settings.RABBITMQ_HOST
        self.port = port or settings.RABBITMQ_PORT
        self.username = username or settings.RABBITMQ_USER
        self.password = password or settings.RABBITMQ_PASSWORD
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        
        # 队列名称
        self.TEST_EXECUTION_QUEUE = 'test_execution'
        self.MESSAGE_PUSH_QUEUE = 'message_push'
    
    def connect(self):
        """建立RabbitMQ连接"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # 声明队列（持久化）
            self.channel.queue_declare(queue=self.TEST_EXECUTION_QUEUE, durable=True)
            self.channel.queue_declare(queue=self.MESSAGE_PUSH_QUEUE, durable=True)
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise
    
    def publish_test_execution(self, execution_data: dict):
        """
        发布测试执行任务到队列
        
        Args:
            execution_data: 执行数据，包含execution_id, case_id等
        """
        if not self.channel:
            self.connect()
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.TEST_EXECUTION_QUEUE,
                body=json.dumps(execution_data, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                    content_type='application/json'
                )
            )
            logger.info(f"Published test execution task: {execution_data.get('execution_id')}")
        except Exception as e:
            logger.error(f"Failed to publish test execution task: {e}")
            raise
    
    def publish_message_push(self, message_data: dict):
        """
        发布消息推送任务到队列
        
        Args:
            message_data: 消息数据，包含robot_id, message等
        """
        if not self.channel:
            self.connect()
        
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=self.MESSAGE_PUSH_QUEUE,
                body=json.dumps(message_data, ensure_ascii=False),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # 消息持久化
                    content_type='application/json'
                )
            )
            logger.info(f"Published message push task for robot: {message_data.get('robot_id')}")
        except Exception as e:
            logger.error(f"Failed to publish message push task: {e}")
            raise
    
    def start_test_execution_consumer(self, callback: Callable):
        """
        启动测试执行消费者
        
        Args:
            callback: 消息处理回调函数
        """
        if not self.channel:
            self.connect()
        
        self.channel.basic_qos(prefetch_count=1)  # 一次只处理一个任务
        self.channel.basic_consume(
            queue=self.TEST_EXECUTION_QUEUE,
            on_message_callback=callback
        )
        logger.info("Started test execution consumer")
        self.channel.start_consuming()
    
    def start_message_push_consumer(self, callback: Callable):
        """
        启动消息推送消费者
        
        Args:
            callback: 消息处理回调函数
        """
        if not self.channel:
            self.connect()
        
        self.channel.basic_qos(prefetch_count=1)  # 一次只处理一个任务
        self.channel.basic_consume(
            queue=self.MESSAGE_PUSH_QUEUE,
            on_message_callback=callback
        )
        logger.info("Started message push consumer")
        self.channel.start_consuming()
    
    def close(self):
        """关闭RabbitMQ连接"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Closed RabbitMQ connection")


# 全局RabbitMQ管理器实例
rabbitmq_manager = RabbitMQManager()
