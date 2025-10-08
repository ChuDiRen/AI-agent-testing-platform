# Copyright (c) 2025 左岚. All rights reserved.
"""
执行API路由
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import APIResponse

from ..services.case_service import CaseService
from ..services.execution_service import ExecutionService
from ..models.execution import ApiEngineExecution
from ..schemas.case import CaseExecuteRequest
from ..schemas.execution import ExecutionStatusResponse, ExecutionResponse, ExecutionListResponse
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


@router.get("", response_model=APIResponse[ExecutionListResponse])
async def get_executions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    case_id: Optional[int] = Query(None, description="用例ID"),
    status: Optional[str] = Query(None, description="执行状态"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行历史列表"""
    execution_service = ExecutionService(db)
    executions, total = await execution_service.get_executions(
        page=page,
        page_size=page_size,
        case_id=case_id,
        status=status
    )

    # 转换为响应格式
    items = [ExecutionResponse.model_validate(execution) for execution in executions]

    return APIResponse(
        success=True,
        data=ExecutionListResponse(total=total, items=items)
    )


@router.get("/{execution_id}", response_model=APIResponse[ExecutionResponse])
async def get_execution_detail(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取执行记录详情"""
    execution_service = ExecutionService(db)
    execution = await execution_service.get_execution(execution_id)

    if not execution:
        return APIResponse(success=False, message="执行记录不存在")

    return APIResponse(
        success=True,
        data=ExecutionResponse.model_validate(execution)
    )


@router.delete("/{execution_id}", response_model=APIResponse[dict])
async def delete_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除执行记录"""
    execution_service = ExecutionService(db)

    # 检查执行记录是否存在
    execution = await execution_service.get_execution(execution_id)
    if not execution:
        return APIResponse(success=False, message="执行记录不存在")

    # 删除
    success = await execution_service.delete_execution(execution_id)

    if success:
        return APIResponse(success=True, message="删除成功")
    else:
        return APIResponse(success=False, message="删除失败")


@router.get("/task/{task_id}/status", response_model=APIResponse[ExecutionStatusResponse])
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

