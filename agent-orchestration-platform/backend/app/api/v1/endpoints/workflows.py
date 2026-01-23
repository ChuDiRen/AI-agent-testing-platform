"""
Workflow API 端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import workflow_crud
from app.schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from app.core.resp_model import RespModel


router = APIRouter(prefix="/Workflow", tags=["Workflow 管理"])


@router.post("/", response_model=RespModel)
async def create_workflow(
    workflow_in: WorkflowCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建 Workflow"""
    workflow = await workflow_crud.workflow.create(db, obj_in=workflow_in)
    # 转换为响应模型
    workflow_response = WorkflowResponse.model_validate(workflow)
    return RespModel.ok_resp(data=workflow_response, msg="Workflow 创建成功")


@router.get("/{workflow_id}", response_model=RespModel)
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取 Workflow"""
    workflow = await workflow_crud.workflow.get(db, id=workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow ID {workflow_id} 不存在"
        )
    # 转换为响应模型
    workflow_response = WorkflowResponse.model_validate(workflow)
    return RespModel.ok_resp(data=workflow_response)


@router.get("/", response_model=RespModel)
async def list_workflows(
    skip: int = 0,
    limit: int = 10,
    is_published: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取 Workflow 列表"""
    if is_published:
        workflows = await workflow_crud.workflow.get_published(db, skip=skip, limit=limit)
    else:
        workflows = await workflow_crud.workflow.get_multi(db, skip=skip, limit=limit)

    total = await workflow_crud.workflow.count(db)

    # 转换为响应模型列表
    workflow_responses = [WorkflowResponse.model_validate(workflow) for workflow in workflows]
    return RespModel.ok_resp_list(data=workflow_responses, total=total)


@router.put("/{workflow_id}", response_model=RespModel)
async def update_workflow(
    workflow_id: int,
    workflow_in: WorkflowUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新 Workflow"""
    db_workflow = await workflow_crud.workflow.get(db, id=workflow_id)
    if not db_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow ID {workflow_id} 不存在"
        )

    workflow = await workflow_crud.workflow.update(db, db_obj=db_workflow, obj_in=workflow_in)
    return RespModel.ok_resp(data=workflow, msg="Workflow 更新成功")


@router.delete("/{workflow_id}", response_model=RespModel)
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除 Workflow"""
    db_workflow = await workflow_crud.workflow.get(db, id=workflow_id)
    if not db_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow ID {workflow_id} 不存在"
        )

    await workflow_crud.workflow.remove(db, id=workflow_id)
    return RespModel.ok_resp(msg="Workflow 删除成功")


@router.post("/{workflow_id}/publish", response_model=RespModel)
async def publish_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db)
):
    """发布 Workflow"""
    db_workflow = await workflow_crud.workflow.get(db, id=workflow_id)
    if not db_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow ID {workflow_id} 不存在"
        )

    workflow = await workflow_crud.workflow.update(
        db, db_obj=db_workflow, obj_in={"is_published": True}
    )
    return RespModel.ok_resp(data=workflow, msg="Workflow 发布成功")
