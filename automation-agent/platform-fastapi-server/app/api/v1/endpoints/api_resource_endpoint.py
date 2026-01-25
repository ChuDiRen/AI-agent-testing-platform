"""
API资源管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.api_resource import ApiResource
from app.core.resp_model import RespModel, ResponseModel
from app.core.exceptions import NotFoundException
from sqlalchemy import select, func
from app.services.api_resource import api_resource as api_crud

router = APIRouter(prefix="/api", tags=["API资源管理"])


@router.get("/queryAll", response_model=ResponseModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有API资源"""
    try:
        result = await db.execute(select(ApiResource))
        items = result.scalars().all()
        return RespModel.success(data=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=ResponseModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    pageSize: int = Query(10, ge=1, le=100, description='每页数量'),
    name: Optional[str] = None,
    path: Optional[str] = None,
    method: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """分页查询API资源"""
    try:
        query = select(ApiResource)
        
        # 添加筛选条件
        if name:
            query = query.where(ApiResource.name.like(f"%{name}%"))
        if path:
            query = query.where(ApiResource.path.like(f"%{path}%"))
        if method:
            query = query.where(ApiResource.method == method)
        
        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()
        
        # 分页查询
        skip = (page - 1) * pageSize
        query = query.offset(skip).limit(pageSize).order_by(ApiResource.id.desc())
        result = await db.execute(query)
        items = result.scalars().all()
        
        return RespModel.success(data=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=ResponseModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='API资源ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询API资源"""
    try:
        result = await db.execute(select(ApiResource).where(ApiResource.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("API资源不存在")
        return RespModel.success(data=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=ResponseModel)
async def insert(
    *,
    api_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建API资源"""
    try:
        # 创建新API资源
        api = ApiResource(
            name=api_data.get('name'),
            path=api_data.get('path'),
            method=api_data.get('method'),
            desc=api_data.get('desc')
        )
        
        db.add(api)
        await db.flush()  # 获取ID
        await db.commit()
        
        return RespModel.success(data={"id": api.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.post("/batchInsert", response_model=ResponseModel)
async def batch_insert(
    *,
    api_list: List[dict],
    db: AsyncSession = Depends(get_db)
):
    """批量创建API资源"""
    try:
        api_ids = []
        for api_data in api_list:
            api = ApiResource(
                name=api_data.get('name'),
                path=api_data.get('path'),
                method=api_data.get('method'),
                desc=api_data.get('desc')
            )
            db.add(api)
            await db.flush()
            api_ids.append(api.id)
        
        await db.commit()
        return RespModel.success(data={"ids": api_ids, "count": len(api_ids)}, msg=f"成功添加{len(api_ids)}条记录")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"批量添加失败: {str(e)}")


@router.put("/update", response_model=ResponseModel)
async def update(
    *,
    api_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新API资源"""
    try:
        api_id = api_data.get('id')
        result = await db.execute(select(ApiResource).where(ApiResource.id == api_id))
        api = result.scalars().first()
        if not api:
            raise NotFoundException("API资源不存在")
        
        # 更新字段
        if 'name' in api_data:
            api.name = api_data['name']
        if 'path' in api_data:
            api.path = api_data['path']
        if 'method' in api_data:
            api.method = api_data['method']
        if 'desc' in api_data:
            api.desc = api_data['desc']
        
        await db.commit()
        return RespModel.success(msg="修改成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=ResponseModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='API资源ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除API资源"""
    try:
        result = await db.execute(select(ApiResource).where(ApiResource.id == id))
        api = result.scalars().first()
        if not api:
            raise NotFoundException("API资源不存在")
        
        await db.delete(api)
        await db.commit()
        return RespModel.success(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/refresh", response_model=ResponseModel)
async def refresh(
    *,
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """刷新API资源列表（从项目API自动生成）"""
    try:
        project_id = data.get('project_id')
        
        if not project_id:
            from app.core.exceptions import BadRequestException
            raise BadRequestException("项目ID不能为空")
        
        # TODO: 从项目中自动生成API资源列表
        # 这里需要根据实际项目API结构来实现
        
        # 临时返回成功响应
        return RespModel.success(msg="刷新成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")
