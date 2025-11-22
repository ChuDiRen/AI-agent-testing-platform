"""
内存级别的消息队列管理器
用于替代RabbitMQ，适用于开发环境和单机部署
"""
import asyncio
import json
from typing import Callable, Optional, Dict, Any
from queue import Queue, Empty
from threading import Thread, Event
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class InMemoryQueue:
    """内存队列"""
    
    def __init__(self, name: str, maxsize: int = 0):
        """
        初始化内存队列
        
        Args:
            name: 队列名称
            maxsize: 队列最大大小，0表示无限制
        """
        self.name = name
        self.queue = Queue(maxsize=maxsize)
        self.consumers = []
        self.is_consuming = False
        self.stop_event = Event()
        self.consumer_thread = None
        
    def put(self, message: dict):
        """
        将消息放入队列
        
        Args:
            message: 消息数据
        """
        try:
            # 添加时间戳
            message['_enqueue_time'] = datetime.now().isoformat()
            self.queue.put(message, block=False)
            logger.info(f"[{self.name}] Message enqueued: {message.get('id', 'unknown')}")
        except Exception as e:
            logger.error(f"[{self.name}] Failed to enqueue message: {e}")
            raise
    
    def get(self, timeout: float = 1.0) -> Optional[dict]:
        """
        从队列获取消息
        
        Args:
            timeout: 超时时间（秒）
            
        Returns:
            消息数据，如果队列为空则返回None
        """
        try:
            message = self.queue.get(timeout=timeout)
            return message
        except Empty:
            return None
    
    def size(self) -> int:
        """获取队列大小"""
        return self.queue.qsize()
    
    def is_empty(self) -> bool:
        """检查队列是否为空"""
        return self.queue.empty()
    
    def clear(self):
        """清空队列"""
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
            except Empty:
                break
        logger.info(f"[{self.name}] Queue cleared")
    
    def add_consumer(self, callback: Callable):
        """
        添加消费者回调函数
        
        Args:
            callback: 消息处理回调函数，接收message参数
        """
        self.consumers.append(callback)
        logger.info(f"[{self.name}] Consumer added, total: {len(self.consumers)}")
    
    def start_consuming(self):
        """启动消费者线程"""
        if self.is_consuming:
            logger.warning(f"[{self.name}] Consumer already running")
            return
        
        self.is_consuming = True
        self.stop_event.clear()
        self.consumer_thread = Thread(target=self._consume_loop, daemon=True)
        self.consumer_thread.start()
        logger.info(f"[{self.name}] Consumer started")
    
    def stop_consuming(self):
        """停止消费者线程"""
        if not self.is_consuming:
            return
        
        self.is_consuming = False
        self.stop_event.set()
        if self.consumer_thread:
            self.consumer_thread.join(timeout=5)
        logger.info(f"[{self.name}] Consumer stopped")
    
    def _consume_loop(self):
        """消费者循环"""
        logger.info(f"[{self.name}] Consumer loop started")
        
        while self.is_consuming and not self.stop_event.is_set():
            try:
                # 从队列获取消息
                message = self.get(timeout=1.0)
                
                if message is None:
                    continue
                
                # 处理消息
                logger.info(f"[{self.name}] Processing message: {message.get('id', 'unknown')}")
                
                for consumer in self.consumers:
                    try:
                        # 调用消费者回调
                        consumer(message)
                    except Exception as e:
                        logger.error(f"[{self.name}] Consumer callback error: {e}", exc_info=True)
                
                logger.info(f"[{self.name}] Message processed successfully")
                
            except Exception as e:
                logger.error(f"[{self.name}] Consume loop error: {e}", exc_info=True)
        
        logger.info(f"[{self.name}] Consumer loop stopped")


class InMemoryQueueManager:
    """内存级别的消息队列管理器"""
    
    def __init__(self):
        """初始化队列管理器"""
        self.queues: Dict[str, InMemoryQueue] = {}
        
        # 预定义队列
        self.TEST_EXECUTION_QUEUE = 'test_execution'
        self.MESSAGE_PUSH_QUEUE = 'message_push'
        
        # 创建默认队列
        self._create_default_queues()
        
        logger.info("InMemoryQueueManager initialized")
    
    def _create_default_queues(self):
        """创建默认队列"""
        self.queues[self.TEST_EXECUTION_QUEUE] = InMemoryQueue(self.TEST_EXECUTION_QUEUE)
        self.queues[self.MESSAGE_PUSH_QUEUE] = InMemoryQueue(self.MESSAGE_PUSH_QUEUE)
    
    def connect(self):
        """
        建立连接（内存队列无需连接，保持接口兼容）
        """
        logger.info("InMemoryQueueManager connected (no-op)")
    
    def get_queue(self, queue_name: str) -> InMemoryQueue:
        """
        获取队列
        
        Args:
            queue_name: 队列名称
            
        Returns:
            队列实例
        """
        if queue_name not in self.queues:
            self.queues[queue_name] = InMemoryQueue(queue_name)
        return self.queues[queue_name]
    
    def publish_test_execution(self, execution_data: dict):
        """
        发布测试执行任务到队列
        
        Args:
            execution_data: 执行数据，包含execution_id, case_id等
        """
        try:
            queue = self.get_queue(self.TEST_EXECUTION_QUEUE)
            queue.put(execution_data)
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
        try:
            queue = self.get_queue(self.MESSAGE_PUSH_QUEUE)
            queue.put(message_data)
            logger.info(f"Published message push task for robot: {message_data.get('robot_id')}")
        except Exception as e:
            logger.error(f"Failed to publish message push task: {e}")
            raise
    
    def start_test_execution_consumer(self, callback: Callable):
        """
        启动测试执行消费者
        
        Args:
            callback: 消息处理回调函数，接收message参数
        """
        queue = self.get_queue(self.TEST_EXECUTION_QUEUE)
        queue.add_consumer(callback)
        queue.start_consuming()
        logger.info("Started test execution consumer")
    
    def start_message_push_consumer(self, callback: Callable):
        """
        启动消息推送消费者
        
        Args:
            callback: 消息处理回调函数，接收message参数
        """
        queue = self.get_queue(self.MESSAGE_PUSH_QUEUE)
        queue.add_consumer(callback)
        queue.start_consuming()
        logger.info("Started message push consumer")
    
    def close(self):
        """关闭所有队列"""
        for queue_name, queue in self.queues.items():
            queue.stop_consuming()
        logger.info("InMemoryQueueManager closed")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            统计信息字典
        """
        stats = {}
        for queue_name, queue in self.queues.items():
            stats[queue_name] = {
                'size': queue.size(),
                'is_empty': queue.is_empty(),
                'is_consuming': queue.is_consuming,
                'consumers_count': len(queue.consumers)
            }
        return stats


# 全局内存队列管理器实例
inmemory_queue_manager = InMemoryQueueManager()
