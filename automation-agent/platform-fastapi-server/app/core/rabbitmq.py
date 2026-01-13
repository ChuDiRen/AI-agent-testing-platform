"""
RabbitMQ 管理模块
单例模式，负责管理 RabbitMQ 连接和消费者
"""
import pika
import threading
from typing import Callable
from app.core.config import settings


class RabbitMQManager:
    """RabbitMQ 管理器（单例模式）"""
    _instance_lock = threading.Lock()
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """单例实现"""
        if not cls._instance:
            with cls._instance_lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True
    
    def start_workers(self, callback: Callable):
        """
        启动消费者线程
        
        Args:
            callback: 消息回调函数
        """
        print("RabbitMQ 初始化完成，准备启动消费者线程...")
        for queue_name, thread_count in settings.QUEUE_LIST:
            for i in range(thread_count):
                thread = threading.Thread(
                    target=self._start_consumer,
                    args=(queue_name, callback),
                    daemon=True,
                    name=f"MQ_Consumer_{queue_name}_{i}"
                )
                thread.start()
    
    def _start_consumer(self, routing_key: str, callback: Callable):
        """
        启动消费者
        
        Args:
            routing_key: 路由键（队列名）
            callback: 消息回调函数
        """
        try:
            # 创建连接
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=settings.RABBITMQ_HOST,
                    port=settings.RABBITMQ_PORT,
                    credentials=credentials
                )
            )
            channel = connection.channel()
            
            # 声明交换机和队列
            exchange = f"{routing_key}_exchange"
            channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)
            channel.queue_declare(queue=routing_key)
            channel.queue_bind(exchange=exchange, queue=routing_key, routing_key=routing_key)
            
            # 消息回调
            def on_message(ch, method, properties, body):
                print(f"[x] 收到消息 来自于 {routing_key}: {body.decode()}")
                # 调用业务回调
                try:
                    callback(body)
                except Exception as e:
                    print(f"处理消息时发生错误: {e}")
            
            # 绑定回调函数
            channel.basic_consume(queue=routing_key, on_message_callback=on_message, auto_ack=True)
            
            # 开始消费
            print(f"[x] 开始监听队列: {routing_key}")
            channel.start_consuming()
            
        except Exception as e:
            print(f"RabbitMQ 消费者线程异常: {e}")
