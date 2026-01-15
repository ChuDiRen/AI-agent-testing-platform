"""
统一日志工具类
支持 trace_id 追踪，提供统一的日志接口
"""
import logging
import sys
import uuid
from contextvars import ContextVar
from typing import Optional

# 使用 ContextVar 存储当前请求的 trace_id
trace_id_var: ContextVar[str] = ContextVar('trace_id', default='')


class TraceIDFilter(logging.Filter):
    """日志过滤器，为日志记录添加 trace_id"""
    
    def filter(self, record):
        trace_id = trace_id_var.get()
        record.trace_id = trace_id if trace_id else 'N/A'
        return True


class Logger:
    """日志工具类"""
    
    @staticmethod
    def get_trace_id() -> str:
        """获取当前请求的 trace_id"""
        return trace_id_var.get() or ''
    
    @staticmethod
    def set_trace_id(trace_id: Optional[str] = None) -> str:
        """
        设置当前请求的 trace_id
        
        Args:
            trace_id: 指定的 trace_id，如果为 None 则自动生成
            
        Returns:
            str: 设置的 trace_id
        """
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        trace_id_var.set(trace_id)
        return trace_id
    
    @staticmethod
    def clear_trace_id():
        """清除当前请求的 trace_id"""
        trace_id_var.set('')
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        获取配置好的 logger 实例
        
        Args:
            name: logger 名称，通常使用 __name__
            
        Returns:
            logging.Logger: 配置好的 logger 实例
        """
        logger = logging.getLogger(name)
        
        # 避免重复添加 filter
        if not any(isinstance(f, TraceIDFilter) for f in logger.filters):
            logger.addFilter(TraceIDFilter())
        
        return logger


def setup_logging(level: int = logging.INFO):
    """
    配置全局日志系统
    
    Args:
        level: 日志级别，默认 INFO
    """
    # 创建自定义格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - [trace_id: %(trace_id)s] - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 配置控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(TraceIDFilter())
    
    # 配置根 logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 清除已有的处理器，避免重复
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # 可选：配置文件处理器（如果需要）
    # file_handler = logging.FileHandler('logs/app.log', encoding='utf-8')
    # file_handler.setLevel(level)
    # file_handler.setFormatter(formatter)
    # file_handler.addFilter(TraceIDFilter())
    # root_logger.addHandler(file_handler)
    
    # 设置第三方库的日志级别，避免过多输出
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.error').setLevel(logging.INFO)


# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """
    便捷函数：获取 logger
    
    Args:
        name: logger 名称
        
    Returns:
        logging.Logger: logger 实例
    """
    return Logger.get_logger(name)

