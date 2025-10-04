# Copyright (c) 2025 左岚. All rights reserved.
"""启动Celery Worker"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app

if __name__ == "__main__":
    # 启动Celery Worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',  # 并发数
        '--queues=document_processing',  # 监听的队列
        '--pool=solo' if sys.platform == 'win32' else '--pool=prefork',  # Windows使用solo模式
    ])

