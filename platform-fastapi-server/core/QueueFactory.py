"""
消息队列工厂
根据配置自动选择RabbitMQ或内存队列
"""
import logging
from typing import Union

logger = logging.getLogger(__name__)


def get_queue_manager() -> Union['RabbitMQManager', 'InMemoryQueueManager']:
    """
    获取队列管理器实例
    
    根据配置文件中的QUEUE_TYPE自动选择:
    - "rabbitmq": 使用RabbitMQ（生产环境推荐）
    - "memory": 使用内存队列（开发环境推荐）
    
    Returns:
        队列管理器实例
    """
    from config.dev_settings import settings
    
    queue_type = settings.QUEUE_TYPE.lower()
    
    if queue_type == "rabbitmq":
        logger.info("Using RabbitMQ queue manager")
        try:
            from core.RabbitMQManager import rabbitmq_manager
            # 尝试连接
            rabbitmq_manager.connect()
            return rabbitmq_manager
        except Exception as e:
            logger.warning(f"Failed to connect to RabbitMQ: {e}")
            logger.info("Falling back to InMemoryQueue manager")
            from core.InMemoryQueueManager import inmemory_queue_manager
            return inmemory_queue_manager
    
    elif queue_type == "memory":
        logger.info("Using InMemoryQueue manager")
        from core.InMemoryQueueManager import inmemory_queue_manager
        return inmemory_queue_manager
    
    else:
        logger.warning(f"Unknown queue type: {queue_type}, using InMemoryQueue")
        from core.InMemoryQueueManager import inmemory_queue_manager
        return inmemory_queue_manager


# 全局队列管理器实例
queue_manager = get_queue_manager()


def get_queue_stats():
    """
    获取队列统计信息
    
    Returns:
        统计信息字典
    """
    from config.dev_settings import settings
    
    stats = {
        "queue_type": settings.QUEUE_TYPE,
        "queues": {}
    }
    
    # 如果是内存队列，获取详细统计
    if hasattr(queue_manager, 'get_stats'):
        stats["queues"] = queue_manager.get_stats()
    
    return stats
