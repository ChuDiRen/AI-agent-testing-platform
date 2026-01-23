"""
统一消息队列管理器
支持RabbitMQ和内存队列的自动降级
优先使用RabbitMQ，连接失败时降级到内存队列
"""
import asyncio
import json
import threading
from typing import Any, Callable, Dict, List, Optional, Awaitable
from app.core.config import settings
from app.core.logger import logger

try:
    import pika
    RABBITMQ_AVAILABLE = True
except ImportError:
    RABBITMQ_AVAILABLE = False
    logger.warning("RabbitMQ库未安装，将直接使用内存队列")

from app.core.memory_queue import MemoryMessageQueue


class UnifiedQueueManager:
    """统一队列管理器（单例模式）"""
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
        
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.memory_queues: Dict[str, MemoryMessageQueue] = {}
        self.use_rabbitmq = False
        self.consumer_tasks: List[asyncio.Task] = []
        self.is_running = False
        self._initialized_queue = False
    
    async def test_rabbitmq_connection(self) -> bool:
        """
        测试RabbitMQ连接是否可用

        Returns:
            True表示可用，False表示不可用
        """
        try:
            # 设置socket超时，让连接失败时能快速返回
            import socket
            socket.setdefaulttimeout(3)  # 3秒超时

            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=10,
                blocked_connection_timeout=5,
                connection_attempts=1,  # 只尝试连接一次
                retry_delay=0  # 不重试
            )

            # 尝试建立连接
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.close()
            connection.close()

            # 恢复默认超时
            socket.setdefaulttimeout(None)
            return True
        except Exception as e:
            logger.warning(f"⚠️ RabbitMQ连接测试失败: {e}")
            # 恢复默认超时
            import socket
            socket.setdefaulttimeout(None)
            return False
    
    async def initialize(self):
        """初始化队列管理器，测试RabbitMQ连接，失败则使用内存队列"""
        if self._initialized_queue:
            return
        
        self._initialized_queue = True
        logger.info("🔄 正在初始化队列管理器...")
        
        # 尝试连接RabbitMQ
        if RABBITMQ_AVAILABLE and settings.RABBITMQ_FALLBACK_ENABLED:
            rabbitmq_available = await self.test_rabbitmq_connection()
            
            if rabbitmq_available:
                try:
                    credentials = pika.PlainCredentials(
                        settings.RABBITMQ_USER,
                        settings.RABBITMQ_PASSWORD
                    )
                    parameters = pika.ConnectionParameters(
                        host=settings.RABBITMQ_HOST,
                        port=settings.RABBITMQ_PORT,
                        credentials=credentials,
                        heartbeat=10
                    )
                    
                    self.rabbitmq_connection = pika.BlockingConnection(parameters)
                    self.rabbitmq_channel = self.rabbitmq_connection.channel()
                    self.use_rabbitmq = True
                    logger.info("✅ 成功使用RabbitMQ消息队列")
                    return
                except Exception as e:
                    logger.warning(f"⚠️ RabbitMQ连接失败: {e}，自动降级到内存队列")
                    if self.rabbitmq_channel:
                        self.rabbitmq_channel.close()
                    if self.rabbitmq_connection:
                        self.rabbitmq_connection.close()
                    self.rabbitmq_channel = None
                    self.rabbitmq_connection = None
        
        # 使用内存队列
        self.use_rabbitmq = False
        logger.info("✅ 使用内存消息队列（降级模式）")
    
    async def send(self, queue_name: str, message: Any) -> bool:
        """
        发送消息到指定队列
        
        Args:
            queue_name: 队列名称
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        try:
            if self.use_rabbitmq and self.rabbitmq_channel:
                # 使用RabbitMQ
                # 序列化消息
                if isinstance(message, (dict, list)):
                    message_str = json.dumps(message, ensure_ascii=False)
                else:
                    message_str = str(message)
                
                # 声明队列
                self.rabbitmq_channel.queue_declare(queue=queue_name, durable=True)
                
                # 发送消息
                self.rabbitmq_channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=message_str,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # 持久化消息
                    )
                )
                logger.debug(f"消息发送到RabbitMQ: {queue_name}")
                return True
            else:
                # 使用内存队列
                if queue_name not in self.memory_queues:
                    self.memory_queues[queue_name] = MemoryMessageQueue(queue_name)
                
                await self.memory_queues[queue_name].put(message)
                logger.debug(f"消息发送到内存队列: {queue_name}")
                return True
        except Exception as e:
            logger.error(f"发送消息失败: queue={queue_name}, error={e}")
            return False
    
    async def send_json(self, queue_name: str, data: Dict[str, Any]) -> bool:
        """
        发送JSON格式消息
        
        Args:
            queue_name: 队列名称
            data: 消息数据（字典）
            
        Returns:
            是否发送成功
        """
        try:
            return await self.send(queue_name, data)
        except Exception as e:
            logger.error(f"发送JSON消息失败: queue={queue_name}, error={e}")
            return False
    
    async def register_consumer(self, queue_name: str, callback: Callable[[Any], Awaitable[Any]], worker_count: int = 1):
        """
        注册队列消费者
        
        Args:
            queue_name: 队列名称
            callback: 消息回调函数（异步函数）
            worker_count: 消费者数量
        """
        try:
            if self.use_rabbitmq and self.rabbitmq_channel:
                # 使用RabbitMQ消费者（需要在线程中运行）
                for i in range(worker_count):
                    task = asyncio.create_task(
                        self._consume_rabbitmq(queue_name, callback),
                        name=f"RabbitMQ_Consumer_{queue_name}_{i}"
                    )
                    self.consumer_tasks.append(task)
                logger.info(f"✅ 队列 {queue_name} 启动 {worker_count} 个RabbitMQ消费者")
            else:
                # 使用内存队列消费者
                if queue_name not in self.memory_queues:
                    self.memory_queues[queue_name] = MemoryMessageQueue(queue_name)
                
                await self.memory_queues[queue_name].start_consumer(callback, worker_count)
                logger.info(f"✅ 队列 {queue_name} 启动 {worker_count} 个内存消费者")
        except Exception as e:
            logger.error(f"注册消费者失败: queue={queue_name}, error={e}")
            raise
    
    async def _consume_rabbitmq(self, queue_name: str, callback: Callable[[Any], Awaitable[Any]]):
        """
        RabbitMQ消费者协程
        
        Args:
            queue_name: 队列名称
            callback: 消息回调函数
        """
        logger.info(f"RabbitMQ消费者线程启动: {queue_name}")
        
        try:
            # 创建新的连接和通道（每个消费者独立）
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER,
                settings.RABBITMQ_PASSWORD
            )
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                credentials=credentials,
                heartbeat=10
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # 声明队列
            channel.queue_declare(queue=queue_name, durable=True)
            
            # 设置QoS
            channel.basic_qos(prefetch_count=1)
            
            # 定义回调
            def on_message(ch, method, properties, body):
                try:
                    # 反序列化消息
                    try:
                        message = json.loads(body.decode())
                    except:
                        message = body.decode()
                    
                    # 异步处理消息
                    asyncio.create_task(callback(message))
                    
                    # 确认消息
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"处理RabbitMQ消息失败: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # 消费消息
            channel.basic_consume(queue=queue_name, on_message_callback=on_message)
            
            # 开始消费（在独立线程中）
            def start_consuming():
                try:
                    channel.start_consuming()
                except Exception as e:
                    logger.error(f"RabbitMQ消费异常: {e}")
            
            import threading
            thread = threading.Thread(target=start_consuming, daemon=True)
            thread.start()
            
            # 保持协程运行
            while self.is_running:
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"RabbitMQ消费者初始化失败: queue={queue_name}, error={e}")
    
    async def start_all(self, queue_configs: Dict[str, Any]):
        """
        启动所有配置的队列消费者
        
        Args:
            queue_configs: 队列配置字典
                {
                    "queue_name": {
                        "worker_count": 3,
                        "callback": callback_function
                    },
                    ...
                }
        """
        if self.is_running:
            logger.warning("队列管理器已在运行")
            return
        
        self.is_running = True
        
        for queue_name, config in queue_configs.items():
            worker_count = config.get("worker_count", 1)
            callback = config.get("callback")
            
            if callback:
                await self.register_consumer(queue_name, callback, worker_count)
        
        logger.info("✅ 所有队列消费者已启动")
    
    async def stop_all(self):
        """停止所有队列消费者"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # 停止内存队列消费者
        for queue in self.memory_queues.values():
            await queue.stop_consumer()
        
        # 取消RabbitMQ消费者任务
        for task in self.consumer_tasks:
            if not task.done():
                task.cancel()
        
        # 等待任务完成
        if self.consumer_tasks:
            await asyncio.gather(*self.consumer_tasks, return_exceptions=True)
        
        self.consumer_tasks.clear()
        
        # 关闭RabbitMQ连接
        if self.rabbitmq_channel:
            try:
                self.rabbitmq_channel.close()
            except:
                pass
            self.rabbitmq_channel = None
        
        if self.rabbitmq_connection:
            try:
                self.rabbitmq_connection.close()
            except:
                pass
            self.rabbitmq_connection = None
        
        logger.info("✅ 所有队列消费者已停止")
    
    def get_backend_type(self) -> str:
        """
        获取当前使用的队列后端类型
        
        Returns:
            "rabbitmq" 或 "memory"
        """
        return "rabbitmq" if self.use_rabbitmq else "memory"
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "is_running": self.is_running,
            "backend_type": self.get_backend_type(),
            "queue_count": len(self.memory_queues) if not self.use_rabbitmq else 0,
            "queues": {}
        }
        
        if not self.use_rabbitmq:
            for queue_name, queue in self.memory_queues.items():
                stats["queues"][queue_name] = {
                    "qsize": queue.qsize(),
                    "consumer_count": len(queue.consumers),
                    "is_running": queue.is_running
                }
        
        return stats


# 全局实例
queue_manager = UnifiedQueueManager()
