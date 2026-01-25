"""
API 元数据管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.services.api_meta import api_meta_crud
from app.schemas.api_meta import ApiMetaCreate, ApiMetaUpdate, ApiMetaResponse
from app.core.resp_model import RespModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/ApiMeta", tags=["API元数据管理"])


@router.get("/queryAll", response_model=ResponseModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有元数据"""
    try:
        items = await api_meta_crud.get_multi(db)
        return RespModel.success(data=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=ResponseModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_id: Optional[int] = Query(None, description='项目ID'),
    module_id: Optional[int] = Query(None, description='模块ID'),
    api_name: Optional[str] = Query(None, description='接口名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询元数据"""
    try:
        items, total = await api_meta_crud.get_multi_with_filters(
            db, 
            page=page, 
            page_size=page_size,
            project_id=project_id,
            module_id=module_id,
            api_name=api_name
        )
        return RespModel.success(data=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=ResponseModel)
async def query_by_id(
    *,
    id: int = Query(..., ge=1, description='元数据ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询元数据"""
    try:
        item = await api_meta_crud.get(db, id=id)
        if not item:
            raise NotFoundException("元数据不存在")
        return RespModel.success(data=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=ResponseModel)
async def insert(
    *,
    meta_data: ApiMetaCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建元数据"""
    try:
        item = await api_meta_crud.create(db, obj_in=meta_data)
        return RespModel.success(data={"id": item.id}, msg="添加成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=ResponseModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='元数据ID'),
    meta_data: ApiMetaUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新元数据"""
    try:
        item = await api_meta_crud.get(db, id=id)
        if not item:
            raise NotFoundException("元数据不存在")
        
        updated_item = await api_meta_crud.update(db, db_obj=item, obj_in=meta_data)
        return RespModel.success(msg="修改成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=ResponseModel)
async def delete(
    *,
    id: int = Query(..., ge=1, description='元数据ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除元数据"""
    try:
        item = await api_meta_crud.get(db, id=id)
        if not item:
            raise NotFoundException("元数据不存在")
        
        await api_meta_crud.remove(db, id=id)
        return RespModel.success(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.get("/downloadFile", response_model=ResponseModel)
async def download_file(
    *,
    id: int = Query(..., ge=1, description='元数据ID'),
    db: AsyncSession = Depends(get_db)
):
    """下载MinIO文件"""
    try:
        # 获取元数据信息
        result = await db.execute(select(ApiMeta).where(ApiMeta.id == id))
        data = result.scalars().first()
        
        if not data:
            raise NotFoundException("元数据不存在")
        
        # 获取object_url
        object_url = data.object_url
        if not object_url:
            raise BadRequestException("获取下载地址失败，文件不存在")
        
        # MinIO客户端URL配置
        minio_client_url = "http://localhost:9000"  # 可以从配置中获取
        
        return RespModel.success(
            data={
                "downloadUrl": f"{minio_client_url}{object_url}"
            },
            msg="获取到下载地址"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
