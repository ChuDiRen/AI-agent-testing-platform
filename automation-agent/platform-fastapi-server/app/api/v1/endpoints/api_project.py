"""
API 项目管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.services.api_project import api_project_crud
from app.schemas.api_project import ApiProjectCreate, ApiProjectUpdate, ApiProjectResponse
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/ApiProject", tags=["API项目管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有项目"""
    try:
        items = await api_project_crud.get_multi(db)
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_name: Optional[str] = Query(None, description='项目名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询项目"""
    try:
        items, total = await api_project_crud.get_multi_with_filters(
            db, 
            page=page, 
            page_size=page_size,
            project_name=project_name
        )
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='项目ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询项目"""
    try:
        item = await api_project_crud.get(db, id=id)
        if not item:
            raise NotFoundException("项目不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    project_data: ApiProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建项目"""
    try:
        item = await api_project_crud.create(db, obj_in=project_data)
        return respModel().ok_resp(dic_t={"id": item.id}, msg="添加成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='项目ID'),
    project_data: ApiProjectUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新项目"""
    try:
        item = await api_project_crud.get(db, id=id)
        if not item:
            raise NotFoundException("项目不存在")
        
        updated_item = await api_project_crud.update(db, db_obj=item, obj_in=project_data)
        return respModel().ok_resp(msg="修改成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=respModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='项目ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除项目"""
    try:
        item = await api_project_crud.get(db, id=id)
        if not item:
            raise NotFoundException("项目不存在")
        
        await api_project_crud.remove(db, id=id)
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
