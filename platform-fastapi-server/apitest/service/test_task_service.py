"""
测试任务Service
提供测试任务的CRUD、调度、执行等功能
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, and_, or_

from apitest.model.TestTaskModel import TestTask


class TestTaskService:
    def __init__(self, session: Session):
        self.session = session
    
    def query_by_page(self, page: int, page_size: int, project_id: Optional[int] = None,
                     task_name: Optional[str] = None, task_status: Optional[str] = None) -> tuple[List[TestTask], int]:
        """分页查询测试任务"""
        statement = select(TestTask)
        
        # 条件筛选
        if project_id:
            statement = statement.where(TestTask.project_id == project_id)
        if task_name:
            statement = statement.where(TestTask.task_name.contains(task_name))
        if task_status:
            statement = statement.where(TestTask.task_status == task_status)
        
        # 排序
        statement = statement.order_by(TestTask.create_time.desc(), TestTask.id.desc())
        
        # 查询总数
        total_statement = select(TestTask)
        if project_id:
            total_statement = total_statement.where(TestTask.project_id == project_id)
        if task_name:
            total_statement = total_statement.where(TestTask.task_name.contains(task_name))
        if task_status:
            total_statement = total_statement.where(TestTask.task_status == task_status)
        
        total = len(self.session.exec(total_statement).all())
        
        # 分页查询
        offset = (page - 1) * page_size
        datas = self.session.exec(statement.limit(page_size).offset(offset)).all()
        
        return datas, total
    
    def get_by_id(self, id: int) -> Optional[TestTask]:
        """根据ID查询测试任务"""
        return self.session.get(TestTask, id)
    
    def create(self, **kwargs) -> TestTask:
        """创建测试任务"""
        data = TestTask(
            **kwargs,
            create_time=datetime.now(),
            update_time=datetime.now()
        )
        self.session.add(data)
        self.session.commit()
        self.session.refresh(data)
        return data
    
    def update(self, id: int, update_data: Dict[str, Any]) -> bool:
        """更新测试任务"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        for key, value in update_data.items():
            if value is not None:
                setattr(data, key, value)
        data.update_time = datetime.now()
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def delete(self, id: int) -> bool:
        """删除测试任务"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        self.session.delete(data)
        self.session.commit()
        return True
    
    def query_by_project(self, project_id: int) -> List[TestTask]:
        """查询项目的所有测试任务"""
        statement = select(TestTask).where(
            TestTask.project_id == project_id
        ).order_by(TestTask.create_time.desc(), TestTask.id.desc())
        
        return self.session.exec(statement).all()
    
    def get_by_status(self, task_status: str, project_id: Optional[int] = None) -> List[TestTask]:
        """根据状态获取测试任务"""
        statement = select(TestTask).where(TestTask.task_status == task_status)
        
        if project_id:
            statement = statement.where(TestTask.project_id == project_id)
        
        statement = statement.order_by(TestTask.create_time.desc())
        
        return self.session.exec(statement).all()
    
    def update_status(self, id: int, new_status: str) -> bool:
        """更新任务状态"""
        data = self.get_by_id(id)
        if not data:
            return False
        
        data.task_status = new_status
        data.update_time = datetime.now()
        
        self.session.add(data)
        self.session.commit()
        return True
    
    def get_pending_tasks(self, project_id: Optional[int] = None) -> List[TestTask]:
        """获取待执行的测试任务"""
        statement = select(TestTask).where(TestTask.task_status == 'pending')
        
        if project_id:
            statement = statement.where(TestTask.project_id == project_id)
        
        statement = statement.order_by(TestTask.create_time.asc())
        
        return self.session.exec(statement).all()
    
    def get_running_tasks(self, project_id: Optional[int] = None) -> List[TestTask]:
        """获取运行中的测试任务"""
        statement = select(TestTask).where(TestTask.task_status == 'running')
        
        if project_id:
            statement = statement.where(TestTask.project_id == project_id)
        
        statement = statement.order_by(TestTask.create_time.desc())
        
        return self.session.exec(statement).all()
