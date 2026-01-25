"""
API 关键字管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.services.api_keyword import api_keyword_crud
from app.schemas.api_keyword import ApiKeyWordCreate, ApiKeyWordUpdate, ApiKeyWordResponse
from app.core.resp_model import RespModel, ResponseModel
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter(prefix="/ApiKeyWord", tags=["API关键字管理"])


@router.get("/queryAll", response_model=ResponseModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有关键字"""
    try:
        items = await api_keyword_crud.get_multi(db)
        return RespModel.success(data=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=ResponseModel)
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
        return RespModel.success(data=items, total=total)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/queryById", response_model=ResponseModel)
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
        return RespModel.success(data=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=ResponseModel)
async def insert(
    *,
    keyword_data: ApiKeyWordCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建关键字"""
    try:
        item = await api_keyword_crud.create(db, obj_in=keyword_data)
        return RespModel.success(data={"id": item.id}, msg="添加成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=ResponseModel)
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
        return RespModel.success(msg="修改成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"修改失败: {str(e)}")


@router.delete("/delete", response_model=ResponseModel)
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
        return RespModel.success(msg="删除成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@router.post("/keywordFile", response_model=ResponseModel)
async def keyword_file(
    *,
    keyword_fun_name: str = Query(..., description='方法名'),
    keyword_value: str = Query(..., description='方法体'),
    db: AsyncSession = Depends(get_db)
):
    """生成关键字Python文件"""
    try:
        import os
        
        # 关键字目录
        key_words_dir = os.path.join(os.getcwd(), "keywords")
        os.makedirs(key_words_dir, exist_ok=True)
        
        # 生成Python文件
        file_path = os.path.join(key_words_dir, f"{keyword_fun_name}.py")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(keyword_value)
        
        return RespModel.success(
            data={"id": keyword_fun_name},
            msg="生成文件成功"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成文件失败: {str(e)}")


@router.get("/queryAllKeyWordList", response_model=ResponseModel)
async def query_all_keyword_list(db: AsyncSession = Depends(get_db)):
    """查询所有关键字数据，生成联级数据"""
    try:
        from app.models.api_operation_type import ApiOperationType
        
        # 获取所有操作类型
        result = await db.execute(select(ApiOperationType))
        all_operation_types = result.scalars().all()
        
        all_datas = []
        
        for operation_type in all_operation_types:
            # 初始数据
            apidata = {
                "id": operation_type.id,
                "value": operation_type.ex_fun_name,
                "label": operation_type.operation_type_name,
                "children": []
            }
            
            # 查询当前操作类型对应的关键字
            keyword_result = await db.execute(
                select(ApiKeyWord).where(ApiKeyWord.operation_type_id == operation_type.id)
            )
            keyword_data = keyword_result.scalars().all()
            
            for keyword in keyword_data:
                child_data = {
                    "id": keyword.id,
                    "value": keyword.keyword_fun_name,
                    "label": keyword.name,
                    "keyword_desc": keyword.keyword_desc
                }
                apidata["children"].append(child_data)
            
            all_datas.append(apidata)
        
        return RespModel.success(data=all_datas, msg="查询成功")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")
