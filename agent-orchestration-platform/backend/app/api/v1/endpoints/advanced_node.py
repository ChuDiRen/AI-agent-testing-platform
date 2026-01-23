"""
高级节点 API 端点（循环、条件、子图）
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.batch_schema import LoopNodeSchema, SubgraphNodeSchema, ConditionNodeSchema
from app.core.resp_model import RespModel


router = APIRouter(prefix="/AdvancedNode", tags=["高级节点"])


@router.post("/node/loop", response_model=RespModel)
async def create_loop_node(
    node_data: LoopNodeSchema,
    db: AsyncSession = Depends(get_db)
):
    """创建循环节点"""
    # TODO: 保存到高级节点表
    return RespModel.ok_resp(data=node_data, msg="循环节点创建成功")


@router.post("/node/condition", response_model=RespModel)
async def create_condition_node(
    node_data: ConditionNodeSchema,
    db: AsyncSession = Depends(get_db)
):
    """创建条件节点"""
    # TODO: 保存到高级节点表
    return RespModel.ok_resp(data=node_data, msg="条件节点创建成功")


@router.post("/node/subgraph", response_model=RespModel)
async def create_subgraph_node(
    node_data: SubgraphNodeSchema,
    db: AsyncSession = Depends(get_db)
):
    """创建子图节点"""
    # TODO: 保存到高级节点表
    return RespModel.ok_resp(data=node_data, msg="子图节点创建成功")


@router.get("/node/types", response_model=RespModel)
async def get_node_types(
    db: AsyncSession = Depends(get_db)
):
    """获取节点类型列表"""
    # TODO: 从高级节点表查询
    types = [
        {"type": "loop", "label": "循环节点", "color": "#E6A23C"},
        {"type": "condition", "label": "条件节点", "color": "#909399"},
        {"type": "subgraph", "label": "子图节点", "color": "#F4F4F5"}
    ]

    return RespModel.ok_resp(data=types, msg="获取节点类型成功")


# 导出高级节点 Schema
@router.get("/node/schema", response_model=RespModel)
async def get_node_schema(
    db: AsyncSession = Depends(get_db)
):
    """获取高级节点 Schema"""
    schema = {
        "AdvancedNode": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "type": {"type": "string", "enum": ["loop", "condition", "subgraph"]},
                "label": {"type": "string"},
                "config": {"type": "object"},
                "node_id": {"type": "integer", "nullable": true},
                "sub_workflow_id": {"type": "integer", "nullable": true}
            }
        }
    }

    return RespModel.ok_resp(data=schema)
