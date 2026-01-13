"""
日志配置模块
"""
import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name: str = "platform_fastapi", log_level: int = logging.INFO) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        name: 日志器名称
        log_level: 日志级别
    
    Returns:
        logging.Logger: 配置好的日志器
    """
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    # 文件处理器
    file_handler = RotatingFileHandler(
        f"{log_dir}/app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# 创建全局日志器
logger = setup_logger()
