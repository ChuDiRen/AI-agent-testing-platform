"""
API 测试用例步骤管理端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.api_info_case_step import ApiInfoCaseStep
from app.schemas.api_info_case_step import ApiInfoCaseStepCreate, ApiInfoCaseStepUpdate, ApiInfoCaseStepResponse
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func

router = APIRouter(prefix="/ApiInfoCaseStep", tags=["API测试用例步骤管理"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有测试用例步骤"""
    try:
        result = await db.execute(select(ApiInfoCaseStep))
        items = result.scalars().all()
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    api_case_info_id: Optional[int] = Query(None, description='用例ID'),
    key_word_id: Optional[int] = Query(None, description='关键字ID'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询测试用例步骤"""
    try:
        query = select(ApiInfoCaseStep)
        
        # 添加筛选条件
        if api_case_info_id:
            query = query.where(ApiInfoCaseStep.api_case_info_id == api_case_info_id)
        
        if key_word_id:
            query = query.where(ApiInfoCaseStep.key_word_id == key_word_id)
        
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
    id: int = Query(..., ge=1, description='测试用例步骤ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询测试用例步骤"""
    try:
        result = await db.execute(select(ApiInfoCaseStep).where(ApiInfoCaseStep.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("测试用例步骤不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    step_data: ApiInfoCaseStepCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建测试用例步骤"""
    try:
        step = ApiInfoCaseStep(**step_data.dict())
        db.add(step)
        await db.flush()
        await db.commit()
        return respModel().ok_resp(dic_t={"id": step.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='测试用例步骤ID'),
    step_data: ApiInfoCaseStepUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新测试用例步骤"""
    try:
        result = await db.execute(select(ApiInfoCaseStep).where(ApiInfoCaseStep.id == id))
        step = result.scalars().first()
        if not step:
            raise NotFoundException("测试用例步骤不存在")
        
        # 更新字段
        update_data = step_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(step, field, value)
        
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
    id: int = Query(..., ge=1, description='测试用例步骤ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除测试用例步骤"""
    try:
        result = await db.execute(select(ApiInfoCaseStep).where(ApiInfoCaseStep.id == id))
        step = result.scalars().first()
        if not step:
            raise NotFoundException("测试用例步骤不存在")
        
        await db.delete(step)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
