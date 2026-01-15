import pika
import time
from config.dev_settings import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD

class RabbitMQError(Exception):
    """RabbitMQ操作异常"""
    pass

def send_perf_message(routing_key, message, max_retries=3, retry_delay=1):
    """
    发送消息到指定的交换机
    
    参数:
        routing_key: 路由键
        message: 要发送的消息内容
        max_retries: 最大重试次数（默认3次）
        retry_delay: 重试间隔（秒，默认1秒）
        
    异常:
        ValueError: 当消息或路由键无效时抛出
        RabbitMQError: 当RabbitMQ操作失败时抛出
    """
    if not message:
        raise ValueError("消息内容不能为空")
    if not routing_key:
        raise ValueError("路由键不能为空")
    
    exchange = f"{routing_key}_exchange"
    attempt = 0
    last_exception = None
    
    while attempt < max_retries:
        attempt += 1
        connection = None
        
        try:
            # 创建连接
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials
                )
            )
            channel = connection.channel()
            
            # 声明交换机
            channel.exchange_declare(
                exchange=exchange,
                exchange_type='direct',
                durable=True
            )
            
            # 发布消息
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2  # 持久化消息
                )
            )
            
            if connection and connection.is_open:
                connection.close()
            return
            
        except Exception as e:
            last_exception = e
            if connection and connection.is_open:
                connection.close()
            if attempt < max_retries:
                time.sleep(retry_delay)
            continue
    
    raise RabbitMQError(
        f"发送消息失败，{max_retries}次重试均失败: {str(last_exception)}"
    ) if last_exception else RabbitMQError(
        f"发送消息失败，{max_retries}次重试均失败"
    )


if __name__ == '__main__':
    send_perf_message('api_queue', '接口自动化测试用例')