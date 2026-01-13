"""
API 集合详情端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.api_collection_detail import ApiCollectionDetail
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func

router = APIRouter(prefix="/ApiCollectionDetail", tags=["API集合详情"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有集合详情"""
    try:
        result = await db.execute(select(ApiCollectionDetail))
        items = result.scalars().all()
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    collection_info_id: Optional[int] = Query(None, description='集合信息ID'),
    api_info_id: Optional[int] = Query(None, description='API信息ID'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询集合详情"""
    try:
        query = select(ApiCollectionDetail)
        
        # 添加筛选条件
        if collection_info_id:
            query = query.where(ApiCollectionDetail.collection_info_id == collection_info_id)
        
        if api_info_id:
            query = query.where(ApiCollectionDetail.api_info_id == api_info_id)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()
        
        return respModel().ok_resp_list(lst=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=respModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='集合详情ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询集合详情"""
    try:
        result = await db.execute(select(ApiCollectionDetail).where(ApiCollectionDetail.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("集合详情不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    collection_detail_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建集合详情"""
    try:
        collection_detail = ApiCollectionDetail(**collection_detail_data)
        db.add(collection_detail)
        await db.flush()
        await db.commit()
        return respModel().ok_resp(dic_t={"id": collection_detail.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='集合详情ID'),
    collection_detail_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新集合详情"""
    try:
        result = await db.execute(select(ApiCollectionDetail).where(ApiCollectionDetail.id == id))
        collection_detail = result.scalars().first()
        if not collection_detail:
            raise NotFoundException("集合详情不存在")
        
        # 更新字段
        for field, value in collection_detail_data.items():
            if hasattr(collection_detail, field):
                setattr(collection_detail, field, value)
        
        await db.commit()
        return respModel().ok_resp(msg="修改成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=respModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='集合详情ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除集合详情"""
    try:
        result = await db.execute(select(ApiCollectionDetail).where(ApiCollectionDetail.id == id))
        collection_detail = result.scalars().first()
        if not collection_detail:
            raise NotFoundException("集合详情不存在")
        
        await db.delete(collection_detail)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
