# Copyright (c) 2025 左岚. All rights reserved.
"""
执行记录服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, desc
from typing import List, Tuple, Optional

from ..models.execution import ApiEngineExecution
from ..models.case import ApiEngineCase


class ExecutionService:
    """执行记录服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_execution(self, execution_id: int) -> Optional[ApiEngineExecution]:
        """获取执行记录详情"""
        result = await self.db.execute(
            select(ApiEngineExecution).where(ApiEngineExecution.execution_id == execution_id)
        )
        return result.scalar_one_or_none()
    
    async def get_execution_by_task_id(self, task_id: str) -> Optional[ApiEngineExecution]:
        """根据任务ID获取执行记录"""
        result = await self.db.execute(
            select(ApiEngineExecution).where(ApiEngineExecution.task_id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def get_executions(
        self,
        page: int = 1,
        page_size: int = 20,
        case_id: Optional[int] = None,
        status: Optional[str] = None,
        executed_by: Optional[int] = None
    ) -> Tuple[List[ApiEngineExecution], int]:
        """获取执行记录列表"""
        # 构建查询
        query = select(ApiEngineExecution)
        
        # 筛选条件
        if case_id:
            query = query.where(ApiEngineExecution.case_id == case_id)
        if status:
            query = query.where(ApiEngineExecution.status == status)
        if executed_by:
            query = query.where(ApiEngineExecution.executed_by == executed_by)
        
        # 按执行时间倒序排列
        query = query.order_by(desc(ApiEngineExecution.executed_at))
        
        # 获取总数
        count_query = select(func.count()).select_from(ApiEngineExecution)
        if case_id:
            count_query = count_query.where(ApiEngineExecution.case_id == case_id)
        if status:
            count_query = count_query.where(ApiEngineExecution.status == status)
        if executed_by:
            count_query = count_query.where(ApiEngineExecution.executed_by == executed_by)
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # 分页
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        # 执行查询
        result = await self.db.execute(query)
        executions = result.scalars().all()
        
        return list(executions), total
    
    async def delete_execution(self, execution_id: int) -> bool:
        """删除执行记录"""
        result = await self.db.execute(
            delete(ApiEngineExecution).where(ApiEngineExecution.execution_id == execution_id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def delete_executions_by_case(self, case_id: int) -> int:
        """删除指定用例的所有执行记录"""
        result = await self.db.execute(
            delete(ApiEngineExecution).where(ApiEngineExecution.case_id == case_id)
        )
        await self.db.commit()
        return result.rowcount
    
    async def update_execution_status(
        self,
        execution_id: int,
        status: str,
        result: Optional[dict] = None,
        logs: Optional[str] = None,
        error_message: Optional[str] = None,
        duration: Optional[float] = None,
        steps_total: Optional[int] = None,
        steps_passed: Optional[int] = None,
        steps_failed: Optional[int] = None
    ) -> Optional[ApiEngineExecution]:
        """更新执行记录状态"""
        execution = await self.get_execution(execution_id)
        if not execution:
            return None
        
        execution.status = status
        if result is not None:
            execution.result = result
        if logs is not None:
            execution.logs = logs
        if error_message is not None:
            execution.error_message = error_message
        if duration is not None:
            execution.duration = duration
        if steps_total is not None:
            execution.steps_total = steps_total
        if steps_passed is not None:
            execution.steps_passed = steps_passed
        if steps_failed is not None:
            execution.steps_failed = steps_failed
        
        # 如果状态为完成状态，更新完成时间
        if status in ['success', 'failed', 'error']:
            from datetime import datetime
            execution.finished_at = datetime.now()
        
        await self.db.commit()
        await self.db.refresh(execution)
        return execution

