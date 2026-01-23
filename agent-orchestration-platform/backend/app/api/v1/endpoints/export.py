"""
导入导出 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import workflow_crud
from app.schemas.batch_schema import ImportWorkflowRequest, ExportWorkflowsRequest
from app.core.resp_model import RespModel


router = APIRouter(prefix="/Export", tags=["导入导出"])


@router.post("/workflows", response_model=RespModel)
async def import_workflows(
    request: ImportWorkflowRequest,
    db: AsyncSession = Depends(get_db)
):
    """导入 Workflows（从 JSON）"""
    import json

    try:
        count = 0
        for workflow_data in request.data:
            workflow = await workflow_crud.create(
                db,
                obj_in={
                    "name": workflow_data.get("name"),
                    "description": workflow_data.get("description"),
                    "graph_data": json.dumps(workflow_data.get("graph_data")),
                    "created_by": 1
                }
            )
            count += 1

        return RespModel.ok_resp(msg=f"成功导入 {count} 个 Workflow")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )


@router.get("/workflows", response_model=RespModel)
async def export_workflows(
    format: str = "json",
    db: AsyncSession = Depends(get_db)
):
    """导出 Workflows（JSON、YAML）"""
    workflows = await workflow_crud.get_multi(db, skip=0, limit=1000)

    if format == "json":
        data = [wf.to_dict() for wf in workflows]
    elif format == "yaml":
        import yaml
        data = yaml.dump([wf.to_dict() for wf in workflows])
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的导出格式: {format}"
        )

    return RespModel.ok_resp(data=data)


@router.get("/workflows/schema", response_model=RespModel)
async def export_workflow_schema(
    db: AsyncSession = Depends(get_db)
):
    """导出 Workflow 结构 Schema"""
    schema = {
        "Workflow": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "graph_data": {"type": "object"},
                "is_published": {"type": "boolean"},
                "created_by": {"type": "integer"}
            }
        }
    }

    return RespModel.ok_resp(data=schema)
