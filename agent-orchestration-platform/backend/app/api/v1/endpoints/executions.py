"""
Execution API 端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import execution_crud
from app.schemas import ExecutionCreate, ExecutionUpdate, ExecutionResponse
from app.core.resp_model import RespModel


router = APIRouter(prefix="/Execution", tags=["Execution 管理"])


@router.post("/", response_model=RespModel)
async def create_execution(
    execution_in: ExecutionCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建 Execution"""
    try:
        execution = await execution_crud.execution.create(db, obj_in=execution_in)
        
        # 简化返回，避免序列化问题
        return RespModel.ok_resp(data={
            "id": execution.id,
            "workflow_id": execution.workflow_id,
            "agent_id": execution.agent_id,
            "status": execution.status,
            "input_data": execution.input_data,
            "started_at": execution.started_at.isoformat() if execution.started_at else None
        }, msg="Execution 创建成功")
    except Exception as e:
        print(f"Error in create_execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建Execution失败: {str(e)}"
        )


@router.get("/{execution_id}", response_model=RespModel)
async def get_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取 Execution"""
    try:
        execution = await execution_crud.execution.get(db, id=execution_id)
        if not execution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Execution ID {execution_id} 不存在"
            )
        
        # 简化返回，避免序列化问题
        return RespModel.ok_resp(data={
            "id": execution.id,
            "workflow_id": execution.workflow_id,
            "agent_id": execution.agent_id,
            "status": execution.status,
            "input_data": execution.input_data,
            "output_data": execution.output_data,
            "error_message": execution.error_message,
            "started_at": execution.started_at.isoformat() if execution.started_at else None,
            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
        })
    except Exception as e:
        print(f"Error in get_execution: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取Execution失败: {str(e)}"
        )


@router.get("/", response_model=RespModel)
async def list_executions(
    skip: int = 0,
    limit: int = 10,
    workflow_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取 Execution 列表"""
    try:
        if status:
            executions = await execution_crud.execution.get_by_status(
                db, status=status, skip=skip, limit=limit
            )
        elif workflow_id:
            executions = await execution_crud.execution.get_by_workflow(
                db, workflow_id=workflow_id, skip=skip, limit=limit
            )
        else:
            executions = await execution_crud.execution.get_multi(db, skip=skip, limit=limit)

        # 简化数据，避免序列化问题
        simplified_executions = []
        for execution in executions:
            simplified_executions.append({
                "id": execution.id,
                "workflow_id": execution.workflow_id,
                "agent_id": execution.agent_id,
                "status": execution.status,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None
            })

        total = len(simplified_executions)

        return RespModel.ok_resp_list(data=simplified_executions, total=total)
    except Exception as e:
        print(f"Error in list_executions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取Execution列表失败: {str(e)}"
        )


@router.put("/{execution_id}", response_model=RespModel)
async def update_execution(
    execution_id: int,
    execution_in: ExecutionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新 Execution"""
    db_execution = await execution_crud.execution.get(db, id=execution_id)
    if not db_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution ID {execution_id} 不存在"
        )

    execution = await execution_crud.execution.update(
        db, db_obj=db_execution, obj_in=execution_in
    )
    return RespModel.ok_resp(data=execution, msg="Execution 更新成功")


@router.post("/{execution_id}/cancel", response_model=RespModel)
async def cancel_execution(
    execution_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取消 Execution"""
    db_execution = await execution_crud.execution.get(db, id=execution_id)
    if not db_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution ID {execution_id} 不存在"
        )

    execution = await execution_crud.execution.update(
        db, db_obj=db_execution, obj_in={"status": "cancelled"}
    )
    return RespModel.ok_resp(data=execution, msg="Execution 已取消")
