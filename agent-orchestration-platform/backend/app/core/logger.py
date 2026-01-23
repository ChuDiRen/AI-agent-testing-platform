"""
日志配置 - 支持结构化日志和文件轮转
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(
    name: str = "app",
    level: str = "INFO",
    log_dir: str = "logs"
) -> logging.Logger:
    """配置日志器"""

    # 创建日志目录
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 错误日志单独文件
    error_handler = RotatingFileHandler(
        filename=f"{log_dir}/error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    return logger


class StructuredLogger:
    """结构化日志器 - 支持上下文绑定"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context: dict = {}

    def bind(self, **kwargs) -> 'StructuredLogger':
        """绑定上下文"""
        new_logger = StructuredLogger(self.logger)
        new_logger.context = {**self.context, **kwargs}
        return new_logger

    def _log(self, level: int, msg: str, **kwargs):
        """内部日志方法"""
        extra_data = {**self.context, **kwargs}
        if extra_data:
            self.logger.log(level, f"{msg} | Context: {extra_data}")
        else:
            self.logger.log(level, msg)

    def info(self, msg: str, **kwargs):
        """INFO 级别日志"""
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        """WARNING 级别日志"""
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, exc_info: bool = False, **kwargs):
        """ERROR 级别日志"""
        self._log(logging.ERROR, msg, exc_info=exc_info, **kwargs)

    def critical(self, msg: str, exc_info: bool = False, **kwargs):
        """CRITICAL 级别日志"""
        self._log(logging.CRITICAL, msg, exc_info=exc_info, **kwargs)

    def debug(self, msg: str, **kwargs):
        """DEBUG 级别日志"""
        self._log(logging.DEBUG, msg, **kwargs)


# 导出日志器
__all__ = ["setup_logger", "StructuredLogger"]
