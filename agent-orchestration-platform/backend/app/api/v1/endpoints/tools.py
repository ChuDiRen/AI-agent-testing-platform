"""
Tool API 端点
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud import tool_crud
from app.schemas import ToolCreate, ToolUpdate, ToolResponse
from app.core.resp_model import RespModel


router = APIRouter(prefix="/Tool", tags=["Tool 管理"])


@router.post("/", response_model=RespModel)
async def create_tool(
    tool_in: ToolCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建 Tool"""
    tool = await tool_crud.tool.create(db, obj_in=tool_in)
    # 转换为响应模型
    tool_response = ToolResponse.model_validate(tool)
    return RespModel.ok_resp(data=tool_response, msg="Tool 创建成功")


@router.get("/{tool_id}", response_model=RespModel)
async def get_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db)
):
    """根据 ID 获取 Tool"""
    tool = await tool_crud.tool.get(db, id=tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool ID {tool_id} 不存在"
        )
    # 转换为响应模型
    tool_response = ToolResponse.model_validate(tool)
    return RespModel.ok_resp(data=tool_response)


@router.get("/", response_model=RespModel)
async def list_tools(
    skip: int = 0,
    limit: int = 10,
    tool_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取 Tool 列表"""
    if tool_type:
        tools = await tool_crud.tool.get_by_type(db, tool_type=tool_type, skip=skip, limit=limit)
    else:
        tools = await tool_crud.tool.get_multi(db, skip=skip, limit=limit)

    total = await tool_crud.tool.count(db)

    # 转换为响应模型列表
    tool_responses = [ToolResponse.model_validate(tool) for tool in tools]
    return RespModel.ok_resp_list(data=tool_responses, total=total)


@router.put("/{tool_id}", response_model=RespModel)
async def update_tool(
    tool_id: int,
    tool_in: ToolUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新 Tool"""
    db_tool = await tool_crud.tool.get(db, id=tool_id)
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool ID {tool_id} 不存在"
        )

    tool = await tool_crud.tool.update(db, db_obj=db_tool, obj_in=tool_in)
    return RespModel.ok_resp(data=tool, msg="Tool 更新成功")


@router.delete("/{tool_id}", response_model=RespModel)
async def delete_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除 Tool"""
    db_tool = await tool_crud.tool.get(db, id=tool_id)
    if not db_tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool ID {tool_id} 不存在"
        )

    await tool_crud.tool.remove(db, id=tool_id)
    return RespModel.ok_resp(msg="Tool 删除成功")


@router.post("/{tool_id}/test", response_model=RespModel)
async def test_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db)
):
    """测试 Tool 连接"""
    tool = await tool_crud.tool.get(db, id=tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tool ID {tool_id} 不存在"
        )

    # TODO: 实现实际的连接测试逻辑
    test_status = "passed"
    error_message = None

    return RespModel.ok_resp(
        data={"tool_id": tool_id, "test_status": test_status, "error_message": error_message},
        msg="Tool 测试完成"
    )
