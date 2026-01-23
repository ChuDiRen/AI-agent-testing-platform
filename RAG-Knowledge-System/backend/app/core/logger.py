"""
日志配置模块
"""
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "app",
    level: str = "INFO",
    log_dir: str = "./logs"
) -> logging.Logger:
    """
    配置日志器

    Args:
        name: 日志器名称
        level: 日志级别
        log_dir: 日志目录

    Returns:
        配置好的日志器实例
    """
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 清除已有的处理器（防止重复添加）
    logger.handlers.clear()

    # 日志格式
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(getattr(logging, level.upper()))
    logger.addHandler(console_handler)

    # 文件处理器（按大小轮转）
    file_handler = RotatingFileHandler(
        filename=log_path / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, level.upper()))
    logger.addHandler(file_handler)

    # 错误日志单独文件
    error_handler = RotatingFileHandler(
        filename=log_path / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)

    return logger


class ContextLogger:
    """带上下文的日志器"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context: dict = {}

    def bind(self, **kwargs) -> 'ContextLogger':
        """绑定上下文"""
        new_logger = ContextLogger(self.logger)
        new_logger.context = {**self.context, **kwargs}
        return new_logger

    def _format_message(self, msg: str, **kwargs) -> str:
        """格式化消息，附加上下文"""
        extra = {**self.context, **kwargs}
        if extra:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra.items()])
            return f"{msg} | {extra_str}"
        return msg

    def debug(self, msg: str, **kwargs):
        self.logger.debug(self._format_message(msg, **kwargs))

    def info(self, msg: str, **kwargs):
        self.logger.info(self._format_message(msg, **kwargs))

    def warning(self, msg: str, **kwargs):
        self.logger.warning(self._format_message(msg, **kwargs))

    def error(self, msg: str, exc_info: bool = False, **kwargs):
        self.logger.error(self._format_message(msg, **kwargs), exc_info=exc_info)

    def critical(self, msg: str, exc_info: bool = False, **kwargs):
        self.logger.critical(self._format_message(msg, **kwargs), exc_info=exc_info)
