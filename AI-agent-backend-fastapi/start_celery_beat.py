# Copyright (c) 2025 左岚. All rights reserved.
"""启动Celery Beat定时任务调度器"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.celery_app import celery_app

if __name__ == "__main__":
    # 启动Celery Beat
    celery_app.start([
        'beat',
        '--loglevel=info',
    ])

