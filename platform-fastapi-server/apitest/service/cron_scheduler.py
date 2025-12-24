"""
Cron 调度器服务
负责扫描 TestTask 表，根据 cron_expression 定时触发测试任务执行
"""
import logging
from typing import Optional
from datetime import datetime
from sqlmodel import Session, select
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

from core.database import get_session
from apitest.model.TestTaskModel import TestTask

logger = logging.getLogger(__name__)


class CronScheduler:
    """Cron 调度器单例"""
    _instance: Optional['CronScheduler'] = None
    _scheduler: Optional[BackgroundScheduler] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._scheduler is None:
            # 配置调度器
            executors = {
                'default': ThreadPoolExecutor(max_workers=5)
            }
            job_defaults = {
                'coalesce': True,  # 合并错过的任务
                'max_instances': 1,  # 同一任务最多1个实例运行
                'misfire_grace_time': 3600  # 错过执行时间的宽限期（秒）
            }
            self._scheduler = BackgroundScheduler(
                executors=executors,
                job_defaults=job_defaults,
                timezone='Asia/Shanghai'
            )

    def start(self):
        """启动调度器"""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Cron 调度器已启动")
            # 加载现有定时任务
            self.load_scheduled_tasks()

    def shutdown(self):
        """关闭调度器"""
        if self._scheduler and self._scheduler.running:
            self._scheduler.shutdown(wait=True)
            logger.info("Cron 调度器已关闭")

    def load_scheduled_tasks(self):
        """从数据库加载所有定时任务"""
        with next(get_session()) as session:
            tasks = session.exec(
                select(TestTask)
                .where(TestTask.task_type == 'scheduled')
                .where(TestTask.task_status != 'disabled')
                .where(TestTask.cron_expression != None)
            ).all()

            for task in tasks:
                self.add_task(task.id, task.cron_expression)

            logger.info(f"已加载 {len(tasks)} 个定时任务")

    def add_task(self, task_id: int, cron_expression: str):
        """添加定时任务到调度器"""
        try:
            job_id = f"test_task_{task_id}"

            # 如果任务已存在，先移除
            if self._scheduler.get_job(job_id):
                self._scheduler.remove_job(job_id)

            # 解析 cron 表达式并添加任务
            trigger = CronTrigger.from_crontab(cron_expression, timezone='Asia/Shanghai')

            self._scheduler.add_job(
                func=self._execute_task,
                trigger=trigger,
                id=job_id,
                args=[task_id],
                name=f"测试任务_{task_id}",
                replace_existing=True
            )

            # 获取下次执行时间
            job = self._scheduler.get_job(job_id)
            next_run_time = job.next_run_time if job else None

            # 更新数据库中的下次执行时间
            self._update_next_run_time(task_id, next_run_time)

            logger.info(f"任务 {task_id} 已添加到调度器，cron: {cron_expression}, 下次执行: {next_run_time}")

        except Exception as e:
            logger.error(f"添加任务 {task_id} 失败: {e}")

    def remove_task(self, task_id: int):
        """从调度器移除任务"""
        job_id = f"test_task_{task_id}"
        if self._scheduler.get_job(job_id):
            self._scheduler.remove_job(job_id)
            logger.info(f"任务 {task_id} 已从调度器移除")

    def _execute_task(self, task_id: int):
        """执行测试任务（由调度器调用）"""
        from apitest.schemas.test_task_schema import TestTaskExecuteRequest
        import asyncio

        logger.info(f"开始执行定时任务 {task_id}")

        try:
            # 创建执行请求
            request = TestTaskExecuteRequest(
                task_id=task_id,
                trigger_type='scheduled'
            )

            # 在异步上下文中执行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # 获取数据库会话并执行
            session = next(get_session())
            from apitest.api.TestTaskController import execute

            # 调用执行接口
            result = loop.run_until_complete(execute(request, session=session))

            loop.close()

            if result.get('code') == 200:
                logger.info(f"定时任务 {task_id} 执行成功")
            else:
                logger.error(f"定时任务 {task_id} 执行失败: {result.get('message')}")

        except Exception as e:
            logger.error(f"定时任务 {task_id} 执行异常: {e}", exc_info=True)

    def _update_next_run_time(self, task_id: int, next_run_time: Optional[datetime]):
        """更新数据库中的下次执行时间"""
        try:
            with next(get_session()) as session:
                task = session.get(TestTask, task_id)
                if task:
                    task.next_run_time = next_run_time
                    session.commit()
        except Exception as e:
            logger.error(f"更新任务 {task_id} 下次执行时间失败: {e}")


# 创建全局调度器实例
cron_scheduler = CronScheduler()
