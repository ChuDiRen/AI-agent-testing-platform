# Copyright (c) 2025 左岚. All rights reserved.
"""Celery应用配置"""
from celery import Celery
from app.core.config import settings

# 创建Celery应用
celery_app = Celery(
    "ai_agent_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.document_tasks"]  # 导入任务模块
)

# Celery配置
celery_app.conf.update(
    task_serializer="json",  # 任务序列化格式
    accept_content=["json"],  # 接受的内容类型
    result_serializer="json",  # 结果序列化格式
    timezone="Asia/Shanghai",  # 时区
    enable_utc=True,  # 启用UTC
    task_track_started=True,  # 跟踪任务开始状态
    task_time_limit=3600,  # 任务超时时间(1小时)
    task_soft_time_limit=3000,  # 任务软超时(50分钟)
    worker_prefetch_multiplier=1,  # 每个worker预取任务数
    worker_max_tasks_per_child=1000,  # 每个worker最多执行任务数
    task_acks_late=True,  # 任务完成后才确认
    task_reject_on_worker_lost=True,  # worker丢失时拒绝任务
    result_expires=3600,  # 结果过期时间(1小时)
)

# 任务路由配置
celery_app.conf.task_routes = {
    "app.tasks.document_tasks.*": {"queue": "document_processing"},  # 文档处理队列
}

# 定时任务配置(可选)
celery_app.conf.beat_schedule = {
    # 示例: 每天清理过期任务结果
    "cleanup-expired-results": {
        "task": "app.tasks.document_tasks.cleanup_expired_results",
        "schedule": 86400.0,  # 24小时
    },
}

