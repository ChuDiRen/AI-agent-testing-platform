"""
API 测试计划图表端点
从 Flask 迁移到 FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.deps import get_db
from app.models.api_test_plan_chart import ApiTestPlanChart
from app.core.resp_model import respModel
from app.core.exceptions import NotFoundException, BadRequestException
from sqlalchemy import select, func

router = APIRouter(prefix="/ApiTestPlanChart", tags=["API测试计划图表"])


@router.get("/queryAll", response_model=respModel)
async def query_all(db: AsyncSession = Depends(get_db)):
    """查询所有测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart))
        items = result.scalars().all()
        return respModel().ok_resp_list(lst=items, msg="查询成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/queryByPage", response_model=respModel)
async def query_by_page(
    *,
    page: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    project_id: Optional[int] = Query(None, description='项目ID'),
    chart_name: Optional[str] = Query(None, description='图表名称'),
    db: AsyncSession = Depends(get_db)
):
    """分页查询测试计划图表"""
    try:
        query = select(ApiTestPlanChart)
        
        # 添加筛选条件
        if project_id:
            query = query.where(ApiTestPlanChart.project_id == project_id)
        
        if chart_name:
            query = query.where(ApiTestPlanChart.chart_name.like(f"%{chart_name}%"))
        
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
    id: int = Query(..., ge=1, description='测试计划图表ID'),
    db: AsyncSession = Depends(get_db)
):
    """根据ID查询测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart).where(ApiTestPlanChart.id == id))
        item = result.scalars().first()
        if not item:
            raise NotFoundException("测试计划图表不存在")
        return respModel().ok_resp(obj=item, msg="查询成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/insert", response_model=respModel)
async def insert(
    *,
    chart_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """创建测试计划图表"""
    try:
        chart = ApiTestPlanChart(**chart_data)
        db.add(chart)
        await db.flush()
        await db.commit()
        return respModel().ok_resp(dic_t={"id": chart.id}, msg="添加成功")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")


@router.put("/update", response_model=respModel)
async def update(
    *,
    id: int = Query(..., ge=1, description='测试计划图表ID'),
    chart_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """更新测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart).where(ApiTestPlanChart.id == id))
        chart = result.scalars().first()
        if not chart:
            raise NotFoundException("测试计划图表不存在")
        
        # 更新字段
        for field, value in chart_data.items():
            if hasattr(chart, field):
                setattr(chart, field, value)
        
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
    id: int = Query(..., ge=1, description='测试计划图表ID'),
    db: AsyncSession = Depends(get_db)
):
    """删除测试计划图表"""
    try:
        result = await db.execute(select(ApiTestPlanChart).where(ApiTestPlanChart.id == id))
        chart = result.scalars().first()
        if not chart:
            raise NotFoundException("测试计划图表不存在")
        
        await db.delete(chart)
        await db.commit()
        return respModel().ok_resp(msg="删除成功")
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
