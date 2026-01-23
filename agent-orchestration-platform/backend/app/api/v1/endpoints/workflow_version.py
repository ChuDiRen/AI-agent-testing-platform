"""
Workflow API 端点（包含版本历史）
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import workflow_version_crud
from app.schemas import WorkflowUpdate, WorkflowResponse
from app.core.resp_model import RespModel


router = APIRouter(prefix="/WorkflowVersion", tags=["Workflow 版本管理"])


@router.get("/workflow/{workflow_id}/versions", response_model=RespModel)
async def list_workflow_versions(
    workflow_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """获取 Workflow 版本历史"""
    versions = await workflow_version_crud.get_by_workflow(
        db, workflow_id=workflow_id, skip=skip, limit=limit
    )

    total = await workflow_version_crud.count_total_versions(db, workflow_id=workflow_id)

    return RespModel.ok_resp_list(data=versions, total=total)


@router.get("/workflow/{workflow_id}/latest", response_model=RespModel)
async def get_latest_version(
    workflow_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取 Workflow 最新版本"""
    version = await workflow_version_crud.get_latest_version(db, workflow_id=workflow_id)

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} 没有已发布的版本"
        )

    return RespModel.ok_resp(data=version)


@router.get("/version/{version_id}/rollback", response_model=RespModel)
async def rollback_workflow_version(
    version_id: int,
    db: AsyncSession = Depends(get_db)
):
    """回滚到指定版本"""
    # TODO: 实现版本回滚逻辑
    from app.crud import workflow_crud

    version = await workflow_crud.get(db, id=version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} 不存在"
        )

    # 获取当前 Workflow
    workflow = await workflow_crud.get(db, id=version.workflow_id)

    # 更新 graph_data 到指定版本的数据
    if workflow:
        # 需要反序列化 version.graph_data
        # await workflow_crud.update(db, db_obj=workflow, obj_in={"graph_data": version.graph_data})
        return RespModel.ok_resp(data=workflow, msg="回滚成功")

    return RespModel.ok_resp(msg="回滚成功")


@router.get("/versions/{version_id}", response_model=RespModel)
async def get_version_detail(
    version_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取版本详情"""
    from app.crud.workflow_version_crud import workflow_version as workflow_version_crud

    version = await workflow_version_crud.get(db, id=version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} 不存在"
        )

    return RespModel.ok_resp(data=version.to_dict(), msg="获取成功")
