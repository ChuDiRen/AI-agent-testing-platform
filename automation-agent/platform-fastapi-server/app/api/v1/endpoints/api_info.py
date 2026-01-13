"""
API 信息 API 端点
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional
from app.db.session import get_db
from app.schemas.api_info import ApiInfoCreate, ApiInfoUpdate, ApiInfoResponse, ApiInfoQuery
from app.models.api_info import ApiInfo
from app.core.resp_model import RespModel

router = APIRouter(prefix="/ApiInfo", tags=["API信息"])


@router.post("/queryByPage")
async def query_by_page(
    query: ApiInfoQuery,
    db: AsyncSession = Depends(get_db)
):
    """分页查询 API 信息"""
    try:
        filters = []
        if query.project_id:
            filters.append(ApiInfo.project_id == query.project_id)
        if query.module_id:
            filters.append(ApiInfo.module_id == query.module_id)
        if query.api_name:
            filters.append(ApiInfo.api_name.like(f'%{query.api_name}%'))
        
        # 构建查询
        query_obj = select(ApiInfo)
        if filters:
            query_obj = query_obj.filter(*filters)
        
        # 执行查询
        result = await db.execute(
            query_obj.offset((query.page - 1) * query.page_size).limit(query.page_size)
        )
        datas = result.scalars().all()
        
        # 查询总数
        count_result = await db.execute(
            select(func.count()).select_from(query_obj.subquery())
        )
        total = count_result.scalar()
        
        # 转换为响应格式
        data_list = []
        for data in datas:
            data_dict = {
                "id": data.id,
                "project_id": data.project_id,
                "module_id": data.module_id,
                "api_name": data.api_name,
                "request_method": data.request_method,
                "request_url": data.request_url,
                "request_params": data.request_params,
                "request_headers": data.request_headers,
                "debug_vars": data.debug_vars,
                "request_form_datas": data.request_form_datas,
                "request_www_form_datas": data.request_www_form_datas,
                "requests_json_data": data.requests_json_data,
                "request_files": data.request_files,
                "create_time": data.create_time.strftime('%Y-%m-%d %H:%M:%S') if data.create_time else ''
            }
            data_list.append(data_dict)
        
        return RespModel.ok_resp_list(data_list, total=total)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.get("/queryById")
async def query_by_id(
    id: int = Query(..., description="ID"),
    db: AsyncSession = Depends(get_db)
):
    """根据 ID 查询 API 信息"""
    try:
        result = await db.execute(
            select(ApiInfo).filter(ApiInfo.id == id)
        )
        data = result.scalars().first()
        
        if data:
            data_dict = {
                "id": data.id,
                "project_id": data.project_id,
                "module_id": data.module_id,
                "api_name": data.api_name,
                "request_method": data.request_method,
                "request_url": data.request_url,
                "request_params": data.request_params,
                "request_headers": data.request_headers,
                "debug_vars": data.debug_vars,
                "request_form_datas": data.request_form_datas,
                "request_www_form_datas": data.request_www_form_datas,
                "requests_json_data": data.requests_json_data,
                "request_files": data.request_files,
                "create_time": data.create_time.strftime('%Y-%m-%d %H:%M:%S') if data.create_time else ''
            }
            return RespModel.ok_resp(data_dict)
        else:
            return RespModel.ok_resp(msg="查询成功,但是没有数据")
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@router.post("/insert")
async def insert(
    obj_in: ApiInfoCreate,
    db: AsyncSession = Depends(get_db)
):
    """添加 API 信息"""
    try:
        db_obj = ApiInfo(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return RespModel.ok_resp(msg="添加成功", dic_t={"id": db_obj.id})
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update")
async def update(
    id: int = Query(..., description="ID"),
    obj_in: ApiInfoUpdate = None,
    db: AsyncSession = Depends(get_db)
):
    """更新 API 信息"""
    try:
        result = await db.execute(
            select(ApiInfo).filter(ApiInfo.id == id)
        )
        db_obj = result.scalars().first()
        
        if not db_obj:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="数据不存在")
        
        # 更新字段
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        return RespModel.ok_resp(msg="修改成功")
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete")
async def delete(
    id: int = Query(..., description="ID"),
    db: AsyncSession = Depends(get_db)
):
    """删除 API 信息"""
    try:
        result = await db.execute(
            select(ApiInfo).filter(ApiInfo.id == id)
        )
        db_obj = result.scalars().first()
        
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        
        return RespModel.ok_resp(msg="删除成功")
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
