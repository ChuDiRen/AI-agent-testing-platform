"""
批量操作 API 端点（批量删除、批量发布）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import workflow_crud
from app.crud import agent_crud
from app.core.resp_model import RespModel


router = APIRouter(prefix="/Batch", tags=["批量操作"])


@router.post("/delete/workflows", response_model=RespModel)
async def batch_delete_workflows(
    ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """批量删除 Workflows"""
    try:
        for workflow_id in ids:
            await workflow_crud.remove(db, id=workflow_id)
        return RespModel.ok_resp(msg=f"成功删除 {len(ids)} 个 Workflow")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除失败: {str(e)}"
        )


@router.post("/publish/workflows", response_model=RespModel)
async def batch_publish_workflows(
    ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """批量发布 Workflows"""
    try:
        for workflow_id in ids:
            await workflow_crud.update(
                db, db_obj=await workflow_crud.get(db, id=workflow_id),
                obj_in={"is_published": True}
            )
        return RespModel.ok_resp(msg=f"成功发布 {len(ids)} 个 Workflow")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量发布失败: {str(e)}"
        )


@router.post("/delete/agents", response_model=RespModel)
async def batch_delete_agents(
    ids: list[int],
    db: AsyncSession = Depends(get_db)
):
    """批量删除 Agents"""
    try:
        for agent_id in ids:
            await agent_crud.remove(db, id=agent_id)
        return RespModel.ok_resp(msg=f"成功删除 {len(ids)} 个 Agent")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除失败: {str(e)}"
        )
