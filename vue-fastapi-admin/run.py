import logging
import os
import sys


class CancelledErrorFilter(logging.Filter):
    """过滤 CancelledError 相关的错误日志"""

    def filter(self, record):
        # 过滤掉包含 CancelledError 的日志
        if "CancelledError" in record.getMessage():
            return False
        # 过滤掉 KeyboardInterrupt 的日志
        if "KeyboardInterrupt" in record.getMessage():
            return False
        return True


def configure_logging():
    """配置日志，过滤 reload 时的正常错误"""
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "fmt": "%(asctime)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "access": {
                "fmt": '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "filters": ["cancelled_error_filter"],
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn.error": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.access": {"handlers": ["access"], "level": "INFO"},
        },
        "filters": {
            "cancelled_error_filter": {
                "()": "__main__.CancelledErrorFilter",
            },
        },
    }
    return LOGGING_CONFIG


if __name__ == "__main__":
    import uvicorn

    # 配置日志
    LOGGING_CONFIG = configure_logging()

    # 从环境变量读取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 9999))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    print(f"Starting server with hot reload on {host}:{port}")

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=reload,
        log_config=LOGGING_CONFIG,
        loop="asyncio",
        use_colors=False,
        reload_delay=0.5,
        reload_includes=["*.py"],
    )
