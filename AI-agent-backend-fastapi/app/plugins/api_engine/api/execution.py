# Copyright (c) 2025 左岚. All rights reserved.
"""
执行API路由
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse

from ..services.case_service import CaseService
from ..models.execution import ApiEngineExecution
from ..schemas.case import CaseExecuteRequest
from ..schemas.execution import ExecutionStatusResponse
from ..tasks.execution import execute_case_task

router = APIRouter()


@router.post("/{case_id}/execute", response_model=APIResponse[dict])
async def execute_case(
    case_id: int,
    execute_data: CaseExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """执行测试用例"""
    # 检查用例是否存在
    case_service = CaseService(db)
    case = await case_service.get_case(case_id)
    
    if not case:
        return APIResponse(success=False, message="用例不存在")
    
    # 创建执行记录
    execution = ApiEngineExecution(
        case_id=case_id,
        task_id="",  # 待Celery任务创建后更新
        status="pending",
        executed_by=current_user.user_id
    )
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    
    # 提交Celery任务
    task = execute_case_task.apply_async(
        args=[
            case_id,
            execute_data.context or {},
            execution.execution_id,
            current_user.user_id
        ]
    )
    
    # 更新task_id
    execution.task_id = task.id
    await db.commit()
    
    return APIResponse(
        success=True,
        message="用例已提交执行",
        data={
            "execution_id": execution.execution_id,
            "task_id": task.id
        }
    )


@router.get("/{task_id}/status", response_model=APIResponse[ExecutionStatusResponse])
async def get_execution_status(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """查询执行状态"""
    from celery.result import AsyncResult
    
    task_result = AsyncResult(task_id)
    
    response_data = ExecutionStatusResponse(
        task_id=task_id,
        status=task_result.state,
        progress=None,
        current_step=None,
        message=None,
        result=None
    )
    
    if task_result.state == 'PENDING':
        response_data.message = "任务等待中"
    elif task_result.state == 'RUNNING':
        if task_result.info:
            response_data.progress = task_result.info.get('progress')
            response_data.message = task_result.info.get('message')
    elif task_result.state == 'SUCCESS':
        response_data.progress = 100
        response_data.message = "执行成功"
        response_data.result = task_result.result
    elif task_result.state == 'FAILURE':
        response_data.message = f"执行失败: {str(task_result.info)}"
    
    return APIResponse(success=True, data=response_data)

