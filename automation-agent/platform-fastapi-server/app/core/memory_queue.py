"""
内存消息队列管理器
使用 asyncio.Queue 实现内存版消息队列
支持多个队列和消费者，提供类似RabbitMQ的功能
"""
import asyncio
import threading
import json
from typing import Any, Callable, Dict, List, Optional, Awaitable
from app.core.logger import logger


class MemoryMessageQueue:
    """内存消息队列"""
    
    def __init__(self, name: str, maxsize: int = 0):
        """
        初始化消息队列
        
        Args:
            name: 队列名称
            maxsize: 队列最大长度，0表示无限制
        """
        self.name = name
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self.consumers: List[asyncio.Task] = []
        self.is_running = False
        self.lock = threading.Lock()
        logger.info(f"✅ 创建内存消息队列: {name}")
    
    async def put(self, message: Any) -> bool:
        """
        向队列发送消息
        
        Args:
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        try:
            await self.queue.put(message)
            logger.debug(f"队列 {self.name} 发送消息: {message}")
            return True
        except Exception as e:
            logger.error(f"队列 {self.name} 发送消息失败: error={e}")
            return False
    
    async def get(self, timeout: Optional[float] = None) -> Any:
        """
        从队列获取消息
        
        Args:
            timeout: 超时时间（秒），None表示无限等待
            
        Returns:
            消息内容
        """
        try:
            if timeout is not None:
                message = await asyncio.wait_for(self.queue.get(), timeout=timeout)
            else:
                message = await self.queue.get()
            
            self.queue.task_done()
            logger.debug(f"队列 {self.name} 获取消息: {message}")
            return message
        except asyncio.TimeoutError:
            # 超时是正常行为（队列空闲时），使用 debug 级别
            logger.debug(f"队列 {self.name} 获取消息超时")
            return None
        except Exception as e:
            logger.error(f"队列 {self.name} 获取消息失败: error={e}")
            return None
    
    def qsize(self) -> int:
        """获取队列当前大小"""
        try:
            return self.queue.qsize()
        except Exception as e:
            logger.error(f"获取队列大小失败: queue={self.name}, error={e}")
            return 0
    
    async def start_consumer(self, callback: Callable[[Any], Awaitable[Any]], worker_count: int = 1):
        """
        启动消费者
        
        Args:
            callback: 消息回调函数（异步函数）
            worker_count: 消费者数量
        """
        with self.lock:
            if self.is_running:
                logger.warning(f"队列 {self.name} 消费者已在运行")
                return
            
            self.is_running = True
            
            # 创建消费者任务
            for i in range(worker_count):
                task = asyncio.create_task(
                    self._consume_worker(callback),
                    name=f"MQ_Consumer_{self.name}_{i}"
                )
                self.consumers.append(task)
            
            logger.info(f"✅ 队列 {self.name} 启动 {worker_count} 个消费者")
    
    async def _consume_worker(self, callback: Callable[[Any], Awaitable[Any]]):
        """
        消费者工作协程
        
        Args:
            callback: 消息回调函数
        """
        logger.info(f"消费者线程启动: {self.name}")
        
        while self.is_running:
            try:
                # 获取消息
                message = await self.get(timeout=1.0)
                
                if message is None:
                    continue
                
                # 处理消息
                try:
                    await callback(message)
                    logger.debug(f"消息处理成功: queue={self.name}, message={message}")
                except Exception as e:
                    logger.error(f"消息处理失败: queue={self.name}, message={message}, error={e}")
                    
            except Exception as e:
                logger.error(f"消费者异常: queue={self.name}, error={e}")
                await asyncio.sleep(1)
        
        logger.info(f"消费者线程停止: {self.name}")
    
    async def stop_consumer(self):
        """停止所有消费者"""
        with self.lock:
            if not self.is_running:
                return
            
            self.is_running = False
            
            # 取消所有消费者任务
            for task in self.consumers:
                if not task.done():
                    task.cancel()
            
            # 等待任务完成
            if self.consumers:
                await asyncio.gather(*self.consumers, return_exceptions=True)
            
            self.consumers.clear()
            logger.info(f"✅ 队列 {self.name} 消费者已停止")
    
    async def clear(self):
        """清空队列"""
        try:
            while not self.queue.empty():
                self.queue.get_nowait()
                self.queue.task_done()
            logger.info(f"✅ 队列 {self.name} 已清空")
        except Exception as e:
            logger.error(f"清空队列失败: queue={self.name}, error={e}")


class MemoryQueueManager:
    """内存队列管理器（单例模式）"""
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
        
        self.queues: Dict[str, MemoryMessageQueue] = {}
        self.is_running = False
        logger.info("✅ 内存队列管理器初始化成功")
    
    def create_queue(self, name: str, maxsize: int = 0) -> MemoryMessageQueue:
        """
        创建或获取队列
        
        Args:
            name: 队列名称
            maxsize: 队列最大长度，0表示无限制
            
        Returns:
            消息队列对象
        """
        if name not in self.queues:
            self.queues[name] = MemoryMessageQueue(name, maxsize)
        return self.queues[name]
    
    async def send(self, queue_name: str, message: Any) -> bool:
        """
        发送消息到指定队列
        
        Args:
            queue_name: 队列名称
            message: 消息内容
            
        Returns:
            是否发送成功
        """
        if queue_name not in self.queues:
            logger.error(f"队列不存在: {queue_name}")
            return False
        
        return await self.queues[queue_name].put(message)
    
    async def receive(self, queue_name: str, timeout: Optional[float] = None) -> Any:
        """
        从指定队列接收消息
        
        Args:
            queue_name: 队列名称
            timeout: 超时时间（秒）
            
        Returns:
            消息内容
        """
        if queue_name not in self.queues:
            logger.error(f"队列不存在: {queue_name}")
            return None
        
        return await self.queues[queue_name].get(timeout)
    
    async def register_consumer(self, queue_name: str, callback: Callable[[Any], Awaitable[Any]], worker_count: int = 1):
        """
        注册队列消费者
        
        Args:
            queue_name: 队列名称
            callback: 消息回调函数（异步函数）
            worker_count: 消费者数量
        """
        if queue_name not in self.queues:
            self.create_queue(queue_name)
        
        await self.queues[queue_name].start_consumer(callback, worker_count)
    
    async def start_all(self, queue_configs: Dict[str, Any]):
        """
        启动所有配置的队列消费者
        
        Args:
            queue_configs: 队列配置字典
                {
                    "queue_name": {
                        "maxsize": 1000,
                        "worker_count": 3,
                        "callback": callback_function
                    },
                    ...
                }
        """
        if self.is_running:
            logger.warning("队列管理器已在运行")
            return
        
        for queue_name, config in queue_configs.items():
            maxsize = config.get("maxsize", 0)
            worker_count = config.get("worker_count", 1)
            callback = config.get("callback")
            
            if callback:
                self.create_queue(queue_name, maxsize)
                await self.register_consumer(queue_name, callback, worker_count)
        
        self.is_running = True
        logger.info("✅ 所有队列消费者已启动")
    
    async def stop_all(self):
        """停止所有队列消费者"""
        if not self.is_running:
            return
        
        for queue in self.queues.values():
            await queue.stop_consumer()
        
        self.is_running = False
        logger.info("✅ 所有队列消费者已停止")
    
    def get_queue(self, queue_name: str) -> Optional[MemoryMessageQueue]:
        """
        获取队列对象
        
        Args:
            queue_name: 队列名称
            
        Returns:
            消息队列对象
        """
        return self.queues.get(queue_name)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取队列统计信息
        
        Returns:
            统计信息字典
        """
        stats = {
            "is_running": self.is_running,
            "queue_count": len(self.queues),
            "queues": {}
        }
        
        for queue_name, queue in self.queues.items():
            stats["queues"][queue_name] = {
                "qsize": queue.qsize(),
                "consumer_count": len(queue.consumers),
                "is_running": queue.is_running
            }
        
        return stats
    
    # ========== JSON消息支持 ==========
    
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
            message = json.dumps(data, ensure_ascii=False)
            return await self.send(queue_name, message)
        except Exception as e:
            logger.error(f"发送JSON消息失败: queue={queue_name}, error={e}")
            return False
    
    async def receive_json(self, queue_name: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        接收JSON格式消息
        
        Args:
            queue_name: 队列名称
            timeout: 超时时间（秒）
            
        Returns:
            解析后的字典数据
        """
        try:
            message = await self.receive(queue_name, timeout)
            if message is None:
                return None
            return json.loads(message)
        except Exception as e:
            logger.error(f"接收JSON消息失败: queue={queue_name}, error={e}")
            return None


# 全局实例
memory_queue_manager = MemoryQueueManager()
