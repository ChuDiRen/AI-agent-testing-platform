"""
API 关键字管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.crud.api_keyword import api_keyword_crud
from app.schemas.api_keyword import ApiKeyWordCreate, ApiKeyWordUpdate, ApiKeyWordResponse
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/ApiKeyWord", tags=["API关键字管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有关键字"""
    try:
        items = await api_keyword_crud.get_multi(db)
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    name: Optional[str] = Query(None, description='关键字名称'),
    operation_type_id: Optional[int] = Query(None, description='操作类型ID'),
    page_id: Optional[int] = Query(None, description='页面ID'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询关键字"""
    try:
        items, total = await api_keyword_crud.get_multi_with_filters(
            db, 
            page=page, 
            page_size=page_size,
            name=name,
            operation_type_id=operation_type_id,
            page_id=page_id
        )
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='关键字ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询关键字"""
    try:
        item = await api_keyword_crud.get(db, id=id)
        if not item:
            raise NotFoundException("关键字不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    keyword_data: ApiKeyWordCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建关键字"""
    try:
        item = await api_keyword_crud.create(db, obj_in=keyword_data)
        return respModel().ok_resp(dic_t={"id": item.id}, msg="添加成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='关键字ID'),
    keyword_data: ApiKeyWordUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新关键字"""
    try:
        item = await api_keyword_crud.get(db, id=id)
        if not item:
            raise NotFoundException("关键字不存在")
        
        updated_item = await api_keyword_crud.update(db, db_obj=item, obj_in=keyword_data)
        return respModel().ok_resp(msg="修改成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=respModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='关键字ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除关键字"""
    try:
        item = await api_keyword_crud.get(db, id=id)
        if not item:
            raise NotFoundException("关键字不存在")
        
        await api_keyword_crud.remove(db, id=id)
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
