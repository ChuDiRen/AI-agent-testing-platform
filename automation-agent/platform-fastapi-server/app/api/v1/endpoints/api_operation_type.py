"""
API 操作类型管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.services.api_operation_type import api_operation_type_crud
from app.schemas.api_operation_type import ApiOperationTypeCreate, ApiOperationTypeUpdate, ApiOperationTypeResponse
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/ApiOperationType", tags=["API操作类型管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有操作类型"""
    try:
        items = await api_operation_type_crud.get_multi(db)
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    operation_type_name: Optional[str] = Query(None, description='操作类型名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询操作类型"""
    try:
        items, total = await api_operation_type_crud.get_multi_with_filters(
            db, 
            page=page, 
            page_size=page_size,
            operation_type_name=operation_type_name
        )
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='操作类型ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询操作类型"""
    try:
        item = await api_operation_type_crud.get(db, id=id)
        if not item:
            raise NotFoundException("操作类型不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    operation_type_data: ApiOperationTypeCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建操作类型"""
    try:
        item = await api_operation_type_crud.create(db, obj_in=operation_type_data)
        return respModel().ok_resp(dic_t={"id": item.id}, msg="添加成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='操作类型ID'),
    operation_type_data: ApiOperationTypeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新操作类型"""
    try:
        item = await api_operation_type_crud.get(db, id=id)
        if not item:
            raise NotFoundException("操作类型不存在")
        
        updated_item = await api_operation_type_crud.update(db, db_obj=item, obj_in=operation_type_data)
        return respModel().ok_resp(msg="修改成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=respModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='操作类型ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除操作类型"""
    try:
        item = await api_operation_type_crud.get(db, id=id)
        if not item:
            raise NotFoundException("操作类型不存在")
        
        await api_operation_type_crud.remove(db, id=id)
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
