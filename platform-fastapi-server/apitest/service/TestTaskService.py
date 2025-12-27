"""
测试任务Service - 已重构为静态方法模式
提供测试任务的CRUD、调度、执行等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlmodel import Session, select

from apitest.model.TestTaskModel import TestTask
from apitest.schemas.TestTaskSchema import TestTaskQuery, TestTaskCreate, TestTaskUpdate


class TestTaskService:
    """测试任务服务类 - 使用静态方法模式"""

    @staticmethod
    def query_by_page(session: Session, query: TestTaskQuery) -> Tuple[List[TestTask], int]:
        """分页查询测试任务"""
        offset = (query.page - 1) * query.pageSize
        statement = select(TestTask)

        # 应用过滤条件
        if query.project_id:
            statement = statement.where(TestTask.project_id == query.project_id)
        if hasattr(query, 'task_name') and query.task_name:
            statement = statement.where(TestTask.task_name.contains(query.task_name))
        if hasattr(query, 'task_status') and query.task_status:
            statement = statement.where(TestTask.task_status == query.task_status)

        # 排序
        statement = statement.order_by(TestTask.create_time.desc(), TestTask.id.desc())
        statement = statement.limit(query.pageSize).offset(offset)
        datas = session.exec(statement).all()

        # 统计总数
        count_statement = select(TestTask)
        if query.project_id:
            count_statement = count_statement.where(TestTask.project_id == query.project_id)
        if hasattr(query, 'task_name') and query.task_name:
            count_statement = count_statement.where(TestTask.task_name.contains(query.task_name))
        if hasattr(query, 'task_status') and query.task_status:
            count_statement = count_statement.where(TestTask.task_status == query.task_status)
        total = len(session.exec(count_statement).all())

        return list(datas), total

    @staticmethod
    def query_by_id(session: Session, id: int) -> Optional[TestTask]:
        """根据ID查询测试任务"""
        return session.get(TestTask, id)

    @staticmethod
    def create(session: Session, task_data: TestTaskCreate) -> TestTask:
        """创建测试任务"""
        data = TestTask(
            **task_data.model_dump(),
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        session.add(data)
        session.commit()
        session.refresh(data)
        return data

    @staticmethod
    def update(session: Session, task_data: TestTaskUpdate) -> Optional[TestTask]:
        """更新测试任务"""
        statement = select(TestTask).where(TestTask.id == task_data.id)
        db_task = session.exec(statement).first()
        if not db_task:
            return None

        update_data = task_data.model_dump(exclude_unset=True, exclude={'id'})
        for key, value in update_data.items():
            setattr(db_task, key, value)
        db_task.update_time = datetime.now()

        session.commit()
        return db_task

    @staticmethod
    def delete(session: Session, id: int) -> bool:
        """删除测试任务"""
        task = session.get(TestTask, id)
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True

    @staticmethod
    def query_by_project(session: Session, project_id: int) -> List[TestTask]:
        """查询项目的所有测试任务"""
        statement = select(TestTask).where(
            TestTask.project_id == project_id
        ).order_by(TestTask.create_time.desc(), TestTask.id.desc())

        return list(session.exec(statement).all())

    @staticmethod
    def get_by_status(session: Session, task_status: str, project_id: Optional[int] = None) -> List[TestTask]:
        """根据状态获取测试任务"""
        statement = select(TestTask).where(TestTask.task_status == task_status)

        if project_id:
            statement = statement.where(TestTask.project_id == project_id)

        statement = statement.order_by(TestTask.create_time.desc())

        return list(session.exec(statement).all())

    @staticmethod
    def update_status(session: Session, id: int, new_status: str) -> bool:
        """更新任务状态"""
        task = session.get(TestTask, id)
        if not task:
            return False

        task.task_status = new_status
        task.update_time = datetime.now()

        session.commit()
        return True

    @staticmethod
    def get_pending_tasks(session: Session, project_id: Optional[int] = None) -> List[TestTask]:
        """获取待执行的测试任务"""
        statement = select(TestTask).where(TestTask.task_status == 'pending')

        if project_id:
            statement = statement.where(TestTask.project_id == project_id)

        statement = statement.order_by(TestTask.create_time.asc())

        return list(session.exec(statement).all())

    @staticmethod
    def get_running_tasks(session: Session, project_id: Optional[int] = None) -> List[TestTask]:
        """获取运行中的测试任务"""
        statement = select(TestTask).where(TestTask.task_status == 'running')

        if project_id:
            statement = statement.where(TestTask.project_id == project_id)

        statement = statement.order_by(TestTask.create_time.desc())

        return list(session.exec(statement).all())
